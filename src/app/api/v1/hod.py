# src/app/api/v1/hod.py
"""
HOD endpoints — all protected routes for the HOD role.

All routes in this module currently return 501 Not Implemented.
They will be fleshed out in Phase 4 (HOD endpoints).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from app.dependencies import CurrentUser, DBSession
from app.exceptions import ForbiddenError
from app.middleware.auth import require_role
from app.models.user import UserRole
from app.schemas.user import LevelOffsetRequest, UserListResponse, UserPublic
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse, 
    CourseOfferingCreate, CourseOfferingResponse
)
from app.services.user import UserService
from app.services.course import CourseService

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


@router.get("/students", response_model=UserListResponse, status_code=status.HTTP_200_OK)
async def list_students(
    session: DBSession,
    current_user: CurrentUser,
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> UserListResponse:
    if not current_user.department_id:
        raise ForbiddenError(detail="HOD must belong to a department", error_code="NO_DEPARTMENT")
    
    svc = UserService(session)
    total, users = await svc.list_users(
        role=UserRole.STUDENT,
        department_id=current_user.department_id,
        search=search,
        page=page,
        limit=limit,
    )
    return UserListResponse(
        users=[UserPublic.model_validate(u) for u in users],
        pagination={"page": page, "limit": limit, "total": total},
    )


@router.get("/students/{student_id}", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def get_student(
    student_id: uuid.UUID,
    session: DBSession,
    current_user: CurrentUser,
) -> UserPublic:
    if not current_user.department_id:
        raise ForbiddenError(detail="HOD must belong to a department", error_code="NO_DEPARTMENT")
    
    svc = UserService(session)
    student = await svc.get_user_or_404(student_id)
    if student.role != UserRole.STUDENT or student.department_id != current_user.department_id:
        raise ForbiddenError(detail="Student not found in your department", error_code="FORBIDDEN")
    return UserPublic.model_validate(student)


@router.patch("/students/{student_id}/level-offset", status_code=status.HTTP_200_OK)
async def update_level_offset(
    student_id: uuid.UUID,
    payload: LevelOffsetRequest,
    session: DBSession,
    current_user: CurrentUser,
) -> JSONResponse:
    if not current_user.department_id:
        raise ForbiddenError(detail="HOD must belong to a department", error_code="NO_DEPARTMENT")
    
    svc = UserService(session)
    student = await svc.get_user_or_404(student_id)
    if student.department_id != current_user.department_id:
        raise ForbiddenError(detail="Student not found in your department", error_code="FORBIDDEN")
    
    await svc.update_level_offset(student_id, payload.level_offset)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Level offset updated successfully."},
    )


# ---------------------------------------------------------------------------
# Lecturers
# ---------------------------------------------------------------------------


@router.get("/lecturers", response_model=UserListResponse, status_code=status.HTTP_200_OK)
async def list_lecturers(
    session: DBSession,
    current_user: CurrentUser,
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> UserListResponse:
    if not current_user.department_id:
        raise ForbiddenError(detail="HOD must belong to a department", error_code="NO_DEPARTMENT")
    
    svc = UserService(session)
    total, users = await svc.list_users(
        role=UserRole.LECTURER,
        department_id=current_user.department_id,
        search=search,
        page=page,
        limit=limit,
    )
    return UserListResponse(
        users=[UserPublic.model_validate(u) for u in users],
        pagination={"page": page, "limit": limit, "total": total},
    )


@router.get("/lecturers/{lecturer_id}", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def get_lecturer(
    lecturer_id: uuid.UUID,
    session: DBSession,
    current_user: CurrentUser,
) -> UserPublic:
    if not current_user.department_id:
        raise ForbiddenError(detail="HOD must belong to a department", error_code="NO_DEPARTMENT")
    
    svc = UserService(session)
    lecturer = await svc.get_user_or_404(lecturer_id)
    if lecturer.role != UserRole.LECTURER or lecturer.department_id != current_user.department_id:
        raise ForbiddenError(detail="Lecturer not found in your department", error_code="FORBIDDEN")
    return UserPublic.model_validate(lecturer)


# ---------------------------------------------------------------------------
# Course Definitions
# ---------------------------------------------------------------------------


@router.post("/courses", status_code=status.HTTP_201_CREATED)
async def create_course(
    payload: CourseCreate, session: DBSession, current_user: CurrentUser
) -> JSONResponse:
    svc = CourseService(session)
    course = await svc.create_course(hod=current_user, payload=payload)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Course created successfully", "course_id": str(course.id)}
    )


@router.get("/courses", response_model=list[CourseResponse], status_code=status.HTTP_200_OK)
async def list_courses(session: DBSession, current_user: CurrentUser) -> list[CourseResponse]:
    svc = CourseService(session)
    courses = await svc.list_department_courses(hod=current_user)
    return [CourseResponse.model_validate(c) for c in courses]


@router.get("/courses/{course_id}", response_model=CourseResponse, status_code=status.HTTP_200_OK)
async def get_course(course_id: uuid.UUID, session: DBSession, current_user: CurrentUser) -> CourseResponse:
    svc = CourseService(session)
    course = await svc.get_department_course(hod=current_user, course_id=course_id)
    return CourseResponse.model_validate(course)


@router.patch("/courses/{course_id}", response_model=CourseResponse, status_code=status.HTTP_200_OK)
async def update_course(
    course_id: uuid.UUID, payload: CourseUpdate, session: DBSession, current_user: CurrentUser
) -> CourseResponse:
    svc = CourseService(session)
    course = await svc.update_course(hod=current_user, course_id=course_id, payload=payload)
    return CourseResponse.model_validate(course)


@router.delete("/courses/{course_id}", status_code=status.HTTP_200_OK)
async def delete_course(course_id: uuid.UUID, session: DBSession, current_user: CurrentUser) -> JSONResponse:
    svc = CourseService(session)
    await svc.delete_course(hod=current_user, course_id=course_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "Course deleted successfully."}
    )


# ---------------------------------------------------------------------------
# Offerings
# ---------------------------------------------------------------------------


@router.post("/courses/{course_id}/offerings", status_code=status.HTTP_201_CREATED)
async def create_offering(
    course_id: uuid.UUID, payload: CourseOfferingCreate, session: DBSession, current_user: CurrentUser
) -> JSONResponse:
    svc = CourseService(session)
    offering = await svc.create_offering(hod=current_user, course_id=course_id, payload=payload)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Offering created successfully", "offering_id": str(offering.id)}
    )


@router.get("/courses/{course_id}/offerings", response_model=list[CourseOfferingResponse], status_code=status.HTTP_200_OK)
async def list_offerings(
    course_id: uuid.UUID, session: DBSession, current_user: CurrentUser
) -> list[CourseOfferingResponse]:
    svc = CourseService(session)
    offerings = await svc.list_course_offerings(hod=current_user, course_id=course_id)
    return [CourseOfferingResponse.model_validate(o) for o in offerings]


@router.get(
    "/courses/{course_id}/offerings/{offering_id}",
    response_model=CourseOfferingResponse,
    status_code=status.HTTP_200_OK,
)
async def get_offering(course_id: uuid.UUID, offering_id: uuid.UUID, session: DBSession, current_user: CurrentUser) -> CourseOfferingResponse:
    svc = CourseService(session)
    await svc.get_department_course(hod=current_user, course_id=course_id)  # Validate auth scope
    offering = await svc.get_offering(offering_id)
    return CourseOfferingResponse.model_validate(offering)


@router.patch(
    "/courses/{course_id}/offerings/{offering_id}/activate",
    response_model=CourseOfferingResponse,
    status_code=status.HTTP_200_OK,
)
async def activate_offering(course_id: uuid.UUID, offering_id: uuid.UUID, session: DBSession, current_user: CurrentUser) -> CourseOfferingResponse:
    svc = CourseService(session)
    offering = await svc.activate_offering(hod=current_user, course_id=course_id, offering_id=offering_id)
    return CourseOfferingResponse.model_validate(offering)


@router.post(
    "/courses/{course_id}/offerings/{offering_id}/assign",
    response_model=CourseOfferingResponse,
    status_code=status.HTTP_200_OK,
)
async def assign_lecturer(course_id: uuid.UUID, offering_id: uuid.UUID, lecturer_id: uuid.UUID, session: DBSession, current_user: CurrentUser) -> CourseOfferingResponse:
    svc = CourseService(session)
    offering = await svc.assign_lecturer(hod=current_user, course_id=course_id, offering_id=offering_id, lecturer_id=lecturer_id)
    return CourseOfferingResponse.model_validate(offering)


@router.delete(
    "/courses/{course_id}/offerings/{offering_id}/assign/{lecturer_id}",
    status_code=status.HTTP_200_OK,
)
async def unassign_lecturer(
    course_id: uuid.UUID, offering_id: uuid.UUID, lecturer_id: uuid.UUID, session: DBSession, current_user: CurrentUser
) -> JSONResponse:
    svc = CourseService(session)
    await svc.unassign_lecturer(hod=current_user, course_id=course_id, offering_id=offering_id, lecturer_id=lecturer_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Lecturer unassigned."})
