# tests/integration/test_user_coverage.py
import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy import select
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_admin_authorize_lecturer_coverage(
    async_client: AsyncClient, 
    admin_headers: dict[str, str],
    db_session: AsyncSession
) -> None:
    # 1. Authorize non-lecturer (student) — should fail gracefully
    student_payload = {
        "email": "student_auth_test@test.com",
        "password": "password123",
        "first_name": "Auth",
        "last_name": "Test",
        "phone": "12345678",
        "matric_num": "STUD001",
        "admission_session": "2024/2025"
    }
    reg_res = await async_client.post("/api/v1/auth/register/student", json=student_payload)
    assert reg_res.status_code == 201
    
    # Fetch student ID from DB since response only contains tokens
    student = await db_session.scalar(select(User).where(User.email == student_payload["email"]))
    student_id = student.id
    
    res_auth = await async_client.post(
        "/api/v1/admin/staff/authorize", 
        json={"user_ids": [str(student_id)]}, 
        headers=admin_headers
    )
    assert res_auth.status_code == 200
    data = res_auth.json()
    assert data["authorized"] == 0
    assert len(data["failed"]) == 1
    assert "Only lecturers can be authorized" in data["failed"][0]["reason"]
    
    # 2. Authorize already authorized lecturer — should report as failed
    lecturer_payload = {
        "email": "lecturer_auth_test@test.com",
        "password": "password123",
        "first_name": "Auth",
        "last_name": "Test",
        "phone": "87654321",
        "staff_id": "STF001"
    }
    reg_res2 = await async_client.post("/api/v1/auth/register/lecturer", json=lecturer_payload)
    assert reg_res2.status_code == 201
    
    lecturer = await db_session.scalar(select(User).where(User.email == lecturer_payload["email"]))
    lecturer_id = lecturer.id
    
    # First authorization
    await async_client.post(
        "/api/v1/admin/staff/authorize", 
        json={"user_ids": [str(lecturer_id)]}, 
        headers=admin_headers
    )
    
    # Second authorization (already authorized)
    res_auth2 = await async_client.post(
        "/api/v1/admin/staff/authorize", 
        json={"user_ids": [str(lecturer_id)]}, 
        headers=admin_headers
    )
    assert res_auth2.status_code == 200
    data2 = res_auth2.json()
    assert data2["authorized"] == 0
    assert len(data2["failed"]) == 1
    assert "already authorized" in data2["failed"][0]["reason"]

@pytest.mark.asyncio
async def test_admin_assign_hod_coverage(
    async_client: AsyncClient, 
    admin_headers: dict[str, str], 
    hod_user: User,
    db_session: AsyncSession
) -> None:
    """
    Validates that assigning a non-HOD role as HOD is rejected.

    Expected response:
      POST /admin/departments/:id/hod with a student's user_id -> 409
      POST /admin/departments/:id/hod with a HOD user's user_id -> 200 { message }
    """
    # Create faculty and dept
    fac_res = await async_client.post(
        "/api/v1/admin/faculties",
        json={"name": "F", "code": "F"},
        headers=admin_headers
    )
    faculty_id = fac_res.json()["faculty"]["id"]

    dept_res = await async_client.post(
        f"/api/v1/admin/faculties/{faculty_id}/departments",
        json={"name": "D", "code": "D"},
        headers=admin_headers
    )
    dept_id = dept_res.json()["department"]["id"]
    
    # 1. Assign HOD: user not HOD role (student) — expect 409
    student_payload = {
        "email": "student_hod_test@test.com",
        "password": "password123",
        "first_name": "Bad",
        "last_name": "Hod",
        "phone": "12345678",
        "matric_num": "STUD002",
        "admission_session": "2024/2025"
    }
    reg_res = await async_client.post("/api/v1/auth/register/student", json=student_payload)
    assert reg_res.status_code == 201
    
    student = await db_session.scalar(select(User).where(User.email == student_payload["email"]))
    student_id = student.id
    
    res_assign = await async_client.post(
        f"/api/v1/admin/departments/{dept_id}/hod", 
        json={"user_id": str(student_id)},   # spec uses user_id not hod_id
        headers=admin_headers
    )
    assert res_assign.status_code == 409
    assert "HOD role" in res_assign.json()["detail"]
