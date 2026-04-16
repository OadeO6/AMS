# src/app/models/class_session.py
"""
ClassSession and Attendance ORM models.

ClassSession: A scheduled class event owned by the creating lecturer.
Attendance:   Per-student attendance record for a ClassSession.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ClassSession(Base, TimestampMixin):
    """A class session (lecture, lab, seminar) for a CourseOffering.

    Owned by the lecturer who created it. Only the owner may:
      - Edit the session
      - Cancel the session
      - Mark attendance
    """

    __tablename__ = "class_sessions"

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
    lecturer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        doc="The owning lecturer. Only this user may modify or cancel the session.",
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    venue: Mapped[str | None] = mapped_column(String(200), nullable=True, default=None)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="upcoming",
        server_default="upcoming",
        doc="upcoming | completed | cancelled",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    def __repr__(self) -> str:
        return f"<ClassSession id={self.id!s} title={self.title!r} status={self.status!r}>"


class Attendance(Base):
    """Attendance record for a student in a ClassSession.

    Only the session owner (ClassSession.lecturer_id) may create records.
    """

    __tablename__ = "attendance"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("class_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        doc="present | absent",
    )
    marked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    marked_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        doc="Must match ClassSession.lecturer_id.",
    )

    def __repr__(self) -> str:
        return f"<Attendance id={self.id!s} student={self.student_id!s} status={self.status!r}>"
