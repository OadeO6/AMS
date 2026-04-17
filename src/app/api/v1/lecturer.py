# src/app/api/v1/lecturer.py
"""
Lecturer endpoints — all protected routes for the lecturer role.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.dependencies import AuthorizedLecturer, DBSession
from app.middleware.active_semester import require_active_semester
from app.middleware.auth import require_authorized_lecturer
from app.schemas.announcement import AnnouncementCreate, AnnouncementResponse, AnnouncementUpdate
from app.schemas.course import CourseOfferingResponse
from app.schemas.gradebook import GradebookEntryResponse, GradebookUpdateRequest
from app.schemas.material import MaterialCreate, MaterialResponse, MaterialUpdate
from app.schemas.session import (
    AttendanceMarkRequest,
    AttendanceResponse,
    ClassSessionCreate,
    ClassSessionResponse,
    ClassSessionUpdate,
)
from app.schemas.task import (
    GradeSubmissionRequest,
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
    SubmissionResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from app.schemas.analytics import LecturerCourseAnalytics, LecturerGlobalAnalytics
from app.schemas.ai_tutor import AITutorRequest, AITutorResponse, AITutorRuleUpdate
from app.services.lecturer import LecturerService
from app.services.analytics import AnalyticsService
from app.services.ai_tutor import AITutorService

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


@router.get("/courses", response_model=list[CourseOfferingResponse])
async def list_courses(current_user: AuthorizedLecturer, session: DBSession):
    svc = LecturerService(session)
    return await svc.list_courses(current_user)


@router.get("/courses/{course_id}", response_model=CourseOfferingResponse)
async def get_course(course_id: uuid.UUID, current_user: AuthorizedLecturer, session: DBSession):
    svc = LecturerService(session)
    return await svc.get_course(current_user, course_id)


# ---------------------------------------------------------------------------
# Students
# ---------------------------------------------------------------------------


@router.get("/courses/{course_id}/students", response_model=list[dict])
async def list_students(course_id: uuid.UUID, current_user: AuthorizedLecturer, session: DBSession):
    svc = LecturerService(session)
    registrations = await svc.list_students(current_user, course_id)
    return [
        {"student_id": str(r.student_id), "status": r.status, "id": str(r.id)}
        for r in registrations
    ]


@router.patch("/courses/{course_id}/students/{student_id}/approve", response_model=dict)
async def approve_student(
    course_id: uuid.UUID,
    student_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    reg = await svc.approve_student(current_user, course_id, student_id)
    return {"student_id": str(reg.student_id), "status": reg.status}


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------


@router.post(
    "/courses/{course_id}/materials",
    response_model=MaterialResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_active_semester)],
)
async def upload_material(
    course_id: uuid.UUID,
    title: str = Form(...),
    type: str = Form(...),
    visibility: str = Form(...),
    file: UploadFile = File(...),
    current_user: AuthorizedLecturer = Depends(),
    session: DBSession = Depends(),
):
    from app.services.storage import StorageService
    from app.schemas.material import MaterialCreate

    storage_svc = StorageService()
    # Read and upload file concurrently or synchronously depending on the client
    file_url = storage_svc.upload_file(file.file, file.filename, file.content_type)
    
    payload = MaterialCreate(title=title, type=type, visibility=visibility, file_url=file_url)
    svc = LecturerService(session)
    return await svc.create_material(current_user, course_id, payload)


@router.patch("/courses/{course_id}/materials/{material_id}", response_model=MaterialResponse)
async def update_material(
    course_id: uuid.UUID,
    material_id: uuid.UUID,
    payload: MaterialUpdate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.update_material(current_user, course_id, material_id, payload)


@router.delete(
    "/courses/{course_id}/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_material(
    course_id: uuid.UUID,
    material_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    await svc.delete_material(current_user, course_id, material_id)


@router.post("/courses/{course_id}/materials/{material_id}/index", response_model=MaterialResponse)
async def index_material(
    course_id: uuid.UUID,
    material_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.index_material(current_user, course_id, material_id)


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


@router.post(
    "/courses/{course_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_active_semester)],
)
async def create_task(
    course_id: uuid.UUID,
    payload: TaskCreate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.create_task(current_user, course_id, payload)


@router.get("/courses/{course_id}/tasks", response_model=list[TaskResponse])
async def list_tasks(course_id: uuid.UUID, current_user: AuthorizedLecturer, session: DBSession):
    svc = LecturerService(session)
    return await svc.list_tasks(current_user, course_id)


@router.get("/courses/{course_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    course_id: uuid.UUID, task_id: uuid.UUID, current_user: AuthorizedLecturer, session: DBSession
):
    svc = LecturerService(session)
    return await svc.get_task(current_user, course_id, task_id)


@router.patch("/courses/{course_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    course_id: uuid.UUID,
    task_id: uuid.UUID,
    payload: TaskUpdate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.update_task(current_user, course_id, task_id, payload)


@router.delete("/courses/{course_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    course_id: uuid.UUID,
    task_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    await svc.delete_task(current_user, course_id, task_id)


@router.post("/courses/{course_id}/tasks/{task_id}/marking-guide", response_model=TaskResponse)
async def upload_marking_guide(
    course_id: uuid.UUID,
    task_id: uuid.UUID,
    payload: dict,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    file_url = payload.get("file_url", "")
    svc = LecturerService(session)
    return await svc.upload_marking_guide(current_user, course_id, task_id, file_url)


@router.patch("/courses/{course_id}/tasks/{task_id}/ai-grading", response_model=TaskResponse)
async def toggle_ai_grading(
    course_id: uuid.UUID,
    task_id: uuid.UUID,
    payload: dict,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    enabled = payload.get("enabled", False)
    svc = LecturerService(session)
    return await svc.toggle_ai_grading(current_user, course_id, task_id, enabled)


# ---------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------


@router.post(
    "/courses/{course_id}/tasks/{task_id}/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_question(
    course_id: uuid.UUID,
    task_id: uuid.UUID,
    payload: QuestionCreate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.create_question(current_user, course_id, task_id, payload)


@router.patch(
    "/courses/{course_id}/tasks/{task_id}/questions/{question_id}", response_model=QuestionResponse
)
async def update_question(
    course_id: uuid.UUID,
    task_id: uuid.UUID,
    question_id: uuid.UUID,
    payload: QuestionUpdate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.update_question(current_user, course_id, task_id, question_id, payload)


@router.delete(
    "/courses/{course_id}/tasks/{task_id}/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_question(
    course_id: uuid.UUID,
    task_id: uuid.UUID,
    question_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    await svc.delete_question(current_user, course_id, task_id, question_id)


# ---------------------------------------------------------------------------
# Submissions
# ---------------------------------------------------------------------------


@router.get(
    "/courses/{course_id}/tasks/{task_id}/submissions", response_model=list[SubmissionResponse]
)
async def list_submissions(
    course_id: uuid.UUID,
    task_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
    graded: bool | None = Query(None),
):
    svc = LecturerService(session)
    return await svc.list_submissions(current_user, course_id, task_id, graded=graded)


@router.get(
    "/courses/{course_id}/tasks/{task_id}/submissions/{submission_id}",
    response_model=SubmissionResponse,
)
async def get_submission(
    course_id: uuid.UUID,
    task_id: uuid.UUID,
    submission_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.get_submission(current_user, course_id, task_id, submission_id)


@router.patch(
    "/courses/{course_id}/tasks/{task_id}/submissions/{submission_id}/grade",
    response_model=SubmissionResponse,
)
async def grade_submission(
    course_id: uuid.UUID,
    task_id: uuid.UUID,
    submission_id: uuid.UUID,
    payload: GradeSubmissionRequest,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.grade_submission(current_user, course_id, task_id, submission_id, payload)


@router.post(
    "/courses/{course_id}/tasks/{task_id}/submissions/approve-ai-grades", response_model=dict
)
async def approve_ai_grades(
    course_id: uuid.UUID,
    task_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    count = await svc.approve_ai_grades(current_user, course_id, task_id)
    return {"approved": count}


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------


@router.post(
    "/courses/{course_id}/sessions",
    response_model=ClassSessionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_active_semester)],
)
async def create_session(
    course_id: uuid.UUID,
    payload: ClassSessionCreate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    sess = await svc.create_session(current_user, course_id, payload)
    return ClassSessionResponse.model_validate(sess).model_copy(update={"is_owner": sess.lecturer_id == current_user.id})


@router.patch("/courses/{course_id}/sessions/{session_id}", response_model=ClassSessionResponse)
async def update_session(
    course_id: uuid.UUID,
    session_id: uuid.UUID,
    payload: ClassSessionUpdate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    sess = await svc.update_session(current_user, course_id, session_id, payload)
    return ClassSessionResponse.model_validate(sess).model_copy(update={"is_owner": sess.lecturer_id == current_user.id})


@router.delete("/courses/{course_id}/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    course_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    await svc.delete_session(current_user, course_id, session_id)


@router.get("/courses/{course_id}/sessions", response_model=list[ClassSessionResponse])
async def list_sessions(course_id: uuid.UUID, current_user: AuthorizedLecturer, session: DBSession):
    svc = LecturerService(session)
    sessions = await svc.list_sessions(current_user, course_id)
    return [
        ClassSessionResponse.model_validate(s).model_copy(update={"is_owner": s.lecturer_id == current_user.id})
        for s in sessions
    ]


@router.get("/courses/{course_id}/sessions/{session_id}", response_model=ClassSessionResponse)
async def get_session(
    course_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    sess = await svc.get_session(current_user, course_id, session_id)
    data = ClassSessionResponse.model_validate(sess)
    data.is_owner = sess.lecturer_id == current_user.id
    return data


@router.post(
    "/courses/{course_id}/sessions/{session_id}/attendance", response_model=list[AttendanceResponse]
)
async def mark_attendance(
    course_id: uuid.UUID,
    session_id: uuid.UUID,
    payload: AttendanceMarkRequest,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.mark_attendance(current_user, course_id, session_id, payload)


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------


@router.post(
    "/courses/{course_id}/announcements",
    response_model=AnnouncementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_announcement(
    course_id: uuid.UUID,
    payload: AnnouncementCreate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.create_announcement(current_user, course_id, payload)


@router.get("/courses/{course_id}/announcements", response_model=list[AnnouncementResponse])
async def list_announcements(
    course_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
    pinned: bool = Query(False),
):
    svc = LecturerService(session)
    return await svc.list_announcements(current_user, course_id, pinned_only=pinned)


@router.get(
    "/courses/{course_id}/announcements/{announcement_id}", response_model=AnnouncementResponse
)
async def get_announcement(
    course_id: uuid.UUID,
    announcement_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.get_announcement(current_user, course_id, announcement_id)


@router.patch(
    "/courses/{course_id}/announcements/{announcement_id}", response_model=AnnouncementResponse
)
async def update_announcement(
    course_id: uuid.UUID,
    announcement_id: uuid.UUID,
    payload: AnnouncementUpdate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.update_announcement(current_user, course_id, announcement_id, payload)


@router.delete(
    "/courses/{course_id}/announcements/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_announcement(
    course_id: uuid.UUID,
    announcement_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    await svc.delete_announcement(current_user, course_id, announcement_id)


# ---------------------------------------------------------------------------
# Gradebook
# ---------------------------------------------------------------------------


@router.get("/courses/{course_id}/gradebook", response_model=list[GradebookEntryResponse])
async def get_gradebook(course_id: uuid.UUID, current_user: AuthorizedLecturer, session: DBSession):
    svc = LecturerService(session)
    return await svc.get_gradebook(current_user, course_id)


@router.patch("/courses/{course_id}/gradebook/{student_id}", response_model=GradebookEntryResponse)
async def update_gradebook_entry(
    course_id: uuid.UUID,
    student_id: uuid.UUID,
    payload: GradebookUpdateRequest,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.update_gradebook_entry(
        current_user,
        course_id,
        student_id,
        manual_grade=payload.manual_grade,
        notes=payload.notes,
    )


# ---------------------------------------------------------------------------
# Analytics & AI Tutor
# ---------------------------------------------------------------------------


@router.get("/analytics", response_model=LecturerGlobalAnalytics, status_code=status.HTTP_200_OK)
async def get_analytics(current_user: AuthorizedLecturer, session: DBSession):
    svc = AnalyticsService(session)
    return await svc.get_lecturer_global_metrics(current_user.id)


@router.get("/courses/{course_id}/analytics", response_model=LecturerCourseAnalytics, status_code=status.HTTP_200_OK)
async def get_course_analytics(course_id: uuid.UUID, _: AuthorizedLecturer, session: DBSession):
    svc = AnalyticsService(session)
    return await svc.get_lecturer_course_metrics(course_id)


@router.post("/courses/{course_id}/ai-tutor", response_model=AITutorResponse, status_code=status.HTTP_200_OK)
async def ai_tutor(
    course_id: uuid.UUID, payload: AITutorRequest, current_user: AuthorizedLecturer, session: DBSession
):
    svc = AITutorService(session)
    return await svc.chat(current_user.id, course_id, payload)


@router.patch("/courses/{course_id}/ai-tutor/rules", status_code=status.HTTP_200_OK)
async def update_ai_tutor_rules(
    course_id: uuid.UUID, payload: AITutorRuleUpdate, _: AuthorizedLecturer, session: DBSession
) -> JSONResponse:
    svc = AITutorService(session)
    await svc.update_rules(course_id, payload.rules)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "AI Tutor rules updated successfully."})
