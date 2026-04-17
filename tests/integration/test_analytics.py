import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_student_analytics(async_client: AsyncClient, setup_lecturer_data, get_auth_headers):
    """Test student global and course analytics endpoints."""
    student_user = setup_lecturer_data["student"]
    offering = setup_lecturer_data["offering"]
    headers = await get_auth_headers(student_user.email, "securepassword123")

    # Global
    resp1 = await async_client.get("/api/v1/student/analytics", headers=headers)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert "courses_enrolled" in data1
    assert data1["overall_attendance_percentage"] is not None

    # Course specific
    resp2 = await async_client.get(f"/api/v1/student/courses/{offering.id}/analytics", headers=headers)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert "attendance_percentage" in data2
    assert "average_score" in data2
    assert "total_assignments" in data2


@pytest.mark.asyncio
async def test_lecturer_analytics(async_client: AsyncClient, setup_lecturer_data, get_auth_headers):
    """Test lecturer global and course analytics endpoints."""
    lecturer_user = setup_lecturer_data["lecturer"]
    offering = setup_lecturer_data["offering"]
    headers = await get_auth_headers(lecturer_user.email, "securepassword123")

    # Global
    resp1 = await async_client.get("/api/v1/lecturer/analytics", headers=headers)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["active_courses"] == 2

    # Course specific
    resp2 = await async_client.get(f"/api/v1/lecturer/courses/{offering.id}/analytics", headers=headers)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert "average_class_score" in data2
    assert "low_performing_students" in data2
