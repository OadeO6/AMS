# src/app/models/faculty.py
"""
Faculty ORM model.

A Faculty is the top-level academic grouping. It contains many Departments.
"""

from __future__ import annotations

import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Faculty(Base, TimestampMixin):
    """Represents an academic faculty (e.g. "Faculty of Engineering")."""

    __tablename__ = "faculties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"<Faculty id={self.id!s} code={self.code!r}>"
