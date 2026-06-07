# src/app/api/v1/shared.py
"""
Shared endpoints — accessible to multiple roles.

All routes in this module currently return 501 Not Implemented.
They will be fleshed out in Phase 6 (Materials) and Phase 10 (Notifications).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.dependencies import CurrentUser, get_current_user

router = APIRouter(
    tags=["shared"],
    dependencies=[Depends(get_current_user)],
)

from app.dependencies import DBSession
from app.schemas.auth import MessageResponse
from app.schemas.notification import NotificationListResponse
from app.schemas.user import UserSharedListResponse, UserSharedPublic
from app.schemas.admin import SessionListResponse, FacultyListResponse, DepartmentListResponse
from app.models.user import UserRole
from app.services.shared import SharedService
from app.services.user import UserService
from app.api.v1.admin import list_sessions, list_faculties, list_departments
from fastapi import Query

_NOT_IMPLEMENTED = JSONResponse(
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    content={"detail": "Not implemented in this phase."},
)

router.add_api_route(
    "/academic-sessions",
    list_sessions,
    methods=["GET"],
    response_model=SessionListResponse,
    status_code=status.HTTP_200_OK,
)

router.add_api_route(
    "/faculties",
    list_faculties,
    methods=["GET"],
    response_model=FacultyListResponse,
    status_code=status.HTTP_200_OK,
)

router.add_api_route(
    "/faculties/{faculty_id}/departments",
    list_departments,
    methods=["GET"],
    response_model=DepartmentListResponse,
    status_code=status.HTTP_200_OK,
)


@router.get(
    "/materials/{material_id}/download",
    status_code=status.HTTP_200_OK,
)
async def download_material(material_id: uuid.UUID, session: DBSession, current_user: CurrentUser) -> JSONResponse:
    svc = SharedService(session)
    url = await svc.get_material_download_url(current_user, material_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"url": url})


@router.get("/notifications", response_model=NotificationListResponse, status_code=status.HTTP_200_OK)
async def list_notifications(
    session: DBSession,
    current_user: CurrentUser,
    read: bool | None = None,
    page: int = 1,
    limit: int = 50,
):
    return NotificationListResponse.model_validate(
        await SharedService(session).list_notification_response(current_user, read, page, limit)
    )


@router.get("/users", response_model=UserSharedListResponse, status_code=status.HTTP_200_OK)
async def list_shared_users(
    session: DBSession,
    current_user: CurrentUser,
    role: UserRole | None = Query(None),
    department: uuid.UUID | None = Query(None),
    search: str | None = Query(None),
    is_active: bool | None = Query(None),
    is_authorized: bool | None = Query(None),
    admission_session: str | None = Query(None),
    level_offset: int | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    roles_in = None
    # If the user is only a student, restrict visibility to students and lecturers
    if UserRole.STUDENT.value in current_user.roles and len(current_user.roles) == 1:
        roles_in = [UserRole.STUDENT.value, UserRole.LECTURER.value]
    
    svc = UserService(session)
    total, users = await svc.list_users(
        role=role,
        roles_in=roles_in,
        department_id=department,
        search=search,
        is_active=is_active,
        is_authorized=is_authorized,
        admission_session=admission_session,
        level_offset=level_offset,
        page=page,
        limit=limit
    )
    return UserSharedListResponse(
        users=[UserSharedPublic.model_validate(u) for u in users],
        pagination={"page": page, "limit": limit, "total": total},
    )
