# src/app/repositories/notification.py
from __future__ import annotations

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification

class NotificationRepository:
    """Repository for managing Notification models."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_user(
        self, user_id: uuid.UUID, read: bool | None = None, page: int = 1, limit: int = 50
    ) -> tuple[int, list[Notification]]:
        """List notifications for a matching user optionally filtered by read status."""
        query = select(Notification).where(Notification.user_id == user_id)
        if read is not None:
            query = query.where(Notification.read == read)

        # Get count
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        # Get results
        offset = (page - 1) * limit
        results = await self.session.scalars(
            query.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
        )
        return total, list(results.all())

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        from sqlalchemy import func
        query = select(func.count(Notification.id)).where(
            Notification.user_id == user_id, Notification.read == False  # noqa: E712
        )
        return await self.session.scalar(query) or 0

    async def get_by_id(self, user_id: uuid.UUID, notification_id: uuid.UUID) -> Notification | None:
        query = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        return await self.session.scalar(query)

    async def mark_read(self, notification: Notification) -> Notification:
        notification.read = True
        await self.session.flush()
        return notification

    async def create(
        self, user_id: uuid.UUID, message: str, type: str, link: str | None = None
    ) -> Notification:
        notification = Notification(user_id=user_id, message=message, type=type, link=link)
        self.session.add(notification)
        await self.session.flush()
        return notification
