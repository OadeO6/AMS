# src/app/core/database.py
"""
Async SQLAlchemy 2.x engine and session factory.

Usage in route handlers / services (via dependency injection):
    from app.core.database import get_db_session
    ...
    async def my_route(session: AsyncSession = Depends(get_db_session)):
        ...

The session auto-commits on a clean exit and rolls back on any exception.
Never instantiate AsyncSession directly in application code.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
# pool_pre_ping=True — connections are tested before use; stale connections
# are transparently replaced (important for long-lived deployments).
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # logs SQL in local/debug mode only
    pool_pre_ping=True,
    pool_size=10,  # persistent connections kept in pool
    max_overflow=20,  # extra connections allowed under burst load
    pool_recycle=3600,  # recycle connections every hour
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
# expire_on_commit=False — prevents lazy-load errors after session.commit()
# because we often return ORM objects to Pydantic schemas after committing.
AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a transactional AsyncSession, commit on success, rollback on error.

    Declare as a dependency in route functions:
        session: AsyncSession = Depends(get_db_session)
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
