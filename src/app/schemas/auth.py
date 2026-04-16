# src/app/schemas/auth.py
"""
Pydantic v2 schemas for the Auth domain.

Schemas
-------
LoginRequest          — email + password sent on POST /auth/login
TokenPair             — access + refresh tokens returned on login / register
AccessTokenResponse   — access-only token returned on POST /auth/refresh
RefreshRequest        — refresh token sent on POST /auth/refresh / logout
TokenPayload          — decoded JWT sub field (user ID string)
ForgotPasswordRequest — email sent on POST /auth/forgot-password
ResetPasswordRequest  — token + new_password sent on POST /auth/reset-password
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Credentials submitted to POST /api/v1/auth/login."""

    email: EmailStr
    password: str = Field(min_length=1)


class TokenPair(BaseModel):
    """Returned after a successful login or registration."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    """Returned by POST /api/v1/auth/refresh."""

    access_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Body of POST /auth/refresh and POST /auth/logout."""

    refresh_token: str


class TokenPayload(BaseModel):
    """Claims extracted from a decoded JWT.

    sub holds the user's UUID as a string (standard JWT claim).
    """

    sub: str


class ForgotPasswordRequest(BaseModel):
    """Body of POST /auth/forgot-password."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Body of POST /auth/reset-password."""

    token: str
    new_password: str = Field(min_length=8, max_length=128)
