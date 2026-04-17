import uuid
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta

@pytest.mark.asyncio
async def test_lecturer_crud_tasks_and_questions(async_client: AsyncClient, get_auth_headers, setup_lecturer_data):
    headers = await get_auth_headers(setup_lecturer_data["lecturer"].email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id
    
    # 1. Create task
    due = datetime.now(timezone.utc) + timedelta(days=7)
    resp = await async_client.post(
        f"/api/v1/lecturer/courses/{offering_id}/tasks",
        json={"title": "Midterm Exam", "due_date": due.isoformat(), "ai_grading": False},
        headers=headers
    )
    assert resp.status_code == 201
    task = resp.json()
    task_id = task["id"]
    
    # 2. Add marking guide & enable AI grading
    resp = await async_client.post(
        f"/api/v1/lecturer/courses/{offering_id}/tasks/{task_id}/marking-guide",
        json={"file_url": "s3://bucket/guide.pdf"},
        headers=headers
    )
    assert resp.status_code == 200
    
    resp = await async_client.patch(
        f"/api/v1/lecturer/courses/{offering_id}/tasks/{task_id}/ai-grading",
        json={"enabled": True},
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["ai_grading"] is True

    # 3. Add question
    resp = await async_client.post(
        f"/api/v1/lecturer/courses/{offering_id}/tasks/{task_id}/questions",
        json={"text": "What is 2+2?", "type": "mcq", "score": 2.5, "options": ["3", "4", "5"]},
        headers=headers
    )
    assert resp.status_code == 201
    q = resp.json()
    q_id = q["id"]
    assert q["score"] == 2.5
    
    # 4. Update question
    resp = await async_client.patch(
        f"/api/v1/lecturer/courses/{offering_id}/tasks/{task_id}/questions/{q_id}",
        json={"score": 5.0},
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["score"] == 5.0
    
    # 5. Delete components
    resp = await async_client.delete(f"/api/v1/lecturer/courses/{offering_id}/tasks/{task_id}", headers=headers)
    assert resp.status_code == 204
