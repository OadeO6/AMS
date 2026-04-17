# src/app/services/admin.py
"""
AdminService — orchestration and business logic for top-level admin functions
(Faculties, Departments, Academic Sessions).
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.exceptions import ConflictError, NotFoundError
from app.models.user import UserRole
from app.repositories.academic import AcademicSessionRepository, SemesterRepository
from app.repositories.department import DepartmentRepository
from app.repositories.faculty import FacultyRepository
from app.repositories.user import UserRepository

if TYPE_CHECKING:
    from collections.abc import Sequence
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.models.academic_session import AcademicSession, Semester
    from app.models.department import Department
    from app.models.faculty import Faculty
    from app.schemas.admin import (
        AcademicSessionCreate,
        AcademicSessionUpdate,
        DepartmentCreate,
        DepartmentUpdate,
        FacultyCreate,
        FacultyUpdate,
        SemesterUpdate,
    )


class AdminService:
    """Business logic for Administrative operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.faculties = FacultyRepository(session)
        self.departments = DepartmentRepository(session)
        self.sessions = AcademicSessionRepository(session)
        self.semesters = SemesterRepository(session)
        self.users = UserRepository(session)

    # ---------------------------------------------------------------------------
    # Faculty
    # ---------------------------------------------------------------------------

    async def create_faculty(self, payload: FacultyCreate) -> Faculty:
        if await self.faculties.get_by_code(payload.code):
            raise ConflictError(f"Faculty with code {payload.code} already exists.")
        return await self.faculties.create(name=payload.name, code=payload.code)

    async def list_faculties(self) -> Sequence[Faculty]:
        facs, _ = await self.faculties.list_paginated(limit=1000)
        return facs

    async def update_faculty(self, faculty_id: uuid.UUID, payload: FacultyUpdate) -> Faculty:
        faculty = await self.faculties.get_by_id(faculty_id)
        if not faculty:
            raise NotFoundError("Faculty not found")

        update_data = payload.model_dump(exclude_unset=True)
        if "code" in update_data and update_data["code"] != faculty.code:
            if await self.faculties.get_by_code(update_data["code"]):
                raise ConflictError(f"Faculty with code {update_data['code']} already exists.")

        return await self.faculties.update(faculty, **update_data)

    async def delete_faculty(self, faculty_id: uuid.UUID) -> None:
        faculty = await self.faculties.get_by_id(faculty_id)
        if not faculty:
            raise NotFoundError("Faculty not found")
        # Ensure no departments exist (or rely on DB ON DELETE RESTRICT)
        # We rely on DB restrictions which will raise IntegrityError that we can catch globally,
        # but manual checking is also good. We'll rely on DB to enforce constraints for less queries.
        await self.faculties.delete(faculty)

    # ---------------------------------------------------------------------------
    # Department
    # ---------------------------------------------------------------------------

    async def create_department(self, faculty_id: uuid.UUID, payload: DepartmentCreate) -> Department:
        fac = await self.faculties.get_by_id(faculty_id)
        if not fac:
            raise NotFoundError("Faculty not found")

        if await self.departments.get_by_code(payload.code):
            raise ConflictError(f"Department with code {payload.code} already exists.")

        return await self.departments.create(
            name=payload.name, code=payload.code, faculty_id=faculty_id
        )

    async def list_departments_by_faculty(self, faculty_id: uuid.UUID) -> Sequence[Department]:
        if not await self.faculties.get_by_id(faculty_id):
            raise NotFoundError("Faculty not found")
        return await self.departments.list_by_faculty(faculty_id)

    async def get_department(self, faculty_id: uuid.UUID, department_id: uuid.UUID) -> Department:
        dept = await self.departments.get_by_id(department_id)
        if not dept or dept.faculty_id != faculty_id:
            raise NotFoundError("Department not found in this faculty")
        return dept

    async def update_department(
        self, faculty_id: uuid.UUID, department_id: uuid.UUID, payload: DepartmentUpdate
    ) -> Department:
        dept = await self.get_department(faculty_id, department_id)
        update_data = payload.model_dump(exclude_unset=True)

        if "code" in update_data and update_data["code"] != dept.code:
            if await self.departments.get_by_code(update_data["code"]):
                raise ConflictError(f"Department with code {update_data['code']} already exists.")

        return await self.departments.update(dept, **update_data)

    async def delete_department(self, faculty_id: uuid.UUID, department_id: uuid.UUID) -> None:
        dept = await self.get_department(faculty_id, department_id)
        await self.departments.delete(dept)

    async def assign_hod(self, department_id: uuid.UUID, user_id: uuid.UUID) -> Department:
        dept = await self.departments.get_by_id(department_id)
        if not dept:
            raise NotFoundError("Department not found")
        
        user = await self.users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        if user.role != UserRole.HOD:
            raise ConflictError("User must have HOD role to be assigned as Head of Department")

        # Set user's department explicitly as well, so their token matches the HOD scoping.
        await self.users.update(user, department_id=dept.id)
        return await self.departments.update(dept, hod_id=user.id)

    # ---------------------------------------------------------------------------
    # Academic sessions and Semesters
    # ---------------------------------------------------------------------------

    async def create_session(self, payload: AcademicSessionCreate) -> AcademicSession:
        if await self.sessions.get_by_name(payload.name):
            raise ConflictError(f"Session '{payload.name}' already exists.")

        session_obj = await self.sessions.create(name=payload.name)
        
        # Create semesters inside
        for sem_data in payload.semesters:
            await self.semesters.create(
                academic_session_id=session_obj.id,
                name=sem_data.name,
                start_date=sem_data.start_date,
                end_date=sem_data.end_date,
            )
        
        # Return eagerly mapped
        full_session = await self.sessions.get_with_semesters(session_obj.id)
        assert full_session is not None
        return full_session

    async def list_sessions(self) -> Sequence[AcademicSession]:
        return await self.sessions.list_all_with_semesters()

    async def get_session(self, session_id: uuid.UUID) -> AcademicSession:
        sess = await self.sessions.get_with_semesters(session_id)
        if not sess:
            raise NotFoundError("Academic session not found")
        return sess

    async def update_session(self, session_id: uuid.UUID, payload: AcademicSessionUpdate) -> AcademicSession:
        sess = await self.get_session(session_id)
        update_data = payload.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"] != sess.name:
            if await self.sessions.get_by_name(update_data["name"]):
                raise ConflictError("Academic session with this name already exists")
        
        updated = await self.sessions.update(sess, **update_data)
        return await self.get_session(updated.id)

    async def delete_session(self, session_id: uuid.UUID) -> None:
        sess = await self.sessions.get_by_id(session_id)
        if not sess:
            raise NotFoundError("Academic session not found")
        await self.sessions.delete(sess)

    async def activate_semester(self, session_id: uuid.UUID, semester_id: uuid.UUID) -> Semester:
        sess = await self.get_session(session_id)  # Validate it belongs to session implicitly if we checked
        sem = await self.semesters.get_by_id(semester_id)
        if not sem or sem.academic_session_id != session_id:
            raise NotFoundError("Semester not found inside this session")
        
        sem_updated = await self.semesters.activate(semester_id)
        return sem_updated  # type: ignore

    async def update_semester(
        self, session_id: uuid.UUID, semester_id: uuid.UUID, payload: SemesterUpdate
    ) -> Semester:
        sem = await self.semesters.get_by_id(semester_id)
        if not sem or sem.academic_session_id != session_id:
            raise NotFoundError("Semester not found inside this session")
            
        update_data = payload.model_dump(exclude_unset=True)
        return await self.semesters.update(sem, **update_data)

    async def delete_semester(self, session_id: uuid.UUID, semester_id: uuid.UUID) -> None:
        sem = await self.semesters.get_by_id(semester_id)
        if not sem or sem.academic_session_id != session_id:
            raise NotFoundError("Semester not found inside this session")
        
        await self.semesters.delete(sem)
