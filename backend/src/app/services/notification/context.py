"""
DeliveryContext — the immutable bag of data passed to every channel's send().

Created by the ARQ task after the Notification row is persisted.
Channels must not mutate this object; they read from it only.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from app.models.notification import NotificationChannel
from app.services.notification.events import NotificationEvent


@dataclass(frozen=True, slots=True)
class DeliveryContext:
    """All information a channel needs to deliver one notification.

    Fields
    ------
    notification_id:
        PK of the ``notifications`` row created by the ARQ task.
        Channels use this if they need to refer back to the DB row.
    user_id:
        Recipient's user PK.
    event:
        The emitted event, e.g. NotificationEvent.GRADE_PUBLISHED.
    channel:
        The channel responsible for delivering this context instance.
    title:
        Rendered notification title (from the event registry template).
    body:
        Rendered notification body.
    data:
        The raw kwargs dict passed to emit() — forwarded to the client
        for deep-linking (e.g. ``{"course_id": "...", "grade": "A"}``).
    recipient_email:
        Email address resolved from the User row; None if unavailable.
    recipient_phone:
        E.164 phone number resolved from the User row; None if unavailable.
    """

    notification_id: uuid.UUID
    user_id: uuid.UUID
    event: NotificationEvent
    channel: NotificationChannel
    title: str
    body: str
    data: dict[str, Any] = field(default_factory=dict)

    # Resolved contact details — populated by the ARQ task from the User row
    recipient_email: str | None = None
    recipient_phone: str | None = None  # E.164 format, e.g. "+2348012345678"
