# src/app/config.py
"""
Application settings loaded once at import time.

Usage anywhere in the codebase:
    from app.config import settings
"""

from __future__ import annotations

import json
from enum import StrEnum
from functools import lru_cache
from typing import Self

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Allow extra env vars without raising an error (useful for OTEL envs etc.)
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    ENVIRONMENT: Environment = Environment.LOCAL
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    DATABASE_URL: str
    TEST_DATABASE_URL: str = ""

    # ------------------------------------------------------------------
    # Cache
    # ------------------------------------------------------------------
    REDIS_URL: str

    # ------------------------------------------------------------------
    # Auth / Security
    # ------------------------------------------------------------------
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    DEFAULT_ADMIN_EMAIL: str = "admin@ams.edu"
    DEFAULT_ADMIN_PASSWORD: str = "TestPass123!"

    # ------------------------------------------------------------------
    # CORS & Trusted Hosts
    # ------------------------------------------------------------------
    # Stored as a JSON array string in env; parsed to list[str] by the validator.
    ALLOWED_ORIGINS: list[str] = ["*"]
    ALLOWED_HOSTS: list[str] = ["*"]

    # ------------------------------------------------------------------
    # OpenTelemetry
    # ------------------------------------------------------------------
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4318"
    OTEL_SERVICE_NAME: str = "ams-api"

    # ------------------------------------------------------------------
    # Server
    # ------------------------------------------------------------------
    PORT: int = 8000
    WEB_CONCURRENCY: int = 4

    # ------------------------------------------------------------------
    # Object Storage (S3-compatible)
    # ------------------------------------------------------------------
    # Works with MinIO, AWS S3, Cloudflare R2, Backblaze B2, Wasabi, etc.
    # Leave STORAGE_ENDPOINT_URL blank to route to real AWS S3.
    #
    # Variable             AWS SDK equivalent
    # ─────────────────────────────────────────────────────────────────
    # STORAGE_ACCESS_KEY   AWS_ACCESS_KEY_ID
    # STORAGE_SECRET_KEY   AWS_SECRET_ACCESS_KEY
    # STORAGE_ENDPOINT_URL endpoint_url kwarg (omit for real AWS S3)
    # STORAGE_REGION       AWS_DEFAULT_REGION
    # ─────────────────────────────────────────────────────────────────
    STORAGE_ENDPOINT_URL: str | None = None
    STORAGE_ACCESS_KEY: str | None = None
    STORAGE_SECRET_KEY: str | None = None
    STORAGE_BUCKET_NAME: str = "ams-storage-bucket"
    STORAGE_REGION: str = "us-east-1"  # Dummy value is fine for MinIO; required for real AWS

    # Public-facing base URL for object storage — what browsers/clients use to fetch files.
    # Differs from STORAGE_ENDPOINT_URL when running inside Docker:
    #   STORAGE_ENDPOINT_URL = http://minio:9000   (server → MinIO, internal Docker hostname)
    #   STORAGE_PUBLIC_URL   = http://localhost:9000 (browser → MinIO, host-accessible)
    # Leave blank for AWS S3 / Cloudflare R2 (presigned URLs embed the host automatically).
    STORAGE_PUBLIC_URL: str | None = None

    # Set to true to serve time-limited presigned download URLs instead of plain public URLs.
    # Keep false in development (public bucket). Flip to true in production for secure access.
    STORAGE_PRESIGNED_DOWNLOADS: bool = False
    STORAGE_PRESIGNED_EXPIRY_SECONDS: int = 3600  # 1 hour

    # Deprecated aliases — kept for one release cycle; will be removed.
    # Prefer the STORAGE_* names above.
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    S3_BUCKET_NAME: str | None = None
    S3_ENDPOINT_URL: str | None = None

    OPENAI_API_KEY: str | None = None

    VECTOR_DB_URL: str | None = None
    VECTOR_DB_API_KEY: str | None = None

    # ------------------------------------------------------------------
    # Notification Subsystem
    # ------------------------------------------------------------------
    # Email (SendGrid or SMTP)
    SENDGRID_API_KEY: str | None = None

    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_USE_TLS: bool = True
    SMTP_START_TLS: bool = False
    SMTP_FROM_EMAIL: str = "noreply@ams.example.com"

    # Push (FCM)
    FCM_PROJECT_ID: str | None = None
    FCM_SERVER_KEY: str | None = None

    # Push (Web / VAPID)
    VAPID_PRIVATE_KEY: str | None = None
    VAPID_CLAIMS_EMAIL: str = "admin@ams.example.com"

    # SMS (Termii or Twilio)
    TERMII_API_KEY: str | None = None
    TERMII_SENDER_ID: str = "AMS"

    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_FROM_NUMBER: str | None = None

    # ------------------------------------------------------------------
    # Field validators
    # ------------------------------------------------------------------

    @field_validator("ALLOWED_ORIGINS", "ALLOWED_HOSTS", mode="before")
    @classmethod
    def _parse_json_list(cls, value: object) -> list[str]:
        """Allow the field to be supplied as a JSON-encoded string in .env."""
        if isinstance(value, str):
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                raise ValueError("Expected a JSON array")
            return parsed  # type: ignore[return-value]
        return value  # type: ignore[return-value]

    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def _uppercase_log_level(cls, value: object) -> str:
        if isinstance(value, str):
            return value.upper()
        raise ValueError("LOG_LEVEL must be a string")

    @field_validator("DEBUG", mode="before")
    @classmethod
    def _parse_debug(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug"}:
                return True
            if normalized in {"0", "false", "no", "off", "release"}:
                return False
        raise ValueError("DEBUG must be a boolean-like value")

    # ------------------------------------------------------------------
    # Cross-field validators
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _enforce_production_constraints(self) -> Self:
        if self.ENVIRONMENT == Environment.PRODUCTION and self.DEBUG:
            raise ValueError(
                "DEBUG must be False when ENVIRONMENT=production. "
                "Set DEBUG=false in your environment."
            )
        return self

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

    @property
    def is_local(self) -> bool:
        return self.ENVIRONMENT == Environment.LOCAL

    @property
    def storage_access_key(self) -> str | None:
        """Resolve storage access key, preferring the new STORAGE_* name."""
        return self.STORAGE_ACCESS_KEY or self.AWS_ACCESS_KEY_ID

    @property
    def storage_secret_key(self) -> str | None:
        """Resolve storage secret key, preferring the new STORAGE_* name."""
        return self.STORAGE_SECRET_KEY or self.AWS_SECRET_ACCESS_KEY

    @property
    def storage_bucket(self) -> str:
        """Resolve bucket name, preferring the new STORAGE_* name."""
        return self.S3_BUCKET_NAME or self.STORAGE_BUCKET_NAME

    @property
    def storage_endpoint_url(self) -> str | None:
        """Resolve endpoint URL, preferring the new STORAGE_* name."""
        return self.STORAGE_ENDPOINT_URL or self.S3_ENDPOINT_URL

    @property
    def storage_public_url(self) -> str | None:
        """Public-facing base URL for storage (what browsers use to fetch files).

        Falls back to storage_endpoint_url when STORAGE_PUBLIC_URL is not set
        (fine for cases where the same URL works both server-side and client-side,
        e.g. AWS S3, Cloudflare R2, or running the app directly on the host).
        """
        return self.STORAGE_PUBLIC_URL or self.storage_endpoint_url

    @property
    def storage_configured(self) -> bool:
        """True when enough credentials are present to talk to an S3-compatible store."""
        return bool(self.storage_access_key and self.storage_secret_key)


@lru_cache
def get_settings() -> Settings:
    """Return the cached Settings singleton.

    Prefer importing `settings` directly; use `get_settings()` only where
    you need to override settings in tests via dependency injection.
    """
    return Settings()


# Module-level singleton — import this throughout the application.
settings: Settings = get_settings()
