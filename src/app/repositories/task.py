"""Repositories for Task, Question, Submission, and Answer models."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import and_, select

from app.models.task import Answer, Question, Submission, Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session) -> None:
        super().__init__(model=Task, session=session)

    async def list_by_offering(self, offering_id: uuid.UUID) -> Sequence[Task]:
        result = await self._session.scalars(
            select(Task).where(Task.offering_id == offering_id).order_by(Task.due_date)
        )
        return result.all()


class QuestionRepository(BaseRepository[Question]):
    def __init__(self, session) -> None:
        super().__init__(model=Question, session=session)

    async def list_by_task(self, task_id: uuid.UUID) -> Sequence[Question]:
        result = await self._session.scalars(select(Question).where(Question.task_id == task_id))
        return result.all()


class SubmissionRepository(BaseRepository[Submission]):
    def __init__(self, session) -> None:
        super().__init__(model=Submission, session=session)

    async def list_by_task(
        self, task_id: uuid.UUID, graded: bool | None = None
    ) -> Sequence[Submission]:
        query = select(Submission).where(Submission.task_id == task_id)
        if graded is True:
            query = query.where(Submission.grading_status != "ungraded")
        elif graded is False:
            query = query.where(Submission.grading_status == "ungraded")
        result = await self._session.scalars(query)
        return result.all()

    async def get_by_student_and_task(
        self, student_id: uuid.UUID, task_id: uuid.UUID
    ) -> Submission | None:
        return await self._session.scalar(
            select(Submission).where(
                and_(Submission.student_id == student_id, Submission.task_id == task_id)
            )
        )

    async def list_ai_draft(self, task_id: uuid.UUID) -> Sequence[Submission]:
        result = await self._session.scalars(
            select(Submission).where(
                and_(Submission.task_id == task_id, Submission.grading_status == "ai_draft")
            )
        )
        return result.all()


class AnswerRepository(BaseRepository[Answer]):
    def __init__(self, session) -> None:
        super().__init__(model=Answer, session=session)

    async def list_by_submission(self, submission_id: uuid.UUID) -> Sequence[Answer]:
        result = await self._session.scalars(
            select(Answer).where(Answer.submission_id == submission_id)
        )
        return result.all()
