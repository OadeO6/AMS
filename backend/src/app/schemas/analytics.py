"""
Schemas for Analytics Module.
"""

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Student Analytics Models
# ---------------------------------------------------------------------------

class StudentCourseAnalytics(BaseModel):
    """Metrics for a single course from the student's perspective."""
    attendance_percentage: float | None
    average_score: float | None
    total_assignments: int
    completed_assignments: int

    model_config = ConfigDict(from_attributes=True)


class StudentGlobalAnalytics(BaseModel):
    """Combined overall metrics for a student across active courses."""
    courses_enrolled: int
    overall_attendance_percentage: float | None
    overall_average_score: float | None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Lecturer Analytics Models
# ---------------------------------------------------------------------------

class StudentPerformance(BaseModel):
    """Sub-model representing a specific student's aggregate performance."""
    student_id: str
    first_name: str
    last_name: str
    average_score: float | None
    attendance_percentage: float | None

    model_config = ConfigDict(from_attributes=True)


class LecturerCourseAnalytics(BaseModel):
    """Metrics for a single course from the lecturer's perspective."""
    total_students: int
    average_class_score: float | None
    average_class_attendance: float | None
    low_performing_students: list[StudentPerformance]

    model_config = ConfigDict(from_attributes=True)


class LecturerGlobalAnalytics(BaseModel):
    """Combined overall metrics for a lecturer across active courses."""
    active_courses: int
    total_students_across_courses: int
    overall_average_score: float | None

    model_config = ConfigDict(from_attributes=True)
