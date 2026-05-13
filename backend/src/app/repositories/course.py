# src/app/repositories/course.py
"""
Repository layer for Course, CourseOffering, CourseRegistration, and OfferingLecturer.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import and_, select

from app.models.course import Course, CourseOffering, CourseRegistration, OfferingLecturer
from app.repositories.base import BaseRepository


class CourseRepository(BaseRepository[Course]):
    def __init__(self, session):
        super().__init__(model=Course, session=session)

    async def get_by_code(self, code: str) -> Course | None:
        """Find a course by its unique code."""
        query = select(Course).where(Course.code == code)
        return await self._session.scalar(query)

    async def list_by_department(self, department_id: uuid.UUID, page: int = 1, limit: int = 20) -> tuple[int, Sequence[Course]]:
        """List all course definitions for a given department with pagination."""
        from sqlalchemy import func
        count_query = select(func.count(Course.id)).where(Course.department_id == department_id)
        total = await self._session.scalar(count_query) or 0
        
        query = select(Course).where(Course.department_id == department_id).order_by(Course.code)
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self._session.scalars(query)
        return total, result.all()

    async def get_with_offerings(self, course_id: uuid.UUID) -> Course | None:
        """Fetch a course definition along with its offerings."""
        # Typically needed for HOD detailed view, depending on how Deep we want to query
        return await self.get_by_id(course_id)


class CourseOfferingRepository(BaseRepository[CourseOffering]):
    def __init__(self, session):
        super().__init__(model=CourseOffering, session=session)

    async def get_with_detail(self, offering_id: uuid.UUID) -> CourseOffering | None:
        """Fetch an offering with course, semester, and academic session eagerly loaded.

        Use only when you need all three nested objects (e.g. HOD detail view).
        For all other paths, use the default get_by_id from BaseRepository.
        """
        from sqlalchemy.orm import joinedload
        from app.models.academic_session import Semester
        query = select(CourseOffering).where(CourseOffering.id == offering_id).options(
            joinedload(CourseOffering.course),
            joinedload(CourseOffering.semester).joinedload(Semester.academic_session),
        )
        return await self._session.scalar(query)

    async def get_by_course_and_semester(
        self, course_id: uuid.UUID, semester_id: uuid.UUID
    ) -> CourseOffering | None:
        """Ensure duplicate offerings aren't created for the same semester."""
        query = select(CourseOffering).where(
            and_(CourseOffering.course_id == course_id, CourseOffering.semester_id == semester_id)
        )
        return await self._session.scalar(query)

    async def list_by_course(self, course_id: uuid.UUID) -> Sequence[CourseOffering]:
        """List all offerings for a specific course."""
        query = select(CourseOffering).where(CourseOffering.course_id == course_id)
        result = await self._session.scalars(query)
        return result.all()

    async def list_by_semester(self, semester_id: uuid.UUID) -> Sequence[CourseOffering]:
        """List all offerings available in a particular semester."""
        query = select(CourseOffering).where(CourseOffering.semester_id == semester_id)
        result = await self._session.scalars(query)
        return result.all()




class CourseRegistrationRepository(BaseRepository[CourseRegistration]):
    def __init__(self, session):
        super().__init__(model=CourseRegistration, session=session)

    async def get_by_student_and_offering(
        self, student_id: uuid.UUID, offering_id: uuid.UUID
    ) -> CourseRegistration | None:
        """Check if student is already registered."""
        query = select(CourseRegistration).where(
            and_(
                CourseRegistration.student_id == student_id,
                CourseRegistration.offering_id == offering_id,
            )
        )
        return await self._session.scalar(query)

    async def list_by_student(self, student_id: uuid.UUID) -> Sequence[CourseRegistration]:
        """Get all registrations for a student."""
        query = select(CourseRegistration).where(CourseRegistration.student_id == student_id)
        result = await self._session.scalars(query)
        return result.all()

    async def list_by_offering(self, offering_id: uuid.UUID) -> Sequence[CourseRegistration]:
        """List registrations for an offering (useful for lecturers)."""
        query = select(CourseRegistration).where(CourseRegistration.offering_id == offering_id)
        result = await self._session.scalars(query)
        return result.all()


class OfferingLecturerRepository(BaseRepository[OfferingLecturer]):
    """Repository for the offering_lecturers junction table."""

    def __init__(self, session):
        super().__init__(model=OfferingLecturer, session=session)

    async def get_by_offering_and_lecturer(
        self, offering_id: uuid.UUID, lecturer_id: uuid.UUID
    ) -> OfferingLecturer | None:
        """Check if a lecturer is already assigned to an offering."""
        query = select(OfferingLecturer).where(
            and_(
                OfferingLecturer.offering_id == offering_id,
                OfferingLecturer.lecturer_id == lecturer_id,
            )
        )
        return await self._session.scalar(query)

    async def list_by_offering(self, offering_id: uuid.UUID) -> Sequence[OfferingLecturer]:
        """List all lecturer assignments for a given offering."""
        query = select(OfferingLecturer).where(OfferingLecturer.offering_id == offering_id)
        result = await self._session.scalars(query)
        return result.all()

    async def list_by_lecturer(self, lecturer_id: uuid.UUID) -> Sequence[OfferingLecturer]:
        """List all offerings a lecturer is assigned to."""
        query = select(OfferingLecturer).where(OfferingLecturer.lecturer_id == lecturer_id)
        result = await self._session.scalars(query)
        return result.all()
