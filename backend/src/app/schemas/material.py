"""Pydantic schemas for Material."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class MaterialType(StrEnum):
    note = "note"
    slide = "slide"
    resource = "resource"
    document = "document"


class MaterialVisibility(StrEnum):
    students_only = "students_only"
    ai_only = "ai_only"
    both = "both"


class MaterialCreate(BaseModel):
    title: str
    type: MaterialType
    file_url: str
    visibility: MaterialVisibility = MaterialVisibility.students_only


class MaterialUpdate(BaseModel):
    title: str | None = None
    visibility: MaterialVisibility | None = None


class MaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    offering_id: uuid.UUID
    uploaded_by: uuid.UUID
    title: str
    type: MaterialType
    file_url: str
    visibility: MaterialVisibility
    indexed: bool
    indexed_at: datetime | None
    created_at: datetime

class MaterialUploadResponse(BaseModel):
    message: str
    material: MaterialResponse

class MaterialUpdateResponse(BaseModel):
    message: str
    material: MaterialResponse

class MaterialIndexResponse(BaseModel):
    message: str
    material: MaterialResponse

class StudentMaterialListResponse(BaseModel):
    materials: list[MaterialResponse]

class LecturerMaterialListResponse(BaseModel):
    materials: list[MaterialResponse]

