# src/app/api/v1/hod.py
"""
HOD endpoints — all protected routes for the HOD role.

All routes in this module currently return 501 Not Implemented.
They will be fleshed out in Phase 4 (HOD endpoints).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.middleware.auth import require_role
from app.models.user import UserRole

router = APIRouter(
    prefix="/hod",
    tags=["hod"],
    dependencies=[require_role(UserRole.HOD)],
)

_NOT_IMPLEMENTED = JSONResponse(
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    content={"detail": "Not implemented in this phase."},
)


# ---------------------------------------------------------------------------
# Students
# ---------------------------------------------------------------------------


@router.get("/students", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def list_students() -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get("/students/{student_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def get_student(student_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch(
    "/students/{student_id}/level-offset",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def update_level_offset(student_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Lecturers
# ---------------------------------------------------------------------------


@router.get("/lecturers", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def list_lecturers() -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get("/lecturers/{lecturer_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def get_lecturer(lecturer_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Course Definitions
# ---------------------------------------------------------------------------


@router.post("/courses", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def create_course() -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get("/courses", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def list_courses() -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get("/courses/{course_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def get_course(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch("/courses/{course_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def update_course(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.delete("/courses/{course_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def delete_course(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Offerings
# ---------------------------------------------------------------------------


@router.post("/courses/{course_id}/offerings", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def create_offering(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get("/courses/{course_id}/offerings", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def list_offerings(course_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get(
    "/courses/{course_id}/offerings/{offering_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def get_offering(course_id: uuid.UUID, offering_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch(
    "/courses/{course_id}/offerings/{offering_id}/activate",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def activate_offering(course_id: uuid.UUID, offering_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.post(
    "/courses/{course_id}/offerings/{offering_id}/assign",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def assign_lecturer(course_id: uuid.UUID, offering_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.delete(
    "/courses/{course_id}/offerings/{offering_id}/assign/{lecturer_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def unassign_lecturer(
    course_id: uuid.UUID, offering_id: uuid.UUID, lecturer_id: uuid.UUID
) -> JSONResponse:
    return _NOT_IMPLEMENTED
