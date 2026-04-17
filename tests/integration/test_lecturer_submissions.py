import uuid
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta
from app.models.task import Task, Submission, Answer, Question
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_lecturer_submissions(async_client: AsyncClient, get_auth_headers, setup_lecturer_data, db_session: AsyncSession):
    headers = await get_auth_headers(setup_lecturer_data["lecturer"].email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id
    student_id = setup_lecturer_data["student"].id
    
    due = datetime.now(timezone.utc) + timedelta(days=7)
    # Create Task manually
    task = Task(offering_id=offering_id, title="Test", due_date=due, ai_grading=False)
    db_session.add(task)
    await db_session.flush()
    
    # Create Question manually
    question = Question(task_id=task.id, text="Q1", type="free_text", score=10.0)
    db_session.add(question)
    await db_session.flush()

    # Create submission manually
    sub = Submission(task_id=task.id, student_id=student_id, submitted_at=datetime.now(timezone.utc), grading_status="ai_draft")
    db_session.add(sub)
    await db_session.flush()

    # Create answer manually
    ans = Answer(submission_id=sub.id, question_id=question.id, text_answer="My answer")
    db_session.add(ans)
    await db_session.commit()
    
    # 1. List submissions
    resp = await async_client.get(f"/api/v1/lecturer/courses/{offering_id}/tasks/{task.id}/submissions", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == str(sub.id)
    
    # 2. Get specific submission
    resp = await async_client.get(f"/api/v1/lecturer/courses/{offering_id}/tasks/{task.id}/submissions/{sub.id}", headers=headers)
    assert resp.status_code == 200

    # 3. Grade submission
    grade_payload = {
        "answers": [
            {"answer_id": str(ans.id), "score": 8.5, "feedback": "Good job"}
        ]
    }
    resp = await async_client.patch(
        f"/api/v1/lecturer/courses/{offering_id}/tasks/{task.id}/submissions/{sub.id}/grade",
        json=grade_payload,
        headers=headers
    )
    assert resp.status_code == 200
    res = resp.json()
    assert res["total_score"] == 8.5
    assert res["grading_status"] == "manually_graded"
    
    # 4. Approve AI drafts
    sub2 = Submission(task_id=task.id, student_id=student_id, submitted_at=datetime.now(timezone.utc), grading_status="ai_draft")
    db_session.add(sub2)
    await db_session.commit()
    
    resp = await async_client.post(f"/api/v1/lecturer/courses/{offering_id}/tasks/{task.id}/submissions/approve-ai-grades", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["approved"] == 1
