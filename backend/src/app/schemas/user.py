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

    model_config = ConfigDict()

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    matric_num: str = Field(max_length=50)
    admission_session: str = Field(max_length=20)  # e.g. "2021/2022"
    phone: str | None = Field(default=None, max_length=30)
    department_id: uuid.UUID | None = None


class LecturerRegister(BaseModel):
    """Payload for POST /api/v1/auth/register/lecturer."""

    model_config = ConfigDict()

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    staff_id: str = Field(max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    department_id: uuid.UUID | None = None


class UserUpdate(BaseModel):
    """Partial profile update for PATCH /auth/me (common fields)."""

    model_config = ConfigDict()

    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    avatar: str | None = Field(default=None, max_length=500)


class LecturerUpdate(BaseModel):
    """Lecturer-specific profile update for PATCH /auth/me/lecturer."""

    model_config = ConfigDict()

    staff_id: str | None = Field(default=None, max_length=100)


class StudentUpdate(BaseModel):
    """Student-specific profile update for PATCH /auth/me/student."""

    model_config = ConfigDict()

    matric_num: str | None = Field(default=None, max_length=50)
    admission_session: str | None = Field(default=None, max_length=20)


class PasswordUpdate(BaseModel):
    """Payload for PATCH /auth/me/password."""

    model_config = ConfigDict()

    current_password: str
    new_password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)


class DepartmentPublic(BaseModel):
    """Nested department object in User responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str

DepartmentNested = DepartmentPublic




class UserPublic(BaseModel):
    """API response schema for a user resource.

    from_attributes=True allows constructing from a SQLAlchemy ORM instance.
    hashed_password is intentionally absent.
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    roles: list[str]
    department: DepartmentPublic | None = None
    department_id: uuid.UUID | None
    phone: str | None
    avatar: str | None
    is_active: bool
    is_authorized: bool | None = Field(default=None, alias="authorized")
    matric_num: str | None = None
    admission_session: str | None = None
    level_offset: int | None
    staff_id: str | None
    created_at: datetime
    updated_at: datetime


class AuthorizeStaffRequest(BaseModel):
    """Payload to authorize lecturer accounts (Admin only)."""

    model_config = ConfigDict()

    user_ids: list[uuid.UUID]


class BulkAuthorizeResponse(BaseModel):
    """Response for bulk authorization."""

    message: str
    authorized: int
    failed: list[dict] = []


class LevelOffsetRequest(BaseModel):
    """Payload to update a student's level offset (HOD only)."""

    model_config = ConfigDict()

    level_offset: int


class UserPagination(BaseModel):
    """Metadata for paginated responses."""

    model_config = ConfigDict()

    page: int
    limit: int
    total: int


class UserListResponse(BaseModel):
    """Paginated list of users."""

    users: list[UserPublic]
    pagination: UserPagination


class UserSharedPublic(BaseModel):
    """Minimal user information for shared endpoints."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    first_name: str
    last_name: str
    roles: list[str]
    email: EmailStr
    department: DepartmentPublic | None = None
    avatar: str | None = None


class UserSharedListResponse(BaseModel):
    """Paginated list of shared users."""
    users: list[UserSharedPublic]
    pagination: UserPagination


class StudentPublicMe(BaseModel):
    """Specific response for GET /auth/me (Student)."""
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr
    roles: list[str]
    matric_num: str | None = None
    admission_session: str | None = None
    level_offset: int | None = None
    department: DepartmentNested | None = None

class LecturerPublicMe(BaseModel):
    """Specific response for GET /auth/me (Lecturer)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr
    roles: list[str]
    staff_id: str | None = None
    is_authorized: bool | None = Field(default=None, alias="authorized")
    department: DepartmentNested | None = None

class UpdateMeResponse(BaseModel):
    message: str
    user: UserPublic

class UpdateStudentProfileData(BaseModel):
    id: uuid.UUID
    matric_num: str | None = None
    admission_session: str | None = None

class UpdateStudentProfileResponse(BaseModel):
    message: str
    user: UpdateStudentProfileData

class UpdateLecturerProfileData(BaseModel):
    id: uuid.UUID
    staff_id: str | None = None

class UpdateLecturerProfileResponse(BaseModel):
    message: str
    user: UpdateLecturerProfileData

class LevelOffsetProfileData(BaseModel):
    id: uuid.UUID
    level_offset: int | None = None
    level: int | None = None

class LevelOffsetResponse(BaseModel):
    message: str
    student: LevelOffsetProfileData

