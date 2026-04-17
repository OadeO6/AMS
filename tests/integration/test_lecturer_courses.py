import uuid
from datetime import date
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academic_session import AcademicSession, Semester
from app.models.course import Course, CourseOffering, CourseRegistration
from app.models.department import Department
from app.models.faculty import Faculty
from app.models.user import User


@pytest.mark.asyncio
async def test_lecturer_list_and_get_courses(async_client: AsyncClient, get_auth_headers, setup_lecturer_data):
    headers = await get_auth_headers(setup_lecturer_data["lecturer"].email, "securepassword123")
    
    # List courses
    resp = await async_client.get("/api/v1/lecturer/courses", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == str(setup_lecturer_data["offering"].id)
    
    # Get specific course
    resp = await async_client.get(f"/api/v1/lecturer/courses/{setup_lecturer_data['offering'].id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == str(setup_lecturer_data["offering"].id)


@pytest.mark.asyncio
async def test_lecturer_manage_students(async_client: AsyncClient, get_auth_headers, setup_lecturer_data, db_session: AsyncSession):
    headers = await get_auth_headers(setup_lecturer_data["lecturer"].email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id
    student_id = setup_lecturer_data["student"].id
    
    # List students
    resp = await async_client.get(f"/api/v1/lecturer/courses/{offering_id}/students", headers=headers)
    assert resp.status_code == 200
    students = resp.json()
    assert len(students) == 1
    assert students[0]["student_id"] == str(student_id)
    assert students[0]["status"] == "approved"
    
    # Approve student
    resp = await async_client.patch(f"/api/v1/lecturer/courses/{offering_id}/students/{student_id}/approve", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"
    
    # Verify via DB
    await db_session.refresh(setup_lecturer_data["registration"])
    assert setup_lecturer_data["registration"].status == "approved"
