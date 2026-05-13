"""Repositories for ClassSession and Attendance models."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import and_, select

from app.models.class_session import Attendance, ClassSession
from app.repositories.base import BaseRepository


class ClassSessionRepository(BaseRepository[ClassSession]):
    def __init__(self, session) -> None:
        super().__init__(model=ClassSession, session=session)

    async def list_by_offering(self, offering_id: uuid.UUID) -> Sequence[ClassSession]:
        result = await self._session.scalars(
            select(ClassSession)
            .where(ClassSession.offering_id == offering_id)
            .order_by(ClassSession.scheduled_at)
        )
        return result.all()


class AttendanceRepository(BaseRepository[Attendance]):
    def __init__(self, session) -> None:
        super().__init__(model=Attendance, session=session)

    async def list_by_session(self, session_id: uuid.UUID) -> Sequence[Attendance]:
        result = await self._session.scalars(
            select(Attendance).where(Attendance.session_id == session_id)
        )
        return result.all()

    async def get_by_student_and_session(
        self, student_id: uuid.UUID, session_id: uuid.UUID
    ) -> Attendance | None:
        return await self._session.scalar(
            select(Attendance).where(
                and_(Attendance.student_id == student_id, Attendance.session_id == session_id)
            )
        )

    async def upsert_attendance(
        self,
        session_id: uuid.UUID,
        student_id: uuid.UUID,
        status: str,
        marked_by: uuid.UUID,
    ) -> Attendance:
        existing = await self.get_by_student_and_session(student_id, session_id)
        if existing:
            return await self.update(
                existing, status=status, marked_at=datetime.now(UTC), marked_by=marked_by
            )
        return await self.create(
            session_id=session_id,
            student_id=student_id,
            status=status,
            marked_at=datetime.now(UTC),
            marked_by=marked_by,
        )
