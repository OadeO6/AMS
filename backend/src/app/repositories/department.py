# src/app/repositories/department.py
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models.department import Department
from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession


class DepartmentRepository(BaseRepository[Department]):
    """Async repository for the `departments` table."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Department, session)

    async def get_by_code(self, code: str) -> Department | None:
        result = await self._session.scalars(
            select(Department).where(Department.code == code).limit(1)
        )
        return result.first()

    async def list_by_faculty(self, faculty_id: uuid.UUID) -> Sequence[Department]:
        result = await self._session.scalars(
            select(Department).where(Department.faculty_id == faculty_id)
        )
        return result.all()
