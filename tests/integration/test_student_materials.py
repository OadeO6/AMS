import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.material import Material

@pytest.mark.asyncio
async def test_student_materials(async_client: AsyncClient, get_auth_headers, setup_lecturer_data, db_session: AsyncSession):
    # Log in as the student
    student_headers = await get_auth_headers(setup_lecturer_data["student"].email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id
    lecturer_id = setup_lecturer_data["lecturer"].id

    # Add materials with different visibilities directly via DB
    m1 = Material(offering_id=offering_id, uploaded_by=lecturer_id, title="Visible", type="document", file_url="1.pdf", visibility="students_only")
    m2 = Material(offering_id=offering_id, uploaded_by=lecturer_id, title="Visible2", type="document", file_url="2.pdf", visibility="both")
    m3 = Material(offering_id=offering_id, uploaded_by=lecturer_id, title="Hidden", type="document", file_url="3.pdf", visibility="ai_only")
    
    db_session.add_all([m1, m2, m3])
    await db_session.commit()

    # Request as student
    resp = await async_client.get(f"/api/v1/student/courses/{offering_id}/materials", headers=student_headers)
    assert resp.status_code == 200
    mats = resp.json()
    assert len(mats) == 2
    titles = [m["title"] for m in mats]
    assert "Visible" in titles
    assert "Visible2" in titles
    assert "Hidden" not in titles
