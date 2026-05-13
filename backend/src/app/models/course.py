# src/app/models/course.py
"""
Course, CourseOffering, and CourseRegistration ORM models.

Course:             The canonical course definition (belongs to a Department).
CourseOffering:     An instance of a Course for a specific Semester.
OfferingLecturer:   Junction table — many lecturers per offering.
CourseRegistration: A student's enrolment in a CourseOffering.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Course(Base, TimestampMixin):
    """Course definition — independent of semester."""

    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    units: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<Course id={self.id!s} code={self.code!r}>"


class CourseOffering(Base):
    """A course scheduled for a specific semester.

    Lecturers are managed via the OfferingLecturer junction table.
    """

    __tablename__ = "course_offerings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    semester_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("semesters.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    # Relationships
    course: Mapped[Course] = relationship("Course", lazy="select")
    semester: Mapped[Semester] = relationship("Semester", lazy="select")

    # Many-to-many: lecturers assigned to this offering
    lecturers: Mapped[list[OfferingLecturer]] = relationship(
        "OfferingLecturer",
        back_populates="offering",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<CourseOffering id={self.id!s} course={self.course_id!s}>"


class OfferingLecturer(Base, TimestampMixin):
    """Junction table: many lecturers — many offerings.

    Each row represents one lecturer's assignment to one offering.
    """

    __tablename__ = "offering_lecturers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    offering_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("course_offerings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lecturer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Back-reference to the offering
    offering: Mapped[CourseOffering] = relationship(
        "CourseOffering", back_populates="lecturers"
    )

    # Reference to the user record
    lecturer: Mapped[User] = relationship("User", lazy="selectin")

    def __repr__(self) -> str:
        return f"<OfferingLecturer offering={self.offering_id!s} lecturer={self.lecturer_id!s}>"


class CourseRegistration(Base, TimestampMixin):
    """A student's registration in a CourseOffering.

    Status starts as 'pending'; lecturer must approve.
    """

    __tablename__ = "course_registrations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    offering_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("course_offerings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
        doc="pending | approved | rejected",
    )

    # Relationships
    student: Mapped[User] = relationship("User", lazy="selectin")
    offering: Mapped[CourseOffering] = relationship("CourseOffering", lazy="selectin")


    def __repr__(self) -> str:
        return f"<CourseRegistration id={self.id!s} status={self.status!r}>"
