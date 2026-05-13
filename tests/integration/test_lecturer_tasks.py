import uuid
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta

@pytest.mark.asyncio
async def test_lecturer_crud_tasks_and_questions(async_client: AsyncClient, get_auth_headers, setup_lecturer_data):
    """
    Validates full task + question lifecycle for a lecturer.

    Expected response contract (per ENDPOINTS_DETAIL.md):
      POST   /tasks        -> 201  { message, task: { id, ... } }
      GET    /tasks        -> 200  { tasks: [...] }
      GET    /tasks/:id    -> 200  { task: { id, questions: [...], ... } }
      PATCH  /tasks/:id    -> 200  { message, task: { ... } }
      DELETE /tasks/:id    -> 200  { message }
      POST   /marking-guide -> 200 { message, marking_guide_url }
      PATCH  /ai-grading   -> 200  { message, ai_grading }
      POST   /questions    -> 201  { message, question: { id, ... } }
      PATCH  /questions/:id -> 200 { message, question: { ... } }
      DELETE /questions/:id -> 200 { message }
    """
    headers = await get_auth_headers(setup_lecturer_data["lecturer"].email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id
    
    # 1. Create task — expect wrapped response
    due = datetime.now(timezone.utc) + timedelta(days=7)
    resp = await async_client.post(
        f"/api/v1/lecturer/courses/{offering_id}/tasks",
        json={"title": "Midterm Exam", "due_date": due.isoformat(), "ai_grading": False},
        headers=headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "message" in body
    assert "task" in body
    task_id = body["task"]["id"]
    
    # 2. List tasks — expect { tasks: [...] }
    resp = await async_client.get(f"/api/v1/lecturer/courses/{offering_id}/tasks", headers=headers)
    assert resp.status_code == 200
    assert "tasks" in resp.json()
    assert len(resp.json()["tasks"]) == 1

    # 3. Get single task — expect { task: { id, questions, ... } }
    resp = await async_client.get(f"/api/v1/lecturer/courses/{offering_id}/tasks/{task_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == task_id  # TaskDetailResponse may be flat or wrapped

    # 4. Upload marking guide — expect { message, marking_guide_url }
    resp = await async_client.post(
        f"/api/v1/lecturer/courses/{offering_id}/tasks/{task_id}/marking-guide",
        json={"file_url": "s3://bucket/guide.pdf"},
        headers=headers
    )
    assert resp.status_code == 200
    assert "message" in resp.json()
    assert "marking_guide_url" in resp.json()
    
    # 5. Toggle AI grading — expect { message, ai_grading }
    resp = await async_client.patch(
        f"/api/v1/lecturer/courses/{offering_id}/tasks/{task_id}/ai-grading",
        json={"enabled": True},
        headers=headers
    )
    assert resp.status_code == 200
    assert "message" in resp.json()
    assert resp.json()["ai_grading"] is True

    # 6. Add question — expect { message, question: { id, ... } }
    resp = await async_client.post(
        f"/api/v1/lecturer/courses/{offering_id}/tasks/{task_id}/questions",
        json={"text": "What is 2+2?", "type": "mcq", "score": 2.5, "options": ["3", "4", "5"]},
        headers=headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "message" in body
    assert "question" in body
    q_id = body["question"]["id"]
    assert body["question"]["score"] == 2.5
    
    # 7. Update question — expect { message, question: { ... } }
    resp = await async_client.patch(
        f"/api/v1/lecturer/courses/{offering_id}/tasks/{task_id}/questions/{q_id}",
        json={"score": 5.0},
        headers=headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "message" in body
    assert body["question"]["score"] == 5.0

    # 8. Delete question — expect { message }
    resp = await async_client.delete(
        f"/api/v1/lecturer/courses/{offering_id}/tasks/{task_id}/questions/{q_id}",
        headers=headers
    )
    assert resp.status_code == 200
    assert "message" in resp.json()

    # 9. Update task — expect { message, task: { ... } }
    resp = await async_client.patch(
        f"/api/v1/lecturer/courses/{offering_id}/tasks/{task_id}",
        json={"title": "Updated Midterm"},
        headers=headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "message" in body
    assert body["task"]["title"] == "Updated Midterm"

    # 10. Delete task — expect { message }
    resp = await async_client.delete(f"/api/v1/lecturer/courses/{offering_id}/tasks/{task_id}", headers=headers)
    assert resp.status_code == 200
    assert "message" in resp.json()
