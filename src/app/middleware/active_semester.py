# src/app/middleware/active_semester.py
"""
Active semester guard dependency.

Blocks any mutating operation on course resources when no semester is active.
This is a stub — the real query against the Semester table is implemented
in Phase 3 when the Semester model and repository are available.
"""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.exceptions import ForbiddenError


async def require_active_semester(
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Raise 403 if there is no currently active semester.

    Phase 1 stub — always raises ForbiddenError until Phase 3 wires the
    real Semester query.
    """
    # Phase 3 will replace this with:
    #   stmt = select(Semester).where(Semester.is_active.is_(True)).limit(1)
    #   active = await session.scalar(stmt)
    #   if active is None:
    #       raise ForbiddenError("No active semester", error_code="NO_ACTIVE_SEMESTER")
    _ = session  # session will be used in Phase 3
    raise ForbiddenError(
        detail="No active semester. Write operations are disabled.",
        error_code="NO_ACTIVE_SEMESTER",
    )
