# tests/integration/test_admin_academic.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_admin_academic_session_crud(async_client: AsyncClient, admin_headers: dict[str, str]) -> None:
    session_payload = {
        "name": "2024/2025",
        "semesters": [
            {"name": "first", "start_date": "2024-09-01", "end_date": "2025-01-31"},
            {"name": "second", "start_date": "2025-02-15", "end_date": "2025-07-30"}
        ]
    }
    
    # 1. Create Session
    response = await async_client.post("/api/v1/admin/academic-sessions", json=session_payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    session_id = data["id"]
    assert len(data["semesters"]) == 2
    first_sem_id = next(s["id"] for s in data["semesters"] if s["name"] == "first")
    second_sem_id = next(s["id"] for s in data["semesters"] if s["name"] == "second")
    
    # duplicate check
    dup_res = await async_client.post("/api/v1/admin/academic-sessions", json=session_payload, headers=admin_headers)
    assert dup_res.status_code == 409
    
    # 2. Activate first semester
    activate_res1 = await async_client.patch(
        f"/api/v1/admin/academic-sessions/{session_id}/semesters/{first_sem_id}/activate",
        headers=admin_headers
    )
    assert activate_res1.status_code == 200
    assert activate_res1.json()["is_active"] == True
    
    # Verify the first semester is the active one in the session get
    get_res = await async_client.get(f"/api/v1/admin/academic-sessions/{session_id}", headers=admin_headers)
    sems = get_res.json()["semesters"]
    first = next(s for s in sems if s["id"] == first_sem_id)
    second = next(s for s in sems if s["id"] == second_sem_id)
    assert first["is_active"] == True
    assert second["is_active"] == False

    # 3. Activate second semester
    activate_res2 = await async_client.patch(
        f"/api/v1/admin/academic-sessions/{session_id}/semesters/{second_sem_id}/activate",
        headers=admin_headers
    )
    assert activate_res2.status_code == 200
    
    # Verify first got deactivated
    get_res2 = await async_client.get(f"/api/v1/admin/academic-sessions/{session_id}", headers=admin_headers)
    sems2 = get_res2.json()["semesters"]
    first2 = next(s for s in sems2 if s["id"] == first_sem_id)
    second2 = next(s for s in sems2 if s["id"] == second_sem_id)
    assert first2["is_active"] == False
    assert second2["is_active"] == True

@pytest.mark.asyncio
async def test_admin_academic_not_found(async_client: AsyncClient, admin_headers: dict[str, str]) -> None:
    import uuid
    fake_id = str(uuid.uuid4())
    
    # Session not found
    res = await async_client.get(f"/api/v1/admin/academic-sessions/{fake_id}", headers=admin_headers)
    assert res.status_code == 404
    
    # Semester not found
    res2 = await async_client.patch(
        f"/api/v1/admin/academic-sessions/{fake_id}/semesters/{fake_id}/activate",
        headers=admin_headers
    )
    assert res2.status_code == 404
    
    # Delete not found
    res3 = await async_client.delete(f"/api/v1/admin/academic-sessions/{fake_id}", headers=admin_headers)
    assert res3.status_code == 404
