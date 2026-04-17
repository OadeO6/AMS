"""Pydantic schemas specific to Student views."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.gradebook import GradebookEntryResponse
from app.schemas.task import SubmissionResponse, TaskResponse, QuestionResponse


class StudentTaskDetailResponse(TaskResponse):
    questions: list[QuestionResponse]

class AnswerSubmit(BaseModel):
    question_id: str
    selected_option: str | None = None
    text_answer: str | None = None
    file_url: str | None = None


class SubmitTaskRequest(BaseModel):
    answers: list[AnswerSubmit]


class StudentGradeSummary(BaseModel):
    submissions: list[SubmissionResponse]
    gradebook: GradebookEntryResponse | None


class StudentAnnouncementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    body: str
    pinned: bool
    created_at: datetime
    viewed: bool = False
