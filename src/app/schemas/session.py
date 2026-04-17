"""Pydantic schemas for ClassSession and Attendance."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class SessionStatus(StrEnum):
    upcoming = "upcoming"
    completed = "completed"
    cancelled = "cancelled"


class AttendanceStatus(StrEnum):
    present = "present"
    absent = "absent"


class ClassSessionCreate(BaseModel):
    title: str
    scheduled_at: datetime
    venue: str | None = None
    notes: str | None = None


class ClassSessionUpdate(BaseModel):
    title: str | None = None
    scheduled_at: datetime | None = None
    venue: str | None = None
    notes: str | None = None
    status: SessionStatus | None = None


class ClassSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    offering_id: uuid.UUID
    lecturer_id: uuid.UUID
    title: str
    scheduled_at: datetime
    venue: str | None
    status: SessionStatus
    notes: str | None
    is_owner: bool = False
    created_at: datetime


class AttendanceMark(BaseModel):
    student_id: uuid.UUID
    status: AttendanceStatus


class AttendanceMarkRequest(BaseModel):
    records: list[AttendanceMark]


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    student_id: uuid.UUID
    status: AttendanceStatus
    marked_at: datetime
