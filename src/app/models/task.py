# src/app/models/task.py
"""
Task, Question, Submission, and Answer ORM models.

Task:       An assignment attached to a CourseOffering (optionally to a ClassSession).
Question:   A single question within a Task; all questions share the task's type.
Submission: A student's submission for a Task.
Answer:     A student's response to one Question within a Submission.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Task(Base, TimestampMixin):
    """An assignment / assessment for a CourseOffering.

    totalScore is computed (sum of question scores) — never stored here.
    """

    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    offering_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("course_offerings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("class_sessions.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ai_grading: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        doc="AI grading can only be enabled after a marking guide is uploaded.",
    )
    marking_guide_url: Mapped[str | None] = mapped_column(String(1000), nullable=True, default=None)

    def __repr__(self) -> str:
        return f"<Task id={self.id!s} title={self.title!r}>"


class Question(Base):
    """A single question within a Task.

    All questions in a Task share the same type (enforced by service logic).
    options is only populated for MCQ questions.
    """

    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        doc="mcq | free_text | document_upload",
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    options: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
        default=None,
        doc="Answer choices for MCQ questions.",
    )

    def __repr__(self) -> str:
        return f"<Question id={self.id!s} type={self.type!r}>"


class Submission(Base):
    """A student's submission for a Task."""

    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    grading_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="ungraded",
        server_default="ungraded",
        doc="ungraded | ai_draft | ai_approved | manually_graded",
    )
    total_score: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    graded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    def __repr__(self) -> str:
        return f"<Submission id={self.id!s} status={self.grading_status!r}>"


class Answer(Base):
    """A student's response to a single Question within a Submission."""

    __tablename__ = "answers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    selected_option: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)
    text_answer: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    file_url: Mapped[str | None] = mapped_column(String(1000), nullable=True, default=None)
    score: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    def __repr__(self) -> str:
        return f"<Answer id={self.id!s} question={self.question_id!s}>"
