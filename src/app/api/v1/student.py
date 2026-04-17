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
from app.schemas.announcement import AnnouncementResponse
from app.schemas.course import CourseOfferingResponse, CourseResponse
from app.schemas.material import MaterialResponse
from app.schemas.session import AttendanceResponse, ClassSessionResponse
from app.schemas.student import StudentAnnouncementResponse, StudentGradeSummary, StudentTaskDetailResponse, SubmitTaskRequest
from app.schemas.task import SubmissionResponse, TaskResponse
from app.schemas.analytics import StudentGlobalAnalytics, StudentCourseAnalytics
from app.schemas.ai_tutor import AITutorRequest, AITutorResponse
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

from app.services.course import CourseService

@router.get("/courses", response_model=list[CourseOfferingResponse])
async def list_available_courses(session: DBSession):
    svc = CourseService(session)
    return await svc.list_available_offerings()

@router.get("/courses/{offering_id}", response_model=CourseOfferingResponse)
async def get_course_offering(offering_id: uuid.UUID, session: DBSession):
    svc = CourseService(session)
    return await svc.get_offering(offering_id)

@router.post("/courses/{offering_id}/register", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_active_semester)])
async def register_for_course(offering_id: uuid.UUID, current_user: AuthorizedStudent, session: DBSession):
    svc = CourseService(session)
    reg = await svc.register_student(current_user, offering_id)
    return {"message": "Success", "status": reg.status}

@router.delete("/courses/{offering_id}/register", status_code=status.HTTP_200_OK, dependencies=[Depends(require_active_semester)])
async def drop_course(offering_id: uuid.UUID, current_user: AuthorizedStudent, session: DBSession):
    svc = CourseService(session)
    await svc.unregister_student(current_user, offering_id)
    return {"message": "Dropped"}

@router.get("/student/courses", response_model=list[CourseOfferingResponse])
async def get_registered_courses(current_user: AuthorizedStudent, session: DBSession):
    svc = CourseService(session)
    return await svc.list_student_offerings(current_user)

# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------


@router.get("/student/courses/{course_id}/materials", response_model=list[MaterialResponse])
async def list_materials(
    course_id: uuid.UUID,
    current_user: AuthorizedStudent,
    session: DBSession,
    type: str | None = Query(None),
):
    svc = StudentService(session)
    return await svc.list_materials(current_user, course_id, type_=type)


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


@router.get("/student/courses/{course_id}/tasks", response_model=list[TaskResponse])
async def list_tasks(
    course_id: uuid.UUID,
    current_user: AuthorizedStudent,
    session: DBSession,
    status: str | None = Query(None),
):
    svc = StudentService(session)
    return await svc.list_tasks(current_user, course_id, status)


@router.get("/student/courses/{course_id}/tasks/{task_id}", response_model=StudentTaskDetailResponse)
async def get_task(
    course_id: uuid.UUID,
    task_id: uuid.UUID,
    current_user: AuthorizedStudent,
    session: DBSession,
):
    svc = StudentService(session)
    return await svc.get_task(current_user, course_id, task_id)


@router.post(
    "/student/courses/{course_id}/tasks/{task_id}/submit",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_active_semester)],
)
async def submit_task(
    course_id: uuid.UUID,
    task_id: uuid.UUID,
    payload: SubmitTaskRequest,
    current_user: AuthorizedStudent,
    session: DBSession,
):
    svc = StudentService(session)
    # Answers data must be dicts
    answers_data = [ans.model_dump() for ans in payload.answers]
    sub = await svc.submit_task(current_user, course_id, task_id, answers_data)
    return {"message": "Success", "submission": {"id": str(sub.id)}}


# ---------------------------------------------------------------------------
# Grades
# ---------------------------------------------------------------------------


@router.get("/student/courses/{course_id}/grades", response_model=StudentGradeSummary)
async def get_grades(
    course_id: uuid.UUID, current_user: AuthorizedStudent, session: DBSession
):
    svc = StudentService(session)
    return await svc.get_grades(current_user, course_id)


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------


@router.get("/student/courses/{course_id}/announcements", response_model=list[StudentAnnouncementResponse])
async def list_announcements(
    course_id: uuid.UUID,
    current_user: AuthorizedStudent,
    session: DBSession,
    pinned: bool | None = Query(None),
):
    svc = StudentService(session)
    anns = await svc.list_announcements(current_user, course_id, pinned_only=pinned or False)
    results = []
    for ann in anns:
        data = StudentAnnouncementResponse.model_validate(ann)
        results.append(data)
    return results


@router.get("/student/courses/{course_id}/announcements/{announcement_id}", response_model=StudentAnnouncementResponse)
async def get_announcement(
    course_id: uuid.UUID,
    announcement_id: uuid.UUID,
    current_user: AuthorizedStudent,
    session: DBSession,
):
    svc = StudentService(session)
    ann = await svc.get_announcement(current_user, course_id, announcement_id)
    return StudentAnnouncementResponse.model_validate(ann)


@router.patch("/student/courses/{course_id}/announcements/{announcement_id}/viewed", status_code=status.HTTP_204_NO_CONTENT)
async def mark_announcement_viewed(
    course_id: uuid.UUID,
    announcement_id: uuid.UUID,
    current_user: AuthorizedStudent,
    session: DBSession,
):
    svc = StudentService(session)
    await svc.mark_announcement_viewed(current_user, course_id, announcement_id)


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------


@router.get("/student/courses/{course_id}/sessions", response_model=list[ClassSessionResponse])
async def list_sessions(
    course_id: uuid.UUID,
    current_user: AuthorizedStudent,
    session: DBSession,
    status: str | None = Query(None),
):
    svc = StudentService(session)
    return await svc.list_sessions(current_user, course_id, status)


@router.get("/student/courses/{course_id}/sessions/{session_id}")
async def get_session(
    course_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: AuthorizedStudent,
    session: DBSession,
):
    svc = StudentService(session)
    data = await svc.get_session(current_user, course_id, session_id)
    return {
        "session": dict(ClassSessionResponse.model_validate(data["session"])),
        "attendance": dict(AttendanceResponse.model_validate(data["attendance"])) if data["attendance"] else None
    }


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------


@router.get("/student/courses/{course_id}/attendance", response_model=list[AttendanceResponse])
async def get_attendance(
    course_id: uuid.UUID, current_user: AuthorizedStudent, session: DBSession
):
    svc = StudentService(session)
    return await svc.get_attendance(current_user, course_id)


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
    "/student/courses/{course_id}/analytics",
    response_model=StudentCourseAnalytics,
    status_code=status.HTTP_200_OK,
)
async def get_course_analytics(
    course_id: uuid.UUID, current_user: AuthorizedStudent, session: DBSession
):
    svc = AnalyticsService(session)
    return await svc.get_student_course_metrics(current_user.id, course_id)


@router.post(
    "/student/courses/{course_id}/ai-tutor",
    response_model=AITutorResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_active_semester)],
)
async def ai_tutor_chat(
    course_id: uuid.UUID,
    payload: AITutorRequest,
    current_user: AuthorizedStudent,
    session: DBSession,
):
    svc = AITutorService(session)
    return await svc.chat(current_user.id, course_id, payload)
