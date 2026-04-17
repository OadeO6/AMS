import pytest
from httpx import AsyncClient
from app.models.user import User
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_admin_faculties_and_departments(async_client: AsyncClient, admin_user: User, lecturer_user: User):
    token = create_access_token(subject=str(admin_user.id))
    headers = {"Authorization": f"Bearer {token}"}

    # List users
    resp = await async_client.get("/api/v1/admin/users", headers=headers)
    assert resp.status_code == 200

    # Create faculty
    resp = await async_client.post(
        "/api/v1/admin/faculties",
        json={"name": "Engineering", "code": "ENG"},
        headers=headers,
    )
    assert resp.status_code == 201
    fac_id = resp.json()["id"]

    # List faculties
    resp = await async_client.get("/api/v1/admin/faculties", headers=headers)
    assert resp.status_code == 200

    # Update faculty
    resp = await async_client.patch(
        f"/api/v1/admin/faculties/{fac_id}",
        json={"name": "Engineering Updated"},
        headers=headers,
    )
    assert resp.status_code == 200

    # Create department
    resp = await async_client.post(
        f"/api/v1/admin/faculties/{fac_id}/departments",
        json={"name": "Civil Engineering", "code": "CVE"},
        headers=headers,
    )
    assert resp.status_code == 201
    dept_id = resp.json()["id"]

    # List departments
    resp = await async_client.get(
        f"/api/v1/admin/faculties/{fac_id}/departments",
        headers=headers,
    )
    assert resp.status_code == 200

    # Get single department
    resp = await async_client.get(
        f"/api/v1/admin/faculties/{fac_id}/departments/{dept_id}",
        headers=headers,
    )
    assert resp.status_code == 200

    # Update department via patch under faculty
    resp = await async_client.patch(
        f"/api/v1/admin/faculties/{fac_id}/departments/{dept_id}",
        json={"name": "Civil Eng"},
        headers=headers,
    )
    assert resp.status_code == 200

    # Delete department and faculty (cover delete paths)
    resp = await async_client.delete(
        f"/api/v1/admin/faculties/{fac_id}/departments/{dept_id}",
        headers=headers,
    )
    assert resp.status_code == 204

    resp = await async_client.delete(
        f"/api/v1/admin/faculties/{fac_id}",
        headers=headers,
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_admin_academic_sessions(async_client: AsyncClient, admin_user: User):
    token = create_access_token(subject=str(admin_user.id))
    headers = {"Authorization": f"Bearer {token}"}

    # Create academic session — semesters are embedded in the payload
    resp = await async_client.post(
        "/api/v1/admin/academic-sessions",
        json={
            "name": "2030/2031",
            "semesters": [
                {"name": "first", "start_date": "2030-01-01", "end_date": "2030-06-01"},
                {"name": "second", "start_date": "2030-07-01", "end_date": "2030-12-01"},
            ]
        },
        headers=headers,
    )
    assert resp.status_code == 201
    sess_id = resp.json()["id"]
    sem_id = resp.json()["semesters"][0]["id"]

    # List sessions
    resp = await async_client.get("/api/v1/admin/academic-sessions", headers=headers)
    assert resp.status_code == 200

    # Get one session
    resp = await async_client.get(f"/api/v1/admin/academic-sessions/{sess_id}", headers=headers)
    assert resp.status_code == 200

    # Activate semester
    resp = await async_client.patch(
        f"/api/v1/admin/academic-sessions/{sess_id}/semesters/{sem_id}/activate",
        headers=headers,
    )
    assert resp.status_code == 200
