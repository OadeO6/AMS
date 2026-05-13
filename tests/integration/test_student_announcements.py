import uuid
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.announcement import Announcement, AnnouncementView

@pytest.mark.asyncio
async def test_student_announcements(async_client: AsyncClient, get_auth_headers, setup_lecturer_data, db_session: AsyncSession):
    """
    Validates a student can list, view, and mark announcements.

    Expected response contract (per ENDPOINTS_DETAIL.md):
      GET   /student/courses/:id/announcements       -> 200 { announcements: [...], pagination: {...} }
      GET   /student/courses/:id/announcements/:id   -> 200 { id, title, body, ... }
      PATCH /student/courses/:id/announcements/:id/viewed -> 204
    """
    student_headers = await get_auth_headers(setup_lecturer_data["student"].email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id
    lecturer_id = setup_lecturer_data["lecturer"].id

    ann = Announcement(offering_id=offering_id, lecturer_id=lecturer_id, title="Test Ann", body="Hello")
    db_session.add(ann)
    await db_session.commit()

    # 1. List announcements — expect { announcements: [...], pagination: {...} }
    resp = await async_client.get(f"/api/v1/student/courses/{offering_id}/announcements", headers=student_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "announcements" in body
    anns = body["announcements"]
    assert len(anns) == 1
    assert anns[0]["viewed"] is False

    # 2. Get specific announcement — expect flat announcement item
    resp = await async_client.get(
        f"/api/v1/student/courses/{offering_id}/announcements/{ann.id}",
        headers=student_headers
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Test Ann"

    # 3. Mark as viewed
    resp = await async_client.patch(
        f"/api/v1/student/courses/{offering_id}/announcements/{ann.id}/viewed",
        headers=student_headers
    )
    assert resp.status_code == 204

    # 4. 404 Not Found
    resp = await async_client.get(
        f"/api/v1/student/courses/{offering_id}/announcements/{uuid.uuid4()}",
        headers=student_headers
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_student_announcements_support_filters_and_pagination(
    async_client: AsyncClient,
    get_auth_headers,
    setup_lecturer_data,
    db_session: AsyncSession,
):
    student = setup_lecturer_data["student"]
    student_headers = await get_auth_headers(student.email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id
    lecturer_id = setup_lecturer_data["lecturer"].id

    pinned_viewed = Announcement(
        offering_id=offering_id,
        lecturer_id=lecturer_id,
        title="Pinned viewed",
        body="Pinned and viewed",
        pinned=True,
    )
    pinned_unviewed = Announcement(
        offering_id=offering_id,
        lecturer_id=lecturer_id,
        title="Pinned unviewed",
        body="Pinned and unread",
        pinned=True,
    )
    regular = Announcement(
        offering_id=offering_id,
        lecturer_id=lecturer_id,
        title="Regular",
        body="Regular announcement",
        pinned=False,
    )
    db_session.add_all([pinned_viewed, pinned_unviewed, regular])
    await db_session.flush()

    db_session.add(
        AnnouncementView(
            announcement_id=pinned_viewed.id,
            student_id=student.id,
            viewed_at=datetime.now(UTC),
        )
    )
    await db_session.commit()

    resp = await async_client.get(
        f"/api/v1/student/courses/{offering_id}/announcements",
        headers=student_headers,
        params={"viewed": "true"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["pagination"] == {"page": 1, "limit": 20, "total": 1}
    assert [item["title"] for item in body["announcements"]] == ["Pinned viewed"]

    resp = await async_client.get(
        f"/api/v1/student/courses/{offering_id}/announcements",
        headers=student_headers,
        params={"pinned": "true", "viewed": "false"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["pagination"] == {"page": 1, "limit": 20, "total": 1}
    assert [item["title"] for item in body["announcements"]] == ["Pinned unviewed"]

    resp = await async_client.get(
        f"/api/v1/student/courses/{offering_id}/announcements",
        headers=student_headers,
        params={"page": 2, "limit": 1},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["pagination"] == {"page": 2, "limit": 1, "total": 3}
    assert len(body["announcements"]) == 1
