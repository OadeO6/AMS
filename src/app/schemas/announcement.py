"""Pydantic schemas for Announcement."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnnouncementCreate(BaseModel):
    title: str
    body: str
    pinned: bool = False


class AnnouncementUpdate(BaseModel):
    title: str | None = None
    body: str | None = None
    pinned: bool | None = None


class AnnouncementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    offering_id: uuid.UUID
    lecturer_id: uuid.UUID
    title: str
    body: str
    pinned: bool
    created_at: datetime
    updated_at: datetime
