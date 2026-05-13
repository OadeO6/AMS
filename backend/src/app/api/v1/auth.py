# src/app/api/v1/auth.py
"""
Auth endpoints — AMS version.

Unauthenticated (except /logout, /me, /me/*):
  POST /auth/register/student
  POST /auth/register/lecturer
  POST /auth/login
  POST /auth/refresh
  POST /auth/forgot-password
  POST /auth/reset-password

Authenticated (Bearer JWT):
  POST   /auth/logout
  GET    /auth/me
  PATCH  /auth/me
  PATCH  /auth/me/student
  PATCH  /auth/me/lecturer
  PATCH  /auth/me/password
"""

from __future__ import annotations

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.dependencies import CurrentUser, DBSession
from app.schemas.auth import (
    AccessTokenResponse,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    ResetPasswordRequest,
    ResetPasswordRequest,
    TokenPair,
    MessageResponse,
)
from app.schemas.user import (
    LecturerRegister,
    LecturerUpdate,
    PasswordUpdate,
    StudentRegister,
    StudentUpdate,
    UserPublic,
    UserUpdate,
    UpdateMeResponse,
    UpdateStudentProfileResponse,
    UpdateLecturerProfileResponse,
)
from app.services.auth import AuthService
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


@router.post(
    "/register/student",
    response_model=TokenPair,
    summary="Register a student account",
    status_code=status.HTTP_201_CREATED,
)
async def register_student(payload: StudentRegister, session: DBSession) -> TokenPair:
    """Create a new student account and return a token pair."""
    # TODO: Spec originally returned MessageResponse. TokenPair kept for PR feedback.
    _, tokens = await AuthService(session).register_student(payload)
    return tokens


@router.post(
    "/register/lecturer",
    response_model=TokenPair,
    summary="Register a lecturer account (starts unauthorized)",
    status_code=status.HTTP_201_CREATED,
)
async def register_lecturer(payload: LecturerRegister, session: DBSession) -> TokenPair:
    """Create a new lecturer account.

    The account is created with is_authorized=False.
    The lecturer cannot access protected routes until an Admin authorizes them.
    """
    # TODO: Spec originally returned MessageResponse. TokenPair kept for PR feedback.
    _, tokens = await AuthService(session).register_lecturer(payload)
    return tokens


# ---------------------------------------------------------------------------
# Login / Tokens
# ---------------------------------------------------------------------------


@router.post(
    "/login",
    response_model=TokenPair,
    summary="Login with email and password",
    status_code=status.HTTP_200_OK,
)
async def login(payload: LoginRequest, session: DBSession) -> TokenPair:
    """Validate credentials and return an access + refresh token pair."""
    return await AuthService(session).login(payload)


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Refresh access token",
    status_code=status.HTTP_200_OK,
)
async def refresh_token(payload: RefreshRequest, session: DBSession) -> AccessTokenResponse:
    """Exchange a valid refresh token for a new access token."""
    return await AuthService(session).refresh(payload.refresh_token)


@router.post(
    "/logout",
    summary="Logout — invalidate refresh token",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    payload: RefreshRequest,
    _: CurrentUser,
    session: DBSession,
) -> None:
    """Revoke the refresh token. The short-lived access token expires on its own."""
    await AuthService(session).logout(payload.refresh_token)


# ---------------------------------------------------------------------------
# Password recovery
# ---------------------------------------------------------------------------


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(payload: ForgotPasswordRequest, session: DBSession) -> JSONResponse:
    """Request a password reset link (returns 200 even if email not found)."""
    svc = AuthService(session)
    await svc.forgot_password(payload.email)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "If that email exists, a reset link was sent."},
    )


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(payload: ResetPasswordRequest, session: DBSession) -> JSONResponse:
    """Reset password using a token."""
    svc = AuthService(session)
    await svc.reset_password(payload.token, payload.new_password)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Password updated successfully."},
    )


# ---------------------------------------------------------------------------
# Authenticated user profile
# ---------------------------------------------------------------------------


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get my profile",
    status_code=status.HTTP_200_OK,
)
async def get_me(current_user: CurrentUser) -> UserPublic:
    """Return the profile of the currently authenticated user."""
    # TODO: Spec specifies StudentPublicMe / LecturerPublicMe. Keeping UserPublic for now.
    return UserPublic.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UpdateMeResponse,
    summary="Update my profile (common fields)",
    status_code=status.HTTP_200_OK,
)
async def update_me(
    payload: UserUpdate,
    current_user: CurrentUser,
    session: DBSession,
) -> UpdateMeResponse:
    """Partially update first_name, last_name, phone, or avatar."""
    svc = UserService(session)
    updated = await svc.update_profile(current_user.id, payload)
    return UpdateMeResponse(
        message="Profile updated",
        user=UserPublic.model_validate(updated)
    )


@router.patch(
    "/me/student",
    response_model=UpdateStudentProfileResponse,
    summary="Update student-specific profile fields",
    status_code=status.HTTP_200_OK,
)
async def update_me_student(
    payload: StudentUpdate,
    current_user: CurrentUser,
    session: DBSession,
) -> UpdateStudentProfileResponse:
    """Student-specific profile patch (admission_year)."""
    svc = UserService(session)
    updated = await svc.update_student_profile(current_user.id, payload)
    return UpdateStudentProfileResponse(
        message="Profile updated successfully.",
        user={"id": updated.id, "matric_num": updated.matric_num, "admission_session": updated.admission_session}
    )


@router.patch(
    "/me/lecturer",
    response_model=UpdateLecturerProfileResponse,
    summary="Update lecturer-specific profile fields",
    status_code=status.HTTP_200_OK,
)
async def update_me_lecturer(
    payload: LecturerUpdate,
    current_user: CurrentUser,
    session: DBSession,
) -> UpdateLecturerProfileResponse:
    """Partially update lecturer-specific fields (staff_id)."""
    svc = UserService(session)
    updated = await svc.update_lecturer_profile(current_user.id, payload)
    return UpdateLecturerProfileResponse(
        message="Profile updated successfully.",
        user={"id": updated.id, "staff_id": updated.staff_id}
    )


@router.patch(
    "/me/password",
    response_model=MessageResponse,
    summary="Change my password",
    status_code=status.HTTP_200_OK,
)
async def change_password(
    payload: PasswordUpdate,
    current_user: CurrentUser,
    session: DBSession,
) -> JSONResponse:
    """Verify current_password then set new_password."""
    svc = UserService(session)
    await svc.change_password(current_user.id, payload)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Password updated."},
    )
