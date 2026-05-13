import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.class_session import ClassSession, Attendance

@pytest.mark.asyncio
async def test_student_sessions_attendance(async_client: AsyncClient, get_auth_headers, setup_lecturer_data, db_session: AsyncSession):
    """
    Validates that a student can view sessions and their own attendance.

    Expected response contract (per ENDPOINTS_DETAIL.md):
      GET /student/courses/:id/sessions          -> 200 { sessions: [...] }
      GET /student/courses/:id/sessions/:id      -> 200 { session: { id, title, ... }, attendance: { status, ... } }
      GET /student/courses/:id/attendance        -> 200 { attendance: [...] }
    """
    student_headers = await get_auth_headers(setup_lecturer_data["student"].email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id
    lecturer_id = setup_lecturer_data["lecturer"].id
    student_id = setup_lecturer_data["student"].id

    dt = datetime.now(timezone.utc) + timedelta(days=1)
    
    sess = ClassSession(offering_id=offering_id, lecturer_id=lecturer_id, title="Class 1", scheduled_at=dt, status="completed")
    db_session.add(sess)
    await db_session.flush()
    
    att = Attendance(session_id=sess.id, student_id=student_id, status="present", marked_by=lecturer_id, marked_at=dt)
    db_session.add(att)
    await db_session.commit()

    # 1. List sessions — expect { sessions: [...] }
    resp = await async_client.get(f"/api/v1/student/courses/{offering_id}/sessions", headers=student_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "sessions" in body
    assert len(body["sessions"]) == 1
    assert body["sessions"][0]["title"] == "Class 1"

    # 2. Get single session — expect { session: { ... }, attendance: { status, ... } }
    resp = await async_client.get(f"/api/v1/student/courses/{offering_id}/sessions/{sess.id}", headers=student_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "attendance" in data
    assert data["attendance"]["marked"] is True
    assert data["attendance"]["attended"] is True
    assert "session" in data
    assert data["session"]["title"] == "Class 1"

    # 3. Get all attendance — expect { attendance: [...] }
    resp = await async_client.get(f"/api/v1/student/courses/{offering_id}/attendance", headers=student_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "attendance" in body
    assert len(body["attendance"]) == 1
    assert body["attendance"][0]["status"] == "present"
