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
    repo = NotificationRepository(db_session)
    n1 = await repo.create(student_user.id, "Hello", "info", None)
    n2 = await repo.create(student_user.id, "Important", "alert", "http://example.com")
    await db_session.commit()

    # List notifications
    resp = await async_client.get("/api/v1/notifications", headers=student_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["notifications"]) == 2
    assert data["unread_count"] == 2

    # Mark read
    patch_resp = await async_client.patch(f"/api/v1/notifications/{n1.id}/read", headers=student_headers)
    assert patch_resp.status_code == 200

    # List unread
    resp2 = await async_client.get("/api/v1/notifications?read=false", headers=student_headers)
    assert resp2.status_code == 200
    assert len(resp2.json()["notifications"]) == 1
    assert resp2.json()["unread_count"] == 1


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
