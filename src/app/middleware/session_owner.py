# src/app/middleware/session_owner.py
"""
Session owner guard dependency.

Restricts class session mutations to the lecturer who created the session.
This is a stub — the real query is implemented in Phase 8 (Sessions).
"""

from __future__ import annotations

import uuid

from fastapi import Depends

from app.dependencies import get_current_user
from app.exceptions import ForbiddenError
from app.models.user import User


async def require_session_owner(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
) -> None:
    """Raise 403 if the current user is not the session owner.

    Phase 1 stub — always raises ForbiddenError until Phase 8 wires the
    real ClassSession lookup.
    """
    # Phase 8 will replace this with:
    #   class_session = await session_repo.get_by_id(session_id)
    #   if class_session is None:
    #       raise NotFoundError("Session not found")
    #   if class_session.lecturer_id != current_user.id:
    #       raise ForbiddenError("Only the session owner can perform this action")
    _ = (session_id, current_user)
    raise ForbiddenError(
        detail="Session owner check not implemented in this phase.",
        error_code="FORBIDDEN",
    )
