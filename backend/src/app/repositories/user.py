from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models.user import User
from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    import uuid

    from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(BaseRepository[User]):
    """Async repository for the ``users`` table."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    # ------------------------------------------------------------------
    # Domain-specific lookups
    # ------------------------------------------------------------------

    async def get_by_email(self, email: str) -> User | None:
        """Return the user with the given email, or ``None``."""
        result = await self._session.scalars(select(User).where(User.email == email).limit(1))
        return result.first()

    async def get_by_id(self, pk: uuid.UUID) -> User | None:  # type: ignore[override]
        """Override to narrow the ``pk`` type to ``uuid.UUID`` and load relationship manually."""
        from app.models.department import Department

        stmt = (
            select(User, Department)
            .outerjoin(Department, User.department_id == Department.id)
            .where(User.id == pk)
        )
        result = await self._session.execute(stmt)
        row = result.first()
        if not row:
            return None

        user, dept = row
        user.department = dept  # Attach manually for Pydantic validation
        return user

    async def exists_by_email(self, email: str) -> bool:
        """Return ``True`` if a user with this email already exists."""
        result = await self._session.scalars(select(User.id).where(User.email == email).limit(1))
        return result.first() is not None

    async def list_users(
        self,
        *,
        role: str | None = None,
        department_id: uuid.UUID | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[int, list[User]]:
        """List users with filtering and pagination."""
        from sqlalchemy import func, or_
        from app.models.department import Department

        stmt = select(User, Department).outerjoin(Department, User.department_id == Department.id)
        count_stmt = select(func.count()).select_from(User)

        if role:
            # NOTE: need review
            stmt = stmt.where(User.roles.contains([role]))
            count_stmt = count_stmt.where(User.roles.contains([role]))
        if department_id:
            stmt = stmt.where(User.department_id == department_id)
            count_stmt = count_stmt.where(User.department_id == department_id)
        if search:
            search_filter = or_(
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        stmt = stmt.order_by(User.created_at.desc()).offset(skip).limit(limit)

        total = await self._session.scalar(count_stmt) or 0
        result = await self._session.execute(stmt)

        users = []
        for user, dept in result.all():
            user.department = dept
            users.append(user)

        return total, users
