# src/app/middleware/auth.py
"""
Role-based access control helpers.

These are FastAPI dependency factories, not ASGI middleware.
They are used at router or route level via `dependencies=[...]`.
"""

from __future__ import annotations

from typing import Any

from fastapi import Depends

from app.dependencies import get_current_user
from app.exceptions import ForbiddenError
from app.models.user import User, UserRole


def require_role(*roles: UserRole) -> Any:
    """Return a FastAPI dependency that enforces at least one of the given roles.

    Usage
    -----
    router = APIRouter(dependencies=[require_role(UserRole.ADMIN)])

    Raises
    ------
    ForbiddenError (403)
        If the authenticated user does not have one of the required roles.
    """

    async def _check(user: User = Depends(get_current_user)) -> User:
        user_roles = {UserRole(r) for r in user.roles}
        if not any(role in user_roles for role in roles):
            raise ForbiddenError(
                detail="You do not have permission to access this resource.",
                error_code="FORBIDDEN",
            )
        return user

    return Depends(_check)


def require_authorized_lecturer() -> Any:
    """Return a FastAPI dependency that enforces lecturer role AND authorization.

    Lecturers self-register but cannot access lecturer routes until an Admin
    sets is_authorized=True on their account.

    Raises
    ------
    ForbiddenError (403)
        If not a lecturer, or lecturer is not yet authorized.
    """

    async def _check(user: User = Depends(get_current_user)) -> User:
        if UserRole.LECTURER.value not in user.roles:
            raise ForbiddenError(
                detail="Only lecturers can access this resource.",
                error_code="FORBIDDEN",
            )
        if not user.is_authorized:
            raise ForbiddenError(
                detail="Your lecturer account has not been authorized by an Admin yet.",
                error_code="UNAUTHORIZED_LECTURER",
            )
        return user

    return Depends(_check)
