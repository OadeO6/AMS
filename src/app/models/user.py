# src/app/models/user.py
"""
User ORM model — AMS domain version.

A User is an authenticated principal with one of four roles:
  student | lecturer | hod | admin

Passwords are NEVER stored in plain text — only the bcrypt hash goes here.
"""

from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class UserRole(StrEnum):
    """Role enum for the User model."""

    STUDENT = "student"
    LECTURER = "lecturer"
    HOD = "hod"
    ADMIN = "admin"


class User(Base, TimestampMixin):
    """Represents an authenticated AMS user.

    Columns
    -------
    id              UUID primary key (generated at creation time).
    email           Unique, indexed login identifier.
    hashed_password Bcrypt hash (cost 12). Never returned in responses.
    first_name      Given name.
    last_name       Family name.
    role            One of: student | lecturer | hod | admin.
    department_id   FK → Department (nullable; FK constraint added in Phase 3).
    phone           Optional contact number.
    avatar          Optional URL to profile image.
    is_active       Soft-disable without deleting the record.

    Student-only
    ------------
    admission_year  The calendar year of admission (e.g. 2021).
    level_offset    Adjustment for deferrals/repeats (default 0).

    Lecturer-only
    -------------
    staff_id        Institution staff identifier.
    is_authorized   Set to True by Admin before lecturer can access routes.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Primary key — UUID generated at creation time.",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="Unique email address used for authentication.",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="bcrypt hash of the user's password (cost factor 12).",
    )
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="User's given name.",
    )
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="User's family name.",
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="One of: student | lecturer | hod | admin.",
    )
    # FK to Department — stored as UUID; FK constraint added in Phase 3 migration
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        default=None,
        doc="Department the user belongs to (FK enforced in Phase 3).",
    )
    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        default=None,
        doc="Optional contact phone number.",
    )
    avatar: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        default=None,
        doc="Optional URL to the user's profile image.",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        doc="Inactive users cannot log in.",
    )

    # ------------------------------------------------------------------
    # Student-only fields
    # ------------------------------------------------------------------
    admission_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=None,
        doc="Year of first admission (e.g. 2021). Student role only.",
    )
    level_offset: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        server_default="0",
        doc="Offset applied to computed level for deferrals/repeats. Student role only.",
    )

    # ------------------------------------------------------------------
    # Lecturer-only fields
    # ------------------------------------------------------------------
    staff_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default=None,
        doc="Institution staff ID. Lecturer role only.",
    )
    is_authorized: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        default=None,
        doc="Set to True by Admin before lecturer can access protected routes.",
    )

    def __repr__(self) -> str:
        return (
            f"<User id={self.id!s} email={self.email!r} role={self.role} active={self.is_active}>"
        )
