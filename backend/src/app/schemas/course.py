from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Course Definition Schemas
# ---------------------------------------------------------------------------


class CourseBase(BaseModel):
    model_config = ConfigDict()

    title: str = Field(..., min_length=2, max_length=200)
    code: str = Field(..., min_length=2, max_length=20)
    description: str | None = None
    units: int = Field(..., ge=1, le=10)


class CourseCreate(CourseBase):
    """Schema for HODs creating a new course definition in their department."""

    pass


class CourseUpdate(BaseModel):
    """Schema for updating a course definition."""

    model_config = ConfigDict()

    title: str | None = Field(None, min_length=2, max_length=200)
    description: str | None = None
    units: int | None = Field(None, ge=1, le=10)


class CourseResponse(CourseBase):
    id: uuid.UUID
    department_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Course Offering Schemas
# ---------------------------------------------------------------------------


class CourseOfferingCreate(BaseModel):
    """Payload for HODs instantiating a Course for a Semester."""

    model_config = ConfigDict()

    semester_id: uuid.UUID
    lecturer_id: uuid.UUID | None = None


class CourseOfferingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    semester_id: uuid.UUID
    lecturers: list[uuid.UUID] = []
    is_active: bool

    @field_validator("lecturers", mode="before")
    def extract_lecturer_ids(cls, v):
        if not v:
            return []
        if hasattr(v[0], "lecturer_id"):
            return [assignment.lecturer_id for assignment in v]
        return v


class CourseOfferingAssignLecturer(BaseModel):
    """Payload to assign a primary lecturer to an offering."""

    model_config = ConfigDict()

    lecturer_id: uuid.UUID


# ---------------------------------------------------------------------------
# Course Registration Schemas
# ---------------------------------------------------------------------------


class CourseRegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    offering_id: uuid.UUID
    student_id: uuid.UUID
    status: str


class CourseRegistrationStatusUpdate(BaseModel):
    """Lecturer reviewing a registration request."""

    model_config = ConfigDict(json_schema_extra={"example": {"status": "approved"}})

    status: str = Field(..., pattern="^(approved|rejected)$")


class CourseStudentListItem(BaseModel):
    """Student in a course for lecturer view."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    registration_status: str

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int

class CourseLecturerNested(BaseModel):
    id: str | uuid.UUID
    first_name: str | None = None
    last_name: str | None = None
    name: str | None = None
    staff_id: str | None = None

class CourseListItem(BaseModel):
    id: uuid.UUID
    title: str
    code: str
    level: int = 0
    department: str | None = None
    lecturer: CourseLecturerNested | None = None
    total_students: int = 0

class CourseListResponse(BaseModel):
    courses: list[CourseListItem]
    pagination: PaginationMeta

class CourseDetailResponse(BaseModel):
    id: uuid.UUID
    title: str
    code: str
    description: str | None = None
    level: int = 0
    department: str | None = None
    lecturer: CourseLecturerNested | None = None
    is_registered: bool = False
    total_students: int = 0

class CourseRegisterResponse(BaseModel):
    message: str
    status: str

class StudentRegisteredCourseItem(BaseModel):
    id: uuid.UUID
    title: str
    code: str
    level: int = 0
    status: str
    lecturer: CourseLecturerNested | None = None

class StudentCourseListResponse(BaseModel):
    courses: list[StudentRegisteredCourseItem]

class LecturerCourseListItem(BaseModel):
    id: uuid.UUID
    title: str
    code: str
    level: int = 0
    total_students: int = 0
    is_active: bool = False
    lecturers: list[CourseLecturerNested] = []

class LecturerCourseListResponse(BaseModel):
    courses: list[LecturerCourseListItem]

class LecturerCourseDetailResponse(BaseModel):
    id: uuid.UUID
    title: str
    code: str
    level: int = 0
    lecturers: list[CourseLecturerNested] = []
    description: str | None = None
    department: str | None = None
    total_students: int = 0
    sessions: int = 0
    tasks_count: int = 0

class CourseStudentListResponse(BaseModel):
    students: list[CourseStudentListItem]

class CourseCreateCourseDetail(BaseModel):
    id: uuid.UUID
    title: str
    code: str
    units: int
    department: dict

class CourseCreateResponse(BaseModel):
    message: str
    course: CourseCreateCourseDetail

class CourseUpdateResponse(BaseModel):
    message: str
    course: CourseResponse

class OfferingCreateResponse(BaseModel):
    message: str
    offering: CourseOfferingResponse

class OfferingDetailResponse(BaseModel):
    id: uuid.UUID
    course: dict
    academic_session: str
    semester: str
    is_active: bool
    lecturers: list[CourseLecturerNested] = []
    total_students: int = 0
    total_sessions: int = 0
    total_tasks: int = 0

class OfferingActivateResponse(BaseModel):
    message: str
    offering: CourseOfferingResponse

class OfferingAssignResponse(BaseModel):
    message: str
    offering: CourseOfferingResponse

class CourseDefinitionListItem(BaseModel):
    id: uuid.UUID
    title: str
    code: str
    units: int
    total_offerings: int = 0
    active_offering: bool = False

class CourseDefinitionListResponse(BaseModel):
    courses: list[CourseDefinitionListItem]
    pagination: PaginationMeta

class CourseDefinitionOfferingNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    academic_session: str
    semester: str
    is_active: bool
    lecturers: list[CourseLecturerNested] = []

class CourseDefinitionDetailResponse(BaseModel):
    id: uuid.UUID
    title: str
    code: str
    description: str | None = None
    units: int
    department: dict | None = None
    offerings: list[CourseDefinitionOfferingNested] = []

