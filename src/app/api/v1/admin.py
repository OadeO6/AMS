# src/app/api/v1/admin.py
"""
Admin endpoints — all protected routes for the admin role.

All routes in this module currently return 501 Not Implemented.
They will be fleshed out in Phase 3 (Admin endpoints).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from app.dependencies import DBSession
from app.middleware.auth import require_role
from app.models.user import UserRole
from app.schemas.admin import (
    AcademicSessionCreate,
    AcademicSessionResponse,
    AcademicSessionUpdate,
    AssignHODRequest,
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
    FacultyCreate,
    FacultyResponse,
    FacultyUpdate,
    SemesterResponse,
    SemesterUpdate,
)
from app.schemas.user import AuthorizeStaffRequest, UserListResponse, UserPublic
from app.services.admin import AdminService
from app.services.user import UserService

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


@router.post("/faculties", response_model=FacultyResponse, status_code=status.HTTP_201_CREATED)
async def create_faculty(payload: FacultyCreate, session: DBSession) -> FacultyResponse:
    svc = AdminService(session)
    fac = await svc.create_faculty(payload)
    return FacultyResponse.model_validate(fac)


@router.get("/faculties", response_model=list[FacultyResponse])
async def list_faculties(session: DBSession) -> list[FacultyResponse]:
    svc = AdminService(session)
    facs = await svc.list_faculties()
    return [FacultyResponse.model_validate(f) for f in facs]


@router.patch("/faculties/{faculty_id}", response_model=FacultyResponse)
async def update_faculty(
    faculty_id: uuid.UUID, payload: FacultyUpdate, session: DBSession
) -> FacultyResponse:
    svc = AdminService(session)
    fac = await svc.update_faculty(faculty_id, payload)
    return FacultyResponse.model_validate(fac)


@router.delete("/faculties/{faculty_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faculty(faculty_id: uuid.UUID, session: DBSession) -> None:
    svc = AdminService(session)
    await svc.delete_faculty(faculty_id)


# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------


@router.post(
    "/faculties/{faculty_id}/departments",
    status_code=status.HTTP_201_CREATED,
    response_model=DepartmentResponse,
)
async def create_department(
    faculty_id: uuid.UUID, payload: DepartmentCreate, session: DBSession
) -> DepartmentResponse:
    svc = AdminService(session)
    dept = await svc.create_department(faculty_id, payload)
    return DepartmentResponse.model_validate(dept)


@router.get("/faculties/{faculty_id}/departments", response_model=list[DepartmentResponse])
async def list_departments(faculty_id: uuid.UUID, session: DBSession) -> list[DepartmentResponse]:
    svc = AdminService(session)
    depts = await svc.list_departments_by_faculty(faculty_id)
    return [DepartmentResponse.model_validate(d) for d in depts]


@router.get(
    "/faculties/{faculty_id}/departments/{department_id}",
    response_model=DepartmentResponse,
)
async def get_department(
    faculty_id: uuid.UUID, department_id: uuid.UUID, session: DBSession
) -> DepartmentResponse:
    svc = AdminService(session)
    dept = await svc.get_department(faculty_id, department_id)
    return DepartmentResponse.model_validate(dept)


@router.patch(
    "/faculties/{faculty_id}/departments/{department_id}",
    response_model=DepartmentResponse,
)
async def update_department(
    faculty_id: uuid.UUID,
    department_id: uuid.UUID,
    payload: DepartmentUpdate,
    session: DBSession,
) -> DepartmentResponse:
    svc = AdminService(session)
    dept = await svc.update_department(faculty_id, department_id, payload)
    return DepartmentResponse.model_validate(dept)


@router.delete(
    "/faculties/{faculty_id}/departments/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_department(
    faculty_id: uuid.UUID, department_id: uuid.UUID, session: DBSession
) -> None:
    svc = AdminService(session)
    await svc.delete_department(faculty_id, department_id)


@router.post("/departments/{department_id}/hod", response_model=DepartmentResponse)
async def assign_hod(
    department_id: uuid.UUID, payload: AssignHODRequest, session: DBSession
) -> DepartmentResponse:
    svc = AdminService(session)
    dept = await svc.assign_hod(department_id, payload.hod_id)
    return DepartmentResponse.model_validate(dept)


@router.patch("/departments/{department_id}/hod", response_model=DepartmentResponse)
async def replace_hod(
    department_id: uuid.UUID, payload: AssignHODRequest, session: DBSession
) -> DepartmentResponse:
    # Logic for assigning/replacing is exactly the same, it overrides hod_id.
    svc = AdminService(session)
    dept = await svc.assign_hod(department_id, payload.hod_id)
    return DepartmentResponse.model_validate(dept)


# ---------------------------------------------------------------------------
# Academic Calendar
# ---------------------------------------------------------------------------


@router.post(
    "/academic-sessions",
    status_code=status.HTTP_201_CREATED,
    response_model=AcademicSessionResponse,
)
async def create_session(
    payload: AcademicSessionCreate, session: DBSession
) -> AcademicSessionResponse:
    svc = AdminService(session)
    sess = await svc.create_session(payload)
    return AcademicSessionResponse.model_validate(sess)


@router.get("/academic-sessions", response_model=list[AcademicSessionResponse])
async def list_sessions(session: DBSession) -> list[AcademicSessionResponse]:
    svc = AdminService(session)
    sessions = await svc.list_sessions()
    return [AcademicSessionResponse.model_validate(s) for s in sessions]


@router.get("/academic-sessions/{session_id}", response_model=AcademicSessionResponse)
async def get_session(session_id: uuid.UUID, session: DBSession) -> AcademicSessionResponse:
    svc = AdminService(session)
    sess = await svc.get_session(session_id)
    return AcademicSessionResponse.model_validate(sess)


@router.patch("/academic-sessions/{session_id}", response_model=AcademicSessionResponse)
async def update_session(
    session_id: uuid.UUID, payload: AcademicSessionUpdate, session: DBSession
) -> AcademicSessionResponse:
    svc = AdminService(session)
    sess = await svc.update_session(session_id, payload)
    return AcademicSessionResponse.model_validate(sess)


@router.delete("/academic-sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: uuid.UUID, session: DBSession) -> None:
    svc = AdminService(session)
    await svc.delete_session(session_id)


@router.patch(
    "/academic-sessions/{session_id}/semesters/{semester_id}/activate",
    response_model=SemesterResponse,
)
async def activate_semester(
    session_id: uuid.UUID, semester_id: uuid.UUID, session: DBSession
) -> SemesterResponse:
    svc = AdminService(session)
    sem = await svc.activate_semester(session_id, semester_id)
    return SemesterResponse.model_validate(sem)


@router.patch(
    "/academic-sessions/{session_id}/semesters/{semester_id}",
    response_model=SemesterResponse,
)
async def update_semester(
    session_id: uuid.UUID,
    semester_id: uuid.UUID,
    payload: SemesterUpdate,
    session: DBSession,
) -> SemesterResponse:
    svc = AdminService(session)
    sem = await svc.update_semester(session_id, semester_id, payload)
    return SemesterResponse.model_validate(sem)


@router.delete(
    "/academic-sessions/{session_id}/semesters/{semester_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_semester(
    session_id: uuid.UUID, semester_id: uuid.UUID, session: DBSession
) -> None:
    svc = AdminService(session)
    await svc.delete_semester(session_id, semester_id)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


@router.get("/users", response_model=UserListResponse, status_code=status.HTTP_200_OK)
async def list_users(
    session: DBSession,
    role: UserRole | None = Query(None),
    department: uuid.UUID | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> UserListResponse:
    svc = UserService(session)
    total, users = await svc.list_users(
        role=role, department_id=department, search=search, page=page, limit=limit
    )
    return UserListResponse(
        users=[UserPublic.model_validate(u) for u in users],
        pagination={"page": page, "limit": limit, "total": total},
    )


@router.post("/staff/authorize", status_code=status.HTTP_200_OK)
async def authorize_staff(
    payload: AuthorizeStaffRequest,
    session: DBSession,
) -> JSONResponse:
    svc = UserService(session)
    await svc.authorize_lecturer(payload.user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Lecturer authorized successfully."},
    )
