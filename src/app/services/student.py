"""Business logic for Student-facing operations.

Enforces:
- Registration: student must be an approved registrant in the offering
- Visibility: materials must be students_only or both
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.models.announcement import Announcement, AnnouncementView
from app.models.class_session import Attendance, ClassSession
from app.models.course import CourseRegistration
from app.models.gradebook import GradebookEntry
from app.models.material import Material
from app.models.task import Answer, Question, Submission, Task
from app.models.user import User
from app.repositories.announcement import AnnouncementRepository, AnnouncementViewRepository
from app.repositories.course import CourseOfferingRepository, CourseRegistrationRepository
from app.repositories.gradebook import GradebookRepository
from app.repositories.material import MaterialRepository
from app.repositories.session import AttendanceRepository, ClassSessionRepository
from app.repositories.task import AnswerRepository, QuestionRepository, SubmissionRepository, TaskRepository


class StudentService:
    """Orchestrates all student domain logic."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.offering_repo = CourseOfferingRepository(session)
        self.registration_repo = CourseRegistrationRepository(session)
        self.material_repo = MaterialRepository(session)
        self.session_repo = ClassSessionRepository(session)
        self.attendance_repo = AttendanceRepository(session)
        self.announcement_repo = AnnouncementRepository(session)
        self.announcement_view_repo = AnnouncementViewRepository(session)
        self.task_repo = TaskRepository(session)
        self.question_repo = QuestionRepository(session)
        self.submission_repo = SubmissionRepository(session)
        self.answer_repo = AnswerRepository(session)
        self.gradebook_repo = GradebookRepository(session)

    # -----------------------------------------------------------------------
    # Guard helpers
    # -----------------------------------------------------------------------

    async def _ensure_registered_and_approved(
        self, student: User, offering_id: uuid.UUID
    ) -> CourseRegistration:
        """Return the registration if the student is approved for this offering."""
        offering = await self.offering_repo.get_by_id(offering_id)
        if not offering:
            raise NotFoundError("Course offering not found")

        reg = await self.registration_repo.get_by_student_and_offering(student.id, offering_id)
        if not reg or reg.status != "approved":
            raise ForbiddenError("You are not an approved student for this course offering")
        return reg

    # -----------------------------------------------------------------------
    # Materials
    # -----------------------------------------------------------------------

    async def list_materials(
        self, student: User, offering_id: uuid.UUID, type_: str | None = None
    ) -> Sequence[Material]:
        """List materials that are visible to students."""
        await self._ensure_registered_and_approved(student, offering_id)

        query = select(Material).where(
            Material.offering_id == offering_id,
            Material.visibility.in_(["students_only", "both"])
        )
        if type_:
            query = query.where(Material.type == type_)
        query = query.order_by(Material.created_at.desc())

        result = await self._session.scalars(query)
        return result.all()

    # -----------------------------------------------------------------------
    # Tasks & Submissions
    # -----------------------------------------------------------------------

    async def list_tasks(
        self, student: User, offering_id: uuid.UUID, status: str | None = None
    ) -> Sequence[Task]:
        """List all tasks for the offering."""
        await self._ensure_registered_and_approved(student, offering_id)
        # Note: In a complete implementation, 'status' filtering (upcoming, ungraded etc)
        # requires complex joins with Submission. For now we fetch all tasks.
        return await self.task_repo.list_by_offering(offering_id)

    async def get_task(
        self, student: User, offering_id: uuid.UUID, task_id: uuid.UUID
    ) -> dict:
        """Get a single task along with its questions."""
        await self._ensure_registered_and_approved(student, offering_id)
        task = await self.task_repo.get_by_id(task_id)
        if not task or task.offering_id != offering_id:
            raise NotFoundError("Task not found")
        
        questions = await self.question_repo.list_by_task(task_id)
        
        response_data = {
            "id": task.id,
            "offering_id": task.offering_id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date,
            "ai_grading": task.ai_grading,
            "marking_guide_url": task.marking_guide_url,
            "created_at": task.created_at,
            "questions": questions
        }
        return response_data

    async def submit_task(
        self, student: User, offering_id: uuid.UUID, task_id: uuid.UUID, answers_data: list[dict]
    ) -> Submission:
        """Submit answers for a task."""
        await self._ensure_registered_and_approved(student, offering_id)
        task = await self.task_repo.get_by_id(task_id)
        if not task or task.offering_id != offering_id:
            raise NotFoundError("Task not found")

        if datetime.now(UTC) > task.due_date:
            raise ValidationError("Task submission deadline has passed")

        # Ensure no existing submission
        existing = await self._session.scalars(
            select(Submission).where(
                Submission.task_id == task_id,
                Submission.student_id == student.id
            )
        )
        if existing.first():
            raise ValidationError("You have already submitted this task")

        # Create submission
        grading_status = "ai_draft" if task.ai_grading else "ungraded"
        sub = await self.submission_repo.create(
            task_id=task_id,
            student_id=student.id,
            submitted_at=datetime.now(UTC),
            grading_status=grading_status
        )

        for ans in answers_data:
            await self.answer_repo.create(
                submission_id=sub.id,
                question_id=uuid.UUID(ans["question_id"]),
                selected_option=ans.get("selected_option"),
                text_answer=ans.get("text_answer"),
                file_url=ans.get("file_url")
            )
            
        return sub

    # -----------------------------------------------------------------------
    # Grades
    # -----------------------------------------------------------------------

    async def get_grades(
        self, student: User, offering_id: uuid.UUID
    ) -> dict:
        """Fetch all graded submissions and overall gradebook entry."""
        await self._ensure_registered_and_approved(student, offering_id)
        
        # Submissions that are finalized
        query = select(Submission).join(Task).where(
            Task.offering_id == offering_id,
            Submission.student_id == student.id,
            Submission.grading_status.in_(["ai_approved", "manually_graded"])
        )
        submissions = (await self._session.scalars(query)).all()
        
        gradebook_entry = await self.gradebook_repo.get_by_student_and_offering(student.id, offering_id)
        
        return {
            "submissions": submissions,
            "gradebook": gradebook_entry
        }

    # -----------------------------------------------------------------------
    # Announcements
    # -----------------------------------------------------------------------

    async def list_announcements(
        self, student: User, offering_id: uuid.UUID, pinned_only: bool = False
    ) -> Sequence[Announcement]:
        """List announcements."""
        await self._ensure_registered_and_approved(student, offering_id)
        return await self.announcement_repo.list_by_offering(offering_id, pinned_only)

    async def get_announcement(
        self, student: User, offering_id: uuid.UUID, announcement_id: uuid.UUID
    ) -> Announcement:
        """Get a single announcement."""
        await self._ensure_registered_and_approved(student, offering_id)
        ann = await self.announcement_repo.get_by_id(announcement_id)
        if not ann or ann.offering_id != offering_id:
            raise NotFoundError("Announcement not found")
        return ann

    async def mark_announcement_viewed(
        self, student: User, offering_id: uuid.UUID, announcement_id: uuid.UUID
    ) -> None:
        """Mark an announcement as read."""
        await self._ensure_registered_and_approved(student, offering_id)
        ann = await self.announcement_repo.get_by_id(announcement_id)
        if not ann or ann.offering_id != offering_id:
            raise NotFoundError("Announcement not found")
            
        view = await self.announcement_view_repo.get_by_student_and_announcement(student.id, announcement_id)
        if not view:
            await self.announcement_view_repo.create(
                announcement_id=announcement_id,
                student_id=student.id,
                viewed_at=datetime.now(UTC)
            )

    # -----------------------------------------------------------------------
    # Class Sessions
    # -----------------------------------------------------------------------

    async def list_sessions(
        self, student: User, offering_id: uuid.UUID, status: str | None = None
    ) -> Sequence[ClassSession]:
        """List class sessions."""
        await self._ensure_registered_and_approved(student, offering_id)
        query = select(ClassSession).where(ClassSession.offering_id == offering_id)
        if status:
            query = query.where(ClassSession.status == status)
        query = query.order_by(ClassSession.scheduled_at.asc())
        return (await self._session.scalars(query)).all()

    async def get_session(
        self, student: User, offering_id: uuid.UUID, session_id: uuid.UUID
    ) -> dict:
        """Get session details and specific attendance for the student."""
        await self._ensure_registered_and_approved(student, offering_id)
        sess = await self.session_repo.get_by_id(session_id)
        if not sess or sess.offering_id != offering_id:
            raise NotFoundError("Session not found")
            
        att = await self._session.scalars(
            select(Attendance).where(
                Attendance.session_id == session_id,
                Attendance.student_id == student.id
            )
        )
        return {
            "session": sess,
            "attendance": att.first()
        }

    async def get_attendance(
        self, student: User, offering_id: uuid.UUID
    ) -> Sequence[Attendance]:
        """Get all attendance records for the student in this offering."""
        await self._ensure_registered_and_approved(student, offering_id)
        query = select(Attendance).join(ClassSession).where(
            ClassSession.offering_id == offering_id,
            Attendance.student_id == student.id
        )
        return (await self._session.scalars(query)).all()
