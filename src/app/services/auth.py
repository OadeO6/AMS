# src/app/services/auth.py
"""
AuthService — authentication and session management (AMS version).

Responsibilities:
- Register student and lecturer accounts.
- Validate credentials on login.
- Issue and refresh JWTs + Redis-backed refresh tokens.
- Invalidate refresh tokens on logout.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.core.security import create_access_token, verify_password
from app.exceptions import UnauthorizedError
from app.repositories.token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.schemas.auth import AccessTokenResponse, LoginRequest, TokenPair
from app.services.user import UserService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models.user import User
    from app.schemas.user import LecturerRegister, StudentRegister


class AuthService:
    """Handles all authentication-related operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._user_repo = UserRepository(session)
        self._token_repo = RefreshTokenRepository()
        self._user_service = UserService(session)

    # ------------------------------------------------------------------
    # Register
    # ------------------------------------------------------------------

    async def register_student(self, payload: StudentRegister) -> tuple[User, TokenPair]:
        """Create a new student account and immediately issue a token pair."""
        user = await self._user_service.create_student(payload)
        tokens = await self._issue_token_pair(user)
        return user, tokens

    async def register_lecturer(self, payload: LecturerRegister) -> tuple[User, TokenPair]:
        """Create a new lecturer account (unauthorized) and issue a token pair."""
        user = await self._user_service.create_lecturer(payload)
        tokens = await self._issue_token_pair(user)
        return user, tokens

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    async def login(self, payload: LoginRequest) -> TokenPair:
        """Validate credentials and return a token pair.

        Raises
        ------
        UnauthorizedError
            If the email is not found, the password is wrong, or the
            account is deactivated.
        """
        user = await self._user_repo.get_by_email(payload.email.lower())

        # Deliberately use the same error message for wrong email OR password
        # to prevent user-enumeration attacks.
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password", error_code="INVALID_CREDENTIALS")
        if not user.is_active:
            raise UnauthorizedError("Account is deactivated", error_code="ACCOUNT_DEACTIVATED")

        return await self._issue_token_pair(user)

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    async def refresh(self, refresh_token: str) -> AccessTokenResponse:
        """Issue a new access token given a valid refresh token.

        Raises
        ------
        UnauthorizedError
            If the refresh token is unknown or invalid.
        """
        user_id_str = await self._token_repo.get_user_id(refresh_token)
        if user_id_str is None:
            raise UnauthorizedError(
                "Invalid or expired refresh token", error_code="INVALID_REFRESH_TOKEN"
            )

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise UnauthorizedError("Malformed token data", error_code="INVALID_REFRESH_TOKEN")

        user = await self._user_repo.get_by_id(user_id)
        if user is None or not user.is_active:
            await self._token_repo.revoke(refresh_token)
            raise UnauthorizedError("User not found or deactivated", error_code="UNAUTHORIZED")

        access_token = create_access_token(subject=str(user.id))
        return AccessTokenResponse(access_token=access_token)

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------

    async def logout(self, refresh_token: str) -> None:
        """Immediately revoke the refresh token.

        Silently ignores unknown tokens so that double-logout is idempotent.
        """
        await self._token_repo.revoke(refresh_token)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _issue_token_pair(self, user: User) -> TokenPair:
        """Create both tokens and persist the refresh token in Redis."""
        access_token = create_access_token(subject=str(user.id))
        refresh_token = await self._token_repo.store(user.id)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)
