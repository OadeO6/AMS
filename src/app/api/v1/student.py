# src/app/api/v1/student.py
"""
Student endpoints — all protected routes for the student role.

All routes in this module currently return 501 Not Implemented.
They will be fleshed out in Phase 5 (Student course flow).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.middleware.auth import require_role
from app.models.user import UserRole

router = APIRouter(
    prefix="",
    tags=["student"],
    dependencies=[require_role(UserRole.STUDENT)],
)

_NOT_IMPLEMENTED = JSONResponse(
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    content={"detail": "Not implemented in this phase."},
)


# ---------------------------------------------------------------------------
# Courses
# ---------------------------------------------------------------------------


@router.get("/courses", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def list_available_courses() -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get("/courses/{course_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def get_course_offering(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.post("/courses/{course_id}/register", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def register_for_course(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.delete("/courses/{course_id}/register", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def drop_course(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get("/student/courses", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def list_my_courses() -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------


@router.get(
    "/student/courses/{course_id}/materials",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def list_course_materials(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


@router.get(
    "/student/courses/{course_id}/tasks",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def list_tasks(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get(
    "/student/courses/{course_id}/tasks/{task_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def get_task(course_id: uuid.UUID, task_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.post(
    "/student/courses/{course_id}/tasks/{task_id}/submit",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def submit_task(course_id: uuid.UUID, task_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Grades
# ---------------------------------------------------------------------------


@router.get(
    "/student/courses/{course_id}/grades",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def get_grades(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------


@router.get(
    "/student/courses/{course_id}/announcements",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def list_announcements(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get(
    "/student/courses/{course_id}/announcements/{announcement_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def get_announcement(course_id: uuid.UUID, announcement_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch(
    "/student/courses/{course_id}/announcements/{announcement_id}/viewed",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def mark_announcement_viewed(
    course_id: uuid.UUID, announcement_id: uuid.UUID
) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------


@router.get(
    "/student/courses/{course_id}/sessions",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def list_sessions(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get(
    "/student/courses/{course_id}/sessions/{session_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def get_session(course_id: uuid.UUID, session_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------


@router.get(
    "/student/courses/{course_id}/attendance",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def get_attendance(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Analytics / AI Tutor (plan not finished)
# ---------------------------------------------------------------------------


@router.get("/student/analytics", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def student_analytics() -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get(
    "/student/courses/{course_id}/analytics",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def course_analytics(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.post(
    "/student/courses/{course_id}/ai-tutor",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def ai_tutor(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED
