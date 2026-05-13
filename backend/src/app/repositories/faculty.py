# src/app/repositories/faculty.py
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models.faculty import Faculty
from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class FacultyRepository(BaseRepository[Faculty]):
    """Async repository for the `faculties` table."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Faculty, session)

    async def get_by_code(self, code: str) -> Faculty | None:
        result = await self._session.scalars(select(Faculty).where(Faculty.code == code).limit(1))
        return result.first()
