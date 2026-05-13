"""
ORM models for the notification subsystem.

Two tables:
  - ``notifications``      — one row per channel per emit() call.
  - ``user_device_tokens`` — FCM / Web Push registration tokens.

Rules (same as every model in this codebase):
  - Mapped[T] + mapped_column() only. Never Column().
  - TimestampMixin on every table.
  - Back-references use lazy="noload" to prevent silent N+1 queries.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class NotificationChannel(StrEnum):
    """Supported delivery channels for a single notification record."""

    INAPP = "inapp"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"


class NotificationStatus(StrEnum):
    """Lifecycle status of one notification delivery attempt."""

    PENDING = "pending"  # queued, not yet attempted
    SENT = "sent"        # successfully handed off to the channel
    FAILED = "failed"    # delivery errored after all retries
    READ = "read"        # user opened it — in-app channel only


class Notification(Base, TimestampMixin):
    """One delivery record per channel per emit() call.

    A single ``NotificationEmitter.emit()`` produces N rows — one per channel
    enabled for that event. This gives a full per-channel audit trail and
    lets the front-end query only ``channel='inapp'`` rows.
    """

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Surrogate PK — UUID generated application-side.",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Owner of this notification.",
    )

    # --- Event identity ---------------------------------------------------
    event: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Dot-notated event name, e.g. 'grade.published'.",
    )
    channel: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Which channel delivered this record (NotificationChannel value).",
    )

    # --- Rendered content -------------------------------------------------
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Short human-readable title for toasts / push titles.",
    )
    body: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Full notification body text.",
    )
    data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        doc="Arbitrary JSON forwarded to the client for deep-linking / context.",
    )

    # --- Lifecycle --------------------------------------------------------
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=NotificationStatus.PENDING,
        index=True,
        doc="Current delivery status (NotificationStatus value).",
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the user read this notification (in-app only).",
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the channel confirmed delivery.",
    )
    failed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp of the final failed attempt.",
    )
    failure_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Last error message truncated to 500 chars.",
    )

    # --- Relationships ----------------------------------------------------
    user: Mapped[User] = relationship(
        back_populates="notifications",
        lazy="noload",
    )


class UserDeviceToken(Base, TimestampMixin):
    """FCM / Web Push (VAPID) registration tokens for a user's devices.

    One user may have many active tokens (multiple browsers / devices).
    Tokens are automatically deactivated when a push delivery returns an
    UNREGISTERED / 410 Gone response from the upstream service.
    """

    __tablename__ = "user_device_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
        doc="Raw FCM registration token OR JSON-serialised Web Push subscription.",
    )
    platform: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="'fcm' for Firebase Cloud Messaging; 'web' for VAPID Web Push.",
    )
    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
        doc="False once the token is known to be stale / unregistered.",
    )

    # --- Relationships ----------------------------------------------------
    user: Mapped[User] = relationship(
        back_populates="device_tokens",
        lazy="noload",
    )
