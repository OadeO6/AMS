import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_lecturer_crud_announcements(async_client: AsyncClient, get_auth_headers, setup_lecturer_data):
    headers = await get_auth_headers(setup_lecturer_data["lecturer"].email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id
    
    create_payload = {
        "title": "Welcome to class",
        "body": "Please read the syllabus",
        "pinned": True
    }
    resp = await async_client.post(f"/api/v1/lecturer/courses/{offering_id}/announcements", json=create_payload, headers=headers)
    assert resp.status_code == 201
    ann = resp.json()
    ann_id = ann["id"]
    assert ann["title"] == "Welcome to class"
    
    # List announcements
    resp = await async_client.get(f"/api/v1/lecturer/courses/{offering_id}/announcements?pinned=true", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    
    # Update announcement
    resp = await async_client.patch(
        f"/api/v1/lecturer/courses/{offering_id}/announcements/{ann_id}",
        json={"title": "Updated Welcome"}, 
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Welcome"
    
    # Delete announcement
    resp = await async_client.delete(f"/api/v1/lecturer/courses/{offering_id}/announcements/{ann_id}", headers=headers)
    assert resp.status_code == 204
    
    resp = await async_client.get(f"/api/v1/lecturer/courses/{offering_id}/announcements", headers=headers)
    assert len(resp.json()) == 0
