# src/app/api/v1/student.py
"""
Student endpoints — all protected routes for the student role.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.dependencies import AuthorizedStudent, DBSession
from app.middleware.active_semester import require_active_semester
from app.schemas.announcement import StudentAnnouncementListResponse, StudentAnnouncementItem
from app.schemas.course import CourseListResponse, CourseDetailResponse, CourseRegisterResponse, StudentCourseListResponse
from app.schemas.auth import MessageResponse
from app.schemas.material import MaterialResponse, StudentMaterialListResponse
from app.schemas.session import SessionListResponse
from app.schemas.student import (
    StudentAttendanceResponse,
    StudentTaskDetailResponse,
    SubmitTaskRequest,
)
from app.schemas.task import StudentGradeListResponse
from app.schemas.task import StudentTaskListResponse, SubmitTaskResponse
from app.schemas.analytics import StudentGlobalAnalytics, StudentCourseAnalytics
from app.schemas.ai_tutor import AITutorRequest, AITutorResponse
from app.services.course import CourseService
from app.services.student import StudentService
from app.services.analytics import AnalyticsService
from app.services.ai_tutor import AITutorService

router = APIRouter(
    prefix="",
    tags=["student"],
    dependencies=[],  # We inject current_user specific dependencies per endpoint or via group
)

_NOT_IMPLEMENTED = JSONResponse(
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    content={"detail": "Not implemented in this phase."},
)


# ---------------------------------------------------------------------------
# Student Registration & Browsing (From Phase 4)
# ---------------------------------------------------------------------------

@router.get("/courses", response_model=CourseListResponse)
async def list_available_offerings(
    current_user: AuthorizedStudent,
    session: DBSession,
    department: str | None = Query(None),
    level: int | None = Query(None, ge=0),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    svc = StudentService(session)
    return await svc.list_available_courses(
        current_user,
        department=department,
        level=level,
        search=search,
        page=page,
        limit=limit,
    )

@router.get("/courses/{offering_id}", response_model=CourseDetailResponse)
async def get_course_offering(offering_id: uuid.UUID, current_user: AuthorizedStudent, session: DBSession):
    return await StudentService(session).get_course_offering_detail(current_user, offering_id)

@router.post("/courses/{offering_id}/register", response_model=CourseRegisterResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_active_semester)])
async def register_for_course(offering_id: uuid.UUID, current_user: AuthorizedStudent, session: DBSession):
    svc = CourseService(session)
    reg = await svc.register_student(current_user, offering_id)
    return CourseRegisterResponse(message="Success", status=reg.status)

@router.delete("/courses/{offering_id}/register", response_model=MessageResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(require_active_semester)])
async def drop_course(offering_id: uuid.UUID, current_user: AuthorizedStudent, session: DBSession):
    svc = CourseService(session)
    await svc.unregister_student(current_user, offering_id)
    return {"message": "Dropped"}

@router.get("/student/courses", response_model=StudentCourseListResponse)
async def get_registered_courses(
    current_user: AuthorizedStudent,
    session: DBSession,
    status: str | None = Query(None, pattern="^(pending|approved)$"),
    semester_id: uuid.UUID | None = Query(None),
):
    return await StudentService(session).list_registered_courses(
        current_user,
        semester_id=semester_id,
        status=status,
    )

# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------


@router.get("/student/courses/{offering_id}/materials", response_model=StudentMaterialListResponse)
async def list_materials(
    offering_id: uuid.UUID,
    current_user: AuthorizedStudent,
    session: DBSession,
    type: str | None = Query(None),
):
    # TODO: Service layer map
    svc = StudentService(session)
    # Materials are already filtered by visibility in service
    materials = await svc.list_materials(current_user, offering_id, type_=type)
    return {"materials": [MaterialResponse.model_validate(m) for m in materials]}


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


@router.get("/student/courses/{offering_id}/tasks", response_model=StudentTaskListResponse)
async def list_tasks(
    offering_id: uuid.UUID,
    current_user: AuthorizedStudent,
    session: DBSession,
    status: str | None = Query(None),
):
    return await StudentService(session).list_task_summaries(current_user, offering_id, status)


@router.get("/student/courses/{offering_id}/tasks/{task_id}", response_model=StudentTaskDetailResponse)
async def get_task(
    offering_id: uuid.UUID,
    task_id: uuid.UUID,
    current_user: AuthorizedStudent,
    session: DBSession,
):
    return await StudentService(session).get_task_detail_response(current_user, offering_id, task_id)


@router.post(
    "/student/courses/{offering_id}/tasks/{task_id}/submit",
    response_model=SubmitTaskResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_active_semester)],
)
async def submit_task(
    offering_id: uuid.UUID,
    task_id: uuid.UUID,
    payload: SubmitTaskRequest,
    current_user: AuthorizedStudent,
    session: DBSession,
):
    svc = StudentService(session)
    # Answers data must be dicts
    answers_data = [ans.model_dump() for ans in payload.answers]
    sub = await svc.submit_task(current_user, offering_id, task_id, answers_data)
    from app.schemas.task import SubmissionResponse
    return SubmitTaskResponse(message="Success", submission=SubmissionResponse.model_validate(sub))


# ---------------------------------------------------------------------------
# Grades
# ---------------------------------------------------------------------------


@router.get("/student/courses/{offering_id}/grades", response_model=StudentGradeListResponse)
async def get_grades(
    offering_id: uuid.UUID, current_user: AuthorizedStudent, session: DBSession
):
    return await StudentService(session).get_grade_response(current_user, offering_id)


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------


@router.get("/student/courses/{offering_id}/announcements", response_model=StudentAnnouncementListResponse)
async def list_announcements(
    offering_id: uuid.UUID,
    current_user: AuthorizedStudent,
    session: DBSession,
    viewed: bool | None = Query(None),
    pinned: bool | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    return await StudentService(session).list_announcements(
        current_user,
        offering_id,
        viewed=viewed,
        pinned_only=bool(pinned),
        page=page,
        limit=limit,
    )


@router.get("/student/courses/{offering_id}/announcements/{announcement_id}", response_model=StudentAnnouncementItem)
async def get_announcement(
    offering_id: uuid.UUID,
    announcement_id: uuid.UUID,
    current_user: AuthorizedStudent,
    session: DBSession,
):
    return await StudentService(session).get_announcement_response(current_user, offering_id, announcement_id)


@router.patch("/student/courses/{offering_id}/announcements/{announcement_id}/viewed", status_code=status.HTTP_204_NO_CONTENT)
async def mark_announcement_viewed(
    offering_id: uuid.UUID,
    announcement_id: uuid.UUID,
    current_user: AuthorizedStudent,
    session: DBSession,
):
    svc = StudentService(session)
    await svc.mark_announcement_viewed(current_user, offering_id, announcement_id)


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------


@router.get("/student/courses/{offering_id}/sessions", response_model=SessionListResponse)
async def list_sessions(
    offering_id: uuid.UUID,
    current_user: AuthorizedStudent,
    session: DBSession,
    status: str | None = Query(None),
):
    return await StudentService(session).list_session_response(current_user, offering_id, status)


@router.get("/student/courses/{offering_id}/sessions/{session_id}")
async def get_session(
    offering_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: AuthorizedStudent,
    session: DBSession,
):
    return await StudentService(session).get_session_response(current_user, offering_id, session_id)


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------


@router.get("/student/courses/{offering_id}/attendance", response_model=StudentAttendanceResponse)
async def get_attendance(
    offering_id: uuid.UUID, current_user: AuthorizedStudent, session: DBSession
):
    svc = StudentService(session)
    return await svc.get_attendance(current_user, offering_id)


# ---------------------------------------------------------------------------
# Analytics & AI Tutor
# ---------------------------------------------------------------------------


@router.get(
    "/student/analytics",
    response_model=StudentGlobalAnalytics,
    status_code=status.HTTP_200_OK,
)
async def get_analytics(current_user: AuthorizedStudent, session: DBSession):
    svc = AnalyticsService(session)
    return await svc.get_student_global_metrics(current_user.id)


@router.get(
    "/student/courses/{offering_id}/analytics",
    response_model=StudentCourseAnalytics,
    status_code=status.HTTP_200_OK,
)
async def get_course_analytics(
    offering_id: uuid.UUID, current_user: AuthorizedStudent, session: DBSession
):
    svc = AnalyticsService(session)
    return await svc.get_student_course_metrics(current_user.id, offering_id)


@router.post(
    "/student/courses/{offering_id}/ai-tutor",
    response_model=AITutorResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_active_semester)],
)
async def ai_tutor_chat(
    offering_id: uuid.UUID,
    payload: AITutorRequest,
    current_user: AuthorizedStudent,
    session: DBSession,
):
    svc = AITutorService(session)
    return await svc.chat(current_user.id, offering_id, payload)
