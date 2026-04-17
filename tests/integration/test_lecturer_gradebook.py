import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_lecturer_gradebook(async_client: AsyncClient, get_auth_headers, setup_lecturer_data):
    headers = await get_auth_headers(setup_lecturer_data["lecturer"].email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id
    student_id = setup_lecturer_data["student"].id
    
    # Get initial gradebook (empty)
    resp = await async_client.get(f"/api/v1/lecturer/courses/{offering_id}/gradebook", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 0
    
    # Create entry via patch
    resp = await async_client.patch(
        f"/api/v1/lecturer/courses/{offering_id}/gradebook/{student_id}",
        json={"manual_grade": "A", "notes": "Great work"},
        headers=headers
    )
    assert resp.status_code == 200
    
    # Verify in list
    resp = await async_client.get(f"/api/v1/lecturer/courses/{offering_id}/gradebook", headers=headers)
    entries = resp.json()
    assert len(entries) == 1
    assert entries[0]["manual_grade"] == "A"
    assert entries[0]["notes"] == "Great work"
