from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class QuestionType(StrEnum):
    mcq = "mcq"
    free_text = "free_text"
    document_upload = "document_upload"


class GradingStatus(StrEnum):
    ungraded = "ungraded"
    ai_draft = "ai_draft"
    ai_approved = "ai_approved"
    manually_graded = "manually_graded"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------


class TaskCreate(BaseModel):
    model_config = ConfigDict()

    title: str
    description: str | None = None
    due_date: datetime
    ai_grading: bool = False
    marking_guide_url: str | None = None
    session_id: uuid.UUID | None = None
    questions: list['QuestionCreate'] = []


class TaskUpdate(BaseModel):
    model_config = ConfigDict()

    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    ai_grading: bool | None = None
    marking_guide_url: str | None = None
    session_id: uuid.UUID | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    offering_id: uuid.UUID
    title: str
    description: str | None
    due_date: datetime
    ai_grading: bool
    marking_guide_url: str | None
    created_at: datetime


class AIGradingToggleRequest(BaseModel):
    """Payload to enable/disable AI grading."""

    model_config = ConfigDict()
    enabled: bool


class MarkingGuideUploadRequest(BaseModel):
    """Payload to update marking guide URL."""

    model_config = ConfigDict()
    file_url: str


# ---------------------------------------------------------------------------
# Question
# ---------------------------------------------------------------------------


class QuestionCreate(BaseModel):
    model_config = ConfigDict()

    text: str
    type: QuestionType
    score: float
    options: list[str] | None = None


class QuestionUpdate(BaseModel):
    model_config = ConfigDict()

    text: str | None = None
    score: float | None = None
    options: list[str] | None = None


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_id: uuid.UUID
    text: str
    type: QuestionType
    score: float
    options: list[str] | None


# ---------------------------------------------------------------------------
# Submission / Grading
# ---------------------------------------------------------------------------


class AnswerGrade(BaseModel):
    model_config = ConfigDict()

    answer_id: uuid.UUID
    score: float
    feedback: str | None = None


class GradeItem(BaseModel):
    question_id: uuid.UUID
    score: float
    feedback: str | None = None


class GradeSubmissionRequest(BaseModel):
    model_config = ConfigDict()

    grades: list[GradeItem]


class AnswerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    question_id: uuid.UUID
    selected_option: str | None
    text_answer: str | None
    file_url: str | None
    score: float | None
    feedback: str | None


class SubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_id: uuid.UUID
    student_id: uuid.UUID
    submitted_at: datetime
    grading_status: GradingStatus
    total_score: float | None
    graded_at: datetime | None

class TaskCreateResponse(BaseModel):
    message: str
    task: TaskResponse

class TaskListItem(BaseModel):
    id: uuid.UUID
    title: str
    due_date: datetime
    question_count: int
    total_score: float
    ai_grading: bool

class TaskListResponse(BaseModel):
    tasks: list[TaskListItem]

class TaskDetailResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    due_date: datetime
    total_score: float
    ai_grading: bool
    marking_guide_url: str | None
    questions: list[QuestionResponse]

class StudentTaskListItem(BaseModel):
    id: uuid.UUID
    title: str
    due_date: datetime
    max_score: float
    submission_status: str
    score: float | None = None

class StudentTaskListResponse(BaseModel):
    tasks: list[StudentTaskListItem]

class TaskUpdateResponse(BaseModel):
    message: str
    task: TaskResponse

class QuestionCreateResponse(BaseModel):
    message: str
    question: QuestionResponse

class QuestionUpdateResponse(BaseModel):
    message: str
    question: QuestionResponse

class MarkingGuideResponse(BaseModel):
    message: str
    marking_guide_url: str

class AIGradingToggleResponse(BaseModel):
    message: str
    ai_grading: bool

class GradeSubmissionResponse(BaseModel):
    message: str
    submission: SubmissionResponse

class SubmissionListItem(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    submitted_at: datetime
    total_score: float | None = None
    grading_status: GradingStatus

class SubmissionListResponse(BaseModel):
    submissions: list[SubmissionListItem]

class ApproveAIGradesRequest(BaseModel):
    submission_ids: list[str] | None = None

class ApproveAIGradesResponse(BaseModel):
    message: str
    approved: int

class StudentGradeItem(BaseModel):
    task_id: uuid.UUID
    task_title: str
    score: float | None
    max_score: float
    graded_at: datetime | None
    feedback: str | None

class StudentGradeListResponse(BaseModel):
    grades: list[StudentGradeItem]
    submissions: list[StudentGradeItem] | None = None # Compatibility with legacy tests
    summary: dict

class SubmitTaskResponse(BaseModel):
    message: str
    submission: SubmissionResponse
