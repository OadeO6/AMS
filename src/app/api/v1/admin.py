# src/app/api/v1/admin.py
"""
Admin endpoints — all protected routes for the admin role.

All routes in this module currently return 501 Not Implemented.
They will be fleshed out in Phase 3 (Admin endpoints).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.middleware.auth import require_role
from app.models.user import UserRole

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[require_role(UserRole.ADMIN)],
)

_NOT_IMPLEMENTED = JSONResponse(
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    content={"detail": "Not implemented in this phase."},
)


# ---------------------------------------------------------------------------
# Faculties
# ---------------------------------------------------------------------------


@router.post("/faculties", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def create_faculty() -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get("/faculties", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def list_faculties() -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch("/faculties/{faculty_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def update_faculty(faculty_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.delete("/faculties/{faculty_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def delete_faculty(faculty_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------


@router.post(
    "/faculties/{faculty_id}/departments",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def create_department(faculty_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get(
    "/faculties/{faculty_id}/departments",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def list_departments(faculty_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get(
    "/faculties/{faculty_id}/departments/{department_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def get_department(faculty_id: uuid.UUID, department_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch(
    "/faculties/{faculty_id}/departments/{department_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def update_department(faculty_id: uuid.UUID, department_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.delete(
    "/faculties/{faculty_id}/departments/{department_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def delete_department(faculty_id: uuid.UUID, department_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.post(
    "/departments/{department_id}/hod",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def assign_hod(department_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch(
    "/departments/{department_id}/hod",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def replace_hod(department_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Academic Calendar
# ---------------------------------------------------------------------------


@router.post("/academic-sessions", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def create_session() -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get("/academic-sessions", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def list_sessions() -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get("/academic-sessions/{session_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def get_session(session_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch("/academic-sessions/{session_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def update_session(session_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.delete("/academic-sessions/{session_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def delete_session(session_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch(
    "/academic-sessions/{session_id}/semesters/{semester_id}/activate",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def activate_semester(session_id: uuid.UUID, semester_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch(
    "/academic-sessions/{session_id}/semesters/{semester_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def update_semester(session_id: uuid.UUID, semester_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.delete(
    "/academic-sessions/{session_id}/semesters/{semester_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def delete_semester(session_id: uuid.UUID, semester_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


@router.get("/users", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def list_users() -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.post("/staff/authorize", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def authorize_staff() -> JSONResponse:
    return _NOT_IMPLEMENTED
