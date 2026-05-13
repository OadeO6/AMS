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
from app.repositories.academic import AcademicSessionRepository, SemesterRepository
from app.repositories.course import CourseOfferingRepository, CourseRegistrationRepository
from app.repositories.course import CourseRepository, OfferingLecturerRepository
from app.repositories.department import DepartmentRepository
from app.repositories.gradebook import GradebookRepository
from app.repositories.material import MaterialRepository
from app.repositories.session import AttendanceRepository, ClassSessionRepository
from app.repositories.task import AnswerRepository, QuestionRepository, SubmissionRepository, TaskRepository
from app.repositories.user import UserRepository


class StudentService:
    """Orchestrates all student domain logic."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.academic_session_repo = AcademicSessionRepository(session)
        self.semester_repo = SemesterRepository(session)
        self.offering_repo = CourseOfferingRepository(session)
        self.course_repo = CourseRepository(session)
        self.registration_repo = CourseRegistrationRepository(session)
        self.department_repo = DepartmentRepository(session)
        self.user_repo = UserRepository(session)
        self.offering_lecturer_repo = OfferingLecturerRepository(session)
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

    def _extract_session_start_year(self, session_name: str | None) -> int | None:
        """Parse the starting year from an academic session name like '2024/2025'."""
        if not session_name:
            return None
        try:
            return int(session_name.split("/")[0])
        except (ValueError, IndexError):
            return None

    def _compute_student_level(self, student: User, current_session_year: int | None) -> int:
        """Compute the student's current level from business rules."""
        admission_year = student.admission_year
        if admission_year is None and student.admission_session:
            admission_year = self._extract_session_start_year(student.admission_session)

        if current_session_year is None or admission_year is None:
            return 0

        return (current_session_year - admission_year + 1) + (student.level_offset or 0)

    async def list_available_courses(
        self,
        student: User,
        *,
        department: str | None = None,
        level: int | None = None,
        search: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict:
        """List active-semester offerings for student discovery with filtering and pagination."""
        active_semester = await self.semester_repo.get_active_semester()
        if not active_semester:
            return {
                "courses": [],
                "pagination": {"page": page, "limit": limit, "total": 0},
            }

        active_session = await self.academic_session_repo.get_by_id(active_semester.academic_session_id)
        current_session_year = self._extract_session_start_year(active_session.name if active_session else None)
        computed_level = self._compute_student_level(student, current_session_year)

        offerings = await self.offering_repo.list_by_semester(active_semester.id)
        normalized_department = department.strip().lower() if department else None
        normalized_search = search.strip().lower() if search else None

        items = []
        for offering in offerings:
            course = await self.course_repo.get_by_id(offering.course_id)
            if not course:
                continue

            dept = await self.department_repo.get_by_id(course.department_id)
            assignments = await self.offering_lecturer_repo.list_by_offering(offering.id)
            lecturer_id = assignments[0].lecturer_id if assignments else None
            lecturer = await self.user_repo.get_by_id(lecturer_id) if lecturer_id else None
            regs = await self.registration_repo.list_by_offering(offering.id)
            total_students = len([reg for reg in regs if reg.status == "approved"])

            item = {
                "id": offering.id,
                "title": course.title,
                "code": course.code,
                "level": computed_level,
                "department": dept.name if dept else "Unknown",
                "lecturer": {
                    "id": lecturer.id,
                    "first_name": lecturer.first_name,
                    "last_name": lecturer.last_name,
                } if lecturer else None,
                "total_students": total_students,
            }

            if normalized_department and normalized_department not in item["department"].lower():
                continue
            if level is not None and item["level"] != level:
                continue
            if normalized_search and not (
                normalized_search in item["title"].lower()
                or normalized_search in item["code"].lower()
                or normalized_search in item["department"].lower()
            ):
                continue

            items.append(item)

        total = len(items)
        start = (page - 1) * limit
        end = start + limit
        return {
            "courses": items[start:end],
            "pagination": {"page": page, "limit": limit, "total": total},
        }

    async def get_course_offering_detail(self, student: User, offering_id: uuid.UUID) -> dict:
        """Return enriched course offering details for student discovery."""
        offering = await self.offering_repo.get_with_detail(offering_id)
        if not offering:
            raise NotFoundError("Course offering not found")

        course = await self.course_repo.get_by_id(offering.course_id)
        dept = await self.department_repo.get_by_id(course.department_id) if course else None
        assignments = await self.offering_lecturer_repo.list_by_offering(offering.id)
        lecturer_id = assignments[0].lecturer_id if assignments else None
        lecturer = await self.user_repo.get_by_id(lecturer_id) if lecturer_id else None
        regs = await self.registration_repo.list_by_offering(offering.id)
        user_reg = await self.registration_repo.get_by_student_and_offering(student.id, offering.id)

        return {
            "id": offering.id,
            "title": course.title if course else "Unknown",
            "code": course.code if course else "Unknown",
            "description": course.description if course else None,
            "level": self._compute_student_level(
                student,
                self._extract_session_start_year(offering.semester.academic_session.name),
            ),
            "department": dept.name if dept else "Unknown",
            "lecturer": {
                "id": lecturer.id,
                "first_name": lecturer.first_name,
                "last_name": lecturer.last_name,
            } if lecturer else None,
            "is_registered": bool(user_reg and user_reg.status == "approved"),
            "total_students": len([reg for reg in regs if reg.status == "approved"]),
        }

    async def list_registered_courses(
        self,
        student: User,
        semester_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> dict:
        """Return the student's registered course list."""
        regs = await self.registration_repo.list_by_student(student.id)
        items = []

        for reg in regs:
            if status and reg.status != status:
                continue

            offering = await self.offering_repo.get_with_detail(reg.offering_id)
            if not offering:
                continue
            if semester_id and offering.semester_id != semester_id:
                continue

            course = await self.course_repo.get_by_id(offering.course_id)
            assignments = await self.offering_lecturer_repo.list_by_offering(offering.id)
            lecturer_id = assignments[0].lecturer_id if assignments else None
            lecturer = await self.user_repo.get_by_id(lecturer_id) if lecturer_id else None
            items.append({
                "id": offering.id,
                "title": course.title if course else "Unknown",
                "code": course.code if course else "Unknown",
                "level": self._compute_student_level(
                    student,
                    self._extract_session_start_year(offering.semester.academic_session.name),
                ),
                "status": reg.status,
                "lecturer": {
                    "id": lecturer.id,
                    "first_name": lecturer.first_name,
                    "last_name": lecturer.last_name,
                } if lecturer else None,
            })

        return {"courses": items}

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

    async def list_task_summaries(
        self, student: User, offering_id: uuid.UUID, status: str | None = None
    ) -> dict:
        """Return task list response for a student."""
        tasks = await self.list_tasks(student, offering_id, status)
        items = []
        for task in tasks:
            questions = await self.question_repo.list_by_task(task.id)
            submission = await self.submission_repo.get_by_student_and_task(student.id, task.id)
            items.append({
                "id": task.id,
                "title": task.title,
                "due_date": task.due_date,
                "max_score": sum(question.score for question in questions),
                "submission_status": submission.grading_status if submission else "not_submitted",
                "score": submission.total_score if submission else None,
            })
        return {"tasks": items}

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

    async def get_task_detail_response(
        self, student: User, offering_id: uuid.UUID, task_id: uuid.UUID
    ) -> dict:
        """Return task detail response for a student."""
        task_data = await self.get_task(student, offering_id, task_id)
        questions = await self.question_repo.list_by_task(task_id)
        submission = await self.submission_repo.get_by_student_and_task(student.id, task_id)
        return {
            **task_data,
            "total_score": sum(question.score for question in questions),
            "questions": questions,
            "submission": {
                "submitted_at": submission.submitted_at,
                "answers": [],
            } if submission else None,
        }

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
        
        # Always aggregate from graded submissions
        total_score = sum(s.total_score for s in submissions if s.total_score)
            
        # Derive status if manual grade is missing
        derived_grade = None
        if gradebook_entry and gradebook_entry.manual_grade:
            derived_grade = gradebook_entry.manual_grade
        elif submissions:
            derived_grade = "Pending"
            
        return {
            "submissions": submissions,
            "summary": {
                "total_score": total_score,
                "average": total_score / len(submissions) if submissions else 0,
                "grade": derived_grade
            }
        }

    async def get_grade_response(self, student: User, offering_id: uuid.UUID) -> dict:
        """Return grade response for a student."""
        result = await self.get_grades(student, offering_id)
        grade_items = []
        for submission in result["submissions"]:
            task = await self.task_repo.get_by_id(submission.task_id)
            questions = await self.question_repo.list_by_task(submission.task_id)
            grade_items.append({
                "task_id": submission.task_id,
                "task_title": task.title if task else "Unknown",
                "score": submission.total_score,
                "max_score": sum(question.score for question in questions),
                "graded_at": submission.graded_at,
                "feedback": None,
            })

        return {
            "grades": grade_items,
            "submissions": grade_items,
            "summary": result["summary"],
        }

    # -----------------------------------------------------------------------
    # Announcements
    # -----------------------------------------------------------------------

    async def list_announcements(
        self,
        student: User,
        offering_id: uuid.UUID,
        *,
        viewed: bool | None = None,
        pinned_only: bool = False,
        page: int = 1,
        limit: int = 20,
    ) -> dict:
        """List announcements with viewed/pinned filters and pagination."""
        await self._ensure_registered_and_approved(student, offering_id)
        announcements = await self.announcement_repo.list_by_offering(offering_id, pinned_only)
        items = []
        for announcement in announcements:
            lecturer = await self.user_repo.get_by_id(announcement.lecturer_id) if announcement.lecturer_id else None
            view = await self.announcement_view_repo.get_by_student_and_announcement(student.id, announcement.id)
            is_viewed = view is not None
            if viewed is not None and is_viewed is not viewed:
                continue
            items.append({
                "id": announcement.id,
                "title": announcement.title,
                "body": announcement.body,
                "created_at": announcement.created_at,
                "lecturer": {
                    "id": lecturer.id,
                    "first_name": lecturer.first_name,
                    "last_name": lecturer.last_name,
                    "name": f"{lecturer.first_name} {lecturer.last_name}",
                } if lecturer else None,
                "viewed": is_viewed,
            })

        total = len(items)
        start = (page - 1) * limit
        end = start + limit
        return {
            "announcements": items[start:end],
            "pagination": {"page": page, "limit": limit, "total": total},
        }

    async def get_announcement(
        self, student: User, offering_id: uuid.UUID, announcement_id: uuid.UUID
    ) -> Announcement:
        """Get a single announcement."""
        await self._ensure_registered_and_approved(student, offering_id)
        ann = await self.announcement_repo.get_by_id(announcement_id)
        if not ann or ann.offering_id != offering_id:
            raise NotFoundError("Announcement not found")
        return ann

    async def get_announcement_response(
        self, student: User, offering_id: uuid.UUID, announcement_id: uuid.UUID
    ) -> dict:
        """Return announcement detail response for a student."""
        announcement = await self.get_announcement(student, offering_id, announcement_id)
        lecturer = await self.user_repo.get_by_id(announcement.lecturer_id) if announcement.lecturer_id else None
        view = await self.announcement_view_repo.get_by_student_and_announcement(student.id, announcement.id)
        return {
            "id": announcement.id,
            "title": announcement.title,
            "body": announcement.body,
            "created_at": announcement.created_at,
            "lecturer": {
                "id": lecturer.id,
                "first_name": lecturer.first_name,
                "last_name": lecturer.last_name,
                "name": f"{lecturer.first_name} {lecturer.last_name}",
            } if lecturer else None,
            "viewed": view is not None,
        }

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
    ) -> list[dict]:
        """List class sessions with attendance status."""
        await self._ensure_registered_and_approved(student, offering_id)
        
        from sqlalchemy import and_
        query = select(ClassSession, Attendance).outerjoin(
            Attendance,
            and_(
                Attendance.session_id == ClassSession.id,
                Attendance.student_id == student.id
            )
        ).where(ClassSession.offering_id == offering_id)
        
        if status:
            query = query.where(ClassSession.status == status)
        query = query.order_by(ClassSession.scheduled_at.asc())
        
        results = (await self._session.execute(query)).all()
        
        mapped = []
        for sess, att in results:
            attended = None
            if att:
                attended = True if att.status == "present" else False
            mapped.append({
                "session": sess,
                "attended": attended
            })
        return mapped

    async def list_session_response(
        self, student: User, offering_id: uuid.UUID, status: str | None = None
    ) -> dict:
        """Return session list response for a student."""
        sessions = await self.list_sessions(student, offering_id, status)
        lecturer_map: dict[uuid.UUID, dict] = {}
        items = []
        for item in sessions:
            session_obj = item["session"]
            if session_obj.lecturer_id not in lecturer_map:
                lecturer = await self.user_repo.get_by_id(session_obj.lecturer_id)
                if lecturer:
                    lecturer_map[session_obj.lecturer_id] = {
                        "id": lecturer.id,
                        "first_name": lecturer.first_name,
                        "last_name": lecturer.last_name,
                    }

            items.append({
                "id": session_obj.id,
                "title": session_obj.title,
                "scheduled_at": session_obj.scheduled_at,
                "venue": session_obj.venue,
                "status": session_obj.status,
                "lecturer": lecturer_map.get(session_obj.lecturer_id),
                "attended": item["attended"],
            })

        return {"sessions": items}

    async def get_session(
        self, student: User, offering_id: uuid.UUID, session_id: uuid.UUID
    ) -> dict:
        """Get session details and specific attendance for the student."""
        await self._ensure_registered_and_approved(student, offering_id)
        sess = await self.session_repo.get_by_id(session_id)
        if not sess or sess.offering_id != offering_id:
            raise NotFoundError("Session not found")
            
        any_att = await self._session.scalars(
            select(Attendance).where(Attendance.session_id == session_id).limit(1)
        )
        is_marked = any_att.first() is not None

        att = await self._session.scalars(
            select(Attendance).where(
                Attendance.session_id == session_id,
                Attendance.student_id == student.id
            )
        )
        student_att = att.first()
        attended = None
        if student_att:
            attended = True if student_att.status == "present" else False

        return {
            "session": sess,
            "marked": is_marked,
            "attended": attended,
        }

    async def get_session_response(
        self, student: User, offering_id: uuid.UUID, session_id: uuid.UUID
    ) -> dict:
        """Return session detail response for a student."""
        data = await self.get_session(student, offering_id, session_id)
        session_obj = data["session"]
        lecturer = await self.user_repo.get_by_id(session_obj.lecturer_id)
        session_payload = {
            "id": session_obj.id,
            "offering_id": session_obj.offering_id,
            "lecturer_id": session_obj.lecturer_id,
            "title": session_obj.title,
            "scheduled_at": session_obj.scheduled_at,
            "venue": session_obj.venue,
            "status": session_obj.status,
            "notes": session_obj.notes,
            "is_owner": False,
            "lecturer": {
                "id": lecturer.id,
                "first_name": lecturer.first_name,
                "last_name": lecturer.last_name,
            } if lecturer else None,
            "attendance": [],
            "tasks": [],
            "created_at": session_obj.created_at,
        }
        return {
            "session": session_payload,
            "attendance": {
                "marked": data["marked"],
                "attended": data["attended"],
            },
        }

    async def get_attendance(
        self, student: User, offering_id: uuid.UUID
    ) -> dict:
        """Get all attendance records and summary for the student."""
        await self._ensure_registered_and_approved(student, offering_id)
        query = select(Attendance).join(ClassSession).where(
            ClassSession.offering_id == offering_id,
            Attendance.student_id == student.id
        )
        records = (await self._session.scalars(query)).all()
        
        total = len(records)
        present = len([r for r in records if r.status == "present"])
        absent = total - present
        percentage = (present / total * 100) if total > 0 else 0.0
        
        return {
            "attendance": records,
            "summary": {
                "total": total,
                "present": present,
                "absent": absent,
                "percentage": percentage
            }
        }
