"""
Canonical list of all notification events emitted by the system.

Naming convention:  <domain>.<past-tense-action>
  e.g.  grade.published   announcement.created   auth.password_reset_requested

To add a new event:
  1. Add a member to NotificationEvent below.
  2. Add an EventConfig entry to registry.py (channels + render function).
  3. Call ``emitter.emit(NotificationEvent.YOUR_EVENT, user_id=..., **kwargs)``
     from the relevant service method.
"""
from __future__ import annotations

from enum import StrEnum
from typing import Any

# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


class NotificationEvent(StrEnum):
    # Academic progress
    GRADE_PUBLISHED = "grade.published"
    GRADE_UPDATED = "grade.updated"

    # Course activity
    ANNOUNCEMENT_CREATED = "announcement.created"
    MATERIAL_UPLOADED = "material.uploaded"
    TASK_CREATED = "task.created"

    # Enrollment
    ENROLLMENT_CONFIRMED = "enrollment.confirmed"
    ENROLLMENT_DROPPED = "enrollment.dropped"

    # Scheduling
    CLASS_SESSION_REMINDER = "class_session.reminder"
    CLASS_SESSION_CANCELLED = "class_session.cancelled"
    CLASS_SESSION_RESCHEDULED = "class_session.rescheduled"

    # Administration
    ADMIN_BROADCAST = "admin.broadcast"

    # Auth / Account
    WELCOME = "auth.welcome"
    PASSWORD_RESET_REQUESTED = "auth.password_reset_requested"
    PASSWORD_CHANGED = "auth.password_changed"


# Type alias — the arbitrary kwargs dict passed to emit()
EventPayload = dict[str, Any]
