import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_lecturer_crud_materials(async_client: AsyncClient, get_auth_headers, setup_lecturer_data):
    headers = await get_auth_headers(setup_lecturer_data["lecturer"].email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id
    
    # Create mock file in memory
    import io
    file_content = b"PDF bytes"
    
    files = {"file": ("syllabus.pdf", file_content, "application/pdf")}
    data = {
        "title": "Syllabus",
        "type": "note",
        "visibility": "students_only"
    }
    
    resp = await async_client.post(
        f"/api/v1/lecturer/courses/{offering_id}/materials",
        data=data,
        files=files,
        headers=headers
    )
    assert resp.status_code == 201
    mat = resp.json()
    mat_id = mat["id"]
    
    # Update Material
    resp = await async_client.patch(f"/api/v1/lecturer/courses/{offering_id}/materials/{mat_id}", json={"title": "Updated Syllabus"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Syllabus"
    
    # Verify index fails for students_only
    resp = await async_client.post(f"/api/v1/lecturer/courses/{offering_id}/materials/{mat_id}/index", headers=headers)
    assert resp.status_code == 400
    assert "Cannot index a students-only material" in resp.json()["detail"]
    
    # Make visible to AI and Index
    await async_client.patch(f"/api/v1/lecturer/courses/{offering_id}/materials/{mat_id}", json={"visibility": "ai_only"}, headers=headers)
    resp = await async_client.post(f"/api/v1/lecturer/courses/{offering_id}/materials/{mat_id}/index", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["indexed"] is True
    
    # Delete Material
    resp = await async_client.delete(f"/api/v1/lecturer/courses/{offering_id}/materials/{mat_id}", headers=headers)
    assert resp.status_code == 204
