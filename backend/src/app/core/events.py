# src/app/core/events.py
"""
Application Lifespan (Startup/Shutdown events).
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import structlog

from app.config import settings
from app.core.database import engine, AsyncSessionFactory
from app.core.redis import redis_pool
from app.core.arq_pool import init_arq_pool, close_arq_pool
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from sqlalchemy import select

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from fastapi import FastAPI

logger = structlog.get_logger()


async def seed_admin() -> None:
    """Seed the default admin user from configuration if they don't exist."""
    async with AsyncSessionFactory() as session:
        try:
            res = await session.execute(select(User).where(User.email == settings.DEFAULT_ADMIN_EMAIL))
            if not res.scalar_one_or_none():
                admin = User(
                    email=settings.DEFAULT_ADMIN_EMAIL,
                    hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                    first_name="System",
                    last_name="Admin",
                    roles=[UserRole.ADMIN.value],
                    is_active=True,
                )
                session.add(admin)
                await session.commit()
                logger.info(f"Seeded default admin user: {settings.DEFAULT_ADMIN_EMAIL}")
        except Exception as e:
            await session.rollback()
            # If multiple workers try to seed simultaneously, one will raise an IntegrityError
            if "UniqueViolation" in str(e) or "UniqueViolationError" in str(e) or "duplicate key" in str(e) or "IntegrityError" in str(e.__class__.__name__):
                logger.info("Default admin user already seeded by another worker.")
            else:
                logger.error(f"Failed to seed admin: {e}")


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
    
    # Seed default admin user
    await seed_admin()

    # 2. Yield control back to FastAPI to serve requests
    yield

    # 3. Shutdown phase
    logger.info("Application shutting down... draining connections")

    await redis_pool.close()
    await engine.dispose()
    await close_arq_pool()
    logger.info("Teardown complete")
