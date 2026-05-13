import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.models.faculty import Faculty
from app.models.user import UserRole, User
from app.models.academic_session import AcademicSession, Semester
from app.models.course import Course, CourseOffering, CourseRegistration
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
    offerings = resp.json().get("courses", [])
    assert len(offerings) == 1
    # Check ID matches the offering id, not course id, since students interact with offerings
    assert offerings[0]["id"] == str(setup_course_data["offering"].id)
    
    # Get specific offering
    off_id = offerings[0]["id"]
    resp2 = await async_client.get(f"/api/v1/courses/{off_id}", headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["id"] == off_id


@pytest.mark.asyncio
async def test_student_course_discovery_supports_filters_and_pagination(
    async_client: AsyncClient,
    get_auth_headers,
    setup_course_data,
    db_session: AsyncSession,
):
    headers = await get_auth_headers(setup_course_data["student"].email, "securepassword123")

    second_course = Course(
        title="Linear Algebra",
        code="MTH102",
        units=3,
        department_id=setup_course_data["course"].department_id,
    )
    db_session.add(second_course)
    await db_session.flush()

    second_offering = CourseOffering(
        course_id=second_course.id,
        semester_id=setup_course_data["semester"].id,
        is_active=True,
    )
    db_session.add(second_offering)
    await db_session.commit()

    resp = await async_client.get(
        "/api/v1/courses",
        params={"department": "math", "search": "linear", "level": 1, "page": 1, "limit": 1},
        headers=headers,
    )
    assert resp.status_code == 200

    payload = resp.json()
    assert payload["pagination"] == {"page": 1, "limit": 1, "total": 1}
    assert len(payload["courses"]) == 1
    assert payload["courses"][0]["id"] == str(second_offering.id)
    assert payload["courses"][0]["level"] == 1

    resp_empty = await async_client.get(
        "/api/v1/courses",
        params={"level": 2},
        headers=headers,
    )
    assert resp_empty.status_code == 200
    assert resp_empty.json()["courses"] == []
    assert resp_empty.json()["pagination"]["total"] == 0

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
    offerings3 = resp3.json().get("courses", [])
    assert len(offerings3) == 1
    assert offerings3[0]["id"] == str(offering_id)
    
    # Drop course
    resp4 = await async_client.delete(f"/api/v1/courses/{offering_id}/register", headers=headers)
    assert resp4.status_code == 200
    
    # Confirm dropped
    resp5 = await async_client.get("/api/v1/student/courses", headers=headers)
    offerings5 = resp5.json().get("courses", [])
    assert len(offerings5) == 0


@pytest.mark.asyncio
async def test_student_registered_courses_supports_status_and_semester_filters(
    async_client: AsyncClient,
    get_auth_headers,
    setup_course_data,
    db_session: AsyncSession,
):
    headers = await get_auth_headers(setup_course_data["student"].email, "securepassword123")

    resp = await async_client.post(
        f"/api/v1/courses/{setup_course_data['offering'].id}/register",
        headers=headers,
    )
    assert resp.status_code == 201

    second_semester = Semester(
        academic_session_id=setup_course_data["semester"].academic_session_id,
        name="second",
        start_date=date(2025, 1, 10),
        end_date=date(2025, 5, 20),
        is_active=True,
    )
    db_session.add(second_semester)
    await db_session.flush()

    second_course = Course(
        title="Linear Algebra",
        code="MTH201",
        units=3,
        department_id=setup_course_data["course"].department_id,
    )
    db_session.add(second_course)
    await db_session.flush()

    second_offering = CourseOffering(
        course_id=second_course.id,
        semester_id=second_semester.id,
        is_active=True,
    )
    db_session.add(second_offering)
    await db_session.flush()

    approved_registration = CourseRegistration(
        student_id=setup_course_data["student"].id,
        offering_id=second_offering.id,
        status="approved",
    )
    db_session.add(approved_registration)
    await db_session.commit()

    resp_by_status = await async_client.get(
        "/api/v1/student/courses",
        params={"status": "approved"},
        headers=headers,
    )
    assert resp_by_status.status_code == 200
    approved_courses = resp_by_status.json()["courses"]
    assert len(approved_courses) == 1
    assert approved_courses[0]["id"] == str(second_offering.id)
    assert approved_courses[0]["status"] == "approved"

    resp_by_semester = await async_client.get(
        "/api/v1/student/courses",
        params={"semester_id": str(setup_course_data["semester"].id)},
        headers=headers,
    )
    assert resp_by_semester.status_code == 200
    semester_courses = resp_by_semester.json()["courses"]
    assert len(semester_courses) == 1
    assert semester_courses[0]["id"] == str(setup_course_data["offering"].id)
    assert semester_courses[0]["status"] == "pending"

    resp_combined = await async_client.get(
        "/api/v1/student/courses",
        params={
            "status": "approved",
            "semester_id": str(setup_course_data["semester"].id),
        },
        headers=headers,
    )
    assert resp_combined.status_code == 200
    assert resp_combined.json()["courses"] == []

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
