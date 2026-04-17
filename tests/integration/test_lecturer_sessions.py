import pytest
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta

@pytest.mark.asyncio
async def test_lecturer_crud_sessions_and_attendance(async_client: AsyncClient, get_auth_headers, setup_lecturer_data):
    headers = await get_auth_headers(setup_lecturer_data["lecturer"].email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id
    student_id = setup_lecturer_data["student"].id
    
    # Create session
    sched = datetime.now(timezone.utc) + timedelta(days=1)
    create_payload = {
        "title": "Week 1 Lecture",
        "scheduled_at": sched.isoformat(),
        "venue": "Room 101"
    }
    resp = await async_client.post(f"/api/v1/lecturer/courses/{offering_id}/sessions", json=create_payload, headers=headers)
    assert resp.status_code == 201
    session_data = resp.json()
    session_id = session_data["id"]
    assert session_data["title"] == "Week 1 Lecture"
    assert session_data["is_owner"] is True
    
    # List sessions
    resp = await async_client.get(f"/api/v1/lecturer/courses/{offering_id}/sessions", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    
    # Update session
    resp = await async_client.patch(
        f"/api/v1/lecturer/courses/{offering_id}/sessions/{session_id}",
        json={"status": "completed"}, 
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"
    
    # Mark attendance
    att_payload = {
        "records": [
            {"student_id": str(student_id), "status": "present"}
        ]
    }
    resp = await async_client.post(f"/api/v1/lecturer/courses/{offering_id}/sessions/{session_id}/attendance", json=att_payload, headers=headers)
    assert resp.status_code == 200
    att_data = resp.json()
    assert len(att_data) == 1
    assert att_data[0]["status"] == "present"
    
    # Delete session
    resp = await async_client.delete(f"/api/v1/lecturer/courses/{offering_id}/sessions/{session_id}", headers=headers)
    assert resp.status_code == 204
    
    resp = await async_client.get(f"/api/v1/lecturer/courses/{offering_id}/sessions", headers=headers)
    assert len(resp.json()) == 0
