# src/app/schemas/admin.py
"""
Pydantic v2 schemas for the Admin-only domains (Faculty, Department, Session).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Faculties
# ---------------------------------------------------------------------------


class FacultyCreate(BaseModel):
    name: str = Field(..., max_length=200)
    code: str = Field(..., max_length=20)


class FacultyUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    code: str | None = Field(default=None, max_length=20)


class FacultyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------


class DepartmentCreate(BaseModel):
    name: str = Field(..., max_length=200)
    code: str = Field(..., max_length=20)


class DepartmentUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    code: str | None = Field(default=None, max_length=20)


class AssignHODRequest(BaseModel):
    user_id: uuid.UUID


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    faculty_id: uuid.UUID
    name: str
    code: str
    hod_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Academic Calendar - Semesters
# ---------------------------------------------------------------------------


class SemesterCreate(BaseModel):
    name: str = Field(..., max_length=10)  # e.g., "first" or "second"
    start_date: date
    end_date: date


class SemesterUpdate(BaseModel):
    start_date: date | None = None
    end_date: date | None = None


class SemesterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    start_date: date
    end_date: date
    is_active: bool


# ---------------------------------------------------------------------------
# Academic Calendar - Sessions
# ---------------------------------------------------------------------------


class AcademicSessionCreate(BaseModel):
    name: str = Field(..., max_length=20, examples=["2024/2025"])
    semesters: list[SemesterCreate] = []


class AcademicSessionUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=20)


class AcademicSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    created_at: datetime
    semesters: list[SemesterResponse] = []


class FacultyCreateResponse(BaseModel):
    message: str
    faculty: FacultyResponse

class FacultyListResponse(BaseModel):
    faculties: list[FacultyResponse]

class DepartmentCreateResponse(BaseModel):
    message: str
    department: DepartmentResponse

class DepartmentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    hod_id: uuid.UUID | None = None
    total_courses: int = 0

class DepartmentListResponse(BaseModel):
    departments: list[DepartmentListItem]

class DepartmentDetailResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    faculty: dict | None = None
    hod: dict | None = None
    total_courses: int = 0
    total_students: int = 0
    total_lecturers: int = 0

class DepartmentUpdateResponse(BaseModel):
    message: str
    department: DepartmentResponse

class SessionCreateResponse(BaseModel):
    message: str
    session: AcademicSessionResponse

class SessionListResponse(BaseModel):
    sessions: list[AcademicSessionResponse]

class SessionDetailResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    semesters: list[SemesterResponse] = []

class SessionUpdateResponse(BaseModel):
    message: str
    session: AcademicSessionResponse

class SemesterActivateResponse(BaseModel):
    message: str
    semester: SemesterResponse

class SemesterUpdateResponse(BaseModel):
    message: str
    semester: SemesterResponse
