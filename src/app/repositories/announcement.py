"""Repository for Announcement model."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select

from app.models.announcement import Announcement, AnnouncementView
from app.repositories.base import BaseRepository


class AnnouncementRepository(BaseRepository[Announcement]):
    def __init__(self, session) -> None:
        super().__init__(model=Announcement, session=session)

    async def list_by_offering(
        self, offering_id: uuid.UUID, pinned_only: bool = False
    ) -> Sequence[Announcement]:
        query = select(Announcement).where(Announcement.offering_id == offering_id)
        if pinned_only:
            query = query.where(Announcement.pinned.is_(True))
        query = query.order_by(Announcement.created_at.desc())
        result = await self._session.scalars(query)
        return result.all()


class AnnouncementViewRepository(BaseRepository[AnnouncementView]):
    def __init__(self, session) -> None:
        super().__init__(model=AnnouncementView, session=session)

    async def get_by_student_and_announcement(
        self, student_id: uuid.UUID, announcement_id: uuid.UUID
    ) -> AnnouncementView | None:
        query = select(AnnouncementView).where(
            AnnouncementView.student_id == student_id,
            AnnouncementView.announcement_id == announcement_id,
        )
        result = await self._session.scalars(query)
        return result.first()

