import uuid
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta
from app.models.task import Task, Submission, Answer, Question
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_lecturer_submissions(async_client: AsyncClient, get_auth_headers, setup_lecturer_data, db_session: AsyncSession):
    """
    Validates submission listing, grading, and AI-approval workflows.

    Expected response contract (per ENDPOINTS_DETAIL.md):
      GET    /tasks/:id/submissions          -> 200  { submissions: [...] }
      GET    /tasks/:id/submissions/:id      -> 200  { id, student_id, grading_status, answers, ... }
      PATCH  /tasks/:id/submissions/:id/grade -> 200 { message, submission: { total_score, grading_status, ... } }
      POST   /tasks/:id/submissions/approve-ai-grades -> 200 { message, approved: N }
    """
    headers = await get_auth_headers(setup_lecturer_data["lecturer"].email, "securepassword123")
    offering_id = setup_lecturer_data["offering"].id
    student_id = setup_lecturer_data["student"].id
    
    due = datetime.now(timezone.utc) + timedelta(days=7)
    # Create Task in DB
    task = Task(offering_id=offering_id, title="Test", due_date=due, ai_grading=False)
    db_session.add(task)
    await db_session.flush()
    
    # Create Question in DB
    question = Question(task_id=task.id, text="Q1", type="free_text", score=10.0)
    db_session.add(question)
    await db_session.flush()

    # Create submission in DB
    sub = Submission(task_id=task.id, student_id=student_id, submitted_at=datetime.now(timezone.utc), grading_status="ai_draft")
    db_session.add(sub)
    await db_session.flush()

    # Create answer in DB
    ans = Answer(submission_id=sub.id, question_id=question.id, text_answer="My answer")
    db_session.add(ans)
    await db_session.commit()
    
    # 1. List submissions — expect { submissions: [...] }
    resp = await async_client.get(
        f"/api/v1/lecturer/courses/{offering_id}/tasks/{task.id}/submissions",
        headers=headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "submissions" in body
    assert len(body["submissions"]) == 1
    assert body["submissions"][0]["id"] == str(sub.id)
    
    # 2. Get specific submission — expect flat submission object
    resp = await async_client.get(
        f"/api/v1/lecturer/courses/{offering_id}/tasks/{task.id}/submissions/{sub.id}",
        headers=headers
    )
    assert resp.status_code == 200
    assert "id" in resp.json()

    # 3. Grade submission — expect { message, submission: { total_score, grading_status } }
    grade_payload = {
        "grades": [
            {"question_id": str(question.id), "score": 8.5, "feedback": "Good job"}
        ]
    }
    resp = await async_client.patch(
        f"/api/v1/lecturer/courses/{offering_id}/tasks/{task.id}/submissions/{sub.id}/grade",
        json=grade_payload,
        headers=headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "message" in body
    assert "submission" in body
    assert body["submission"]["total_score"] == 8.5
    assert body["submission"]["grading_status"] == "manually_graded"
    
    # 4. Approve AI drafts — expect { message, approved: N }
    sub2 = Submission(
        task_id=task.id,
        student_id=student_id,
        submitted_at=datetime.now(timezone.utc),
        grading_status="ai_draft"
    )
    db_session.add(sub2)
    await db_session.commit()
    
    resp = await async_client.post(
        f"/api/v1/lecturer/courses/{offering_id}/tasks/{task.id}/submissions/approve-ai-grades",
        headers=headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "message" in body
    assert "approved" in body
    assert body["approved"] == 1
