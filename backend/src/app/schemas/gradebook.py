from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GradebookUpdateRequest(BaseModel):
    model_config = ConfigDict()

    manual_grade: str | None = None
    notes: str | None = None


class GradebookEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    offering_id: uuid.UUID
    student_id: uuid.UUID
    name: str | None = None  # Student name for lecturer view
    
    # Enriched fields
    tasks: list[dict] = []  # [{ taskId, title, score, maxScore }]
    total_score: float = 0.0
    average: float = 0.0
    grade: str | None = None
    
    manual_grade: str | None
    notes: str | None
    updated_at: datetime


class GradebookStudentEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: uuid.UUID
    name: str | None = None
    tasks: list[dict] = []
    total_score: float = 0.0
    average: float = 0.0
    grade: str | None = None
    manual_grade: str | None = None
    notes: str | None = None

class GradebookListResponse(BaseModel):
    """Wrapped response for lecturer gradebook view."""
    
    model_config = ConfigDict()
    
    students: list[GradebookStudentEntry]

GradebookResponse = GradebookListResponse
