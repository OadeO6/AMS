# src/app/models/academic_session.py
"""
AcademicSession and Semester ORM models.

AcademicSession: e.g. "2024/2025" — contains two Semesters.
Semester:        first | second — only one is active globally at any time.
"""

from __future__ import annotations

import uuid
from datetime import date
from enum import StrEnum

from sqlalchemy import Boolean, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class SemesterName(StrEnum):
    FIRST = "first"
    SECOND = "second"


class AcademicSession(Base, TimestampMixin):
    """An academic session, e.g. "2024/2025"."""

    __tablename__ = "academic_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        doc='e.g. "2024/2025"',
    )

    def __repr__(self) -> str:
        return f"<AcademicSession id={self.id!s} name={self.name!r}>"


class Semester(Base):
    """A semester within an AcademicSession.

    Only one Semester.is_active may be True globally at any time.
    Admin controls activation; activating one automatically deactivates others.
    """

    __tablename__ = "semesters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    academic_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academic_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        doc="first | second",
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        doc="Only one Semester may be active globally.",
    )

    def __repr__(self) -> str:
        return f"<Semester id={self.id!s} name={self.name!r} active={self.is_active}>"
