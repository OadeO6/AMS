# src/app/api/v1/lecturer.py
"""
Lecturer endpoints — all protected routes for the lecturer role.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.core.arq_pool import ArqPool
from app.dependencies import AuthorizedLecturer, DBSession
from app.middleware.active_semester import require_active_semester
from app.middleware.auth import require_authorized_lecturer
from app.schemas.auth import MessageResponse
from app.schemas.announcement import AnnouncementCreate, AnnouncementResponse, AnnouncementUpdate, AnnouncementCreateResponse, AnnouncementListResponse
from app.schemas.gradebook import GradebookEntryResponse, GradebookListResponse, GradebookUpdateRequest
from app.schemas.material import MaterialUpdate, MaterialUploadResponse, MaterialUpdateResponse, MaterialIndexResponse

from app.schemas.session import (
    AttendanceMarkRequest, ClassSessionCreate, ClassSessionResponse, ClassSessionUpdate,
    SessionCreateResponse, SessionListResponse, AttendanceMarkResponse
)
from app.schemas.task import (
    AIGradingToggleRequest, GradeSubmissionRequest, MarkingGuideUploadRequest, QuestionCreate, QuestionResponse, QuestionUpdate, SubmissionResponse, TaskCreate, TaskResponse, TaskUpdate,
    TaskCreateResponse, TaskListResponse, TaskDetailResponse, TaskUpdateResponse, MarkingGuideResponse, AIGradingToggleResponse, QuestionCreateResponse, QuestionUpdateResponse, SubmissionListResponse, GradeSubmissionResponse, ApproveAIGradesResponse, ApproveAIGradesRequest
)
from app.schemas.course import (
    CourseOfferingResponse, CourseRegistrationStatusUpdate, LecturerCourseListResponse, LecturerCourseDetailResponse, CourseStudentListResponse
)
from app.schemas.analytics import LecturerCourseAnalytics, LecturerGlobalAnalytics
from app.schemas.ai_tutor import AITutorRequest, AITutorResponse, AITutorRuleUpdate, AITutorRulesResponse
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


@router.get("/courses", response_model=LecturerCourseListResponse)
async def list_courses(current_user: AuthorizedLecturer, session: DBSession):
    return await LecturerService(session).list_course_response(current_user)


@router.get("/courses/{offering_id}", response_model=LecturerCourseDetailResponse)
async def get_course(offering_id: uuid.UUID, current_user: AuthorizedLecturer, session: DBSession):
    return await LecturerService(session).get_course_detail_response(current_user, offering_id)


# ---------------------------------------------------------------------------
# Students
# ---------------------------------------------------------------------------


@router.get("/courses/{offering_id}/students", response_model=CourseStudentListResponse)
async def list_students(offering_id: uuid.UUID, current_user: AuthorizedLecturer, session: DBSession):
    return await LecturerService(session).list_student_response(current_user, offering_id)


@router.patch("/courses/{offering_id}/students/{student_id}/approve", response_model=MessageResponse)
async def approve_student(
    offering_id: uuid.UUID,
    student_id: uuid.UUID,
    payload: CourseRegistrationStatusUpdate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    reg = await svc.update_student_registration_status(current_user, offering_id, student_id, status=payload.status)
    return MessageResponse(message="Student status updated")


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------


@router.post(
    "/courses/{offering_id}/materials",
    response_model=MaterialUploadResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_active_semester)],
)
async def upload_material(
    current_user: AuthorizedLecturer,
    session: DBSession,
    offering_id: uuid.UUID,
    title: str = Form(...),
    type: str = Form(...),
    visibility: str = Form(...),
    file: UploadFile = File(...),
):
    from app.services.storage import StorageService
    from app.schemas.material import MaterialCreate

    storage_svc = StorageService()
    # Read and upload file concurrently or synchronously depending on the client
    file_url = storage_svc.upload_file(file.file, file.filename, file.content_type)
    
    payload = MaterialCreate(title=title, type=type, visibility=visibility, file_url=file_url)
    svc = LecturerService(session)
    mat = await svc.create_material(current_user, offering_id, payload)
    return MaterialUploadResponse(message="Uploaded successfully", material=mat)


@router.patch("/courses/{offering_id}/materials/{material_id}", response_model=MaterialUpdateResponse)
async def update_material(
    offering_id: uuid.UUID,
    material_id: uuid.UUID,
    payload: MaterialUpdate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    mat = await svc.update_material(current_user, offering_id, material_id, payload)
    return MaterialUpdateResponse(message="Updated successfully", material=mat)


@router.delete(
    "/courses/{offering_id}/materials/{material_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK
)
async def delete_material(
    offering_id: uuid.UUID,
    material_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    await svc.delete_material(current_user, offering_id, material_id)
    return MessageResponse(message="Deleted successfully")


@router.post("/courses/{offering_id}/materials/{material_id}/index", response_model=MaterialIndexResponse)
async def index_material(
    offering_id: uuid.UUID,
    material_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    mat = await svc.index_material(current_user, offering_id, material_id)
    return MaterialIndexResponse(message="Indexed successfully", material=mat)


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


@router.post(
    "/courses/{offering_id}/tasks",
    response_model=TaskCreateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_active_semester)],
)
async def create_task(
    offering_id: uuid.UUID,
    payload: TaskCreate,
    current_user: AuthorizedLecturer,
    session: DBSession,
    arq: ArqPool,
):
    svc = LecturerService(session)
    task = await svc.create_task(current_user, offering_id, payload, arq=arq)
    return TaskCreateResponse(message="Task created", task=task)


@router.get("/courses/{offering_id}/tasks", response_model=TaskListResponse)
async def list_tasks(offering_id: uuid.UUID, current_user: AuthorizedLecturer, session: DBSession):
    return await LecturerService(session).list_task_response(current_user, offering_id)


@router.get("/courses/{offering_id}/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task(
    offering_id: uuid.UUID, task_id: uuid.UUID, current_user: AuthorizedLecturer, session: DBSession
):
    return await LecturerService(session).get_task_detail_response(current_user, offering_id, task_id)


@router.patch("/courses/{offering_id}/tasks/{task_id}", response_model=TaskUpdateResponse)
async def update_task(
    offering_id: uuid.UUID,
    task_id: uuid.UUID,
    payload: TaskUpdate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    task = await svc.update_task(current_user, offering_id, task_id, payload)
    return TaskUpdateResponse(message="Task updated", task=TaskResponse.model_validate(task))


@router.delete("/courses/{offering_id}/tasks/{task_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_task(
    offering_id: uuid.UUID,
    task_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    await svc.delete_task(current_user, offering_id, task_id)
    return MessageResponse(message="Task deleted")


@router.post("/courses/{offering_id}/tasks/{task_id}/marking-guide", response_model=MarkingGuideResponse)
async def upload_marking_guide(
    offering_id: uuid.UUID,
    task_id: uuid.UUID,
    payload: MarkingGuideUploadRequest,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    res = await svc.upload_marking_guide(current_user, offering_id, task_id, payload.file_url)
    return MarkingGuideResponse(message="Marking guide uploaded", marking_guide_url=payload.file_url)


@router.patch("/courses/{offering_id}/tasks/{task_id}/ai-grading", response_model=AIGradingToggleResponse)
async def toggle_ai_grading(
    offering_id: uuid.UUID,
    task_id: uuid.UUID,
    payload: AIGradingToggleRequest,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    res = await svc.toggle_ai_grading(current_user, offering_id, task_id, payload.enabled)
    return AIGradingToggleResponse(message="AI Grading toggled", ai_grading=payload.enabled)


# ---------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------


@router.post(
    "/courses/{offering_id}/tasks/{task_id}/questions",
    response_model=QuestionCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_question(
    offering_id: uuid.UUID,
    task_id: uuid.UUID,
    payload: QuestionCreate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    q = await svc.create_question(current_user, offering_id, task_id, payload)
    return QuestionCreateResponse(message="Question created", question=q)


@router.patch(
    "/courses/{offering_id}/tasks/{task_id}/questions/{question_id}", response_model=QuestionUpdateResponse
)
async def update_question(
    offering_id: uuid.UUID,
    task_id: uuid.UUID,
    question_id: uuid.UUID,
    payload: QuestionUpdate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    q = await svc.update_question(current_user, offering_id, task_id, question_id, payload)
    return QuestionUpdateResponse(message="Question updated", question=QuestionResponse.model_validate(q))


@router.delete(
    "/courses/{offering_id}/tasks/{task_id}/questions/{question_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_question(
    offering_id: uuid.UUID,
    task_id: uuid.UUID,
    question_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    await svc.delete_question(current_user, offering_id, task_id, question_id)
    return MessageResponse(message="Question deleted")


# ---------------------------------------------------------------------------
# Submissions
# ---------------------------------------------------------------------------


@router.get(
    "/courses/{offering_id}/tasks/{task_id}/submissions", response_model=SubmissionListResponse
)
async def list_submissions(
    offering_id: uuid.UUID,
    task_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
    graded: bool | None = Query(None),
):
    return await LecturerService(session).list_submission_response(current_user, offering_id, task_id, graded=graded)


@router.get(
    "/courses/{offering_id}/tasks/{task_id}/submissions/{submission_id}",
    response_model=SubmissionResponse,
)
async def get_submission(
    offering_id: uuid.UUID,
    task_id: uuid.UUID,
    submission_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.get_submission(current_user, offering_id, task_id, submission_id)


@router.patch(
    "/courses/{offering_id}/tasks/{task_id}/submissions/{submission_id}/grade",
    response_model=GradeSubmissionResponse,
)
async def grade_submission(
    offering_id: uuid.UUID,
    task_id: uuid.UUID,
    submission_id: uuid.UUID,
    payload: GradeSubmissionRequest,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    sub = await svc.grade_submission(current_user, offering_id, task_id, submission_id, payload)
    return GradeSubmissionResponse(message="Submission graded", submission=SubmissionResponse.model_validate(sub))


@router.post(
    "/courses/{offering_id}/tasks/{task_id}/submissions/approve-ai-grades", response_model=ApproveAIGradesResponse
)
async def approve_ai_grades(
    offering_id: uuid.UUID,
    task_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
    payload: ApproveAIGradesRequest | None = None,
):
    svc = LecturerService(session)
    count = await svc.approve_ai_grades(current_user, offering_id, task_id)
    return ApproveAIGradesResponse(message="AI Grades approved", approved=count)


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------


@router.post(
    "/courses/{offering_id}/sessions",
    response_model=SessionCreateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_active_semester)],
)
async def create_session(
    offering_id: uuid.UUID,
    payload: ClassSessionCreate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    sess = await svc.create_session(current_user, offering_id, payload)
    from app.schemas.session import SessionBasicResponse
    
    return SessionCreateResponse(
        message="Session created", 
        session=SessionBasicResponse.model_validate(sess)
    )


@router.patch("/courses/{offering_id}/sessions/{session_id}", response_model=MessageResponse)
async def update_session(
    offering_id: uuid.UUID,
    session_id: uuid.UUID,
    payload: ClassSessionUpdate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    sess = await svc.update_session(current_user, offering_id, session_id, payload)
    return MessageResponse(message="Session updated")


@router.delete("/courses/{offering_id}/sessions/{session_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_session(
    offering_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    await svc.delete_session(current_user, offering_id, session_id)
    return MessageResponse(message="Session deleted")


@router.get("/courses/{offering_id}/sessions", response_model=SessionListResponse)
async def list_sessions(offering_id: uuid.UUID, current_user: AuthorizedLecturer, session: DBSession):
    svc = LecturerService(session)
    sessions = await svc.list_sessions(current_user, offering_id)
    return {"sessions": sessions}


@router.get("/courses/{offering_id}/sessions/{session_id}", response_model=ClassSessionResponse)
async def get_session(
    offering_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    sess, attendance_records = await svc.get_session(current_user, offering_id, session_id)
    data = ClassSessionResponse.model_validate(sess)
    data.is_owner = sess.lecturer_id == current_user.id
    data.attendance = attendance_records
    return data


@router.post(
    "/courses/{offering_id}/sessions/{session_id}/attendance", response_model=AttendanceMarkResponse
)
async def mark_attendance(
    offering_id: uuid.UUID,
    session_id: uuid.UUID,
    payload: AttendanceMarkRequest,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    count = await svc.mark_attendance(current_user, offering_id, session_id, payload)
    return AttendanceMarkResponse(message="Attendance marked", marked=len(count) if isinstance(count, list) else count)


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------


@router.post(
    "/courses/{offering_id}/announcements",
    response_model=AnnouncementCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_announcement(
    offering_id: uuid.UUID,
    payload: AnnouncementCreate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    ann = await svc.create_announcement(current_user, offering_id, payload)
    return AnnouncementCreateResponse(message="Announcement created", announcement=ann)


@router.get("/courses/{offering_id}/announcements", response_model=AnnouncementListResponse)
async def list_announcements(
    offering_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
    pinned: bool = Query(False),
):
    return await LecturerService(session).list_announcement_response(current_user, offering_id, pinned_only=pinned)


@router.get(
    "/courses/{offering_id}/announcements/{announcement_id}", response_model=AnnouncementResponse
)
async def get_announcement(
    offering_id: uuid.UUID,
    announcement_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.get_announcement(current_user, offering_id, announcement_id)


@router.patch(
    "/courses/{offering_id}/announcements/{announcement_id}", response_model=AnnouncementResponse
)
async def update_announcement(
    offering_id: uuid.UUID,
    announcement_id: uuid.UUID,
    payload: AnnouncementUpdate,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.update_announcement(current_user, offering_id, announcement_id, payload)


@router.delete(
    "/courses/{offering_id}/announcements/{announcement_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK
)
async def delete_announcement(
    offering_id: uuid.UUID,
    announcement_id: uuid.UUID,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    await svc.delete_announcement(current_user, offering_id, announcement_id)
    return MessageResponse(message="Announcement deleted")


# ---------------------------------------------------------------------------
# Gradebook
# ---------------------------------------------------------------------------


@router.get("/courses/{offering_id}/gradebook", response_model=GradebookListResponse)
async def get_gradebook(offering_id: uuid.UUID, current_user: AuthorizedLecturer, session: DBSession):
    svc = LecturerService(session)
    entries = await svc.get_gradebook(current_user, offering_id)
    return GradebookListResponse(students=entries)


@router.patch("/courses/{offering_id}/gradebook/{student_id}", response_model=GradebookEntryResponse)
async def update_gradebook_entry(
    offering_id: uuid.UUID,
    student_id: uuid.UUID,
    payload: GradebookUpdateRequest,
    current_user: AuthorizedLecturer,
    session: DBSession,
):
    svc = LecturerService(session)
    return await svc.update_gradebook_entry(
        current_user,
        offering_id,
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


@router.get("/courses/{offering_id}/analytics", response_model=LecturerCourseAnalytics, status_code=status.HTTP_200_OK)
async def get_course_analytics(offering_id: uuid.UUID, _: AuthorizedLecturer, session: DBSession):
    svc = AnalyticsService(session)
    return await svc.get_lecturer_course_metrics(offering_id)


@router.post("/courses/{offering_id}/ai-tutor", response_model=AITutorResponse, status_code=status.HTTP_200_OK)
async def ai_tutor(
    offering_id: uuid.UUID, payload: AITutorRequest, current_user: AuthorizedLecturer, session: DBSession
):
    svc = AITutorService(session)
    return await svc.chat(current_user.id, offering_id, payload)


@router.patch("/courses/{offering_id}/ai-tutor/rules", response_model=AITutorRulesResponse, status_code=status.HTTP_200_OK)
async def update_ai_tutor_rules(
    offering_id: uuid.UUID, payload: AITutorRuleUpdate, _: AuthorizedLecturer, session: DBSession
):
    svc = AITutorService(session)
    await svc.update_rules(offering_id, payload.rules)
    return AITutorRulesResponse(message="AI Tutor rules updated successfully.", rules=payload.rules)
