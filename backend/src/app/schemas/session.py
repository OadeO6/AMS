from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class SessionStatus(StrEnum):
    upcoming = "upcoming"
    completed = "completed"
    cancelled = "cancelled"


class AttendanceStatus(StrEnum):
    present = "present"
    absent = "absent"


class ClassSessionCreate(BaseModel):
    model_config = ConfigDict()

    title: str
    scheduled_at: datetime
    venue: str | None = None
    notes: str | None = None


class ClassSessionUpdate(BaseModel):
    model_config = ConfigDict()

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
    
    lecturer: dict | None = None
    
    # Enriched fields for lecturer view
    attendance: list[AttendanceResponse] = []
    tasks: list[dict] = []  # [{ taskId, title, submissionsCount }]
    
    created_at: datetime


class AttendanceMark(BaseModel):
    model_config = ConfigDict()

    student_id: uuid.UUID
    status: AttendanceStatus


class AttendanceMarkRequest(BaseModel):
    model_config = ConfigDict()

    records: list[AttendanceMark]


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    student_id: uuid.UUID
    name: str | None = None  # For enriched session view
    status: AttendanceStatus
    marked_at: datetime


class AttendanceSummary(BaseModel):
    """Overall attendance summary for a student in a course."""
    
    model_config = ConfigDict()
    
    total: int
    present: int
    absent: int
    percentage: float


class StudentAttendanceResponse(BaseModel):
    """Wrapped response for student attendance view."""
    
    model_config = ConfigDict()
    
    attendance: list[AttendanceResponse]
    summary: AttendanceSummary


class SessionBasicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    scheduled_at: datetime
    venue: str | None = None
    status: str

class SessionCreateResponse(BaseModel):
    message: str
    session: SessionBasicResponse

class SessionListItem(BaseModel):
    id: uuid.UUID
    title: str
    scheduled_at: datetime
    venue: str | None = None
    status: SessionStatus
    attendance_count: int | None = None
    attended: bool | None = None
    lecturer: dict | None = None

class SessionListResponse(BaseModel):
    sessions: list[SessionListItem]

class AttendanceMarkResponse(BaseModel):
    message: str
    marked: int
