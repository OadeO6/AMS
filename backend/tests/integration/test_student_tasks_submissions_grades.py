import uuid
import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task, Question

@pytest.mark.asyncio
async def test_student_tasks_submissions_grades(async_client: AsyncClient, get_auth_headers, setup_lecturer_data, db_session: AsyncSession):
    """
    Validates a student's task listing, submission, and grade viewing workflow.

    Expected response contract (per ENDPOINTS_DETAIL.md):
      GET    /student/courses/:id/tasks          -> 200  { tasks: [...] }
      GET    /student/courses/:id/tasks/:id      -> 200  { id, title, questions: [...], ... }
      POST   /student/courses/:id/tasks/:id/submit -> 201 { message, submission: { id, ... } }
      GET    /student/courses/:id/grades         -> 200  { submissions: [...] }
    """
    student_headers = await get_auth_headers(setup_lecturer_data["student"].email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id

    due = datetime.now(timezone.utc) + timedelta(days=7)
    
    task = Task(offering_id=offering_id, title="Midterm", due_date=due, ai_grading=False)
    db_session.add(task)
    await db_session.flush()
    
    q1 = Question(task_id=task.id, text="Q1", type="free_text", score=10.0)
    db_session.add(q1)
    await db_session.commit()

    # 1. List tasks — expect { tasks: [...] }
    resp = await async_client.get(f"/api/v1/student/courses/{offering_id}/tasks", headers=student_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "tasks" in body
    assert len(body["tasks"]) == 1

    # 2. Get task details — expect flat task object with questions array
    resp = await async_client.get(f"/api/v1/student/courses/{offering_id}/tasks/{task.id}", headers=student_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "questions" in body
    assert len(body["questions"]) == 1

    # 3. Submit — expect { message, submission: { id, ... } }
    payload = {
        "answers": [
            {"question_id": str(q1.id), "text_answer": "My final answer"}
        ]
    }
    resp = await async_client.post(
        f"/api/v1/student/courses/{offering_id}/tasks/{task.id}/submit",
        json=payload,
        headers=student_headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "message" in body
    assert "submission" in body

    # 3b. Duplicate submission should be 409 or 400
    resp = await async_client.post(
        f"/api/v1/student/courses/{offering_id}/tasks/{task.id}/submit",
        json=payload,
        headers=student_headers
    )
    assert resp.status_code in (400, 409)

    # 4. View Grades — expect { submissions: [...] }
    resp = await async_client.get(f"/api/v1/student/courses/{offering_id}/grades", headers=student_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "submissions" in body

    # 5. Invalid path — 404 on unknown task
    resp = await async_client.get(f"/api/v1/student/courses/{offering_id}/tasks/{uuid.uuid4()}", headers=student_headers)
    assert resp.status_code == 404
