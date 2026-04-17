# src/app/dependencies.py
"""
Shared FastAPI dependency injection helpers.

Import and use via:
    from app.dependencies import CurrentUser, DBSession
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import decode_access_token
from app.exceptions import ForbiddenError, UnauthorizedError
from app.models.user import User, UserRole
from app.repositories.user import UserRepository

# HTTPBearer scheme — tells Swagger UI to expect a raw Bearer token
bearer_scheme = HTTPBearer()


async def get_current_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    """Validate the Bearer JWT and return the authenticated User.

    Steps:
    1. Extract + decode the JWT (raises 401 if expired / invalid).
    2. Parse subject as UUID (raises 401 if malformed).
    3. Load the user from DB (raises 401 if not found or inactive).

    Protected routers declare this at router level:
        router = APIRouter(dependencies=[Depends(get_current_user)])

    Route handlers that also need the user object inject it directly:
        async def me(current_user: CurrentUser) -> UserPublic: ...
    """
    user_id_str = decode_access_token(token.credentials)

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedError("Invalid token subject — expected a UUID")

    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)

    if user is None:
        raise UnauthorizedError("User not found")
    if not user.is_active:
        raise UnauthorizedError("User account is deactivated")

    return user


async def get_authorized_lecturer(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Validate that the current user is a lecturer AND is authorized.

    Raises
    ------
    ForbiddenError
        If the user is not a lecturer or hasn't been authorized by an Admin.
    """
    if current_user.role != UserRole.LECTURER:
        raise ForbiddenError("Only lecturers can access this resource", error_code="FORBIDDEN")
    if not current_user.is_authorized:
        raise ForbiddenError("Lecturer account is pending authorization", error_code="UNAUTHORIZED_LECTURER")
    return current_user


async def get_student(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Validate that the current user is a student."""
    if current_user.role != UserRole.STUDENT:
        raise ForbiddenError("Only students can access this resource", error_code="FORBIDDEN")
    return current_user


# ---------------------------------------------------------------------------
# Annotated shorthand aliases — use these in route function signatures.
# ---------------------------------------------------------------------------

# Injects and validates the current user; raises 401 on any failure.
CurrentUser = Annotated[User, Depends(get_current_user)]

# Injects and validates an authorized lecturer; raises 401/403 on failure.
AuthorizedLecturer = Annotated[User, Depends(get_authorized_lecturer)]

# Injects and validates a student; raises 401/403 on failure.
AuthorizedStudent = Annotated[User, Depends(get_student)]

# Injects a transactional DB session; auto-commits / rolls back.
DBSession = Annotated[AsyncSession, Depends(get_db_session)]

