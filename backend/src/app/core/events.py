# src/app/core/events.py
"""
Application Lifespan (Startup/Shutdown events).
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import structlog

from app.core.database import engine
from app.core.redis import redis_pool
from app.core.arq_pool import init_arq_pool, close_arq_pool

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from fastapi import FastAPI

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Execute startup and shutdown hooks.

    Replaces deprecated @app.on_event("startup") and ("shutdown").
    """
    # 1. Startup phase
    logger.info("Application starting up... connecting to external services")

    # Ensure redis connection is viable and pingable
    try:
        await redis_pool.ping()
        logger.info("Redis connected successfully")
    except Exception as exc:
        logger.error(f"Redis connection failed: {exc}")
        # Note: Do NOT raise here. Let the `/readyz` probe handle exposing
        # bad state so kubernetes knows it's unready, rather than crashing loop.

    # Initialize ARQ pool
    await init_arq_pool()
    logger.info("ARQ pool initialized")

    # 2. Yield control back to FastAPI to serve requests
    yield

    # 3. Shutdown phase
    logger.info("Application shutting down... draining connections")

    await redis_pool.close()
    await engine.dispose()
    await close_arq_pool()
    logger.info("Teardown complete")
