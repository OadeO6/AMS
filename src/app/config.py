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

    # ------------------------------------------------------------------
    # CORS & Trusted Hosts
    # ------------------------------------------------------------------
    # Stored as a JSON array string in env; parsed to list[str] by the validator.
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]

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
    # External Systems (Phase 9)
    # ------------------------------------------------------------------
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    S3_BUCKET_NAME: str = "ams-storage-bucket"

    OPENAI_API_KEY: str | None = None

    VECTOR_DB_URL: str | None = None
    VECTOR_DB_API_KEY: str | None = None

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


@lru_cache
def get_settings() -> Settings:
    """Return the cached Settings singleton.

    Prefer importing `settings` directly; use `get_settings()` only where
    you need to override settings in tests via dependency injection.
    """
    return Settings()


# Module-level singleton — import this throughout the application.
settings: Settings = get_settings()
