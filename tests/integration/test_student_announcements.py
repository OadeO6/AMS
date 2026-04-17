import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.announcement import Announcement

@pytest.mark.asyncio
async def test_student_announcements(async_client: AsyncClient, get_auth_headers, setup_lecturer_data, db_session: AsyncSession):
    student_headers = await get_auth_headers(setup_lecturer_data["student"].email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id
    lecturer_id = setup_lecturer_data["lecturer"].id

    ann = Announcement(offering_id=offering_id, lecturer_id=lecturer_id, title="Test Ann", body="Hello")
    db_session.add(ann)
    await db_session.commit()

    # 1. List announcements
    resp = await async_client.get(f"/api/v1/student/courses/{offering_id}/announcements", headers=student_headers)
    assert resp.status_code == 200
    anns = resp.json()
    assert len(anns) == 1
    assert anns[0]["viewed"] is False

    # 2. Get specific announcement
    resp = await async_client.get(f"/api/v1/student/courses/{offering_id}/announcements/{ann.id}", headers=student_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Test Ann"

    # 3. Mark as viewed
    resp = await async_client.patch(f"/api/v1/student/courses/{offering_id}/announcements/{ann.id}/viewed", headers=student_headers)
    assert resp.status_code == 204

    # 4. 404 Not Found
    resp = await async_client.get(f"/api/v1/student/courses/{offering_id}/announcements/{uuid.uuid4()}", headers=student_headers)
    assert resp.status_code == 404
