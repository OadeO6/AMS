# tests/unit/test_user_service.py
"""
Unit tests for the UserService (AMS version).

All database access via UserRepository is mocked to isolate business logic.
"""

from __future__ import annotations

import uuid
from typing import cast
from unittest.mock import AsyncMock, patch

import pytest

from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.user import User, UserRole
from app.schemas.user import LecturerUpdate, PasswordUpdate, StudentRegister, UserUpdate
from app.services.user import UserService


@pytest.fixture
def repo_mock() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(repo_mock: AsyncMock) -> UserService:
    # Pass None session because we mock the entire repo anyway
    with patch("app.services.user.UserRepository", return_value=repo_mock):
        from sqlalchemy.ext.asyncio import AsyncSession

        return UserService(session=cast(AsyncSession, None))


# ---------------------------------------------------------------------------
# create_student
# ---------------------------------------------------------------------------


async def test_create_student_success(service: UserService, repo_mock: AsyncMock) -> None:
    """UserService should hash the password and create a student user."""
    repo_mock.exists_by_email.return_value = False

    stub_user = User(
        id=uuid.uuid4(),
        email="student@example.com",
        first_name="Ada",
        last_name="Lovelace",
        hashed_password="fakehash",
        role=UserRole.STUDENT,
        is_active=True,
    )
    repo_mock.create.return_value = stub_user

    payload = StudentRegister(
        email="student@example.com",
        password="password123",
        first_name="Ada",
        last_name="Lovelace",
    )

    with patch("app.services.user.get_password_hash", return_value="fakehash") as mock_hash:
        result = await service.create_student(payload)

        mock_hash.assert_called_once_with("password123")
        repo_mock.create.assert_called_once_with(
            email="student@example.com",
            hashed_password="fakehash",
            first_name="Ada",
            last_name="Lovelace",
            role=UserRole.STUDENT,
            phone=None,
            department_id=None,
            is_active=True,
        )
        assert result.email == "student@example.com"
        assert result.role == UserRole.STUDENT


async def test_create_student_email_conflict(service: UserService, repo_mock: AsyncMock) -> None:
    """UserService should raise ConflictError if email exists."""
    repo_mock.exists_by_email.return_value = True

    payload = StudentRegister(
        email="existing@example.com",
        password="password123",
        first_name="Ada",
        last_name="Lovelace",
    )

    with pytest.raises(ConflictError) as exc:
        await service.create_student(payload)

    assert exc.value.error_code == "EMAIL_CONFLICT"
    repo_mock.create.assert_not_called()


# ---------------------------------------------------------------------------
# create_lecturer
# ---------------------------------------------------------------------------


async def test_create_lecturer_success(service: UserService, repo_mock: AsyncMock) -> None:
    """Creating a lecturer should set role=LECTURER and is_authorized=False."""
    repo_mock.exists_by_email.return_value = False

    stub_user = User(
        id=uuid.uuid4(),
        email="lecturer@example.com",
        first_name="Grace",
        last_name="Hopper",
        hashed_password="fakehash",
        role=UserRole.LECTURER,
        is_active=True,
        is_authorized=False,
    )
    repo_mock.create.return_value = stub_user

    from app.schemas.user import LecturerRegister

    payload = LecturerRegister(
        email="lecturer@example.com",
        password="password123",
        first_name="Grace",
        last_name="Hopper",
        staff_id="STAFF001",
    )

    with patch("app.services.user.get_password_hash", return_value="fakehash"):
        result = await service.create_lecturer(payload)

    assert result.role == UserRole.LECTURER
    assert result.is_authorized is False


# ---------------------------------------------------------------------------
# get_user_or_404
# ---------------------------------------------------------------------------


async def test_get_user_or_404_not_found(service: UserService, repo_mock: AsyncMock) -> None:
    """Should raise NotFoundError if user does not exist."""
    repo_mock.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await service.get_user_or_404(uuid.uuid4())


# ---------------------------------------------------------------------------
# update_profile
# ---------------------------------------------------------------------------


async def test_update_profile_success(service: UserService, repo_mock: AsyncMock) -> None:
    """Updating common profile fields should call repo.update with correct data."""
    user_id = uuid.uuid4()
    stub_user = User(
        id=user_id,
        email="test@example.com",
        first_name="Old",
        last_name="Name",
        role=UserRole.STUDENT,
    )
    updated_user = User(
        id=user_id,
        email="test@example.com",
        first_name="New",
        last_name="Name",
        role=UserRole.STUDENT,
    )
    repo_mock.get_by_id.return_value = stub_user
    repo_mock.update.return_value = updated_user

    payload = UserUpdate(first_name="New")
    result = await service.update_profile(user_id, payload)

    assert result.first_name == "New"
    repo_mock.update.assert_called_once()


# ---------------------------------------------------------------------------
# update_lecturer_profile
# ---------------------------------------------------------------------------


async def test_update_lecturer_profile_forbidden_for_student(
    service: UserService, repo_mock: AsyncMock
) -> None:
    """A student should not be able to update lecturer-specific fields."""
    user_id = uuid.uuid4()
    stub_user = User(
        id=user_id,
        email="student@example.com",
        first_name="Test",
        last_name="Student",
        role=UserRole.STUDENT,
    )
    repo_mock.get_by_id.return_value = stub_user

    payload = LecturerUpdate(staff_id="STAFF999")

    with pytest.raises(ForbiddenError) as exc:
        await service.update_lecturer_profile(user_id, payload)

    assert exc.value.error_code == "FORBIDDEN"


# ---------------------------------------------------------------------------
# change_password
# ---------------------------------------------------------------------------


async def test_change_password_wrong_current(service: UserService, repo_mock: AsyncMock) -> None:
    """change_password should raise ForbiddenError if current password is wrong."""
    user_id = uuid.uuid4()
    stub_user = User(
        id=user_id,
        email="test@example.com",
        first_name="T",
        last_name="U",
        hashed_password="correcthash",
        role=UserRole.STUDENT,
    )
    repo_mock.get_by_id.return_value = stub_user

    payload = PasswordUpdate(current_password="wrongpass", new_password="newpass123")

    with (
        patch("app.services.user.verify_password", return_value=False),
        pytest.raises(ForbiddenError) as exc,
    ):
        await service.change_password(user_id, payload)

    assert exc.value.error_code == "WRONG_PASSWORD"
