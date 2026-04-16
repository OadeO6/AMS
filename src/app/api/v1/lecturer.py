# src/app/api/v1/lecturer.py
"""
Lecturer endpoints — all protected routes for the lecturer role.

All routes in this module currently return 501 Not Implemented.
They will be fleshed out in Phases 6–9.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.middleware.auth import require_authorized_lecturer

router = APIRouter(
    prefix="/lecturer",
    tags=["lecturer"],
    dependencies=[require_authorized_lecturer()],
)

_NOT_IMPLEMENTED = JSONResponse(
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    content={"detail": "Not implemented in this phase."},
)


# ---------------------------------------------------------------------------
# Courses
# ---------------------------------------------------------------------------


@router.get("/courses", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def list_courses() -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get("/courses/{course_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def get_course(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Students
# ---------------------------------------------------------------------------


@router.get("/courses/{course_id}/students", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def list_students(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch(
    "/courses/{course_id}/students/{student_id}/approve",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def approve_student(course_id: uuid.UUID, student_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------


@router.post("/courses/{course_id}/materials", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def upload_material(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch(
    "/courses/{course_id}/materials/{material_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def update_material(course_id: uuid.UUID, material_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.delete(
    "/courses/{course_id}/materials/{material_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def delete_material(course_id: uuid.UUID, material_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.post(
    "/courses/{course_id}/materials/{material_id}/index",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def index_material(course_id: uuid.UUID, material_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


@router.post("/courses/{course_id}/tasks", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def create_task(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch("/courses/{course_id}/tasks/{task_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def update_task(course_id: uuid.UUID, task_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.delete("/courses/{course_id}/tasks/{task_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def delete_task(course_id: uuid.UUID, task_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get("/courses/{course_id}/tasks", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def list_tasks(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get("/courses/{course_id}/tasks/{task_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def get_task(course_id: uuid.UUID, task_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.post(
    "/courses/{course_id}/tasks/{task_id}/marking-guide",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def upload_marking_guide(course_id: uuid.UUID, task_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch(
    "/courses/{course_id}/tasks/{task_id}/ai-grading",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def toggle_ai_grading(course_id: uuid.UUID, task_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------


@router.post(
    "/courses/{course_id}/tasks/{task_id}/questions",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def create_question(course_id: uuid.UUID, task_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch(
    "/courses/{course_id}/tasks/{task_id}/questions/{question_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def update_question(
    course_id: uuid.UUID, task_id: uuid.UUID, question_id: uuid.UUID
) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.delete(
    "/courses/{course_id}/tasks/{task_id}/questions/{question_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def delete_question(
    course_id: uuid.UUID, task_id: uuid.UUID, question_id: uuid.UUID
) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Submissions
# ---------------------------------------------------------------------------


@router.get(
    "/courses/{course_id}/tasks/{task_id}/submissions",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def list_submissions(course_id: uuid.UUID, task_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get(
    "/courses/{course_id}/tasks/{task_id}/submissions/{submission_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def get_submission(
    course_id: uuid.UUID, task_id: uuid.UUID, submission_id: uuid.UUID
) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch(
    "/courses/{course_id}/tasks/{task_id}/submissions/{submission_id}/grade",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def grade_submission(
    course_id: uuid.UUID, task_id: uuid.UUID, submission_id: uuid.UUID
) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.post(
    "/courses/{course_id}/tasks/{task_id}/submissions/approve-ai-grades",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def approve_ai_grades(course_id: uuid.UUID, task_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------


@router.post("/courses/{course_id}/sessions", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def create_session(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch(
    "/courses/{course_id}/sessions/{session_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def update_session(course_id: uuid.UUID, session_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.delete(
    "/courses/{course_id}/sessions/{session_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def delete_session(course_id: uuid.UUID, session_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get("/courses/{course_id}/sessions", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def list_sessions(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get(
    "/courses/{course_id}/sessions/{session_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def get_session(course_id: uuid.UUID, session_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.post(
    "/courses/{course_id}/sessions/{session_id}/attendance",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def mark_attendance(course_id: uuid.UUID, session_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------


@router.post(
    "/courses/{course_id}/announcements",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def create_announcement(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get(
    "/courses/{course_id}/announcements",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def list_announcements(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get(
    "/courses/{course_id}/announcements/{announcement_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def get_announcement(course_id: uuid.UUID, announcement_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch(
    "/courses/{course_id}/announcements/{announcement_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def update_announcement(course_id: uuid.UUID, announcement_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.delete(
    "/courses/{course_id}/announcements/{announcement_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def delete_announcement(course_id: uuid.UUID, announcement_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Gradebook
# ---------------------------------------------------------------------------


@router.get("/courses/{course_id}/gradebook", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def get_gradebook(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch(
    "/courses/{course_id}/gradebook/{student_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def update_gradebook_entry(course_id: uuid.UUID, student_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Analytics / AI Tutor (plan not finished)
# ---------------------------------------------------------------------------


@router.get("/courses/{course_id}/analytics", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def course_analytics(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get("/analytics", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def lecturer_analytics() -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.post("/courses/{course_id}/ai-tutor", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def ai_tutor(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch("/courses/{course_id}/ai-tutor/rules", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def update_ai_tutor_rules(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED
