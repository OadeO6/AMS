# src/app/models/__init__.py
"""
ORM model registry.

Import all models here so that Alembic's autogenerate can detect them
via the metadata attached to Base. Order matters for FK resolution.
"""

from app.models.academic_session import AcademicSession, Semester
from app.models.announcement import Announcement, AnnouncementView
from app.models.base import Base, TimestampMixin
from app.models.class_session import Attendance, ClassSession
from app.models.course import Course, CourseOffering, CourseRegistration
from app.models.department import Department
from app.models.faculty import Faculty
from app.models.gradebook import AITutorRule, GradebookEntry
from app.models.material import Material
from app.models.notification import Notification
from app.models.task import Answer, Question, Submission, Task
from app.models.user import User, UserRole

__all__ = [
    "AITutorRule",
    "AcademicSession",
    "Announcement",
    "AnnouncementView",
    "Answer",
    "Attendance",
    "Base",
    "ClassSession",
    "Course",
    "CourseOffering",
    "CourseRegistration",
    "Department",
    "Faculty",
    "GradebookEntry",
    "Material",
    "Notification",
    "Question",
    "Semester",
    "Submission",
    "Task",
    "TimestampMixin",
    "User",
    "UserRole",
]
