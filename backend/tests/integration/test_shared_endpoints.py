import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

@pytest.mark.asyncio
async def test_shared_notifications(async_client: AsyncClient, get_auth_headers, setup_lecturer_data, db_session: AsyncSession):
    student_user = setup_lecturer_data["student"]
    student_headers = await get_auth_headers(student_user.email, "securepassword123")
    
    # Create dummy notifications
    from app.repositories.notification import NotificationRepository
    from app.models.notification import NotificationChannel
    repo = NotificationRepository(db_session)
    # New schema: user_id, event, channel, title, body, data
    n1 = await repo.create(
        user_id=student_user.id,
        event="test.info",
        channel=NotificationChannel.INAPP,
        title="Hello",
        body="This is a test notification",
        data={"link": None}
    )
    n2 = await repo.create(
        user_id=student_user.id,
        event="test.alert",
        channel=NotificationChannel.INAPP,
        title="Important",
        body="This is an important notification",
        data={"link": "http://example.com"}
    )
    await db_session.commit()

    # List notifications
    resp = await async_client.get("/api/v1/notifications", headers=student_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["notifications"]) == 2
    assert data["unread_count"] == 2

    # Mark read
    patch_resp = await async_client.patch(
        "/api/v1/notifications/read",
        json={"notification_ids": [str(n1.id)]},
        headers=student_headers,
    )
    assert patch_resp.status_code == 200

    # List unread
    resp2 = await async_client.get("/api/v1/notifications?read=false", headers=student_headers)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert len(data2["notifications"]) == 1
    assert data2["unread_count"] == 1


@pytest.mark.asyncio
async def test_shared_material_download(async_client: AsyncClient, get_auth_headers, setup_lecturer_data, db_session: AsyncSession):
    student_user = setup_lecturer_data["student"]
    lecturer_user = setup_lecturer_data["lecturer"]
    student_headers = await get_auth_headers(student_user.email, "securepassword123")
    lecturer_headers = await get_auth_headers(lecturer_user.email, "securepassword123")
    
    offering_id = setup_lecturer_data["offering"].id

    from app.models.material import Material
    m1 = Material(offering_id=offering_id, uploaded_by=lecturer_user.id, title="Visible", type="document", file_url="1.pdf", visibility="students_only")
    m2 = Material(offering_id=offering_id, uploaded_by=lecturer_user.id, title="AI", type="document", file_url="2.pdf", visibility="ai_only")
    db_session.add_all([m1, m2])
    await db_session.commit()

    # Student download visible
    resp1 = await async_client.get(f"/api/v1/materials/{m1.id}/download", headers=student_headers)
    assert resp1.status_code == 200
    assert resp1.json()["url"] == "1.pdf"

    # Student download AI only -> 403
    resp2 = await async_client.get(f"/api/v1/materials/{m2.id}/download", headers=student_headers)
    assert resp2.status_code == 403

    # Lecturer download AI only -> 200
    resp3 = await async_client.get(f"/api/v1/materials/{m2.id}/download", headers=lecturer_headers)
    assert resp3.status_code == 200


@pytest.mark.asyncio
async def test_shared_users_list(async_client: AsyncClient, get_auth_headers, setup_lecturer_data, db_session: AsyncSession):
    student_user = setup_lecturer_data["student"]
    lecturer_user = setup_lecturer_data["lecturer"]
    student_headers = await get_auth_headers(student_user.email, "securepassword123")
    
    # Create an admin user to verify filtering logic
    from app.repositories.user import UserRepository
    from app.models.user import UserRole
    from app.core.security import get_password_hash
    repo = UserRepository(db_session)
    admin = await repo.create(
        email="admin_shared_test@example.com",
        hashed_password=get_password_hash("securepassword123"),
        first_name="Admin",
        last_name="Test",
        roles=[UserRole.ADMIN.value],
        is_active=True
    )
    await db_session.commit()

    # Student requests shared users
    resp = await async_client.get("/api/v1/users", headers=student_headers)
    assert resp.status_code == 200
    data = resp.json()
    users = data["users"]
    
    # Admin should not be visible to student
    assert any(u["email"] == student_user.email for u in users)
    assert any(u["email"] == lecturer_user.email for u in users)
    assert not any(u["email"] == admin.email for u in users)

    # Filter by role
    resp = await async_client.get("/api/v1/users?role=lecturer", headers=student_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["users"]) >= 1
    assert all("lecturer" in u["roles"] for u in data["users"])

