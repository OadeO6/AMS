# tests/integration/test_auth.py
"""
Integration tests for the AMS /api/v1/auth endpoints.

These hit the real database and real redis, exercising the full request lifecycle.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models.user import User, UserRole

if TYPE_CHECKING:
    import httpx
    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncSession


async def test_register_student_success(
    async_client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    """Registering a student should return 201 with access and refresh tokens."""
    payload = {
        "email": "newstudent@example.com",
        "password": "strongpassword",
        "first_name": "Ada",
        "last_name": "Lovelace",
        "matric_num": "2021/CS/001",
        "admission_session": "2021/2022",
    }

    response = await async_client.post("/api/v1/auth/register/student", json=payload)

    print("TEST_OUTPUT_B77: ", response.text)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Assert DB state
    user = await db_session.scalar(select(User).where(User.email == "newstudent@example.com"))
    assert user is not None
    assert user.first_name == "Ada"
    assert user.last_name == "Lovelace"
    assert UserRole.STUDENT.value in user.roles


async def test_register_lecturer_success(
    async_client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    """Registering a lecturer should return 201 and create an unauthorized account."""
    payload = {
        "email": "newlecturer@example.com",
        "password": "strongpassword",
        "first_name": "Grace",
        "last_name": "Hopper",
        "staff_id": "STAFF001",
    }

    response = await async_client.post("/api/v1/auth/register/lecturer", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data

    user = await db_session.scalar(select(User).where(User.email == "newlecturer@example.com"))
    assert user is not None
    assert UserRole.LECTURER.value in user.roles
    assert user.is_authorized is False


async def test_register_duplicate_email(async_client: httpx.AsyncClient, test_user: User) -> None:
    """Registering with an existing email should return 409 Conflict."""
    payload = {
        "email": "inactive@example.com",  # Uses test_user's email
        "password": "newpassword",
        "first_name": "Dup",
        "last_name": "User",
        "matric_num": "2021/CS/002",
        "admission_session": "2021/2022",
    }
    response = await async_client.post("/api/v1/auth/register/student", json=payload)

    assert response.status_code == 409
    assert response.json()["error"] == "EMAIL_CONFLICT"


async def test_login_success(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Valid credentials should return a 200 with tokens."""
    payload = {
        "email": "student@example.com",
        "password": "securepassword123",
    }
    response = await async_client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_login_invalid_password(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Wrong password should return 401."""
    payload = {"email": "student@example.com", "password": "wrongpassword"}
    response = await async_client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 401
    assert response.json()["error"] == "INVALID_CREDENTIALS"


async def test_refresh_and_logout(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    redis_client: Redis,
) -> None:
    """Full lifecycle: login -> refresh -> logout -> refresh fails."""
    # 1. Login
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "student@example.com", "password": "securepassword123"},
    )
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["refresh_token"]

    # 2. Refresh
    refresh_resp = await async_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.json()

    # 3. Logout — spec says 204 No Content
    logout_resp = await async_client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
        headers=auth_headers,
    )
    assert logout_resp.status_code == 204

    # 4. Refresh should now fail
    fail_resp = await async_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert fail_resp.status_code == 401
    assert fail_resp.json()["error"] == "INVALID_REFRESH_TOKEN"


async def test_get_me(async_client: httpx.AsyncClient, auth_headers: dict[str, str]) -> None:
    """GET /auth/me should return the current user profile."""
    response = await async_client.get("/api/v1/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "student@example.com"
    assert "student" in data["roles"]
    assert "first_name" in data
    assert "last_name" in data
    assert "hashed_password" not in data


async def test_get_me_unauthenticated(async_client: httpx.AsyncClient) -> None:
    """GET /auth/me without token should return 401."""
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_update_me(async_client: httpx.AsyncClient, auth_headers: dict[str, str]) -> None:
    """PATCH /auth/me should update common profile fields and return the updated user."""
    response = await async_client.patch(
        "/api/v1/auth/me",
        json={"first_name": "Updated"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    # spec: returns { message, user: { first_name, ... } } or flat UserPublic
    body = response.json()
    # Accept either nested or flat — implementation detail
    first_name = body.get("user", body).get("first_name", body.get("first_name"))
    assert first_name == "Updated"


async def test_lecturer_route_unauthorized_if_not_lecturer(
    async_client: httpx.AsyncClient, auth_headers: dict[str, str]
) -> None:
    """A student trying to access lecturer routes should get 403."""
    response = await async_client.get("/api/v1/lecturer/courses", headers=auth_headers)
    assert response.status_code == 403


async def test_admin_route_unauthorized_if_not_admin(
    async_client: httpx.AsyncClient, auth_headers: dict[str, str]
) -> None:
    """A student trying to access admin routes should get 403."""
    response = await async_client.get("/api/v1/admin/faculties", headers=auth_headers)
    assert response.status_code == 403


async def test_unauth_lecturer_forbidden(
    async_client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    """An unauthorized lecturer should get 403 on all lecturer routes."""
    from app.core.security import create_access_token, get_password_hash

    # Create an unauthorized lecturer
    unauth = User(
        email="unauth_lecturer@example.com",
        first_name="New",
        last_name="Lecturer",
        hashed_password=get_password_hash("password123"),
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
