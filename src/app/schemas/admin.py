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
    hod_id: uuid.UUID


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
    semesters: list[SemesterCreate]


class AcademicSessionUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=20)


class AcademicSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    created_at: datetime
    semesters: list[SemesterResponse] = []
