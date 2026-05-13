import pytest
from httpx import AsyncClient
from app.models.user import User
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_admin_faculties_and_departments(async_client: AsyncClient, admin_user: User, lecturer_user: User):
    """
    Coverage test for admin faculty and department CRUD.

    Expected response contract (per ENDPOINTS_DETAIL.md):
      POST   /admin/faculties                   -> 201 { message, faculty: { id, name, code } }
      GET    /admin/faculties                   -> 200 { faculties: [...] }
      PATCH  /admin/faculties/:id               -> 200 { id, name, ... } (FacultyResponse)
      DELETE /admin/faculties/:id               -> 200 { message }
      POST   /admin/faculties/:id/departments   -> 201 { message, department: { id, ... } }
      GET    /admin/faculties/:id/departments   -> 200 { departments: [...] }
      PATCH  /admin/faculties/:id/departments/:id -> 200 { message, department: { ... } }
      DELETE /admin/faculties/:id/departments/:id -> 200 { message }
    """
    token = create_access_token(subject=str(admin_user.id))
    headers = {"Authorization": f"Bearer {token}"}

    # List users
    resp = await async_client.get("/api/v1/admin/users", headers=headers)
    assert resp.status_code == 200

    # Create faculty — expect { message, faculty: { id, ... } }
    resp = await async_client.post(
        "/api/v1/admin/faculties",
        json={"name": "Engineering", "code": "ENG"},
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "faculty" in body
    fac_id = body["faculty"]["id"]

    # List faculties — expect { faculties: [...] }
    resp = await async_client.get("/api/v1/admin/faculties", headers=headers)
    assert resp.status_code == 200
    assert "faculties" in resp.json()

    # Update faculty — expect flat FacultyResponse
    resp = await async_client.patch(
        f"/api/v1/admin/faculties/{fac_id}",
        json={"name": "Engineering Updated"},
        headers=headers,
    )
    assert resp.status_code == 200

    # Create department — expect { message, department: { id, ... } }
    resp = await async_client.post(
        f"/api/v1/admin/faculties/{fac_id}/departments",
        json={"name": "Civil Engineering", "code": "CVE"},
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "department" in body
    dept_id = body["department"]["id"]

    # List departments — expect { departments: [...] }
    resp = await async_client.get(
        f"/api/v1/admin/faculties/{fac_id}/departments",
        headers=headers,
    )
    assert resp.status_code == 200
    assert "departments" in resp.json()

    # Get single department
    resp = await async_client.get(
        f"/api/v1/admin/faculties/{fac_id}/departments/{dept_id}",
        headers=headers,
    )
    assert resp.status_code == 200

    # Update department — expect { message, department: { ... } }
    resp = await async_client.patch(
        f"/api/v1/admin/faculties/{fac_id}/departments/{dept_id}",
        json={"name": "Civil Eng"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert "department" in resp.json()

    # Delete department — expect { message }
    resp = await async_client.delete(
        f"/api/v1/admin/faculties/{fac_id}/departments/{dept_id}",
        headers=headers,
    )
    assert resp.status_code == 200
    assert "message" in resp.json()

    # Delete faculty — expect { message }
    resp = await async_client.delete(
        f"/api/v1/admin/faculties/{fac_id}",
        headers=headers,
    )
    assert resp.status_code == 200
    assert "message" in resp.json()


@pytest.mark.asyncio
async def test_admin_academic_sessions(async_client: AsyncClient, admin_user: User):
    """
    Coverage test for admin academic session CRUD.

    Expected response contract (per ENDPOINTS_DETAIL.md):
      POST   /admin/academic-sessions               -> 201 { message, session: { id, semesters: [...] } }
      GET    /admin/academic-sessions               -> 200 { sessions: [...] }
      GET    /admin/academic-sessions/:id           -> 200 { id, semesters: [...] }
      PATCH  /admin/academic-sessions/:id/semesters/:id/activate -> 200 { message, semester: { ... } }
    """
    token = create_access_token(subject=str(admin_user.id))
    headers = {"Authorization": f"Bearer {token}"}

    # Create academic session — expect { message, session: { id, semesters } }
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
    body = resp.json()
    assert "session" in body
    sess_id = body["session"]["id"]
    sem_id = body["session"]["semesters"][0]["id"]

    # List sessions — expect { sessions: [...] }
    resp = await async_client.get("/api/v1/admin/academic-sessions", headers=headers)
    assert resp.status_code == 200
    assert "sessions" in resp.json()

    # Get one session
    resp = await async_client.get(f"/api/v1/admin/academic-sessions/{sess_id}", headers=headers)
    assert resp.status_code == 200

    # Activate semester — expect { message, semester: { ... } }
    resp = await async_client.patch(
        f"/api/v1/admin/academic-sessions/{sess_id}/semesters/{sem_id}/activate",
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "message" in body
    assert "semester" in body
