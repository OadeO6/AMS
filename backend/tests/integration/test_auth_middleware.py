# tests/integration/test_auth_middleware.py
"""
Integration tests for authentication and access-control middleware.

These tests exercise the middleware layer through the real FastAPI app — they
send HTTP requests and verify that the correct status codes and error codes are
returned based on the caller's role and authorisation state.

Not tested here: the internal implementation of the middleware functions
(those belong in unit tests once the middleware has pure-logic extractable
from the FastAPI dependency).

Fixtures used: async_client, db_session (from conftest.py)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from app.core.security import create_access_token, get_password_hash
from app.models.user import User, UserRole
from tests.conftest import TEST_PASSWORD

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


class TestActiveSmesterMiddleware:
    """require_active_semester blocks write operations when no semester is active.

    This is a FastAPI dependency injected into all write endpoints under
    /courses/:id/*. It raises 403 NO_ACTIVE_SEMESTER when the DB has no active
    semester row.
    """

    async def test_blocks_when_no_active_semester(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Any endpoint gated by require_active_semester should 403 with no active semester."""
        from app.middleware.active_semester import require_active_semester
        from app.exceptions import ForbiddenError
        from tests.conftest import TestingSessionLocal

        # Call the dependency directly against the test DB (which has no active semester)
        async with TestingSessionLocal() as session:
            with pytest.raises(ForbiddenError) as exc_info:
                await require_active_semester(session=session)
            assert exc_info.value.error_code == "NO_ACTIVE_SEMESTER"


class TestSessionOwnerMiddleware:
    """require_session_owner restricts session mutations to the session creator."""

    async def test_raises_forbidden_when_user_is_none(self) -> None:
        """Calling the guard with no current_user always raises FORBIDDEN."""
        import uuid
        from app.middleware.session_owner import require_session_owner
        from app.exceptions import ForbiddenError

        fake_id = uuid.uuid4()
        with pytest.raises(ForbiddenError) as exc_info:
            await require_session_owner(session_id=fake_id, current_user=None)  # type: ignore[arg-type]
        assert exc_info.value.error_code == "FORBIDDEN"


class TestRoleBasedAccessControl:
    """HTTP-level checks that roles are enforced on protected routes."""

    async def test_student_cannot_access_lecturer_routes(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """A student JWT returns 403 on any /lecturer/* endpoint."""
        response = await async_client.get("/api/v1/lecturer/courses", headers=auth_headers)
        assert response.status_code == 403

    async def test_student_cannot_access_admin_routes(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """A student JWT returns 403 on any /admin/* endpoint."""
        response = await async_client.get("/api/v1/admin/faculties", headers=auth_headers)
        assert response.status_code == 403

    async def test_unauthorized_lecturer_is_blocked(
        self, async_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """A lecturer whose is_authorized=False receives 403 UNAUTHORIZED_LECTURER."""
        unauth = User(
            email="unauth_lecturer_mw@example.com",
            first_name="Unauth",
            last_name="Lecturer",
            hashed_password=get_password_hash(TEST_PASSWORD),
            roles=[UserRole.LECTURER.value],
            is_active=True,
            is_authorized=False,
        )
        db_session.add(unauth)
        await db_session.commit()

        token = create_access_token(subject=str(unauth.id))
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get("/api/v1/lecturer/courses", headers=headers)
        assert response.status_code == 403
        assert response.json()["error"] == "UNAUTHORIZED_LECTURER"

    async def test_unauthenticated_request_returns_401(
        self, async_client: AsyncClient
    ) -> None:
        """A request with no Authorization header returns 401."""
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 401
