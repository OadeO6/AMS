"""Repository for GradebookEntry model."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import and_, select

from app.models.gradebook import GradebookEntry
from app.repositories.base import BaseRepository


class GradebookRepository(BaseRepository[GradebookEntry]):
    def __init__(self, session) -> None:
        super().__init__(model=GradebookEntry, session=session)

    async def list_by_offering(self, offering_id: uuid.UUID) -> Sequence[GradebookEntry]:
        result = await self._session.scalars(
            select(GradebookEntry).where(GradebookEntry.offering_id == offering_id)
        )
        return result.all()

    async def get_by_student_and_offering(
        self, student_id: uuid.UUID, offering_id: uuid.UUID
    ) -> GradebookEntry | None:
        return await self._session.scalar(
            select(GradebookEntry).where(
                and_(
                    GradebookEntry.student_id == student_id,
                    GradebookEntry.offering_id == offering_id,
                )
            )
        )
