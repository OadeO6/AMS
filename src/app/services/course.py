# src/app/services/course.py
"""
Business logic for Courses, Offerings, and Registrations.
Enforces rules:
- HOD scope bounds
- Active semester checks for registration
"""

import uuid
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.course import Course, CourseOffering, CourseRegistration
from app.models.user import User
from app.repositories.course import (
    CourseOfferingRepository,
    CourseRegistrationRepository,
    CourseRepository,
)
from app.schemas.course import CourseCreate, CourseOfferingCreate, CourseUpdate


class CourseService:
    """Orchestrates course management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.course_repo = CourseRepository(session)
        self.offering_repo = CourseOfferingRepository(session)
        self.registration_repo = CourseRegistrationRepository(session)

    # -----------------------------------------------------------------------
    # HOD: Course Definitions
    # -----------------------------------------------------------------------

    async def create_course(self, hod: User, payload: CourseCreate) -> Course:
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
        return course

    async def list_department_courses(self, hod: User) -> Sequence[Course]:
        """List all courses for the HOD's department."""
        if not hod.department_id:
            return []
        return await self.course_repo.list_by_department(hod.department_id)

    async def get_department_course(self, hod: User, course_id: uuid.UUID) -> Course:
        """Fetch a specific course, ensuring it belongs to the HOD's department."""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("Course not found")
        if course.department_id != hod.department_id:
            raise ForbiddenError("Course does not belong to your department")
        return course

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
            lecturer_id=payload.lecturer_id,
            is_active=True,
        )
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

    async def activate_offering(self, hod: User, course_id: uuid.UUID, offering_id: uuid.UUID) -> CourseOffering:
        # First ensure the HOD owns the course
        await self.get_department_course(hod, course_id)
        offering = await self.get_offering(offering_id)
        if offering.course_id != course_id:
            raise ForbiddenError("Offering does not belong to this course")
            
        offering.is_active = True
        await self.session.flush()
        return offering

    async def assign_lecturer(self, hod: User, course_id: uuid.UUID, offering_id: uuid.UUID, lecturer_id: uuid.UUID) -> CourseOffering:
        await self.get_department_course(hod, course_id)
        offering = await self.get_offering(offering_id)
        if offering.course_id != course_id:
            raise ForbiddenError("Offering does not belong to this course")
            
        # Optional: could check if lecturer exists and is authorized
        offering.lecturer_id = lecturer_id
        await self.session.flush()
        return offering

    async def unassign_lecturer(self, hod: User, course_id: uuid.UUID, offering_id: uuid.UUID, lecturer_id: uuid.UUID) -> None:
        await self.get_department_course(hod, course_id)
        offering = await self.get_offering(offering_id)
        if offering.course_id != course_id:
            raise ForbiddenError("Offering does not belong to this course")
            
        if offering.lecturer_id == lecturer_id:
            offering.lecturer_id = None
            await self.session.flush()

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
