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
from app.exceptions import UnauthorizedError
from app.models.user import User
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


# ---------------------------------------------------------------------------
# Annotated shorthand aliases — use these in route function signatures.
# ---------------------------------------------------------------------------

# Injects and validates the current user; raises 401 on any failure.
CurrentUser = Annotated[User, Depends(get_current_user)]

# Injects a transactional DB session; auto-commits / rolls back.
DBSession = Annotated[AsyncSession, Depends(get_db_session)]
