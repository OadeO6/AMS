import pytest
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta

@pytest.mark.asyncio
async def test_lecturer_crud_sessions_and_attendance(async_client: AsyncClient, get_auth_headers, setup_lecturer_data):
    """
    Validates full session + attendance lifecycle for a lecturer.

    Expected response contract (per ENDPOINTS_DETAIL.md):
      POST   /sessions        -> 201  { message, session: { id, ... } }
      GET    /sessions        -> 200  { sessions: [...] }
      GET    /sessions/:id    -> 200  { id, title, ... }
      PATCH  /sessions/:id    -> 200  { message }
      DELETE /sessions/:id    -> 200  { message }
      POST   /sessions/:id/attendance -> 200  { message, marked: N }
    """
    headers = await get_auth_headers(setup_lecturer_data["lecturer"].email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id
    student_id = setup_lecturer_data["student"].id
    
    # Create session — expect { message, session: { id, ... } }
    sched = datetime.now(timezone.utc) + timedelta(days=1)
    create_payload = {
        "title": "Week 1 Lecture",
        "scheduled_at": sched.isoformat(),
        "venue": "Room 101"
    }
    resp = await async_client.post(
        f"/api/v1/lecturer/courses/{offering_id}/sessions",
        json=create_payload,
        headers=headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "message" in body
    assert "session" in body
    session_id = body["session"]["id"]
    assert body["session"]["title"] == "Week 1 Lecture"
    
    # List sessions — expect { sessions: [...] }
    resp = await async_client.get(f"/api/v1/lecturer/courses/{offering_id}/sessions", headers=headers)
    assert resp.status_code == 200
    assert "sessions" in resp.json()
    assert len(resp.json()["sessions"]) == 1
    
    # Update session — expect { message }
    resp = await async_client.patch(
        f"/api/v1/lecturer/courses/{offering_id}/sessions/{session_id}",
        json={"status": "completed"}, 
        headers=headers
    )
    assert resp.status_code == 200
    assert "message" in resp.json()
    
    # Mark attendance — expect { message, marked: N }
    att_payload = {
        "records": [
            {"student_id": str(student_id), "status": "present"}
        ]
    }
    resp = await async_client.post(
        f"/api/v1/lecturer/courses/{offering_id}/sessions/{session_id}/attendance",
        json=att_payload,
        headers=headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "message" in body
    assert "marked" in body
    assert body["marked"] == 1
    
    # Delete session — expect { message }
    resp = await async_client.delete(
        f"/api/v1/lecturer/courses/{offering_id}/sessions/{session_id}",
        headers=headers
    )
    assert resp.status_code == 200
    assert "message" in resp.json()
    
    # Verify deletion: list should be empty
    resp = await async_client.get(f"/api/v1/lecturer/courses/{offering_id}/sessions", headers=headers)
    assert len(resp.json()["sessions"]) == 0
