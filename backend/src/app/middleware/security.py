# src/app/middleware/security.py
"""
CORS, Trusted Hosts, and Rate Limiting configurations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.core.redis import limiter

if TYPE_CHECKING:
    from fastapi import FastAPI


def setup_security_middlewares(app: FastAPI) -> None:
    """Attach security-related middlewares to the FastAPI app."""

    # 1. Rate Limiting via slowapi
    # State holds the limiter so routers can use @limiter.limit("100/minute")
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

    # 2. CORS
    # In production, never allow "*". Settings parses the JSON array.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 3. Trusted Host
    # Prevents HTTP Host header attacks.
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )
