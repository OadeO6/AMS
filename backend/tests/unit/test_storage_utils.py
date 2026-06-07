# tests/unit/test_storage_utils.py
"""
Unit tests for pure storage utility logic.

These tests are fast, synchronous, and require no I/O, no mocking, and no
external services.  Each test is a simple call-and-assert.

Covered modules / functions:
  - alembic migration ``_extract_key()``
        Parses full S3/MinIO URLs back to plain object keys.  The migration
        runs once against live data; we verify the extraction logic in isolation.
  - ``StorageService._build_public_url()``
        Pure string construction from the configured public base URL.
  - ``app.config.Settings`` storage convenience properties
        Credential resolution with STORAGE_* → AWS_* fallback chain.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import types

import pytest

# ---------------------------------------------------------------------------
# Load the migration module via importlib.
#
# The migration filename starts with a digit (20260607_...) which makes it a
# SyntaxError to use in a standard ``from alembic.versions.20260607_... import``
# statement.  We use importlib to load it by file path instead, registering it
# under a sanitised module name so it is importable by the rest of the test.
# ---------------------------------------------------------------------------

_MIGRATION_FILE = (
    pathlib.Path(__file__).parents[2]  # backend/
    / "alembic"
    / "versions"
    / "20260607_1600_strip_material_file_urls.py"
)

_MIGRATION_MODULE_NAME = "migration_strip_material_file_urls"

if _MIGRATION_MODULE_NAME not in sys.modules:
    # Stub out the `alembic.op` dependency so the module-level import of
    # ``from alembic import op`` doesn't try to connect to a real database.
    alembic_stub = types.ModuleType("alembic")
    alembic_stub.op = types.SimpleNamespace(get_bind=lambda: None)  # type: ignore[attr-defined]
    sys.modules.setdefault("alembic", alembic_stub)
    sys.modules.setdefault("alembic.op", alembic_stub)

    _spec = importlib.util.spec_from_file_location(_MIGRATION_MODULE_NAME, _MIGRATION_FILE)
    assert _spec and _spec.loader, f"Could not locate migration: {_MIGRATION_FILE}"
    _migration = importlib.util.module_from_spec(_spec)
    sys.modules[_MIGRATION_MODULE_NAME] = _migration
    _spec.loader.exec_module(_migration)  # type: ignore[union-attr]

from migration_strip_material_file_urls import _extract_key  # noqa: E402


# ---------------------------------------------------------------------------
# Section 1 — Migration key extraction (_extract_key)
# ---------------------------------------------------------------------------


class TestExtractKey:
    """_extract_key strips the host/bucket prefix, leaving the object key.

    The function must handle three real-world URL patterns that may be present
    in the database after the original (buggy) StorageService produced full URLs.
    """

    def test_aws_subdomain_style(self) -> None:
        """AWS subdomain-style URL: bucket as subdomain, path contains key."""
        url = "https://ams-storage-bucket.s3.amazonaws.com/uploads/abc-file.pdf"
        assert _extract_key(url) == "uploads/abc-file.pdf"

    def test_aws_path_style(self) -> None:
        """AWS path-style URL: bucket as first path segment."""
        url = "https://s3.amazonaws.com/ams-storage-bucket/uploads/abc-file.pdf"
        assert _extract_key(url) == "uploads/abc-file.pdf"

    def test_minio_path_style(self) -> None:
        """MinIO local URL: host:port/bucket/key format."""
        url = "http://minio:9000/ams-storage-bucket/uploads/abc-file.pdf"
        assert _extract_key(url) == "uploads/abc-file.pdf"

    def test_localhost_minio_style(self) -> None:
        """Localhost MinIO URL as returned during local development."""
        url = "http://localhost:9000/ams-storage-bucket/uploads/80d23282-ECE506.pdf"
        assert _extract_key(url) == "uploads/80d23282-ECE506.pdf"

    def test_already_a_key_is_returned_unchanged(self) -> None:
        """A plain object key with no 'uploads/' prefix is left untouched.

        This is a safe-by-default behaviour — we never corrupt data we don't
        recognise.
        """
        key = "uploads/plain-object-key.pdf"
        assert _extract_key(key) == key

    def test_unknown_format_returned_unchanged(self) -> None:
        """An URL that contains no 'uploads/' segment is returned as-is.

        This prevents silent data corruption for unexpected legacy formats.
        """
        weird = "http://some-cdn.example.com/files/document.pdf"
        assert _extract_key(weird) == weird

    def test_preserves_uuid_in_key(self) -> None:
        """The UUID portion of the key is preserved exactly."""
        uid = "80d23282-8fb7-4907-b8a1-8dabcac8e131"
        url = f"https://bucket.s3.amazonaws.com/uploads/{uid}-ECE_506.pdf"
        key = _extract_key(url)
        assert uid in key
        assert key == f"uploads/{uid}-ECE_506.pdf"


# ---------------------------------------------------------------------------
# Section 2 — Public URL construction (StorageService._build_public_url)
# ---------------------------------------------------------------------------


def _make_bare_service(
    *,
    public_url: str | None,
    bucket: str = "my-bucket",
    region: str = "us-east-1",
) -> object:
    """Return a minimal object that has the same _build_public_url logic.

    We bypass the full StorageService constructor (which reads live settings)
    by patching attributes directly on a bare instance.
    """
    from app.services.storage import StorageService

    svc = object.__new__(StorageService)
    svc._public_url = public_url  # type: ignore[attr-defined]
    svc._bucket = bucket  # type: ignore[attr-defined]
    svc._region = region  # type: ignore[attr-defined]
    return svc


class TestBuildPublicUrl:
    """StorageService._build_public_url constructs a plain HTTP download URL."""

    def test_basic_url_format(self) -> None:
        """URL is: <public_base>/<bucket>/<key>."""
        svc = _make_bare_service(public_url="http://localhost:9000", bucket="ams-bucket")
        url = svc._build_public_url("uploads/abc-file.pdf")  # type: ignore[attr-defined]
        assert url == "http://localhost:9000/ams-bucket/uploads/abc-file.pdf"

    def test_trailing_slash_on_base_is_stripped(self) -> None:
        """A trailing slash on public_url must not produce a double slash."""
        svc = _make_bare_service(public_url="http://localhost:9000/", bucket="ams-bucket")
        url = svc._build_public_url("uploads/file.pdf")  # type: ignore[attr-defined]
        # Verify there's no // after stripping the scheme
        assert "//" not in url.replace("http://", "").replace("https://", "")

    def test_falls_back_to_aws_url_when_no_public_url(self) -> None:
        """When public_url is None, produces an AWS S3-style URL using the region."""
        svc = _make_bare_service(public_url=None, bucket="prod-bucket", region="eu-west-1")
        url = svc._build_public_url("uploads/report.pdf")  # type: ignore[attr-defined]
        assert "s3.eu-west-1.amazonaws.com" in url
        assert "prod-bucket" in url
        assert "uploads/report.pdf" in url

    def test_internal_docker_hostname_does_not_appear_in_public_url(self) -> None:
        """The internal Docker hostname must never be exposed in the download URL."""
        svc = _make_bare_service(public_url="http://localhost:9000", bucket="ams-bucket")
        url = svc._build_public_url("uploads/test.pdf")  # type: ignore[attr-defined]
        assert "minio" not in url, (
            "Internal Docker hostname 'minio' must not appear in the public download URL"
        )


# ---------------------------------------------------------------------------
# Section 3 — Settings storage property resolution
# ---------------------------------------------------------------------------


def _make_settings(**kwargs: object) -> object:
    """Instantiate Settings with only the minimum required fields plus overrides.

    Passes ``_env_file=None`` to suppress pydantic-settings' automatic .env
    file loading, ensuring each test starts from a clean baseline regardless
    of what is configured on the developer's machine.
    """
    from app.config import Settings

    base: dict[str, object] = {
        "DATABASE_URL": "postgresql+asyncpg://u:p@localhost/db",
        "REDIS_URL": "redis://localhost:6379/0",
        "SECRET_KEY": "test-secret-key-at-least-32-chars-long!",
        "ENVIRONMENT": "local",
    }
    base.update(kwargs)
    # _env_file=None is a pydantic-settings init kwarg that prevents the
    # class from reading the project's real .env file, so each test sees only
    # the values we explicitly pass in.
    return Settings(_env_file=None, **base)  # type: ignore[call-arg]


class TestStorageSettingsProperties:
    """Settings convenience properties resolve credentials correctly.

    The STORAGE_* names are preferred; the legacy AWS_* / S3_* names serve as
    a fallback for one release cycle.
    """

    def test_storage_configured_true_when_both_keys_set(self) -> None:
        s = _make_settings(STORAGE_ACCESS_KEY="key", STORAGE_SECRET_KEY="secret")
        assert s.storage_configured is True  # type: ignore[attr-defined]

    def test_storage_configured_false_when_keys_absent(self) -> None:
        s = _make_settings()
        assert s.storage_configured is False  # type: ignore[attr-defined]

    def test_storage_access_key_prefers_storage_over_aws(self) -> None:
        s = _make_settings(STORAGE_ACCESS_KEY="new-key", AWS_ACCESS_KEY_ID="old-key")
        assert s.storage_access_key == "new-key"  # type: ignore[attr-defined]

    def test_storage_access_key_falls_back_to_aws(self) -> None:
        """When STORAGE_ACCESS_KEY is absent, falls back to AWS_ACCESS_KEY_ID."""
        s = _make_settings(AWS_ACCESS_KEY_ID="aws-key")
        assert s.storage_access_key == "aws-key"  # type: ignore[attr-defined]

    def test_storage_bucket_s3_overrides_storage_bucket_name(self) -> None:
        """S3_BUCKET_NAME takes precedence over STORAGE_BUCKET_NAME.

        The ``storage_bucket`` property is ``S3_BUCKET_NAME or STORAGE_BUCKET_NAME``,
        so the legacy S3 variable wins when both are present.  This is the documented
        fallback chain for this release cycle.
        """
        s = _make_settings(STORAGE_BUCKET_NAME="storage-bucket", S3_BUCKET_NAME="s3-bucket")
        assert s.storage_bucket == "s3-bucket"  # type: ignore[attr-defined]

    def test_storage_bucket_falls_back_to_s3(self) -> None:
        """When STORAGE_BUCKET_NAME is at default, S3_BUCKET_NAME wins."""
        s = _make_settings(S3_BUCKET_NAME="legacy-bucket")
        # S3_BUCKET_NAME takes precedence when STORAGE_BUCKET_NAME is default
        assert s.storage_bucket == "legacy-bucket"  # type: ignore[attr-defined]

    def test_storage_public_url_returns_endpoint_when_not_set(self) -> None:
        """storage_public_url falls back to storage_endpoint_url when unset."""
        s = _make_settings(STORAGE_ENDPOINT_URL="http://localhost:9000")
        assert s.storage_public_url == "http://localhost:9000"  # type: ignore[attr-defined]

    def test_storage_public_url_overrides_endpoint(self) -> None:
        """STORAGE_PUBLIC_URL is returned as-is, independent of STORAGE_ENDPOINT_URL."""
        s = _make_settings(
            STORAGE_ENDPOINT_URL="http://minio:9000",
            STORAGE_PUBLIC_URL="http://localhost:9000",
        )
        assert s.storage_public_url == "http://localhost:9000"  # type: ignore[attr-defined]
