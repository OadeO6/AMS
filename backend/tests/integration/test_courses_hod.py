import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.models.faculty import Faculty
from app.models.user import User, UserRole

@pytest.fixture
async def hod_context(db_session: AsyncSession, hod_user: User):
    # Create faculty & dept first
    faculty = Faculty(name="Engineering", code="ENG")
    db_session.add(faculty)
    await db_session.flush()

    dept = Department(faculty_id=faculty.id, name="Computer Science", code="CS", hod_id=hod_user.id)
    db_session.add(dept)
    await db_session.flush()
    
    # Update HOD to belong to the dept
    hod_user.department_id = dept.id
    await db_session.commit()
    
    return {"hod": hod_user, "faculty": faculty, "dept": dept}

@pytest.fixture
async def sec_hod_context(db_session: AsyncSession, hod_context):
    from app.core.security import get_password_hash
    hod_user = User(
        email="hodSCI@test.com", first_name="Hod2", last_name="Two",
        hashed_password=get_password_hash("securepassword123"), roles=[UserRole.HOD.value], is_active=True
    )
    db_session.add(hod_user)
    await db_session.flush()
    
    dept = Department(faculty_id=hod_context["faculty"].id, name="Physics", code="PHY", hod_id=hod_user.id)
    db_session.add(dept)
    await db_session.flush()
    
    hod_user.department_id = dept.id
    await db_session.commit()
    
    return {"hod": hod_user, "dept": dept}

@pytest.mark.asyncio
async def test_hod_create_course(async_client: AsyncClient, get_auth_headers, hod_context):
    headers = await get_auth_headers(hod_context["hod"].email, "securepassword123")
    
    payload = {
        "title": "Intro to Programming",
        "code": "CS101",
        "description": "Basics of Python",
        "units": 3
    }
    
    resp = await async_client.post("/api/v1/hod/courses", json=payload, headers=headers)
    assert resp.status_code == 201
    body = resp.json()
    # spec: { message, course: { id, ... } }
    assert "message" in body
    assert "course" in body
    assert "id" in body["course"]
    
    # Duplicate code
    resp2 = await async_client.post("/api/v1/hod/courses", json=payload, headers=headers)
    assert resp2.status_code == 409

@pytest.mark.asyncio
async def test_hod_list_and_get_course(async_client: AsyncClient, get_auth_headers, hod_context, sec_hod_context):
    headers = await get_auth_headers(hod_context["hod"].email, "securepassword123")
    
    # Create
    await async_client.post("/api/v1/hod/courses", json={
        "title": "Data Structures", "code": "CS201", "units": 4
    }, headers=headers)
    
    # List courses — spec: { courses: [...], pagination: {...} }
    resp = await async_client.get("/api/v1/hod/courses", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "courses" in body
    assert len(body["courses"]) == 1
    course_id = body["courses"][0]["id"]
    
    # Get details
    resp2 = await async_client.get(f"/api/v1/hod/courses/{course_id}", headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["code"] == "CS201"
    
    # Other HOD should not see it — mint token directly (fixtures share the same DB transaction)
    from app.core.security import create_access_token
    token2 = create_access_token(subject=str(sec_hod_context["hod"].id))
    headers2 = {"Authorization": f"Bearer {token2}"}
    resp3 = await async_client.get(f"/api/v1/hod/courses/{course_id}", headers=headers2)
    assert resp3.status_code == 403

@pytest.mark.asyncio
async def test_hod_create_offering(async_client: AsyncClient, get_auth_headers, hod_context, db_session: AsyncSession):
    headers = await get_auth_headers(hod_context["hod"].email, "securepassword123")
    
    # Needs a session/semester
    from app.models.academic_session import AcademicSession, Semester
    from datetime import date
    
    session = AcademicSession(name="2025/2026")
    db_session.add(session)
    await db_session.flush()
    
    semester = Semester(
        academic_session_id=session.id,
        name="first",
        start_date=date(2025, 9, 1),
        end_date=date(2025, 12, 15),
        is_active=True
    )
    db_session.add(semester)
    await db_session.commit()
    
    # Create course
    payload = {"title": "Operating Systems", "code": "CS301", "units": 3}
    course_resp = await async_client.post("/api/v1/hod/courses", json=payload, headers=headers)
    course_id = course_resp.json()["course"]["id"]   # spec: { course: { id, ... } }
    
    # Create offering
    offer_payload = {"semester_id": str(semester.id)}
    offer_resp = await async_client.post(f"/api/v1/hod/courses/{course_id}/offerings", json=offer_payload, headers=headers)
    assert offer_resp.status_code == 201
    
    # Duplicate offering
    offer_resp2 = await async_client.post(f"/api/v1/hod/courses/{course_id}/offerings", json=offer_payload, headers=headers)
    assert offer_resp2.status_code == 409

    # Update course — spec: { message, course: { title, ... } }
    patch_resp = await async_client.patch(f"/api/v1/hod/courses/{course_id}", json={"title": "Advanced OS"}, headers=headers)
    assert patch_resp.status_code == 200
    assert patch_resp.json()["course"]["title"] == "Advanced OS"

    # List offerings
    list_resp = await async_client.get(f"/api/v1/hod/courses/{course_id}/offerings", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # Try deleting a course with offerings (should be 409)
    del_resp = await async_client.delete(f"/api/v1/hod/courses/{course_id}", headers=headers)
    assert del_resp.status_code == 409

    # Create a fresh course and delete it successfully — spec: { message }
    payload_new = {"title": "Math 101", "code": "MTH101", "units": 3}
    course_resp2 = await async_client.post("/api/v1/hod/courses", json=payload_new, headers=headers)
    c2 = course_resp2.json()["course"]["id"]   # spec: { course: { id, ... } }

    del_resp2 = await async_client.delete(f"/api/v1/hod/courses/{c2}", headers=headers)
    assert del_resp2.status_code == 200
    assert "message" in del_resp2.json()

@pytest.mark.asyncio
async def test_hod_course_offering_lecturer_assignment(async_client: AsyncClient, get_auth_headers, hod_context, db_session: AsyncSession, lecturer_user: User):
    headers = await get_auth_headers(hod_context["hod"].email, "securepassword123")
    
    # Session & Semester
    from app.models.academic_session import AcademicSession, Semester
    from datetime import date
    sess = AcademicSession(name="2026/2027")
    db_session.add(sess)
    await db_session.flush()
    sem = Semester(academic_session_id=sess.id, name="first", start_date=date(2026, 9, 1), end_date=date(2026, 12, 1), is_active=True)
    db_session.add(sem)
    
    # Course
    from app.models.course import Course
    course = Course(department_id=hod_context["dept"].id, title="Algorithm", code="CS202", units=3)
    db_session.add(course)
    await db_session.commit()
    
    # 1. Create Offering — spec: { message, offering: { id, ... } }
    offer_resp = await async_client.post(
        f"/api/v1/hod/courses/{course.id}/offerings",
        json={"semester_id": str(sem.id)},
        headers=headers
    )
    offering_id = offer_resp.json()["offering"]["id"]
    
    # 2. Assign first Lecturer — spec: { message, offering: { lecturers: [...], ... } }
    assign_resp = await async_client.post(
        f"/api/v1/hod/courses/{course.id}/offerings/{offering_id}/assign", 
        json={"lecturer_id": str(lecturer_user.id)}, 
        headers=headers
    )
    assert assign_resp.status_code == 200
    body = assign_resp.json()
    lecturer_ids = [lec["lecturer_id"] for lec in body["offering"]["lecturers"]]
    assert str(lecturer_user.id) in lecturer_ids

    # 3. Duplicate assignment — should return 409
    dup_resp = await async_client.post(
        f"/api/v1/hod/courses/{course.id}/offerings/{offering_id}/assign", 
        json={"lecturer_id": str(lecturer_user.id)}, 
        headers=headers
    )
    assert dup_resp.status_code == 409

    # 4. Unassign Lecturer
    unassign_resp = await async_client.delete(f"/api/v1/hod/courses/{course.id}/offerings/{offering_id}/assign/{lecturer_user.id}", headers=headers)
    assert unassign_resp.status_code == 200
    
    # 5. Assignment error (Not a lecturer)
    admin_id = hod_context["hod"].id
    bad_assign = await async_client.post(
        f"/api/v1/hod/courses/{course.id}/offerings/{offering_id}/assign", 
        json={"lecturer_id": str(admin_id)}, 
        headers=headers
    )
    assert bad_assign.status_code in [400, 403, 409]
