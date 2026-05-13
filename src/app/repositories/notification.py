"""
Repositories for the notification subsystem.

Two classes:
  - NotificationRepository   — CRUD + queries for Notification rows.
  - DeviceTokenRepository    — CRUD + queries for UserDeviceToken rows.

Rules (same as BaseRepository):
  - Zero business logic. Pure DB access only.
  - Always select() + session.scalars(). Never Session.query().
  - No raw SQL.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import func, select, update

from app.models.notification import (
    Notification,
    NotificationChannel,
    NotificationStatus,
    UserDeviceToken,
)
from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Notification, session)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        channel: NotificationChannel = NotificationChannel.INAPP,
        unread_only: bool = False,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Notification], int]:
        """Return a paginated list of a user's notifications for one channel."""
        base_q = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.channel == channel)
        )
        if unread_only:
            base_q = base_q.where(Notification.status != NotificationStatus.READ)

        total = int(
            await self._session.scalar(
                select(func.count()).select_from(base_q.subquery())
            )
            or 0
        )
        rows = await self._session.scalars(
            base_q.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
        )
        return rows.all(), total

    async def count_unread(self, user_id: uuid.UUID) -> int:
        """Return the number of unread in-app notifications for a user."""
        result = await self._session.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.channel == NotificationChannel.INAPP)
            .where(Notification.status != NotificationStatus.READ)
        )
        return int(result or 0)

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    async def mark_read(
        self,
        notification_ids: list[uuid.UUID],
        user_id: uuid.UUID,
    ) -> int:
        """Mark specific notifications as READ. Returns rows updated.

        Scoped to ``user_id`` so users cannot mark other users' notifications.
        Idempotent: already-read rows are ignored.
        """
        result = await self._session.execute(
            update(Notification)
            .where(Notification.id.in_(notification_ids))
            .where(Notification.user_id == user_id)
            .where(Notification.status != NotificationStatus.READ)
            .values(
                status=NotificationStatus.READ,
                read_at=datetime.now(timezone.utc),
            )
        )
        return result.rowcount  # type: ignore[return-value]

    async def mark_all_read(self, user_id: uuid.UUID) -> int:
        """Mark every unread in-app notification for a user as READ."""
        result = await self._session.execute(
            update(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.channel == NotificationChannel.INAPP)
            .where(Notification.status != NotificationStatus.READ)
            .values(
                status=NotificationStatus.READ,
                read_at=datetime.now(timezone.utc),
            )
        )
        return result.rowcount  # type: ignore[return-value]

    async def mark_sent(
        self,
        notification_id: uuid.UUID,
        *,
        sent_at: datetime | None = None,
    ) -> None:
        """Transition a notification to SENT status."""
        await self._session.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(
                status=NotificationStatus.SENT,
                sent_at=sent_at or datetime.now(timezone.utc),
            )
        )

    async def mark_failed(
        self,
        notification_id: uuid.UUID,
        reason: str,
    ) -> None:
        """Transition a notification to FAILED status with a reason."""
        await self._session.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(
                status=NotificationStatus.FAILED,
                failed_at=datetime.now(timezone.utc),
                failure_reason=reason[:500],
            )
        )


class DeviceTokenRepository(BaseRepository[UserDeviceToken]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(UserDeviceToken, session)

    async def get_active_tokens(
        self,
        user_id: uuid.UUID,
    ) -> Sequence[UserDeviceToken]:
        """Return all active device tokens for a user."""
        rows = await self._session.scalars(
            select(UserDeviceToken)
            .where(UserDeviceToken.user_id == user_id)
            .where(UserDeviceToken.is_active.is_(True))
        )
        return rows.all()

    async def upsert(
        self,
        user_id: uuid.UUID,
        token: str,
        platform: str,
    ) -> UserDeviceToken:
        """Insert or reactivate a device token.

        If the token string already exists (possibly for another user,
        e.g. after re-install), it is reassigned to the current user.
        """
        existing = await self._session.scalar(
            select(UserDeviceToken).where(UserDeviceToken.token == token)
        )
        if existing is not None:
            return await self.update(
                existing,
                user_id=user_id,
                platform=platform,
                is_active=True,
            )
        return await self.create(
            user_id=user_id,
            token=token,
            platform=platform,
            is_active=True,
        )

    async def deactivate(self, token: str) -> None:
        """Soft-delete a device token (is_active → False).

        Called when a push delivery returns UNREGISTERED / 410 Gone.
        """
        existing = await self._session.scalar(
            select(UserDeviceToken).where(UserDeviceToken.token == token)
        )
        if existing is not None:
            await self.update(existing, is_active=False)
