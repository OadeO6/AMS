# src/app/schemas/notification.py
"""
Pydantic v2 schemas for the Notification domain.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    """API response schema for a Notification resource."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    message: str
    type: str
    read: bool
    created_at: datetime
    link: str | None

class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    unread_count: int
