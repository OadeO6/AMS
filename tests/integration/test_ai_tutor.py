import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ai_tutor_student_chat(async_client: AsyncClient, setup_lecturer_data, get_auth_headers):
    """Test that a student can query the AI tutor."""
    student_user = setup_lecturer_data["student"]
    offering = setup_lecturer_data["offering"]
    headers = await get_auth_headers(student_user.email, "securepassword123")

    # Send chat
    resp = await async_client.post(
        f"/api/v1/student/courses/{offering.id}/ai-tutor",
        headers=headers,
        json={"message": "Can you explain recursion?"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert "Simulated AI Tutor response to: 'Can you explain recursion?'." in data["reply"]


@pytest.mark.asyncio
async def test_ai_tutor_lecturer(async_client: AsyncClient, setup_lecturer_data, get_auth_headers):
    """Test lecturer updating rules and querying AI tutor."""
    lecturer_user = setup_lecturer_data["lecturer"]
    offering = setup_lecturer_data["offering"]
    headers = await get_auth_headers(lecturer_user.email, "securepassword123")

    # Update Rules
    custom_rules = "Always reply with 'Hello Academic'."
    patch_resp = await async_client.patch(
        f"/api/v1/lecturer/courses/{offering.id}/ai-tutor/rules",
        headers=headers,
        json={"rules": custom_rules}
    )
    assert patch_resp.status_code == 200

    # Lecturer Chat (should reflect the rules in the mock response)
    chat_resp = await async_client.post(
        f"/api/v1/lecturer/courses/{offering.id}/ai-tutor",
        headers=headers,
        json={"message": "Testing my rules"}
    )
    assert chat_resp.status_code == 200
    reply = chat_resp.json()["reply"]
    assert "Lecturer Rule snippet" in reply
