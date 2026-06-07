"""Business logic for Lecturer-facing operations.

Enforces:
- Offering access: lecturer must be assigned to the offering (offering.lecturer_id == lecturer.id)
- Session ownership: only the creating lecturer may edit/cancel/mark attendance
- Material indexing: students_only materials cannot be indexed
- AI grading: requires marking_guide_url to be set first
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.models.announcement import Announcement
from app.models.class_session import Attendance, ClassSession
from app.models.course import CourseOffering
from app.models.gradebook import GradebookEntry
from app.models.material import Material
from app.models.task import Question, Submission, Task
from app.models.user import User
from app.repositories.announcement import AnnouncementRepository
from app.repositories.course import CourseRepository
from app.repositories.course import CourseOfferingRepository, CourseRegistrationRepository, OfferingLecturerRepository
from app.repositories.department import DepartmentRepository
from app.repositories.gradebook import GradebookRepository
from app.repositories.material import MaterialRepository
from app.repositories.session import AttendanceRepository, ClassSessionRepository
from app.repositories.task import (
    AnswerRepository,
    QuestionRepository,
    SubmissionRepository,
    TaskRepository,
)
from app.repositories.user import UserRepository
from app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate
from app.schemas.material import MaterialCreate, MaterialUpdate
from app.schemas.session import AttendanceMarkRequest, ClassSessionCreate, ClassSessionUpdate
from app.schemas.task import (
    GradeSubmissionRequest,
    QuestionCreate,
    QuestionUpdate,
    TaskCreate,
    TaskUpdate,
)


class LecturerService:
    """Orchestrates all lecturer domain logic."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.offering_repo = CourseOfferingRepository(session)
        self.offering_lecturer_repo = OfferingLecturerRepository(session)
        self.course_repo = CourseRepository(session)
        self.department_repo = DepartmentRepository(session)
        self.registration_repo = CourseRegistrationRepository(session)
        self.material_repo = MaterialRepository(session)
        self.session_repo = ClassSessionRepository(session)
        self.attendance_repo = AttendanceRepository(session)
        self.announcement_repo = AnnouncementRepository(session)
        self.task_repo = TaskRepository(session)
        self.question_repo = QuestionRepository(session)
        self.submission_repo = SubmissionRepository(session)
        self.answer_repo = AnswerRepository(session)
        self.gradebook_repo = GradebookRepository(session)
        self.user_repo = UserRepository(session)

    # -----------------------------------------------------------------------
    # Guard helpers
    # -----------------------------------------------------------------------

    async def get_assigned_offering(self, lecturer: User, offering_id: uuid.UUID) -> CourseOffering:
        """Return offering only if this lecturer is assigned to it via the junction table."""
        offering = await self.offering_repo.get_by_id(offering_id)
        if not offering:
            raise NotFoundError("Course offering not found")
        row = await self.offering_lecturer_repo.get_by_offering_and_lecturer(
            offering_id, lecturer.id
        )
        if not row:
            raise ForbiddenError("You are not assigned to this offering")
        return offering

    async def get_owned_session(self, lecturer: User, session_id: uuid.UUID) -> ClassSession:
        """Return session only if this lecturer owns it."""
        sess = await self.session_repo.get_by_id(session_id)
        if not sess:
            raise NotFoundError("Class session not found")
        if sess.lecturer_id != lecturer.id:
            raise ForbiddenError("You do not own this session")
        return sess

    # -----------------------------------------------------------------------
    # Courses
    # -----------------------------------------------------------------------

    async def list_courses(self, lecturer: User) -> Sequence[CourseOffering]:
        """List all offerings the lecturer is assigned to (via junction table)."""
        from app.repositories.academic import SemesterRepository
        from app.models.course import OfferingLecturer

        sem_repo = SemesterRepository(self._session)
        active_semester = await sem_repo.get_active_semester()
        if not active_semester:
            return []

        from sqlalchemy import select
        from app.models.course import CourseOffering as CO

        # Join via OfferingLecturer
        result = await self._session.scalars(
            select(CO)
            .join(OfferingLecturer, OfferingLecturer.offering_id == CO.id)
            .where(
                OfferingLecturer.lecturer_id == lecturer.id,
                CO.semester_id == active_semester.id,
            )
        )
        return result.all()

    async def list_course_response(self, lecturer: User) -> dict:
        """Return enriched course list response for lecturer routes."""
        offerings = await self.list_courses(lecturer)
        items = []
        for offering in offerings:
            course = await self.course_repo.get_by_id(offering.course_id)
            department = await self.department_repo.get_by_id(course.department_id) if course else None
            registrations = await self.registration_repo.list_by_offering(offering.id)
            lecturers = []
            for assignment in offering.lecturers:
                assigned = assignment.lecturer
                if assigned:
                    lecturers.append({
                        "id": assigned.id,
                        "name": f"{assigned.first_name} {assigned.last_name}",
                    })

            items.append({
                "id": offering.id,
                "title": course.title if course else "Unknown",
                "code": course.code if course else "Unknown",
                "level": 0,
                "department": department.name if department else None,
                "total_students": len([reg for reg in registrations if reg.status == "approved"]),
                "is_active": offering.is_active,
                "lecturers": lecturers,
            })

        return {
            "courses": items,
            "pagination": {"page": 1, "limit": len(items) if items else 20, "total": len(items)},
        }

    async def get_course(self, lecturer: User, offering_id: uuid.UUID) -> CourseOffering:
        return await self.get_assigned_offering(lecturer, offering_id)

    async def get_course_detail_response(self, lecturer: User, offering_id: uuid.UUID) -> dict:
        """Return enriched course detail response for lecturer routes."""
        offering = await self.get_course(lecturer, offering_id)
        course = await self.course_repo.get_by_id(offering.course_id)
        department = await self.department_repo.get_by_id(course.department_id) if course else None
        registrations = await self.registration_repo.list_by_offering(offering.id)
        sessions = await self.session_repo.list_by_offering(offering.id)
        tasks = await self.task_repo.list_by_offering(offering.id)
        lecturers = []
        for assignment in offering.lecturers:
            assigned = assignment.lecturer
            if assigned:
                lecturers.append({
                    "id": assigned.id,
                    "name": f"{assigned.first_name} {assigned.last_name}",
                })

        return {
            "id": offering.id,
            "title": course.title if course else "Unknown",
            "code": course.code if course else "Unknown",
            "level": 0,
            "lecturers": lecturers,
            "description": course.description if course else None,
            "department": department.name if department else None,
            "total_students": len([reg for reg in registrations if reg.status == "approved"]),
            "sessions": len(sessions),
            "tasks_count": len(tasks),
        }

    # -----------------------------------------------------------------------
    # Students
    # -----------------------------------------------------------------------

    async def list_students(self, lecturer: User, offering_id: uuid.UUID):
        await self.get_assigned_offering(lecturer, offering_id)
        return await self.registration_repo.list_by_offering(offering_id)

    async def list_student_response(self, lecturer: User, offering_id: uuid.UUID) -> dict:
        """Return lecturer-facing student list response."""
        registrations = await self.list_students(lecturer, offering_id)
        return {
            "students": [
                {
                    "id": registration.student.id,
                    "first_name": registration.student.first_name,
                    "last_name": registration.student.last_name,
                    "email": registration.student.email,
                    "registration_status": registration.status,
                }
                for registration in registrations
            ]
        }

    async def update_student_registration_status(self, lecturer: User, offering_id: uuid.UUID, student_id: uuid.UUID, status: str):
        await self.get_assigned_offering(lecturer, offering_id)
        reg = await self.registration_repo.get_by_student_and_offering(student_id, offering_id)
        if not reg:
            raise NotFoundError("Student is not registered for this offering")
        return await self.registration_repo.update(reg, status=status)

    # -----------------------------------------------------------------------
    # Materials
    # -----------------------------------------------------------------------

    async def list_materials(self, lecturer: User, offering_id: uuid.UUID) -> Sequence[Material]:
        return await self.material_repo.list_by_offering(offering_id)

    async def create_material(
        self, lecturer: User, offering_id: uuid.UUID, payload: MaterialCreate
    ) -> Material:
        await self.get_assigned_offering(lecturer, offering_id)
        return await self.material_repo.create(
            offering_id=offering_id,
            uploaded_by=lecturer.id,
            title=payload.title,
            type=payload.type.value,
            file_url=payload.file_url,
            visibility=payload.visibility.value,
        )

    async def update_material(
        self,
        lecturer: User,
        offering_id: uuid.UUID,
        material_id: uuid.UUID,
        payload: MaterialUpdate,
    ) -> Material:
        await self.get_assigned_offering(lecturer, offering_id)
        material = await self.material_repo.get_by_id(material_id)
        if not material or material.offering_id != offering_id:
            raise NotFoundError("Material not found")
        updates = payload.model_dump(exclude_none=True)
        if "visibility" in updates:
            updates["visibility"] = updates["visibility"].value
        return await self.material_repo.update(material, **updates)

    async def delete_material(
        self, lecturer: User, offering_id: uuid.UUID, material_id: uuid.UUID
    ) -> None:
        await self.get_assigned_offering(lecturer, offering_id)
        material = await self.material_repo.get_by_id(material_id)
        if not material or material.offering_id != offering_id:
            raise NotFoundError("Material not found")
        await self.material_repo.delete(material)

    async def index_material(
        self, lecturer: User, offering_id: uuid.UUID, material_id: uuid.UUID
    ) -> Material:
        await self.get_assigned_offering(lecturer, offering_id)
        material = await self.material_repo.get_by_id(material_id)
        if not material or material.offering_id != offering_id:
            raise NotFoundError("Material not found")
        if material.visibility == "students_only":
            raise ValidationError("Cannot index a students-only material")
        return await self.material_repo.update(
            material, indexed=True, indexed_at=datetime.now(UTC)
        )

    # -----------------------------------------------------------------------
    # Class Sessions
    # -----------------------------------------------------------------------

    async def create_session(
        self, lecturer: User, offering_id: uuid.UUID, payload: ClassSessionCreate
    ) -> ClassSession:
        await self.get_assigned_offering(lecturer, offering_id)
        return await self.session_repo.create(
            offering_id=offering_id,
            lecturer_id=lecturer.id,
            title=payload.title,
            scheduled_at=payload.scheduled_at,
            venue=payload.venue,
            notes=payload.notes,
            status="upcoming",
        )

    async def update_session(
        self,
        lecturer: User,
        offering_id: uuid.UUID,
        session_id: uuid.UUID,
        payload: ClassSessionUpdate,
    ) -> ClassSession:
        await self.get_assigned_offering(lecturer, offering_id)
        sess = await self.get_owned_session(lecturer, session_id)
        updates = payload.model_dump(exclude_none=True)
        if "status" in updates:
            updates["status"] = updates["status"].value
        return await self.session_repo.update(sess, **updates)

    async def delete_session(
        self, lecturer: User, offering_id: uuid.UUID, session_id: uuid.UUID
    ) -> None:
        await self.get_assigned_offering(lecturer, offering_id)
        sess = await self.get_owned_session(lecturer, session_id)
        await self.session_repo.delete(sess)

    async def list_sessions(self, lecturer: User, offering_id: uuid.UUID) -> Sequence[ClassSession]:
        await self.get_assigned_offering(lecturer, offering_id)
        return await self.session_repo.list_by_offering(offering_id)

    async def get_session(
        self, lecturer: User, offering_id: uuid.UUID, session_id: uuid.UUID
    ) -> tuple[ClassSession, list[dict]]:
        await self.get_assigned_offering(lecturer, offering_id)
        sess = await self.session_repo.get_by_id(session_id)
        if not sess or sess.offering_id != offering_id:
            raise NotFoundError("Session not found")
            
        records = await self.attendance_repo.list_by_session(session_id)
        from app.repositories.user import UserRepository
        u_repo = UserRepository(self._session)
        enriched = []
        for att in records:
            student = await u_repo.get_by_id(att.student_id)
            name = f"{student.first_name} {student.last_name}" if student else "Unknown"
            enriched.append({
                "id": att.id,
                "session_id": att.session_id,
                "student_id": att.student_id,
                "name": name,
                "status": att.status,
                "marked_at": att.marked_at
            })
            
        return sess, enriched

    async def mark_attendance(
        self,
        lecturer: User,
        offering_id: uuid.UUID,
        session_id: uuid.UUID,
        payload: AttendanceMarkRequest,
    ) -> Sequence[Attendance]:
        await self.get_assigned_offering(lecturer, offering_id)
        await self.get_owned_session(lecturer, session_id)
        results = []
        for record in payload.records:
            att = await self.attendance_repo.upsert_attendance(
                session_id=session_id,
                student_id=record.student_id,
                status=record.status.value,
                marked_by=lecturer.id,
            )
            results.append(att)
        return results

    # -----------------------------------------------------------------------
    # Announcements
    # -----------------------------------------------------------------------

    async def create_announcement(
        self, lecturer: User, offering_id: uuid.UUID, payload: AnnouncementCreate
    ) -> Announcement:
        await self.get_assigned_offering(lecturer, offering_id)
        return await self.announcement_repo.create(
            offering_id=offering_id,
            lecturer_id=lecturer.id,
            title=payload.title,
            body=payload.body,
            pinned=payload.pinned,
        )

    async def list_announcements(
        self, lecturer: User, offering_id: uuid.UUID, pinned_only: bool = False
    ) -> Sequence[Announcement]:
        await self.get_assigned_offering(lecturer, offering_id)
        return await self.announcement_repo.list_by_offering(offering_id, pinned_only=pinned_only)

    async def list_announcement_response(
        self, lecturer: User, offering_id: uuid.UUID, pinned_only: bool = False
    ) -> dict:
        """Return lecturer-facing announcement list response."""
        announcements = await self.list_announcements(lecturer, offering_id, pinned_only=pinned_only)
        return {
            "announcements": announcements,
            "pagination": {"page": 1, "limit": len(announcements), "total": len(announcements)},
        }

    async def get_announcement(
        self, lecturer: User, offering_id: uuid.UUID, announcement_id: uuid.UUID
    ) -> Announcement:
        await self.get_assigned_offering(lecturer, offering_id)
        ann = await self.announcement_repo.get_by_id(announcement_id)
        if not ann or ann.offering_id != offering_id:
            raise NotFoundError("Announcement not found")
        return ann

    async def update_announcement(
        self,
        lecturer: User,
        offering_id: uuid.UUID,
        announcement_id: uuid.UUID,
        payload: AnnouncementUpdate,
    ) -> Announcement:
        ann = await self.get_announcement(lecturer, offering_id, announcement_id)
        return await self.announcement_repo.update(ann, **payload.model_dump(exclude_none=True))

    async def delete_announcement(
        self, lecturer: User, offering_id: uuid.UUID, announcement_id: uuid.UUID
    ) -> None:
        ann = await self.get_announcement(lecturer, offering_id, announcement_id)
        await self.announcement_repo.delete(ann)

    # -----------------------------------------------------------------------
    # Tasks
    # -----------------------------------------------------------------------

    async def create_task(
        self, lecturer: User, offering_id: uuid.UUID, payload: TaskCreate, arq: Any = None
    ) -> Task:
        offering = await self.get_assigned_offering(lecturer, offering_id)
        if payload.ai_grading and not payload.marking_guide_url:
            raise ValidationError(
                "Cannot enable AI grading at creation time without providing a marking_guide_url."
            )
        task = await self.task_repo.create(
            offering_id=offering_id,
            title=payload.title,
            description=payload.description,
            due_date=payload.due_date,
            ai_grading=payload.ai_grading,
            marking_guide_url=payload.marking_guide_url,
        )
        for q in payload.questions:
            await self.question_repo.create(
                task_id=task.id,
                text=q.text,
                type=q.type.value,
                score=q.score,
                options=q.options,
            )
        return task

    async def get_task(self, lecturer: User, offering_id: uuid.UUID, task_id: uuid.UUID) -> Task:
        await self.get_assigned_offering(lecturer, offering_id)
        task = await self.task_repo.get_by_id(task_id)
        if not task or task.offering_id != offering_id:
            raise NotFoundError("Task not found")
        return task

    async def list_tasks(self, lecturer: User, offering_id: uuid.UUID) -> Sequence[Task]:
        await self.get_assigned_offering(lecturer, offering_id)
        return await self.task_repo.list_by_offering(offering_id)

    async def list_task_response(self, lecturer: User, offering_id: uuid.UUID) -> dict:
        """Return lecturer-facing task list response."""
        tasks = await self.list_tasks(lecturer, offering_id)
        items = []
        for task in tasks:
            questions = await self.question_repo.list_by_task(task.id)
            items.append({
                "id": task.id,
                "title": task.title,
                "due_date": task.due_date,
                "question_count": len(questions),
                "total_score": sum(question.score for question in questions),
                "ai_grading": task.ai_grading,
            })
        return {"tasks": items}

    async def get_task_detail_response(
        self, lecturer: User, offering_id: uuid.UUID, task_id: uuid.UUID
    ) -> dict:
        """Return lecturer-facing task detail response."""
        task = await self.get_task(lecturer, offering_id, task_id)
        questions = await self.question_repo.list_by_task(task_id)
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date,
            "total_score": sum(question.score for question in questions),
            "ai_grading": task.ai_grading,
            "marking_guide_url": task.marking_guide_url,
            "questions": questions,
        }

    async def update_task(
        self, lecturer: User, offering_id: uuid.UUID, task_id: uuid.UUID, payload: TaskUpdate
    ) -> Task:
        task = await self.get_task(lecturer, offering_id, task_id)
        updates = payload.model_dump(exclude_none=True)
        # Guard: enabling AI grading requires marking guide
        if (
            updates.get("ai_grading")
            and not task.marking_guide_url
            and not updates.get("marking_guide_url")
        ):
            raise ValidationError("Cannot enable AI grading without a marking guide")
        return await self.task_repo.update(task, **updates)

    async def delete_task(self, lecturer: User, offering_id: uuid.UUID, task_id: uuid.UUID) -> None:
        task = await self.get_task(lecturer, offering_id, task_id)
        await self.task_repo.delete(task)

    async def upload_marking_guide(
        self, lecturer: User, offering_id: uuid.UUID, task_id: uuid.UUID, file_url: str
    ) -> Task:
        task = await self.get_task(lecturer, offering_id, task_id)
        return await self.task_repo.update(task, marking_guide_url=file_url)

    async def toggle_ai_grading(
        self, lecturer: User, offering_id: uuid.UUID, task_id: uuid.UUID, enabled: bool
    ) -> Task:
        task = await self.get_task(lecturer, offering_id, task_id)
        if enabled and not task.marking_guide_url:
            raise ValidationError("Cannot enable AI grading without a marking guide")
        return await self.task_repo.update(task, ai_grading=enabled)

    # -----------------------------------------------------------------------
    # Questions
    # -----------------------------------------------------------------------

    async def create_question(
        self, lecturer: User, offering_id: uuid.UUID, task_id: uuid.UUID, payload: QuestionCreate
    ) -> Question:
        await self.get_task(lecturer, offering_id, task_id)
        return await self.question_repo.create(
            task_id=task_id,
            text=payload.text,
            type=payload.type.value,
            score=payload.score,
            options=payload.options,
        )

    async def update_question(
        self,
        lecturer: User,
        offering_id: uuid.UUID,
        task_id: uuid.UUID,
        question_id: uuid.UUID,
        payload: QuestionUpdate,
    ) -> Question:
        await self.get_task(lecturer, offering_id, task_id)
        question = await self.question_repo.get_by_id(question_id)
        if not question or question.task_id != task_id:
            raise NotFoundError("Question not found")
        return await self.question_repo.update(question, **payload.model_dump(exclude_none=True))

    async def delete_question(
        self, lecturer: User, offering_id: uuid.UUID, task_id: uuid.UUID, question_id: uuid.UUID
    ) -> None:
        await self.get_task(lecturer, offering_id, task_id)
        question = await self.question_repo.get_by_id(question_id)
        if not question or question.task_id != task_id:
            raise NotFoundError("Question not found")
        await self.question_repo.delete(question)

    # -----------------------------------------------------------------------
    # Submissions
    # -----------------------------------------------------------------------

    async def list_submissions(
        self, lecturer: User, offering_id: uuid.UUID, task_id: uuid.UUID, graded: bool | None = None
    ) -> Sequence[Submission]:
        await self.get_task(lecturer, offering_id, task_id)
        return await self.submission_repo.list_by_task(task_id, graded=graded)

    async def list_submission_response(
        self, lecturer: User, offering_id: uuid.UUID, task_id: uuid.UUID, graded: bool | None = None
    ) -> dict:
        """Return lecturer-facing submission list response."""
        submissions = await self.list_submissions(lecturer, offering_id, task_id, graded=graded)
        items = []
        for submission in submissions:
            student = await self.user_repo.get_by_id(submission.student_id)
            items.append({
                "id": submission.id,
                "student_id": submission.student_id,
                "student_name": f"{student.first_name} {student.last_name}" if student else "Unknown",
                "submitted_at": submission.submitted_at,
                "total_score": submission.total_score,
                "grading_status": submission.grading_status,
            })
        return {"submissions": items}

    async def get_submission(
        self, lecturer: User, offering_id: uuid.UUID, task_id: uuid.UUID, submission_id: uuid.UUID
    ) -> Submission:
        await self.get_task(lecturer, offering_id, task_id)
        sub = await self.submission_repo.get_by_id(submission_id)
        if not sub or sub.task_id != task_id:
            raise NotFoundError("Submission not found")
        return sub

    async def grade_submission(
        self,
        lecturer: User,
        offering_id: uuid.UUID,
        task_id: uuid.UUID,
        submission_id: uuid.UUID,
        payload: GradeSubmissionRequest,
    ) -> Submission:
        sub = await self.get_submission(lecturer, offering_id, task_id, submission_id)
        total = 0.0
        for grade_item in payload.grades:
            answer = await self.answer_repo.get_by_submission_and_question(
                submission_id, grade_item.question_id
            )
            if not answer:
                raise NotFoundError(
                    f"Answer for question {grade_item.question_id} not found in this submission"
                )
            await self.answer_repo.update(
                answer, score=grade_item.score, feedback=grade_item.feedback
            )
            total += grade_item.score
        return await self.submission_repo.update(
            sub,
            total_score=total,
            grading_status="manually_graded",
            graded_at=datetime.now(UTC),
        )

    async def approve_ai_grades(
        self, lecturer: User, offering_id: uuid.UUID, task_id: uuid.UUID
    ) -> int:
        await self.get_task(lecturer, offering_id, task_id)
        drafts = await self.submission_repo.list_ai_draft(task_id)
        for sub in drafts:
            await self.submission_repo.update(sub, grading_status="ai_approved")
        return len(drafts)

    # -----------------------------------------------------------------------
    # Gradebook
    # -----------------------------------------------------------------------

    async def get_gradebook(
        self, lecturer: User, offering_id: uuid.UUID
    ) -> Sequence[GradebookEntry]:
        await self.get_assigned_offering(lecturer, offering_id)
        return await self.gradebook_repo.list_by_offering(offering_id)

    async def update_gradebook_entry(
        self,
        lecturer: User,
        offering_id: uuid.UUID,
        student_id: uuid.UUID,
        manual_grade: str | None,
        notes: str | None,
    ) -> GradebookEntry:
        await self.get_assigned_offering(lecturer, offering_id)
        entry = await self.gradebook_repo.get_by_student_and_offering(student_id, offering_id)
        if not entry:
            entry = await self.gradebook_repo.create(
                offering_id=offering_id,
                student_id=student_id,
                manual_grade=manual_grade,
                notes=notes,
            )
        else:
            updates = {}
            if manual_grade is not None:
                updates["manual_grade"] = manual_grade
            if notes is not None:
                updates["notes"] = notes
            entry = await self.gradebook_repo.update(entry, **updates)
        return entry
