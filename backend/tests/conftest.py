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
from unittest.mock import MagicMock
import sys

# Mock boto3 to avoid ModuleNotFoundError in environments where it's not installed
sys.modules["boto3"] = MagicMock()

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
        from sqlalchemy import text
        # Robustly clean the database by dropping the entire public schema
        await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        from sqlalchemy import text
        await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
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
    # Override get_db_session and get_arq_pool
    from app.core.arq_pool import get_arq_pool
    
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_arq_pool] = lambda: mock.AsyncMock()

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
        roles=[UserRole.STUDENT.value],
        is_active=True,
        admission_year=2024,
        admission_session="2024/2025",
        level_offset=0,
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
        roles=[UserRole.LECTURER.value],
        is_active=True,
        is_authorized=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


from datetime import date
import uuid
from app.models.academic_session import AcademicSession, Semester
from app.models.course import Course, CourseOffering, CourseRegistration
from app.models.department import Department
from app.models.faculty import Faculty

@pytest.fixture
async def setup_lecturer_data(db_session: AsyncSession, lecturer_user: User, student_user: User):
    # Semester setup
    academic_session = AcademicSession(name=f"2024/2025-{uuid.uuid4().hex[:4]}")
    db_session.add(academic_session)
    await db_session.flush()
    
    semester = Semester(
        academic_session_id=academic_session.id,
        name="first",
        start_date=date(2024, 9, 1),
        end_date=date(2024, 12, 15),
        is_active=True
    )
    db_session.add(semester)
    
    # Faculty & Dept & Course
    fac = Faculty(name="Science", code=f"SCI-{uuid.uuid4().hex[:4]}")
    db_session.add(fac)
    await db_session.flush()
    
    dept = Department(faculty_id=fac.id, name="Math", code=f"MTH-{uuid.uuid4().hex[:4]}")
    db_session.add(dept)
    await db_session.flush()
    
    course = Course(title="Calculus I", code=f"MTH101-{uuid.uuid4().hex[:4]}", units=3, department_id=dept.id)
    db_session.add(course)
    await db_session.flush()
    
    # Assign lecturer to offering via junction table
    offering = CourseOffering(course_id=course.id, semester_id=semester.id, is_active=True)
    db_session.add(offering)
    await db_session.flush()

    # Insert OfferingLecturer row (junction table)
    from app.models.course import OfferingLecturer
    offering_lecturer = OfferingLecturer(offering_id=offering.id, lecturer_id=lecturer_user.id)
    db_session.add(offering_lecturer)
    await db_session.flush()

    # Register student
    reg = CourseRegistration(student_id=student_user.id, offering_id=offering.id, status="approved")
    db_session.add(reg)
    await db_session.commit()
    
    return {
        "lecturer": lecturer_user,
        "student": student_user,
        "semester": semester,
        "course": course,
        "offering": offering,
        "registration": reg
    }


@pytest.fixture
async def lecturer_headers(lecturer_user: User) -> dict[str, str]:
    """Return Authorization headers for the authorized lecturer user."""
    token = create_access_token(subject=str(lecturer_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin user."""
    user = User(
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        hashed_password=get_password_hash("securepassword123"),
        roles=[UserRole.ADMIN.value],
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def admin_headers(admin_user: User) -> dict[str, str]:
    """Return Authorization headers for the admin user."""
    token = create_access_token(subject=str(admin_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def hod_user(db_session: AsyncSession) -> User:
    """Create an HOD user."""
    user = User(
        email="hod@example.com",
        first_name="HOD",
        last_name="User",
        hashed_password=get_password_hash("securepassword123"),
        roles=[UserRole.HOD.value, UserRole.LECTURER.value],
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def hod_headers(hod_user: User) -> dict[str, str]:
    """Return Authorization headers for the HOD user."""
    token = create_access_token(subject=str(hod_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def inactive_user(db_session: AsyncSession) -> User:
    """Create an inactive user for failure scenario tests."""
    user = User(
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        hashed_password=get_password_hash("securepassword123"),
        roles=[UserRole.STUDENT.value],
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
        roles=[UserRole.STUDENT.value],
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
def get_auth_headers(async_client: AsyncClient):
    """Returns an async function that generates auth headers via login."""
    async def _get_auth_headers(email: str, password: str) -> dict[str, str]:
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return _get_auth_headers
