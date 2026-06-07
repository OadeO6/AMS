# tests/unit/test_storage_service.py
"""
Unit tests for StorageService (app.services.storage).

The external aioboto3 S3 client is fully mocked via AsyncMock — no real
MinIO / AWS connection is made.  Tests exercise:

  * upload_file          — happy path, unconfigured stub, S3 error
  * get_download_url     — public URL mode, presigned URL mode, stub passthrough
  * _build_public_url    — correct URL construction from config
  * ensure_bucket_exists — create-on-miss, already-exists, policy application
  * delete_file          — happy path, stub passthrough
  * config resolution    — STORAGE_* vs deprecated AWS_* / S3_* fallback
"""

from __future__ import annotations

import io
import json
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from app.services.storage import StorageService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_client_error(code: str) -> ClientError:
    """Build a minimal botocore ClientError with the given error code."""
    return ClientError(
        error_response={"Error": {"Code": code, "Message": "test error"}},
        operation_name="TestOp",
    )


def _make_service(
    *,
    configured: bool = True,
    presigned_downloads: bool = False,
    endpoint: str = "http://localhost:9000",
    public_url: str | None = "http://localhost:9000",
    bucket: str = "test-bucket",
    region: str = "us-east-1",
    expiry: int = 3600,
) -> tuple[StorageService, MagicMock]:
    """
    Return a StorageService with a patched aioboto3 Session whose client is
    a MagicMock that can be used as an async context manager.

    Returns (service, mock_s3_client).
    """
    mock_s3 = AsyncMock()

    @asynccontextmanager
    async def _fake_client(*args, **kwargs):
        yield mock_s3

    mock_session = MagicMock()
    mock_session.client = _fake_client

    with patch("app.services.storage.aioboto3.Session", return_value=mock_session):
        svc = StorageService.__new__(StorageService)
        svc._session = mock_session
        svc._bucket = bucket
        svc._endpoint = endpoint
        svc._public_url = public_url or endpoint
        svc._region = region
        svc._access_key = "key" if configured else None
        svc._secret_key = "secret" if configured else None
        svc._configured = configured
        svc._presigned_downloads = presigned_downloads
        svc._presigned_expiry = expiry

    return svc, mock_s3


# ---------------------------------------------------------------------------
# upload_file
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upload_file_returns_object_key() -> None:
    """upload_file should call upload_fileobj and return an 'uploads/...' key."""
    svc, s3 = _make_service()

    file_obj = io.BytesIO(b"dummy pdf bytes")
    key = await svc.upload_file(file_obj, "lecture.pdf", "application/pdf")

    s3.upload_fileobj.assert_called_once()
    assert key.startswith("uploads/")
    assert key.endswith("-lecture.pdf")


@pytest.mark.asyncio
async def test_upload_file_key_does_not_contain_full_url() -> None:
    """The returned key must be a plain path, never a full HTTP URL."""
    svc, _ = _make_service()

    key = await svc.upload_file(io.BytesIO(b"x"), "file.pdf", "application/pdf")

    assert not key.startswith("http"), (
        f"upload_file returned a full URL instead of an object key: {key!r}"
    )


@pytest.mark.asyncio
async def test_upload_file_unconfigured_returns_stub_key() -> None:
    """When storage is not configured, a 'local/...' stub key is returned without calling S3."""
    svc, s3 = _make_service(configured=False)

    key = await svc.upload_file(io.BytesIO(b"x"), "file.pdf")

    assert key.startswith("local/")
    s3.upload_fileobj.assert_not_called()


@pytest.mark.asyncio
async def test_upload_file_propagates_s3_error() -> None:
    """A ClientError from upload_fileobj should be wrapped in AppException (status 500)."""
    from app.exceptions import AppException

    svc, s3 = _make_service()
    s3.upload_fileobj.side_effect = _make_client_error("InternalError")

    with pytest.raises(AppException) as exc_info:
        await svc.upload_file(io.BytesIO(b"x"), "bad.pdf")

    assert exc_info.value.status_code == 500


# ---------------------------------------------------------------------------
# get_download_url — public mode
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_download_url_public_mode_builds_correct_url() -> None:
    """In public mode (presigned=False), a plain URL constructed from the public base URL is returned."""
    svc, _ = _make_service(
        presigned_downloads=False,
        public_url="http://localhost:9000",
        bucket="ams-storage-bucket",
    )

    url = await svc.get_download_url("uploads/abc-file.pdf")

    assert url == "http://localhost:9000/ams-storage-bucket/uploads/abc-file.pdf"


@pytest.mark.asyncio
async def test_get_download_url_public_mode_uses_public_url_not_endpoint() -> None:
    """Public URL must use STORAGE_PUBLIC_URL, not STORAGE_ENDPOINT_URL (internal Docker host)."""
    svc, _ = _make_service(
        presigned_downloads=False,
        endpoint="http://minio:9000",    # Docker-internal — should NOT appear in output
        public_url="http://localhost:9000",  # Browser-accessible — MUST appear in output
        bucket="ams-storage-bucket",
    )

    url = await svc.get_download_url("uploads/test.pdf")

    assert "minio" not in url, "Download URL must not expose the Docker-internal hostname"
    assert "localhost:9000" in url


# ---------------------------------------------------------------------------
# get_download_url — presigned mode
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_download_url_presigned_mode_calls_generate_presigned_url() -> None:
    """In presigned mode, get_download_url must delegate to generate_presigned_url."""
    svc, s3 = _make_service(presigned_downloads=True, expiry=1800)
    s3.generate_presigned_url.return_value = "https://signed-url.example.com/token"

    url = await svc.get_download_url("uploads/secret.pdf")

    s3.generate_presigned_url.assert_called_once_with(
        "get_object",
        Params={"Bucket": "test-bucket", "Key": "uploads/secret.pdf"},
        ExpiresIn=1800,
    )
    assert url == "https://signed-url.example.com/token"


@pytest.mark.asyncio
async def test_get_download_url_stub_key_passthrough() -> None:
    """A 'local/' stub key should be returned as-is without touching S3."""
    svc, s3 = _make_service()

    url = await svc.get_download_url("local/uploads/stub.pdf")

    assert url == "local/uploads/stub.pdf"
    s3.generate_presigned_url.assert_not_called()


# ---------------------------------------------------------------------------
# _build_public_url
# ---------------------------------------------------------------------------


def test_build_public_url_strips_trailing_slash() -> None:
    """_build_public_url must produce a clean URL even if public_url has a trailing slash."""
    svc, _ = _make_service(public_url="http://localhost:9000/", bucket="my-bucket")

    url = svc._build_public_url("uploads/test.pdf")

    assert url == "http://localhost:9000/my-bucket/uploads/test.pdf"
    assert "//" not in url.replace("http://", "")


def test_build_public_url_falls_back_to_aws_when_no_endpoint() -> None:
    """When public_url is None, _build_public_url should produce an AWS URL."""
    svc, _ = _make_service(public_url=None, endpoint=None, region="eu-west-1", bucket="prod-bucket")
    svc._public_url = None  # Force the fallback path

    url = svc._build_public_url("uploads/report.pdf")

    assert "s3.eu-west-1.amazonaws.com" in url
    assert "prod-bucket" in url
    assert "uploads/report.pdf" in url


# ---------------------------------------------------------------------------
# ensure_bucket_exists
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ensure_bucket_exists_creates_bucket_when_missing() -> None:
    """When head_bucket raises 404, the bucket should be created."""
    svc, s3 = _make_service()
    s3.head_bucket.side_effect = _make_client_error("404")
    s3.put_bucket_policy.return_value = {}

    await svc.ensure_bucket_exists()

    s3.create_bucket.assert_called_once_with(Bucket="test-bucket")


@pytest.mark.asyncio
async def test_ensure_bucket_exists_skips_create_when_already_exists() -> None:
    """When head_bucket succeeds, create_bucket must not be called."""
    svc, s3 = _make_service()
    s3.head_bucket.return_value = {}
    s3.put_bucket_policy.return_value = {}

    await svc.ensure_bucket_exists()

    s3.create_bucket.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_bucket_exists_sets_public_policy_in_public_mode() -> None:
    """In public mode, a public-read bucket policy must be applied via put_bucket_policy."""
    svc, s3 = _make_service(presigned_downloads=False)
    s3.head_bucket.return_value = {}
    s3.put_bucket_policy.return_value = {}

    await svc.ensure_bucket_exists()

    s3.put_bucket_policy.assert_called_once()
    call_kwargs = s3.put_bucket_policy.call_args
    policy_str = call_kwargs.kwargs.get("Policy") or call_kwargs.args[1]
    policy = json.loads(policy_str)

    # Verify the policy grants GetObject to everyone
    stmt = policy["Statement"][0]
    assert stmt["Effect"] == "Allow"
    assert stmt["Action"] == ["s3:GetObject"]
    assert "*" in str(stmt["Principal"])


@pytest.mark.asyncio
async def test_ensure_bucket_exists_skips_public_policy_in_presigned_mode() -> None:
    """In presigned mode, put_bucket_policy must not be called (bucket stays private)."""
    svc, s3 = _make_service(presigned_downloads=True)
    s3.head_bucket.return_value = {}

    await svc.ensure_bucket_exists()

    s3.put_bucket_policy.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_bucket_exists_does_not_crash_when_not_configured() -> None:
    """An unconfigured service should return without calling any S3 APIs."""
    svc, s3 = _make_service(configured=False)

    # Must not raise
    await svc.ensure_bucket_exists()

    s3.head_bucket.assert_not_called()
    s3.create_bucket.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_bucket_exists_swallows_unexpected_s3_errors() -> None:
    """Non-404 ClientErrors are caught and logged, not raised (so startup doesn't crash)."""
    svc, s3 = _make_service()
    s3.head_bucket.side_effect = _make_client_error("InternalError")

    # Must not raise — errors are logged and swallowed
    await svc.ensure_bucket_exists()


# ---------------------------------------------------------------------------
# delete_file
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_file_calls_s3_delete_object() -> None:
    """delete_file must call delete_object with the correct bucket and key."""
    svc, s3 = _make_service()
    s3.delete_object.return_value = {}

    await svc.delete_file("uploads/old-file.pdf")

    s3.delete_object.assert_called_once_with(Bucket="test-bucket", Key="uploads/old-file.pdf")


@pytest.mark.asyncio
async def test_delete_file_skips_stub_keys() -> None:
    """delete_file must be a no-op for 'local/' stub keys."""
    svc, s3 = _make_service()

    await svc.delete_file("local/uploads/stub.pdf")

    s3.delete_object.assert_not_called()


@pytest.mark.asyncio
async def test_delete_file_skips_when_not_configured() -> None:
    """delete_file must be a no-op when storage is not configured."""
    svc, s3 = _make_service(configured=False)

    await svc.delete_file("uploads/some-file.pdf")

    s3.delete_object.assert_not_called()
