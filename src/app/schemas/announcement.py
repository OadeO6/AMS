"""Pydantic schemas for Announcement."""

from __future__ import annotations

import uuid
from datetime import datetime

from app.schemas.course import PaginationMeta

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


class AnnouncementCreateResponse(BaseModel):
    message: str
    announcement: AnnouncementResponse

class AnnouncementListResponse(BaseModel):
    announcements: list[AnnouncementResponse]
    pagination: PaginationMeta

class LecturerNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    first_name: str
    last_name: str
    name: str | None = None

class StudentAnnouncementItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    body: str
    created_at: datetime
    lecturer: LecturerNested | None = None
    viewed: bool = False

class StudentAnnouncementListResponse(BaseModel):
    announcements: list[StudentAnnouncementItem]
    pagination: PaginationMeta
