# src/app/services/user.py
"""
UserService — orchestration and business logic for the User domain (AMS version).

Raises domain-specific AppExceptions (ConflictError, NotFoundError, ForbiddenError)
which are automatically converted to JSON responses by the global handlers.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.core.security import get_password_hash, verify_password
from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.user import UserRole
from app.repositories.user import UserRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models.user import User
    from app.schemas.user import (
        LecturerRegister,
        LecturerUpdate,
        PasswordUpdate,
        StudentRegister,
        UserUpdate,
    )


class UserService:
    """Business logic for User operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = UserRepository(session)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    async def create_student(self, payload: StudentRegister) -> User:
        """Create a new student account.

        Raises
        ------
        ConflictError
            If a user with the same email already exists.
        """
        email = payload.email.lower()
        if await self.repo.exists_by_email(email):
            raise ConflictError(detail="Email already registered", error_code="EMAIL_CONFLICT")

        hashed_password = get_password_hash(payload.password)
        return await self.repo.create(
            email=email,
            hashed_password=hashed_password,
            first_name=payload.first_name,
            last_name=payload.last_name,
            role=UserRole.STUDENT,
            phone=payload.phone,
            department_id=payload.department_id,
            is_active=True,
        )

    async def create_lecturer(self, payload: LecturerRegister) -> User:
        """Create a new lecturer account (starts unauthorized).

        Raises
        ------
        ConflictError
            If a user with the same email already exists.
        """
        email = payload.email.lower()
        if await self.repo.exists_by_email(email):
            raise ConflictError(detail="Email already registered", error_code="EMAIL_CONFLICT")

        hashed_password = get_password_hash(payload.password)
        return await self.repo.create(
            email=email,
            hashed_password=hashed_password,
            first_name=payload.first_name,
            last_name=payload.last_name,
            role=UserRole.LECTURER,
            phone=payload.phone,
            staff_id=payload.staff_id,
            department_id=payload.department_id,
            is_active=True,
            is_authorized=False,
        )

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    async def get_optional_user(self, user_id: uuid.UUID) -> User | None:
        """Get a user by ID, returning None if not found."""
        return await self.repo.get_by_id(user_id)

    async def get_user_or_404(self, user_id: uuid.UUID) -> User:
        """Get a user by ID, or raise NotFoundError."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(detail="User not found", error_code="USER_NOT_FOUND")
        return user

    # ------------------------------------------------------------------
    # Profile updates
    # ------------------------------------------------------------------

    async def update_profile(self, user_id: uuid.UUID, payload: UserUpdate) -> User:
        """Update common profile fields (first_name, last_name, phone, avatar).

        Raises
        ------
        NotFoundError
            If the user_id does not exist.
        """
        user = await self.get_user_or_404(user_id)
        update_data = payload.model_dump(exclude_unset=True, exclude_none=False)
        return await self.repo.update(user, **update_data)

    async def update_lecturer_profile(self, user_id: uuid.UUID, payload: LecturerUpdate) -> User:
        """Update lecturer-specific profile fields.

        Raises
        ------
        NotFoundError
            If user not found.
        ForbiddenError
            If the user is not a lecturer.
        """
        user = await self.get_user_or_404(user_id)
        if user.role != UserRole.LECTURER:
            raise ForbiddenError(
                detail="Only lecturers can update lecturer profile fields",
                error_code="FORBIDDEN",
            )
        update_data = payload.model_dump(exclude_unset=True, exclude_none=False)
        return await self.repo.update(user, **update_data)

    async def update_student_profile(self, user_id: uuid.UUID, payload: StudentUpdate) -> User:
        """Update student-specific profile fields.

        Raises
        ------
        NotFoundError
            If user not found.
        ForbiddenError
            If the user is not a student.
        """
        user = await self.get_user_or_404(user_id)
        if user.role != UserRole.STUDENT:
            raise ForbiddenError(
                detail="Only students can update student profile fields",
                error_code="FORBIDDEN",
            )
        update_data = payload.model_dump(exclude_unset=True, exclude_none=False)
        return await self.repo.update(user, **update_data)

    async def change_password(self, user_id: uuid.UUID, payload: PasswordUpdate) -> None:
        """Change the user's password after verifying the current one.

        Raises
        ------
        NotFoundError
            If user not found.
        ForbiddenError
            If current_password does not match stored hash.
        """
        user = await self.get_user_or_404(user_id)
        if not verify_password(payload.current_password, user.hashed_password):
            raise ForbiddenError(
                detail="Current password is incorrect", error_code="WRONG_PASSWORD"
            )
        hashed = get_password_hash(payload.new_password)
        await self.repo.update(user, hashed_password=hashed)

    # ------------------------------------------------------------------
    # Admin / HOD Actions
    # ------------------------------------------------------------------

    async def list_users(
        self,
        *,
        role: UserRole | None = None,
        department_id: uuid.UUID | None = None,
        search: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[int, list[User]]:
        """List users with pagination and optional filtering."""
        skip = max(0, page - 1) * limit
        return await self.repo.list_users(
            role=role.value if role else None,
            department_id=department_id,
            search=search,
            skip=skip,
            limit=limit,
        )

    async def authorize_lecturer(self, user_id: uuid.UUID) -> User:
        """Authorize a lecturer account."""
        user = await self.get_user_or_404(user_id)
        if user.role != UserRole.LECTURER:
            raise ConflictError(detail="Only lecturers can be authorized", error_code="NOT_A_LECTURER")
        if user.is_authorized:
            raise ConflictError(detail="Lecturer is already authorized", error_code="ALREADY_AUTHORIZED")
        return await self.repo.update(user, is_authorized=True)

    async def update_level_offset(self, student_id: uuid.UUID, offset: int) -> User:
        """Update a student's level offset."""
        user = await self.get_user_or_404(student_id)
        if user.role != UserRole.STUDENT:
            raise ConflictError(detail="User is not a student", error_code="NOT_A_STUDENT")
        return await self.repo.update(user, level_offset=offset)
