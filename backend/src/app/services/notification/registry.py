"""
Event registry — maps every NotificationEvent to:
  - Which channels to fan out to.
  - A render() callable that turns the emit() kwargs into (title, body).

Design rules:
  - No I/O here. Render functions are pure string transformations.
  - Use the most specific channel set that makes sense for each event.
    Not everything needs SMS ($$); not everything needs in-app.
  - render() should be defensive: use .get() with sensible defaults so a
    missing kwarg never raises a KeyError in production.

To add a new event:
  1. Add it to events.py.
  2. Add an EventConfig here with channels + render.
  That's it — the emitter and task dispatcher pick it up automatically.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.models.notification import NotificationChannel
from app.services.notification.events import EventPayload, NotificationEvent

# ---------------------------------------------------------------------------
# Config dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EventConfig:
    """Routing + rendering config for a single event type."""

    channels: tuple[NotificationChannel, ...]
    render: Callable[[EventPayload], tuple[str, str]]
    """render(payload) → (title, body)"""


# ---------------------------------------------------------------------------
# Channel presets  (shorthand for the registry table below)
# ---------------------------------------------------------------------------

_ALL = (
    NotificationChannel.INAPP,
    NotificationChannel.EMAIL,
    NotificationChannel.PUSH,
    NotificationChannel.SMS,
)
_NO_SMS = (
    NotificationChannel.INAPP,
    NotificationChannel.EMAIL,
    NotificationChannel.PUSH,
)
_INAPP_EMAIL = (
    NotificationChannel.INAPP,
    NotificationChannel.EMAIL,
)
_EMAIL_ONLY = (NotificationChannel.EMAIL,)
_INAPP_PUSH = (
    NotificationChannel.INAPP,
    NotificationChannel.PUSH,
)

# ---------------------------------------------------------------------------
# Render functions  (pure; no I/O)
# ---------------------------------------------------------------------------


def _grade_published(p: EventPayload) -> tuple[str, str]:
    course = p.get("course_name", "your course")
    grade = p.get("grade", "N/A")
    score = p.get("score")
    detail = f" (score: {score})" if score is not None else ""
    return (
        "Grade Published",
        f"Your grade for {course} has been published: {grade}{detail}.",
    )


def _grade_updated(p: EventPayload) -> tuple[str, str]:
    course = p.get("course_name", "your course")
    grade = p.get("grade", "N/A")
    return (
        "Grade Updated",
        f"Your grade for {course} has been updated to {grade}.",
    )


def _announcement_created(p: EventPayload) -> tuple[str, str]:
    course = p.get("course_name", "your course")
    ann_title = p.get("announcement_title", "New announcement")
    return (
        f"New Announcement: {ann_title}",
        f"A new announcement has been posted for {course}: \"{ann_title}\".",
    )


def _material_uploaded(p: EventPayload) -> tuple[str, str]:
    course = p.get("course_name", "your course")
    filename = p.get("filename", "a new file")
    return (
        f"New Material: {course}",
        f"New course material has been uploaded for {course}: {filename}.",
    )


def _task_created(p: EventPayload) -> tuple[str, str]:
    course = p.get("course_name", "your course")
    task_title = p.get("task_title", "a new task")
    return (
        f"New Task: {course}",
        f"A new task '{task_title}' has been assigned for {course}.",
    )


def _enrollment_confirmed(p: EventPayload) -> tuple[str, str]:
    course = p.get("course_name", "a course")
    return (
        "Enrollment Confirmed",
        f"You have been successfully enrolled in {course}.",
    )


def _enrollment_dropped(p: EventPayload) -> tuple[str, str]:
    course = p.get("course_name", "a course")
    return (
        "Enrollment Dropped",
        f"You have been removed from {course}.",
    )


def _class_reminder(p: EventPayload) -> tuple[str, str]:
    course = p.get("course_name", "your class")
    start_time = p.get("start_time", "soon")
    venue = p.get("venue", "TBD")
    return (
        f"Class Reminder: {course}",
        f"Your {course} class starts at {start_time} in {venue}. Don't be late!",
    )


def _class_cancelled(p: EventPayload) -> tuple[str, str]:
    course = p.get("course_name", "your class")
    reason = p.get("reason")
    detail = f" Reason: {reason}." if reason else ""
    return (
        f"Class Cancelled: {course}",
        f"Your {course} class scheduled for today has been cancelled.{detail}",
    )


def _class_rescheduled(p: EventPayload) -> tuple[str, str]:
    course = p.get("course_name", "your class")
    new_time = p.get("new_time", "a new time")
    venue = p.get("venue", "TBD")
    return (
        f"Class Rescheduled: {course}",
        f"Your {course} class has been rescheduled to {new_time} in {venue}.",
    )


def _admin_broadcast(p: EventPayload) -> tuple[str, str]:
    title = str(p.get("title", "Important Announcement"))
    message = str(p.get("message", ""))
    return title, message


def _welcome(p: EventPayload) -> tuple[str, str]:
    name = p.get("first_name", "there")
    return (
        "Welcome to AMS!",
        (
            f"Hi {name}, your account has been created successfully. "
            "Welcome to the Academic Management System."
        ),
    )


def _password_reset_requested(p: EventPayload) -> tuple[str, str]:
    token = p.get("reset_token", "")
    return (
        "Password Reset Request",
        (
            f"A password reset was requested for your account. "
            f"Use this token to reset your password: {token}\n\n"
            "If you did not request this, ignore this message."
        ),
    )


def _password_changed(p: EventPayload) -> tuple[str, str]:
    return (
        "Password Changed",
        (
            "Your account password was successfully changed. "
            "If you did not make this change, contact support immediately."
        ),
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

EVENT_REGISTRY: dict[NotificationEvent, EventConfig] = {
    NotificationEvent.GRADE_PUBLISHED: EventConfig(
        channels=_ALL,
        render=_grade_published,
    ),
    NotificationEvent.GRADE_UPDATED: EventConfig(
        channels=_NO_SMS,
        render=_grade_updated,
    ),
    NotificationEvent.ANNOUNCEMENT_CREATED: EventConfig(
        channels=_NO_SMS,
        render=_announcement_created,
    ),
    NotificationEvent.MATERIAL_UPLOADED: EventConfig(
        channels=_INAPP_PUSH,
        render=_material_uploaded,
    ),
    NotificationEvent.TASK_CREATED: EventConfig(
        channels=_ALL,
        render=_task_created,
    ),
    NotificationEvent.ENROLLMENT_CONFIRMED: EventConfig(
        channels=_ALL,
        render=_enrollment_confirmed,
    ),
    NotificationEvent.ENROLLMENT_DROPPED: EventConfig(
        channels=_INAPP_EMAIL,
        render=_enrollment_dropped,
    ),
    NotificationEvent.CLASS_SESSION_REMINDER: EventConfig(
        channels=_ALL,
        render=_class_reminder,
    ),
    NotificationEvent.CLASS_SESSION_CANCELLED: EventConfig(
        channels=_ALL,
        render=_class_cancelled,
    ),
    NotificationEvent.CLASS_SESSION_RESCHEDULED: EventConfig(
        channels=_ALL,
        render=_class_rescheduled,
    ),
    NotificationEvent.ADMIN_BROADCAST: EventConfig(
        channels=_ALL,
        render=_admin_broadcast,
    ),
    NotificationEvent.WELCOME: EventConfig(
        channels=_EMAIL_ONLY,
        render=_welcome,
    ),
    NotificationEvent.PASSWORD_RESET_REQUESTED: EventConfig(
        channels=_EMAIL_ONLY,
        render=_password_reset_requested,
    ),
    NotificationEvent.PASSWORD_CHANGED: EventConfig(
        channels=_INAPP_EMAIL,
        render=_password_changed,
    ),
}
