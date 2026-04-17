"""Repository for Material model."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select

from app.models.material import Material
from app.repositories.base import BaseRepository


class MaterialRepository(BaseRepository[Material]):
    def __init__(self, session) -> None:
        super().__init__(model=Material, session=session)

    async def list_by_offering(self, offering_id: uuid.UUID) -> Sequence[Material]:
        result = await self._session.scalars(
            select(Material)
            .where(Material.offering_id == offering_id)
            .order_by(Material.created_at)
        )
        return result.all()
