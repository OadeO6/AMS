from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.gradebook import GradebookEntryResponse
from app.schemas.session import AttendanceResponse
from app.schemas.task import QuestionResponse, SubmissionResponse, TaskResponse


class StudentTaskDetailResponse(TaskResponse):
    model_config = ConfigDict()
    questions: list[QuestionResponse]


class AnswerSubmit(BaseModel):
    model_config = ConfigDict()
    question_id: str
    selected_option: str | None = None
    text_answer: str | None = None
    file_url: str | None = None


class SubmitTaskRequest(BaseModel):
    model_config = ConfigDict()
    answers: list[AnswerSubmit]


class GradeSummarySection(BaseModel):
    model_config = ConfigDict()
    total_score: float
    average: float
    grade: str | None


class StudentGradeSummary(BaseModel):
    model_config = ConfigDict()
    submissions: list[SubmissionResponse]
    summary: GradeSummarySection


class StudentAnnouncementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    body: str
    pinned: bool
    created_at: datetime
    viewed: bool = False


class AttendanceSummary(BaseModel):
    """Overall attendance summary for a student in a course."""
    
    model_config = ConfigDict()
    
    total: int
    present: int
    absent: int
    percentage: float


class StudentAttendanceResponse(BaseModel):
    """Wrapped response for student attendance view."""
    
    model_config = ConfigDict()
    
    attendance: list[AttendanceResponse]
    summary: AttendanceSummary
