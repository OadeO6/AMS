import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

@pytest.mark.asyncio
async def test_student_profile_update(async_client: AsyncClient, get_auth_headers, setup_lecturer_data, db_session: AsyncSession):
    student_user = setup_lecturer_data["student"]
    student_headers = await get_auth_headers(student_user.email, "securepassword123")
    
    # Try updating admission year
    resp = await async_client.patch(
        "/api/v1/auth/me/student",
        json={"admission_year": 2025},
        headers=student_headers
    )
    assert resp.status_code == 200
    assert resp.json()["admission_year"] == 2025

    # Check that it persisted
    await db_session.refresh(student_user)
    assert student_user.admission_year == 2025

@pytest.mark.asyncio
async def test_lecturer_update_student_profile_forbidden(async_client: AsyncClient, get_auth_headers, setup_lecturer_data):
    lecturer_user = setup_lecturer_data["lecturer"]
    lecturer_headers = await get_auth_headers(lecturer_user.email, "securepassword123")
    
    # Lecturer cannot update student profile
    resp = await async_client.patch(
        "/api/v1/auth/me/student",
        json={"admission_year": 2025},
        headers=lecturer_headers
    )
    assert resp.status_code == 403
