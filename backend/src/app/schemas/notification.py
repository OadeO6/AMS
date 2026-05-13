"""
Pydantic v2 schemas for the notification subsystem.

Naming convention (same as the rest of the codebase):
  - <Resource>Response     — API read shape (from_attributes=True)
  - <Resource>Create/Register — API write shapes
  - <Resource>ListResponse — paginated list wrapper
"""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.notification import NotificationChannel, NotificationStatus


# ---------------------------------------------------------------------------
# In-app notification read schemas
# ---------------------------------------------------------------------------


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event: str
    channel: NotificationChannel
    title: str
    body: str
    data: dict | None
    status: NotificationStatus
    read_at: datetime | None
    sent_at: datetime | None
    created_at: datetime


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    unread_count: int
    total: int
    offset: int
    limit: int


# ---------------------------------------------------------------------------
# Read / mark-as-read mutations
# ---------------------------------------------------------------------------


class MarkReadRequest(BaseModel):
    notification_ids: list[uuid.UUID] = Field(
        min_length=1,
        max_length=100,
        description="IDs of notifications to mark as read (max 100 per call).",
    )


class MarkReadResponse(BaseModel):
    marked: int = Field(description="Number of notifications actually updated.")


# ---------------------------------------------------------------------------
# Device token registration (push channel)
# ---------------------------------------------------------------------------


class DeviceTokenRegister(BaseModel):
    token: str = Field(
        min_length=1,
        description=(
            "FCM registration token (string) "
            "or JSON-serialised Web Push subscription object."
        ),
    )
    platform: str = Field(
        pattern="^(fcm|web)$",
        description="'fcm' for Firebase Cloud Messaging, 'web' for VAPID Web Push.",
    )


class DeviceTokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    platform: str
    is_active: bool
    created_at: datetime
