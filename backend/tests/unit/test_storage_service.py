# tests/unit/test_storage_service.py
"""
Unit tests for StorageService (app.services.storage).

'Unit' here means: the full StorageService object is exercised against an
AsyncMock S3 client — no real network, no database, no filesystem I/O.
This is the correct layer for testing async service behaviour, S3 API call
conventions, and error propagation.

Fixtures:
  ``s3_mock``      — AsyncMock representing the S3 client inside the context manager
  ``make_service`` — factory that injects s3_mock into a real StorageService instance

Covered methods:
  StorageService.upload_file()
  StorageService.get_download_url()
  StorageService._build_public_url()
  StorageService.ensure_bucket_exists()
  StorageService.delete_file()
"""

from __future__ import annotations

import io
import json
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest
from botocore.exceptions import ClientError

from app.services.storage import StorageService


# ---------------------------------------------------------------------------
# Helpers / shared fixtures
# ---------------------------------------------------------------------------


def _client_error(code: str) -> ClientError:
    """Construct a minimal botocore ClientError with the given error code."""
    return ClientError(
        error_response={"Error": {"Code": code, "Message": "test"}},
        operation_name="TestOp",
    )


@pytest.fixture()
def s3_mock() -> AsyncMock:
    """A mock S3 client whose methods are all AsyncMocks."""
    return AsyncMock()


@pytest.fixture()
def make_service(s3_mock: AsyncMock):
    """Factory: return a real StorageService with its S3 client patched.

    Usage::

        def test_something(make_service, s3_mock):
            svc = make_service()                  # defaults
            svc = make_service(presigned=True)    # presigned downloads
            svc = make_service(configured=False)  # unconfigured storage
    """
    def _factory(
        *,
        configured: bool = True,
        presigned: bool = False,
        endpoint: str = "http://localhost:9000",
        public_url: str = "http://localhost:9000",
        bucket: str = "test-bucket",
        region: str = "us-east-1",
        expiry: int = 3600,
    ) -> StorageService:
        @asynccontextmanager
        async def _fake_client(*args, **kwargs):
            yield s3_mock

        mock_session = MagicMock()
        mock_session.client = _fake_client

        svc = object.__new__(StorageService)
        svc._session = mock_session
        svc._bucket = bucket
        svc._endpoint = endpoint
        svc._public_url = public_url
        svc._region = region
        svc._access_key = "key" if configured else None
        svc._secret_key = "secret" if configured else None
        svc._configured = configured
        svc._presigned_downloads = presigned
        svc._presigned_expiry = expiry
        return svc

    return _factory


# ---------------------------------------------------------------------------
# TestUploadFile
# ---------------------------------------------------------------------------


class TestUploadFile:
    """upload_file() uploads a file object and returns an object key (not a URL)."""

    async def test_happy_path_returns_object_key(self, make_service, s3_mock) -> None:
        """Successful upload returns an 'uploads/...' object key."""
        svc = make_service()
        key = await svc.upload_file(io.BytesIO(b"data"), "report.pdf", "application/pdf")

        s3_mock.upload_fileobj.assert_called_once()
        assert key.startswith("uploads/")
        assert key.endswith("-report.pdf")

    async def test_returned_key_is_never_a_full_url(self, make_service, s3_mock) -> None:
        """The object key must not start with 'http' — it is a path, not a URL."""
        svc = make_service()
        key = await svc.upload_file(io.BytesIO(b"data"), "file.pdf")

        assert not key.startswith("http"), (
            f"upload_file returned a full URL instead of an object key: {key!r}"
        )

    async def test_unconfigured_storage_returns_stub_key(self, make_service, s3_mock) -> None:
        """When no credentials are set, a 'local/' stub key is returned without S3 I/O."""
        svc = make_service(configured=False)
        key = await svc.upload_file(io.BytesIO(b"data"), "file.pdf")

        assert key.startswith("local/")
        s3_mock.upload_fileobj.assert_not_called()

    async def test_s3_client_error_raises_app_exception(self, make_service, s3_mock) -> None:
        """An S3 ClientError must be wrapped in AppException (HTTP 500)."""
        from app.exceptions import AppException

        svc = make_service()
        s3_mock.upload_fileobj.side_effect = _client_error("InternalError")

        with pytest.raises(AppException) as exc_info:
            await svc.upload_file(io.BytesIO(b"data"), "bad.pdf")

        assert exc_info.value.status_code == 500


# ---------------------------------------------------------------------------
# TestGetDownloadUrl
# ---------------------------------------------------------------------------


class TestGetDownloadUrl:
    """get_download_url() returns the appropriate URL for a given object key."""

    async def test_public_mode_builds_url_from_public_base(self, make_service) -> None:
        """In public mode (presigned=False), returns a plain URL from the public base URL."""
        svc = make_service(presigned=False, public_url="http://localhost:9000", bucket="ams-bucket")
        url = await svc.get_download_url("uploads/abc-file.pdf")
        assert url == "http://localhost:9000/ams-bucket/uploads/abc-file.pdf"

    async def test_public_mode_never_exposes_internal_hostname(self, make_service) -> None:
        """When STORAGE_ENDPOINT_URL is an internal Docker hostname, it must not leak into URLs."""
        svc = make_service(
            presigned=False,
            endpoint="http://minio:9000",      # internal Docker host
            public_url="http://localhost:9000",  # browser-accessible
            bucket="ams-bucket",
        )
        url = await svc.get_download_url("uploads/test.pdf")
        assert "minio" not in url, "Internal Docker hostname must not appear in download URLs"
        assert "localhost:9000" in url

    async def test_presigned_mode_delegates_to_s3(self, make_service, s3_mock) -> None:
        """In presigned mode, generate_presigned_url is called with correct parameters."""
        s3_mock.generate_presigned_url.return_value = "https://signed.example.com/token"
        svc = make_service(presigned=True, expiry=1800)

        url = await svc.get_download_url("uploads/secret.pdf")

        s3_mock.generate_presigned_url.assert_called_once_with(
            "get_object",
            Params={"Bucket": "test-bucket", "Key": "uploads/secret.pdf"},
            ExpiresIn=1800,
        )
        assert url == "https://signed.example.com/token"

    async def test_local_stub_key_passthrough(self, make_service, s3_mock) -> None:
        """A key prefixed with 'local/' is returned unchanged without any S3 call."""
        svc = make_service()
        url = await svc.get_download_url("local/uploads/stub.pdf")
        assert url == "local/uploads/stub.pdf"
        s3_mock.generate_presigned_url.assert_not_called()

    async def test_unconfigured_passthrough(self, make_service, s3_mock) -> None:
        """When storage is not configured, the key itself is returned as a best-effort."""
        svc = make_service(configured=False)
        url = await svc.get_download_url("uploads/some-key.pdf")
        assert url == "uploads/some-key.pdf"


# ---------------------------------------------------------------------------
# TestBuildPublicUrl
# ---------------------------------------------------------------------------


class TestBuildPublicUrl:
    """_build_public_url() constructs a plain HTTP download URL from config.

    This is a synchronous pure-function test — no mocking needed.
    """

    def test_basic_url_format(self, make_service) -> None:
        """URL is: <public_base>/<bucket>/<key>."""
        svc = make_service(public_url="http://localhost:9000", bucket="ams-bucket")
        url = svc._build_public_url("uploads/abc-file.pdf")
        assert url == "http://localhost:9000/ams-bucket/uploads/abc-file.pdf"

    def test_trailing_slash_on_base_is_stripped(self, make_service) -> None:
        """A trailing slash on public_url must not produce a double slash."""
        svc = make_service(public_url="http://localhost:9000/", bucket="my-bucket")
        url = svc._build_public_url("uploads/test.pdf")
        assert url == "http://localhost:9000/my-bucket/uploads/test.pdf"
        assert "//" not in url.replace("http://", "").replace("https://", "")

    def test_falls_back_to_aws_url_when_no_public_url(self, make_service) -> None:
        """When public_url is None, produces an AWS S3-style URL using the region."""
        svc = make_service(public_url="http://localhost:9000", region="eu-west-1", bucket="prod-bucket")
        svc._public_url = None  # type: ignore[attr-defined]  # force the fallback path

        url = svc._build_public_url("uploads/report.pdf")

        assert "s3.eu-west-1.amazonaws.com" in url
        assert "prod-bucket" in url
        assert "uploads/report.pdf" in url


# ---------------------------------------------------------------------------
# TestEnsureBucketExists
# ---------------------------------------------------------------------------


class TestEnsureBucketExists:
    """ensure_bucket_exists() is an idempotent startup helper called by lifespan."""

    async def test_creates_bucket_when_404(self, make_service, s3_mock) -> None:
        """When head_bucket returns 404 the bucket is created."""
        svc = make_service()
        s3_mock.head_bucket.side_effect = _client_error("404")
        s3_mock.put_bucket_policy.return_value = {}

        await svc.ensure_bucket_exists()

        s3_mock.create_bucket.assert_called_once_with(Bucket="test-bucket")

    async def test_skips_create_when_bucket_already_exists(self, make_service, s3_mock) -> None:
        """When head_bucket succeeds, create_bucket is never called."""
        svc = make_service()
        s3_mock.head_bucket.return_value = {}
        s3_mock.put_bucket_policy.return_value = {}

        await svc.ensure_bucket_exists()

        s3_mock.create_bucket.assert_not_called()

    async def test_applies_public_read_policy_in_public_mode(self, make_service, s3_mock) -> None:
        """In public mode, put_bucket_policy is called with a valid public-read statement."""
        svc = make_service(presigned=False)
        s3_mock.head_bucket.return_value = {}
        s3_mock.put_bucket_policy.return_value = {}

        await svc.ensure_bucket_exists()

        s3_mock.put_bucket_policy.assert_called_once()
        call_kwargs = s3_mock.put_bucket_policy.call_args.kwargs
        policy = json.loads(call_kwargs["Policy"])
        stmt = policy["Statement"][0]
        assert stmt["Effect"] == "Allow"
        assert stmt["Action"] == ["s3:GetObject"]
        assert "*" in str(stmt["Principal"])

    async def test_does_not_apply_policy_in_presigned_mode(self, make_service, s3_mock) -> None:
        """In presigned mode the bucket stays private — no put_bucket_policy call."""
        svc = make_service(presigned=True)
        s3_mock.head_bucket.return_value = {}

        await svc.ensure_bucket_exists()

        s3_mock.put_bucket_policy.assert_not_called()

    async def test_no_op_when_not_configured(self, make_service, s3_mock) -> None:
        """Unconfigured storage logs a warning and returns without touching S3."""
        svc = make_service(configured=False)
        await svc.ensure_bucket_exists()
        s3_mock.head_bucket.assert_not_called()

    async def test_non_404_client_error_is_swallowed(self, make_service, s3_mock) -> None:
        """Unexpected S3 errors are caught and logged so the application still starts."""
        svc = make_service()
        s3_mock.head_bucket.side_effect = _client_error("InternalError")
        # Must not raise — errors are logged, not propagated
        await svc.ensure_bucket_exists()


# ---------------------------------------------------------------------------
# TestDeleteFile
# ---------------------------------------------------------------------------


class TestDeleteFile:
    """delete_file() removes an object from the bucket."""

    async def test_calls_s3_delete_object(self, make_service, s3_mock) -> None:
        """Deleting a real object key issues a delete_object call."""
        svc = make_service()
        s3_mock.delete_object.return_value = {}

        await svc.delete_file("uploads/old-file.pdf")

        s3_mock.delete_object.assert_called_once_with(
            Bucket="test-bucket", Key="uploads/old-file.pdf"
        )

    async def test_no_op_for_local_stub_key(self, make_service, s3_mock) -> None:
        """'local/' prefixed keys are skipped — no S3 call is made."""
        svc = make_service()
        await svc.delete_file("local/uploads/stub.pdf")
        s3_mock.delete_object.assert_not_called()

    async def test_no_op_when_not_configured(self, make_service, s3_mock) -> None:
        """Unconfigured storage skips the delete silently."""
        svc = make_service(configured=False)
        await svc.delete_file("uploads/some-file.pdf")
        s3_mock.delete_object.assert_not_called()

    async def test_s3_delete_error_raises_app_exception(self, make_service, s3_mock) -> None:
        """A ClientError during delete is wrapped in AppException (HTTP 500)."""
        from app.exceptions import AppException

        svc = make_service()
        s3_mock.delete_object.side_effect = _client_error("InternalError")

        with pytest.raises(AppException) as exc_info:
            await svc.delete_file("uploads/file.pdf")

        assert exc_info.value.status_code == 500
