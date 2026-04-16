# tests/conftest.py
"""
Shared pytest fixtures and application overrides.

Configures an isolated PostgreSQL test database (schema dropped/recreated
once per session), and runs every test inside a rolled-back transaction
to ensure pristine state.

Also sets up a test namespace for Redis and an AsyncClient bound to the app.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING
from unittest import mock

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.core.database import get_db_session
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.base import Base
from app.models.user import User, UserRole

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

# Fail early if the test DB URL is not set
if not settings.TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is required to run tests.")

from sqlalchemy.pool import NullPool

# Create the test engine (NullPool is strictly required because pytest-asyncio
# runs tests and fixtures in different event loops, which crashes pooled connections).
test_engine = create_async_engine(settings.TEST_DATABASE_URL, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Provide a session-scoped event loop to support session-scoped async fixtures."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db() -> AsyncGenerator[None, None]:
    """Create the test database schema once per session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session bound to a transaction that rolls back after the test."""
    async with test_engine.connect() as conn:
        # Begin a nested transaction
        transaction = await conn.begin()

        # Bind a session to this connection
        async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False,
            # join_transaction_mode allows the session to use the outer transaction
            join_transaction_mode="create_savepoint",
        )

        async with async_session() as session:
            yield session

        await transaction.rollback()


@pytest.fixture
async def redis_client() -> AsyncGenerator[Redis, None]:
    """Yield a real Redis client configured for a test database namespace (DB 1).

    Flushes the test database before each test.
    """
    # Replace the default /0 with /1 for isolated tests
    test_url = settings.REDIS_URL.rstrip("/0") + "/1"
    client = Redis.from_url(test_url, decode_responses=True)
    await client.flushdb()

    yield client

    await client.flushdb()
    await client.aclose()


@pytest.fixture
async def async_client(
    db_session: AsyncSession,
    redis_client: Redis,
) -> AsyncGenerator[AsyncClient, None]:
    """Yield a pre-configured AsyncClient hitting the FastAPI app.

    Overrides the database and redis dependencies with test equivalents.
    """
    # Override get_db_session
    app.dependency_overrides[get_db_session] = lambda: db_session

    # Monkey-patch the global redis_pool used by health check and token repository
    with (
        mock.patch("app.core.redis.redis_pool", redis_client),
        mock.patch("app.repositories.token.redis_pool", redis_client),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://localhost",
        ) as client:
            yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def student_user(db_session: AsyncSession) -> User:
    """Create a default active student user for tests."""
    user = User(
        email="student@example.com",
        first_name="Test",
        last_name="Student",
        hashed_password=get_password_hash("securepassword123"),
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def auth_headers(student_user: User) -> dict[str, str]:
    """Return Authorization headers for the default student user."""
    token = create_access_token(subject=str(student_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def lecturer_user(db_session: AsyncSession) -> User:
    """Create an authorized lecturer user."""
    user = User(
        email="lecturer@example.com",
        first_name="Test",
        last_name="Lecturer",
        hashed_password=get_password_hash("securepassword123"),
        role=UserRole.LECTURER,
        is_active=True,
        is_authorized=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def lecturer_headers(lecturer_user: User) -> dict[str, str]:
    """Return Authorization headers for the authorized lecturer user."""
    token = create_access_token(subject=str(lecturer_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def inactive_user(db_session: AsyncSession) -> User:
    """Create an inactive user for failure scenario tests."""
    user = User(
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        hashed_password=get_password_hash("securepassword123"),
        role=UserRole.STUDENT,
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()
    return user


# Keep test_user as an alias for inactive_user for backward compat in tests
@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create and yield an inactive test user (used in auth conflict tests)."""
    user = User(
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        hashed_password=get_password_hash("securepassword123"),
        role=UserRole.STUDENT,
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()
    return user
