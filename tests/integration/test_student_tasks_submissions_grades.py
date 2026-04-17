import uuid
import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task, Question

@pytest.mark.asyncio
async def test_student_tasks_submissions_grades(async_client: AsyncClient, get_auth_headers, setup_lecturer_data, db_session: AsyncSession):
    student_headers = await get_auth_headers(setup_lecturer_data["student"].email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id

    due = datetime.now(timezone.utc) + timedelta(days=7)
    
    task = Task(offering_id=offering_id, title="Midterm", due_date=due, ai_grading=False)
    db_session.add(task)
    await db_session.flush()
    
    q1 = Question(task_id=task.id, text="Q1", type="free_text", score=10.0)
    db_session.add(q1)
    await db_session.commit()

    # 1. List tasks
    resp = await async_client.get(f"/api/v1/student/courses/{offering_id}/tasks", headers=student_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # 2. Get active task details
    resp = await async_client.get(f"/api/v1/student/courses/{offering_id}/tasks/{task.id}", headers=student_headers)
    assert resp.status_code == 200
    assert len(resp.json()["questions"]) == 1

    # 3. Submit
    payload = {
        "answers": [
            {"question_id": str(q1.id), "text_answer": "My final answer"}
        ]
    }
    resp = await async_client.post(f"/api/v1/student/courses/{offering_id}/tasks/{task.id}/submit", json=payload, headers=student_headers)
    assert resp.status_code == 201
    
    # 3b. Verify duplicate submission caught
    resp = await async_client.post(f"/api/v1/student/courses/{offering_id}/tasks/{task.id}/submit", json=payload, headers=student_headers)
    assert resp.status_code == 400
    assert "already submitted" in resp.json()["detail"]

    # 4. View Grades
    resp = await async_client.get(f"/api/v1/student/courses/{offering_id}/grades", headers=student_headers)
    assert resp.status_code == 200
    # Nothing was finalized as we didn't grade it. Gradebook handles only graded stuff
    assert len(resp.json()["submissions"]) == 0

    # 5. Invalid paths
    # Not found task
    resp = await async_client.get(f"/api/v1/student/courses/{offering_id}/tasks/{uuid.uuid4()}", headers=student_headers)
    assert resp.status_code == 404
