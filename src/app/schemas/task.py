"""Pydantic schemas for Task, Question, Submission, and Answer."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


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
    title: str
    description: str | None = None
    due_date: datetime
    ai_grading: bool = False


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    ai_grading: bool | None = None
    marking_guide_url: str | None = None


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


# ---------------------------------------------------------------------------
# Question
# ---------------------------------------------------------------------------


class QuestionCreate(BaseModel):
    text: str
    type: QuestionType
    score: float
    options: list[str] | None = None


class QuestionUpdate(BaseModel):
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
    answer_id: uuid.UUID
    score: float
    feedback: str | None = None


class GradeSubmissionRequest(BaseModel):
    answers: list[AnswerGrade]


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
