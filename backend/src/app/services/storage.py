# src/app/services/storage.py
"""
Async S3-compatible object storage service.

Works with any S3-compatible provider out of the box:
  - MinIO       (local dev / self-hosted)
  - AWS S3      (leave STORAGE_ENDPOINT_URL unset)
  - Cloudflare R2
  - Backblaze B2
  - Wasabi

Configuration is driven entirely from app.config.settings.
See config.py for the full variable reference and AWS SDK equivalents.

Usage
-----
The module exposes a single, lazily initialised singleton:

    from app.services.storage import storage_service

    object_key = await storage_service.upload_file(file.file, file.filename, file.content_type)
    url         = await storage_service.get_download_url(object_key)

Call ``await storage_service.ensure_bucket_exists()`` once at application
startup (already wired into ``app.core.events.lifespan``).
"""

from __future__ import annotations

import uuid
from typing import BinaryIO

import aioboto3
import structlog
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings
from app.exceptions import AppException

logger = structlog.get_logger()


class StorageService:
    """Async, provider-agnostic S3 object storage service.

    The internal ``aioboto3.Session`` is shared across all callers (connection
    pooling). Individual operations use ``async with session.client(...)`` which
    opens a context-managed connection from the pool — not a new TCP connection
    per call.
    """

    def __init__(self) -> None:
        self._session = aioboto3.Session()
        self._bucket = settings.storage_bucket
        self._endpoint = settings.storage_endpoint_url      # server → MinIO (internal)
        self._public_url = settings.storage_public_url       # browser → MinIO (external)
        self._region = settings.STORAGE_REGION
        self._access_key = settings.storage_access_key
        self._secret_key = settings.storage_secret_key
        self._configured = settings.storage_configured
        self._presigned_downloads = settings.STORAGE_PRESIGNED_DOWNLOADS
        self._presigned_expiry = settings.STORAGE_PRESIGNED_EXPIRY_SECONDS

    # ------------------------------------------------------------------
    # Internal helper
    # ------------------------------------------------------------------

    def _client(self):  # type: ignore[return]
        """Return a context-managed async S3 client from the shared session."""
        kwargs: dict = {
            "region_name": self._region,
            "config": Config(signature_version="s3v4"),
        }
        if self._access_key and self._secret_key:
            kwargs["aws_access_key_id"] = self._access_key
            kwargs["aws_secret_access_key"] = self._secret_key
        if self._endpoint:
            kwargs["endpoint_url"] = self._endpoint
        return self._session.client("s3", **kwargs)

    # ------------------------------------------------------------------
    # Startup helper
    # ------------------------------------------------------------------

    async def ensure_bucket_exists(self) -> None:
        """Create the configured bucket if it doesn't already exist, and apply
        the appropriate access policy.

        * When ``STORAGE_PRESIGNED_DOWNLOADS=false`` (public mode): the bucket
          is set to public-read so plain URLs work without signatures.
        * When ``STORAGE_PRESIGNED_DOWNLOADS=true`` (presigned mode): no public
          policy is applied — all access goes through time-limited signed URLs.

        Safe to call multiple times (idempotent). Called once during application
        startup via the lifespan handler.
        """
        if not self._configured:
            logger.warning(
                "storage.not_configured",
                detail="STORAGE_ACCESS_KEY / STORAGE_SECRET_KEY not set — "
                       "file uploads will fail. Set these in .env or docker-compose.",
            )
            return

        try:
            async with self._client() as s3:
                # 1. Create bucket if missing
                try:
                    await s3.head_bucket(Bucket=self._bucket)
                    logger.info("storage.bucket_exists", bucket=self._bucket)
                except ClientError as exc:
                    error_code = exc.response.get("Error", {}).get("Code", "")
                    if error_code in ("404", "NoSuchBucket"):
                        await s3.create_bucket(Bucket=self._bucket)
                        logger.info("storage.bucket_created", bucket=self._bucket)
                    else:
                        raise

                # 2. Apply bucket access policy
                if not self._presigned_downloads:
                    # Public mode: apply a public-read policy so plain URLs work.
                    import json
                    policy = json.dumps({
                        "Version": "2012-10-17",
                        "Statement": [{
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{self._bucket}/*"],
                        }],
                    })
                    await s3.put_bucket_policy(Bucket=self._bucket, Policy=policy)
                    logger.info("storage.bucket_policy_public", bucket=self._bucket)
                else:
                    logger.info(
                        "storage.presigned_mode",
                        detail="Skipping public policy — downloads use presigned URLs.",
                    )
        except (BotoCoreError, ClientError) as exc:
            # Log but don't crash — /readyz probe will expose unhealthy state.
            logger.error("storage.bucket_check_failed", error=str(exc))

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------

    async def upload_file(
        self,
        file_obj: BinaryIO,
        filename: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload a file and return its **object key** (not a URL).

        The key is what you store in the database.  Retrieve a URL later
        via :meth:`get_download_url`.

        If storage is not configured, returns a stub key prefixed with
        ``local/`` and logs a warning — useful so the rest of the request
        pipeline doesn't crash during development without MinIO.
        """
        object_key = f"uploads/{uuid.uuid4()}-{filename}"

        if not self._configured:
            logger.warning(
                "storage.upload_skipped",
                detail="Storage not configured; returning stub key.",
                object_key=object_key,
            )
            return f"local/{object_key}"

        try:
            async with self._client() as s3:
                await s3.upload_fileobj(
                    file_obj,
                    self._bucket,
                    object_key,
                    ExtraArgs={"ContentType": content_type},
                )
            logger.info("storage.upload_ok", object_key=object_key, bucket=self._bucket)
            return object_key
        except (BotoCoreError, ClientError) as exc:
            logger.error("storage.upload_failed", error=str(exc))
            raise AppException(status_code=500, detail=f"File upload failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Download URL
    # ------------------------------------------------------------------

    async def get_download_url(self, object_key: str) -> str:
        """Return the URL a client should use to download *object_key*.

        Behaviour is controlled by ``STORAGE_PRESIGNED_DOWNLOADS``:

        * ``false`` (default / dev) — returns a plain public URL constructed
          from the endpoint and bucket.  Requires the bucket to have public-read
          access (set by ``create_minio_bucket.sh``).

        * ``true`` (recommended for production) — generates a time-limited
          presigned GET URL.  No public bucket access needed.

        If the key starts with ``local/`` (stub from unconfigured storage),
        the key itself is returned unchanged.
        """
        if object_key.startswith("local/"):
            return object_key  # stub passthrough for unconfigured dev

        if not self._configured:
            return object_key  # best-effort passthrough

        if self._presigned_downloads:
            return await self._generate_presigned_url(object_key)

        return self._build_public_url(object_key)

    def _build_public_url(self, object_key: str) -> str:
        """Construct a plain public URL for the object using the public-facing base URL.

        Uses ``STORAGE_PUBLIC_URL`` (what browsers can reach) rather than
        ``STORAGE_ENDPOINT_URL`` (the internal Docker hostname).
        """
        base = self._public_url or f"https://s3.{self._region}.amazonaws.com"
        base = base.rstrip("/")
        return f"{base}/{self._bucket}/{object_key}"

    async def _generate_presigned_url(self, object_key: str) -> str:
        """Generate a time-limited presigned GET URL."""
        try:
            async with self._client() as s3:
                url: str = await s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self._bucket, "Key": object_key},
                    ExpiresIn=self._presigned_expiry,
                )
            return url
        except (BotoCoreError, ClientError) as exc:
            logger.error("storage.presign_failed", error=str(exc))
            raise AppException(
                status_code=500, detail=f"URL generation failed: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    async def delete_file(self, object_key: str) -> None:
        """Delete an object from the bucket. Silently no-ops for stub keys."""
        if object_key.startswith("local/") or not self._configured:
            return
        try:
            async with self._client() as s3:
                await s3.delete_object(Bucket=self._bucket, Key=object_key)
            logger.info("storage.delete_ok", object_key=object_key)
        except (BotoCoreError, ClientError) as exc:
            logger.error("storage.delete_failed", error=str(exc))
            raise AppException(status_code=500, detail=f"File deletion failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Module-level singleton — import and use this everywhere.
#
#   from app.services.storage import storage_service
#
# Instantiated once at import time; the aioboto3 Session and its connection
# pool persist for the lifetime of the process.
# ---------------------------------------------------------------------------
storage_service = StorageService()
