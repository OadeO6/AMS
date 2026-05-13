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
from app.schemas.auth import MessageResponse
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
    FacultyListResponse, FacultyCreateResponse,
    DepartmentListResponse, DepartmentCreateResponse, DepartmentDetailResponse, DepartmentUpdateResponse,
    SessionListResponse, SessionCreateResponse, SessionUpdateResponse, SessionDetailResponse,
    SemesterActivateResponse, SemesterUpdateResponse,
)
from app.schemas.user import AuthorizeStaffRequest, BulkAuthorizeResponse, UserListResponse, UserPublic
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


@router.post("/faculties", response_model=FacultyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_faculty(payload: FacultyCreate, session: DBSession):
    svc = AdminService(session)
    fac = await svc.create_faculty(payload)
    return FacultyCreateResponse(message="Faculty created successfully", faculty=FacultyResponse.model_validate(fac))


@router.get("/faculties", response_model=FacultyListResponse)
async def list_faculties(session: DBSession):
    svc = AdminService(session)
    facs = await svc.list_faculties()
    return FacultyListResponse(faculties=[FacultyResponse.model_validate(f) for f in facs])


@router.patch("/faculties/{faculty_id}", response_model=FacultyResponse)
async def update_faculty(
    faculty_id: uuid.UUID, payload: FacultyUpdate, session: DBSession
):
    svc = AdminService(session)
    fac = await svc.update_faculty(faculty_id, payload)
    return FacultyResponse.model_validate(fac)


@router.delete("/faculties/{faculty_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_faculty(faculty_id: uuid.UUID, session: DBSession):
    svc = AdminService(session)
    await svc.delete_faculty(faculty_id)
    return MessageResponse(message="Faculty deleted successfully")


# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------


@router.post(
    "/faculties/{faculty_id}/departments",
    status_code=status.HTTP_201_CREATED,
    response_model=DepartmentCreateResponse,
)
async def create_department(
    faculty_id: uuid.UUID, payload: DepartmentCreate, session: DBSession
):
    svc = AdminService(session)
    dept = await svc.create_department(faculty_id, payload)
    return DepartmentCreateResponse(message="Department created", department=DepartmentResponse.model_validate(dept))


@router.get("/faculties/{faculty_id}/departments", response_model=DepartmentListResponse)
async def list_departments(faculty_id: uuid.UUID, session: DBSession):
    svc = AdminService(session)
    depts = await svc.list_departments_by_faculty(faculty_id)
    return DepartmentListResponse(departments=[DepartmentResponse.model_validate(d) for d in depts])


@router.get(
    "/faculties/{faculty_id}/departments/{department_id}",
    response_model=DepartmentDetailResponse,
)
async def get_department(
    faculty_id: uuid.UUID, department_id: uuid.UUID, session: DBSession
):
    svc = AdminService(session)
    dept = await svc.get_department(faculty_id, department_id)
    return dept


@router.patch(
    "/faculties/{faculty_id}/departments/{department_id}",
    response_model=DepartmentUpdateResponse,
)
async def update_department(
    faculty_id: uuid.UUID,
    department_id: uuid.UUID,
    payload: DepartmentUpdate,
    session: DBSession,
):
    svc = AdminService(session)
    dept = await svc.update_department(faculty_id, department_id, payload)
    return DepartmentUpdateResponse(message="Department updated", department=DepartmentResponse.model_validate(dept))


@router.delete(
    "/faculties/{faculty_id}/departments/{department_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_department(
    faculty_id: uuid.UUID, department_id: uuid.UUID, session: DBSession
):
    svc = AdminService(session)
    await svc.delete_department(faculty_id, department_id)
    return MessageResponse(message="Department deleted")


@router.post("/departments/{department_id}/hod", response_model=MessageResponse)
async def assign_hod(
    department_id: uuid.UUID, payload: AssignHODRequest, session: DBSession
):
    svc = AdminService(session)
    dept = await svc.assign_hod(department_id, payload.user_id)
    return MessageResponse(message="HOD assigned successfully")


@router.patch("/departments/{department_id}/hod", response_model=MessageResponse)
async def replace_hod(
    department_id: uuid.UUID, payload: AssignHODRequest, session: DBSession
):
    # Logic for assigning/replacing is exactly the same, it overrides hod_id.
    svc = AdminService(session)
    dept = await svc.assign_hod(department_id, payload.user_id)
    return MessageResponse(message="HOD replaced successfully")


# ---------------------------------------------------------------------------
# Academic Calendar
# ---------------------------------------------------------------------------


@router.post(
    "/academic-sessions",
    status_code=status.HTTP_201_CREATED,
    response_model=SessionCreateResponse,
)
async def create_session(
    payload: AcademicSessionCreate, session: DBSession
):
    svc = AdminService(session)
    sess = await svc.create_session(payload)
    return SessionCreateResponse(message="Session created", session=AcademicSessionResponse.model_validate(sess))


@router.get("/academic-sessions", response_model=SessionListResponse)
async def list_sessions(session: DBSession):
    svc = AdminService(session)
    sessions = await svc.list_sessions()
    return SessionListResponse(sessions=[AcademicSessionResponse.model_validate(s) for s in sessions])


@router.get("/academic-sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: uuid.UUID, session: DBSession):
    svc = AdminService(session)
    sess = await svc.get_session(session_id)
    return sess


@router.patch("/academic-sessions/{session_id}", response_model=SessionUpdateResponse)
async def update_session(
    session_id: uuid.UUID, payload: AcademicSessionUpdate, session: DBSession
):
    svc = AdminService(session)
    sess = await svc.update_session(session_id, payload)
    return SessionUpdateResponse(message="Session updated", session=AcademicSessionResponse.model_validate(sess))


@router.delete("/academic-sessions/{session_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_session(session_id: uuid.UUID, session: DBSession):
    svc = AdminService(session)
    await svc.delete_session(session_id)
    return MessageResponse(message="Session deleted")


@router.patch(
    "/academic-sessions/{session_id}/semesters/{semester_id}/activate",
    response_model=SemesterActivateResponse,
)
async def activate_semester(
    session_id: uuid.UUID, semester_id: uuid.UUID, session: DBSession
):
    svc = AdminService(session)
    sem = await svc.activate_semester(session_id, semester_id)
    return SemesterActivateResponse(message="Semester activated", semester=SemesterResponse.model_validate(sem))


@router.patch(
    "/academic-sessions/{session_id}/semesters/{semester_id}",
    response_model=SemesterUpdateResponse,
)
async def update_semester(
    session_id: uuid.UUID,
    semester_id: uuid.UUID,
    payload: SemesterUpdate,
    session: DBSession,
):
    svc = AdminService(session)
    sem = await svc.update_semester(session_id, semester_id, payload)
    return SemesterUpdateResponse(message="Semester updated", semester=SemesterResponse.model_validate(sem))


@router.delete(
    "/academic-sessions/{session_id}/semesters/{semester_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_semester(
    session_id: uuid.UUID, semester_id: uuid.UUID, session: DBSession
):
    svc = AdminService(session)
    await svc.delete_semester(session_id, semester_id)
    return MessageResponse(message="Semester deleted")


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


@router.post("/staff/authorize", response_model=BulkAuthorizeResponse, status_code=status.HTTP_200_OK)
async def authorize_staff(
    payload: AuthorizeStaffRequest,
    session: DBSession,
) -> BulkAuthorizeResponse:
    svc = UserService(session)
    authorized, failed = await svc.authorize_lecturers(payload.user_ids)
    return BulkAuthorizeResponse(
        message=f"Authorized {authorized} lecturers.",
        authorized=authorized,
        failed=failed,
    )
