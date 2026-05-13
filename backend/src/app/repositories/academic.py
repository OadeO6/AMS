# src/app/repositories/academic.py
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.academic_session import AcademicSession, Semester
from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession


class AcademicSessionRepository(BaseRepository[AcademicSession]):
    """Async repository for the `academic_sessions` table."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AcademicSession, session)

    async def get_by_name(self, name: str) -> AcademicSession | None:
        result = await self._session.scalars(
            select(AcademicSession).where(AcademicSession.name == name).limit(1)
        )
        return result.first()

    async def get_with_semesters(self, session_id: uuid.UUID) -> AcademicSession | None:
        """Returns the session with its semesters eagerness-loaded."""
        result = await self._session.scalars(
            select(AcademicSession)
            .options(selectinload(AcademicSession.semesters))
            .where(AcademicSession.id == session_id)
            .limit(1)
        )
        return result.first()

    async def list_all_with_semesters(self) -> Sequence[AcademicSession]:
        """Returns all sessions eagerly loading their semesters."""
        result = await self._session.scalars(
            select(AcademicSession)
            .options(selectinload(AcademicSession.semesters))
            .order_by(AcademicSession.name.desc())
        )
        return result.all()


class SemesterRepository(BaseRepository[Semester]):
    """Async repository for the `semesters` table."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Semester, session)

    async def deactivate_all(self) -> None:
        """Ensure no semester is globally active."""
        stmt = update(Semester).where(Semester.is_active == True).values(is_active=False)
        await self._session.execute(stmt)
        await self._session.flush()

    async def get_active_semester(self) -> Semester | None:
        """Returns the globally active semester."""
        result = await self._session.scalars(
            select(Semester).where(Semester.is_active == True).limit(1)
        )
        return result.first()

    async def activate(self, semester_id: uuid.UUID) -> Semester | None:
        """Activate the specified semester and deactivate all others."""
        await self.deactivate_all()

        # Now activate the specified one
        semester = await self.get_by_id(semester_id)
        if semester:
            semester.is_active = True
            await self._session.flush()
        return semester
