# src/app/schemas/course.py
"""
Pydantic schemas for the Course domain.

Provides validation and serialization for Course definitions,
Course Offerings, and Registrations.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Course Definition Schemas
# ---------------------------------------------------------------------------


class CourseBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    code: str = Field(..., min_length=2, max_length=20)
    description: str | None = None
    units: int = Field(..., ge=1, le=10)


class CourseCreate(CourseBase):
    """Schema for HODs creating a new course definition in their department."""

    pass


class CourseUpdate(BaseModel):
    """Schema for updating a course definition."""

    title: str | None = Field(None, min_length=2, max_length=200)
    description: str | None = None
    units: int | None = Field(None, ge=1, le=10)


class CourseResponse(CourseBase):
    id: uuid.UUID
    department_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Course Offering Schemas
# ---------------------------------------------------------------------------


class CourseOfferingCreate(BaseModel):
    """Payload for HODs instantiating a Course for a Semester."""

    semester_id: uuid.UUID
    lecturer_id: uuid.UUID | None = None


class CourseOfferingResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    semester_id: uuid.UUID
    lecturer_id: uuid.UUID | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class CourseOfferingAssignLecturer(BaseModel):
    """Payload to assign a primary lecturer to an offering."""

    lecturer_id: uuid.UUID


# ---------------------------------------------------------------------------
# Course Registration Schemas
# ---------------------------------------------------------------------------


class CourseRegistrationResponse(BaseModel):
    id: uuid.UUID
    offering_id: uuid.UUID
    student_id: uuid.UUID
    status: str

    model_config = ConfigDict(from_attributes=True)


class CourseRegistrationStatusUpdate(BaseModel):
    """Lecturer reviewing a registration request."""

    status: str = Field(..., pattern="^(approved|rejected)$")
