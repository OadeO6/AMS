# src/app/models/material.py
"""
Material ORM model.

Materials are files uploaded to a CourseOffering.
Visibility controls who may see them and whether they may be indexed for AI.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Material(Base, TimestampMixin):
    """A file resource uploaded for a CourseOffering.

    visibility:
        students_only — visible to enrolled students only; cannot be AI-indexed.
        ai_only       — used only for AI grounding; not shown to students.
        both          — visible to students and available for AI indexing.
    """

    __tablename__ = "materials"

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
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="note | slide | resource",
    )
    file_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    visibility: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="students_only | ai_only | both",
    )
    indexed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    indexed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    def __repr__(self) -> str:
        return f"<Material id={self.id!s} title={self.title!r}>"
