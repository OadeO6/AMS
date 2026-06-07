# src/app/services/course.py
"""
Business logic for Courses, Offerings, and Registrations.
Enforces rules:
- HOD scope bounds
- Active semester checks for registration
"""

import uuid
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.class_session import ClassSession
from app.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.models.course import Course, CourseOffering, CourseRegistration
from app.models.task import Task
from app.models.user import User, UserRole
from app.repositories.course import (
    CourseOfferingRepository,
    CourseRegistrationRepository,
    CourseRepository,
    OfferingLecturerRepository,
)
from app.repositories.user import UserRepository
from app.schemas.course import CourseCreate, CourseOfferingCreate, CourseUpdate


class CourseService:
    """Orchestrates course management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.course_repo = CourseRepository(session)
        self.offering_repo = CourseOfferingRepository(session)
        self.registration_repo = CourseRegistrationRepository(session)
        self.user_repo = UserRepository(session)
        self.offering_lecturer_repo = OfferingLecturerRepository(session)

    # -----------------------------------------------------------------------
    # HOD: Course Definitions
    # -----------------------------------------------------------------------

    async def create_course(self, hod: User, payload: CourseCreate) -> dict:
        """Create a new course definition in the HOD's department."""
        if not hod.department_id:
            raise ForbiddenError("HOD is not assigned to a department")

        # Check for duplicate code anywhere (could restrict to dept, but code is globally unique)
        existing = await self.course_repo.get_by_code(payload.code)
        if existing:
            raise ConflictError(f"Course with code {payload.code} already exists")

        course = await self.course_repo.create(
            department_id=hod.department_id,
            title=payload.title,
            code=payload.code,
            description=payload.description,
            units=payload.units,
        )
        
        from app.repositories.department import DepartmentRepository
        dept_repo = DepartmentRepository(self.session)
        dept = await dept_repo.get_by_id(hod.department_id)
        
        return {
            "id": course.id,
            "title": course.title,
            "code": course.code,
            "units": course.units,
            "department": {"id": str(dept.id), "name": dept.name} if dept else {"id": str(hod.department_id), "name": ""}
        }

    async def list_department_courses(self, hod: User, page: int = 1, limit: int = 20) -> tuple[int, list[tuple[Course, int, bool]]]:
        """List all courses for the HOD's department with offering stats."""
        if not hod.department_id:
            return 0, []
        return await self.course_repo.list_by_department(hod.department_id, page=page, limit=limit)

    async def get_department_course(self, hod: User, course_id: uuid.UUID) -> Course:
        """Fetch a specific course, ensuring it belongs to the HOD's department."""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("Course not found")
        if course.department_id != hod.department_id:
            raise ForbiddenError("Course does not belong to your department")
        return course

    async def get_department_course_detail(self, hod: User, course_id: uuid.UUID) -> dict:
        """Fetch course details formatted for the HOD API."""
        course = await self.get_department_course(hod, course_id)
        
        offerings = await self.offering_repo.list_by_course_with_detail(course_id)
        
        offerings_data = []
        for off in offerings:
            academic_session_name = ""
            semester_name = ""
            if hasattr(off, "semester") and off.semester:
                if getattr(off.semester, "academic_session", None):
                    academic_session_name = off.semester.academic_session.name
                semester_name = off.semester.name
            
            lecturers_data = []
            for l in getattr(off, "lecturers", []):
                if getattr(l, "lecturer", None) and getattr(l.lecturer, "user", None):
                    u = l.lecturer.user
                    lecturers_data.append({
                        "id": u.id,
                        "first_name": u.first_name,
                        "last_name": u.last_name,
                        "name": f"{u.first_name} {u.last_name}" if u.first_name else None,
                        "staff_id": l.lecturer.staff_id,
                    })

            offerings_data.append({
                "id": off.id,
                "academic_session": academic_session_name,
                "semester": semester_name,
                "is_active": off.is_active,
                "lecturers": lecturers_data
            })

        department_data = None
        if getattr(course, "department", None):
            department_data = {"id": str(course.department.id), "name": course.department.name}

        return {
            "id": course.id,
            "title": course.title,
            "code": course.code,
            "description": course.description,
            "units": course.units,
            "department": department_data,
            "offerings": offerings_data
        }

    async def update_course(self, hod: User, course_id: uuid.UUID, payload: CourseUpdate) -> Course:
        """Update a course definition."""
        course = await self.get_department_course(hod, course_id)
        
        update_data = payload.model_dump(exclude_unset=True)
        # Note: BaseRepository doesn't natively have partial update dict support without fetching.
        # We can just mutate and commit.
        for key, value in update_data.items():
            setattr(course, key, value)
            
        await self.session.flush()
        return course

    async def delete_course(self, hod: User, course_id: uuid.UUID) -> None:
        """Delete a course definition."""
        course = await self.get_department_course(hod, course_id)
        # Check if offerings exist
        offerings = await self.offering_repo.list_by_course(course.id)
        if offerings:
            raise ConflictError("Cannot delete course with existing offerings", error_code="COURSE_HAS_OFFERINGS")
            
        await self.course_repo.delete(course)

    # -----------------------------------------------------------------------
    # HOD: Offerings
    # -----------------------------------------------------------------------

    async def create_offering(
        self, hod: User, course_id: uuid.UUID, payload: CourseOfferingCreate
    ) -> CourseOffering:
        """Instantiate a course for a specific semester."""
        course = await self.get_department_course(hod, course_id)

        # Check dupes
        existing = await self.offering_repo.get_by_course_and_semester(
            course_id, payload.semester_id
        )
        if existing:
            raise ConflictError("Course is already offered in this semester")

        offering = await self.offering_repo.create(
            course_id=course.id,
            semester_id=payload.semester_id,
            is_active=True,
        )

        # Optionally assign first lecturer via junction table
        if payload.lecturer_id:
            await self._do_assign_lecturer(offering.id, payload.lecturer_id)

        # Reload to populate lecturers relationship
        await self.session.refresh(offering)
        return offering

    async def list_course_offerings(
        self, hod: User, course_id: uuid.UUID
    ) -> Sequence[CourseOffering]:
        """List all offerings for a specific course."""
        course = await self.get_department_course(hod, course_id)
        return await self.offering_repo.list_by_course(course.id)

    async def get_offering(self, offering_id: uuid.UUID) -> CourseOffering:
        offering = await self.offering_repo.get_by_id(offering_id)
        if not offering:
            raise NotFoundError("Course offering not found")
        return offering

    async def get_offering_detail(self, hod: User, course_id: uuid.UUID, offering_id: uuid.UUID) -> dict:
        """Return enriched HOD offering detail response."""
        await self.get_department_course(hod, course_id)
        # Use get_with_detail so course/semester/academic_session are eagerly loaded
        offering = await self.offering_repo.get_with_detail(offering_id)
        if not offering:
            raise NotFoundError("Course offering not found")
        if offering.course_id != course_id:
            raise ForbiddenError("Offering does not belong to this course")

        lecturers = []
        for assignment in offering.lecturers:
            lecturer = assignment.lecturer
            if lecturer:
                lecturers.append({
                    "id": lecturer.id,
                    "first_name": lecturer.first_name,
                    "last_name": lecturer.last_name,
                    "name": f"{lecturer.first_name} {lecturer.last_name}",
                    "staff_id": lecturer.staff_id,
                })

        # Use COUNT(*) — avoid fetching all rows just to count them
        total_students = await self.session.scalar(
            select(func.count(CourseRegistration.id)).where(
                CourseRegistration.offering_id == offering_id
            )
        ) or 0
        total_sessions = await self.session.scalar(
            select(func.count(ClassSession.id)).where(ClassSession.offering_id == offering_id)
        ) or 0
        total_tasks = await self.session.scalar(
            select(func.count(Task.id)).where(Task.offering_id == offering_id)
        ) or 0

        return {
            "id": offering.id,
            "course": {"id": offering.course.id, "title": offering.course.title, "code": offering.course.code},
            "academic_session": offering.semester.academic_session.name,
            "semester": offering.semester.name,
            "is_active": offering.is_active,
            "lecturers": lecturers,
            "total_students": total_students,
            "total_sessions": total_sessions,
            "total_tasks": total_tasks,
        }

    async def activate_offering(self, hod: User, course_id: uuid.UUID, offering_id: uuid.UUID) -> CourseOffering:
        # First ensure the HOD owns the course
        await self.get_department_course(hod, course_id)
        offering = await self.get_offering(offering_id)
        if offering.course_id != course_id:
            raise ForbiddenError("Offering does not belong to this course")
            
        offering.is_active = True
        await self.session.flush()
        return offering

    async def _do_assign_lecturer(self, offering_id: uuid.UUID, lecturer_id: uuid.UUID) -> None:
        """Internal helper: validate and insert a row into offering_lecturers."""
        assignee = await self.user_repo.get_by_id(lecturer_id)
        if not assignee:
            raise NotFoundError("User not found")
        if UserRole.LECTURER.value not in assignee.roles:
            raise ConflictError(
                "Only users with the LECTURER role can be assigned to a course offering",
                error_code="NOT_A_LECTURER",
            )
        if not assignee.is_authorized:
            raise ValidationError("Lecturer must be authorized before being assigned a course")

        # Dedup guard
        existing = await self.offering_lecturer_repo.get_by_offering_and_lecturer(
            offering_id, lecturer_id
        )
        if existing:
            raise ConflictError(
                "Lecturer is already assigned to this offering",
                error_code="ALREADY_ASSIGNED",
            )

        await self.offering_lecturer_repo.create(
            offering_id=offering_id, lecturer_id=lecturer_id
        )

    async def assign_lecturer(
        self, hod: User, course_id: uuid.UUID, offering_id: uuid.UUID, lecturer_id: uuid.UUID
    ) -> CourseOffering:
        await self.get_department_course(hod, course_id)
        offering = await self.get_offering(offering_id)
        if offering.course_id != course_id:
            raise ForbiddenError("Offering does not belong to this course")

        await self._do_assign_lecturer(offering.id, lecturer_id)

        # Reload to populate lecturers relationship
        await self.session.refresh(offering)
        return offering

    async def unassign_lecturer(self, hod: User, course_id: uuid.UUID, offering_id: uuid.UUID, lecturer_id: uuid.UUID) -> None:
        await self.get_department_course(hod, course_id)
        offering = await self.get_offering(offering_id)
        if offering.course_id != course_id:
            raise ForbiddenError("Offering does not belong to this course")

        row = await self.offering_lecturer_repo.get_by_offering_and_lecturer(
            offering_id, lecturer_id
        )
        if row:
            await self.offering_lecturer_repo.delete(row)

    # -----------------------------------------------------------------------
    # Student / Shared: Registration & Discovery
    # -----------------------------------------------------------------------

    async def list_available_offerings(self) -> Sequence[CourseOffering]:
        """List active offerings for the globally active semester."""
        from app.repositories.academic import SemesterRepository
        
        sem_repo = SemesterRepository(self.session)
        active_semester = await sem_repo.get_active_semester()
        if not active_semester:
            return []
            
        return await self.offering_repo.list_by_semester(active_semester.id)

    async def list_student_offerings(self, student: User, semester_id: uuid.UUID | None = None) -> Sequence[CourseOffering]:
        """List course offerings the student is registered for."""
        regs = await self.registration_repo.list_by_student(student.id)
        offering_ids = [r.offering_id for r in regs]
        
        offerings = []
        # A more optimal implementation would be a join in the repository.
        # But for Phase 4 we can instantiate individually.
        for oid in offering_ids:
            off = await self.get_offering(oid)
            if semester_id and off.semester_id != semester_id:
                continue
            offerings.append(off)
            
        return offerings

    async def get_registration(self, student: User, offering_id: uuid.UUID) -> CourseRegistration:
        reg = await self.registration_repo.get_by_student_and_offering(student.id, offering_id)
        if not reg:
            raise NotFoundError("Registration not found")
        return reg

    async def register_student(self, student: User, offering_id: uuid.UUID) -> CourseRegistration:
        """Student registers for an active offering."""
        offering = await self.get_offering(offering_id)
        if not offering.is_active:
            raise ForbiddenError("Cannot register for an inactive offering")

        existing = await self.registration_repo.get_by_student_and_offering(
            student.id, offering.id
        )
        if existing:
            raise ConflictError("Already registered for this course offering")

        reg = await self.registration_repo.create(
            offering_id=offering.id,
            student_id=student.id,
            status="pending",
        )
        return reg

    async def unregister_student(self, student: User, offering_id: uuid.UUID) -> None:
        """Drop a course."""
        reg = await self.registration_repo.get_by_student_and_offering(student.id, offering_id)
        if not reg:
            raise NotFoundError("Registration not found")
            
        await self.registration_repo.delete(reg)

    async def list_student_registrations(self, student: User) -> Sequence[CourseRegistration]:
        return await self.registration_repo.list_by_student(student.id)
