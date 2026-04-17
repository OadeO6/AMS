import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.models.faculty import Faculty
from app.models.user import UserRole, User
from app.models.academic_session import AcademicSession, Semester
from app.models.course import Course, CourseOffering
from datetime import date

@pytest.fixture
async def setup_course_data(db_session: AsyncSession, student_user: User):
    student = student_user
    
    # Semester setup
    academic_session = AcademicSession(name="2024/2025")
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
    fac = Faculty(name="Science", code="SCI")
    db_session.add(fac)
    await db_session.flush()
    
    dept = Department(faculty_id=fac.id, name="Math", code="MTH")
    db_session.add(dept)
    await db_session.flush()
    
    course = Course(title="Calculus I", code="MTH101", units=3, department_id=dept.id)
    db_session.add(course)
    await db_session.flush()
    
    offering = CourseOffering(course_id=course.id, semester_id=semester.id, is_active=True)
    db_session.add(offering)
    await db_session.commit()
    
    return {
        "student": student,
        "semester": semester,
        "course": course,
        "offering": offering
    }

@pytest.mark.asyncio
async def test_student_course_discovery(async_client: AsyncClient, get_auth_headers, setup_course_data):
    headers = await get_auth_headers(setup_course_data["student"].email, "securepassword123")
    
    # List offerings
    resp = await async_client.get("/api/v1/courses", headers=headers)
    assert resp.status_code == 200
    offerings = resp.json()
    assert len(offerings) == 1
    assert offerings[0]["course_id"] == str(setup_course_data["course"].id)
    
    # Get specific offering
    off_id = offerings[0]["id"]
    resp2 = await async_client.get(f"/api/v1/courses/{off_id}", headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["id"] == off_id

@pytest.mark.asyncio
async def test_student_register_and_drop(async_client: AsyncClient, get_auth_headers, setup_course_data):
    headers = await get_auth_headers(setup_course_data["student"].email, "securepassword123")
    offering_id = setup_course_data["offering"].id
    
    # Register
    resp = await async_client.post(f"/api/v1/courses/{offering_id}/register", headers=headers)
    assert resp.status_code == 201
    assert resp.json()["status"] == "pending"
    
    # Prevent duplicate
    resp2 = await async_client.post(f"/api/v1/courses/{offering_id}/register", headers=headers)
    assert resp2.status_code == 409
    
    # View my courses
    resp3 = await async_client.get("/api/v1/student/courses", headers=headers)
    assert resp3.status_code == 200
    assert len(resp3.json()) == 1
    assert resp3.json()[0]["id"] == str(offering_id)
    
    # Drop course
    resp4 = await async_client.delete(f"/api/v1/courses/{offering_id}/register", headers=headers)
    assert resp4.status_code == 200
    
    # Confirm dropped
    resp5 = await async_client.get("/api/v1/student/courses", headers=headers)
    assert len(resp5.json()) == 0

@pytest.mark.asyncio
async def test_student_cannot_register_inactive_semester(
    async_client: AsyncClient, get_auth_headers, setup_course_data, db_session: AsyncSession
):
    headers = await get_auth_headers(setup_course_data["student"].email, "securepassword123")
    offering_id = setup_course_data["offering"].id
    
    # Deactivate the semester natively
    semester = await db_session.get(Semester, setup_course_data["semester"].id)
    semester.is_active = False
    await db_session.commit()
    
    # Try register
    resp = await async_client.post(f"/api/v1/courses/{offering_id}/register", headers=headers)
    assert resp.status_code == 403
    assert "No active semester" in resp.json()["detail"]
