# src/app/schemas/user.py
"""
Pydantic v2 schemas for the User domain (AMS version).

Schema hierarchy:
    UserPublic          — API response (never exposes password / hash)
    UserUpdate          — PATCH /auth/me (common fields)
    LecturerUpdate      — PATCH /auth/me/lecturer (lecturer-only fields)
    PasswordUpdate      — PATCH /auth/me/password
    StudentRegister     — POST /auth/register/student
    LecturerRegister    — POST /auth/register/lecturer
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class StudentRegister(BaseModel):
    """Payload for POST /api/v1/auth/register/student."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    department_id: uuid.UUID | None = None


class LecturerRegister(BaseModel):
    """Payload for POST /api/v1/auth/register/lecturer."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    staff_id: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    department_id: uuid.UUID | None = None


class UserUpdate(BaseModel):
    """Partial profile update for PATCH /auth/me (common fields)."""

    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    avatar: str | None = Field(default=None, max_length=500)


class LecturerUpdate(BaseModel):
    """Lecturer-specific profile update for PATCH /auth/me/lecturer."""

    staff_id: str | None = Field(default=None, max_length=100)


class PasswordUpdate(BaseModel):
    """Payload for PATCH /auth/me/password."""

    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    """API response schema for a user resource.

    from_attributes=True allows constructing from a SQLAlchemy ORM instance.
    hashed_password is intentionally absent.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    department_id: uuid.UUID | None
    phone: str | None
    avatar: str | None
    is_active: bool
    is_authorized: bool | None
    admission_year: int | None
    level_offset: int | None
    staff_id: str | None
    created_at: datetime
    updated_at: datetime
