"""Pydantic schemas for Gradebook."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GradebookUpdateRequest(BaseModel):
    manual_grade: str | None = None
    notes: str | None = None


class GradebookEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    offering_id: uuid.UUID
    student_id: uuid.UUID
    manual_grade: str | None
    notes: str | None
    updated_at: datetime
