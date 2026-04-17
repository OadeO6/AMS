import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.models.faculty import Faculty
from app.models.user import User, UserRole
from app.core.security import get_password_hash


@pytest.fixture
async def setup_department(db_session: AsyncSession) -> Department:
    faculty = Faculty(name="Engineering", code="ENG")
    db_session.add(faculty)
    await db_session.flush()

    department = Department(name="Computer Science", code="CS", faculty_id=faculty.id)
    db_session.add(department)
    await db_session.commit()
    return department


@pytest.mark.asyncio
async def test_admin_list_users(
    async_client: AsyncClient, admin_headers: dict[str, str], student_user: User, lecturer_user: User
) -> None:
    response = await async_client.get("/api/v1/admin/users", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert len(data["users"]) >= 2  # The populated fixtures


@pytest.mark.asyncio
async def test_admin_authorize_staff(
    async_client: AsyncClient, admin_headers: dict[str, str], db_session: AsyncSession
) -> None:
    # 1. Create unauthorized lecturer
    unauth_lecturer = User(
        email=f"unauth_{uuid.uuid4()}@example.com",
        first_name="Unauth",
        last_name="Lecturer",
        hashed_password=get_password_hash("password123"),
        role=UserRole.LECTURER,
        is_active=True,
        is_authorized=False,
    )
    db_session.add(unauth_lecturer)
    await db_session.commit()

    # 2. They should get 403 hitting a lecturer protected route
    # Let's manually get their token:
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": unauth_lecturer.email, "password": "password123"}
    )
    unauth_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
    
    # Try getting courses (which requires AuthorizedLecturer)
    resp1 = await async_client.get("/api/v1/lecturer/courses", headers=unauth_headers)
    assert resp1.status_code == 403
    assert resp1.json()["detail"] == "Your lecturer account has not been authorized by an Admin yet."

    # 3. Admin authorizes them
    auth_resp = await async_client.post(
        "/api/v1/admin/staff/authorize",
        json={"user_id": str(unauth_lecturer.id)},
        headers=admin_headers
    )
    assert auth_resp.status_code == 200

    # 4. Now they should be able to access the route! (wait, we need to refresh state, the token is valid, user is re-fetched on each request by dependency)
    resp2 = await async_client.get("/api/v1/lecturer/courses", headers=unauth_headers)
    # Route is now fully implemented — authorized lecturer gets 200
    assert resp2.status_code == 200


@pytest.mark.asyncio
async def test_hod_list_and_update_student(
    async_client: AsyncClient, 
    hod_headers: dict[str, str], 
    hod_user: User,
    student_user: User,
    setup_department: Department,
    db_session: AsyncSession
) -> None:
    # 1. Assign HOD and Student to the same department
    hod_user.department_id = setup_department.id
    student_user.department_id = setup_department.id
    db_session.add_all([hod_user, student_user])
    await db_session.commit()

    # 2. HOD lists students
    resp_list = await async_client.get("/api/v1/hod/students", headers=hod_headers)
    assert resp_list.status_code == 200
    data = resp_list.json()
    assert len(data["users"]) == 1
    assert data["users"][0]["id"] == str(student_user.id)

    # 3. HOD updates student level offset
    resp_patch = await async_client.patch(
        f"/api/v1/hod/students/{student_user.id}/level-offset",
        json={"level_offset": 2},
        headers=hod_headers
    )
    assert resp_patch.status_code == 200

    # Verify that the offset was updated
    await db_session.refresh(student_user)
    assert student_user.level_offset == 2
