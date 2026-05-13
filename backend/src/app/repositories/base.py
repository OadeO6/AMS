# src/app/repositories/base.py
"""
Generic async CRUD base repository.

All domain repositories inherit from BaseRepository[ModelT] and call
``super().__init__(ModelT, session)`` to bind the model class.

Rules:
- Zero business logic here — pure DB access only.
- Always use ``select()`` + ``session.scalars()``; never ``Session.query()``.
- No raw SQL; ORM-only to prevent SQL injection by design.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from sqlalchemy import func, select

from app.models.base import Base

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository[ModelT: Base]:
    """Typed async CRUD repository.

    Parameters
    ----------
    model:
        The SQLAlchemy ORM class this repository manages.
    session:
        The injected ``AsyncSession`` for the current request.
    """

    def __init__(self, model: type[ModelT], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    async def get_by_id(self, pk: Any) -> ModelT | None:
        """Return a single row by primary key, or ``None`` if not found."""
        return await self._session.get(self._model, pk)

    async def list_paginated(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[ModelT], int]:
        """Return a page of rows and the total count.

        Returns
        -------
        (rows, total):
            ``rows`` — the current page; ``total`` — count of all matching rows.
        """
        total_scalar = await self._session.scalar(
            select(func.count()).select_from(self._model)  # type: ignore[arg-type]
        )
        total = int(total_scalar or 0)

        result = await self._session.scalars(select(self._model).offset(offset).limit(limit))
        return result.all(), total

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    async def create(self, **values: Any) -> ModelT:
        """Persist a new row and return the refreshed ORM instance."""
        instance = self._model(**values)
        self._session.add(instance)
        await self._session.flush()  # write to DB within the transaction
        await self._session.refresh(instance)  # load server-generated values
        return instance

    async def update(self, instance: ModelT, **values: Any) -> ModelT:
        """Apply ``values`` to ``instance``, flush, and return the updated row."""
        for key, val in values.items():
            setattr(instance, key, val)
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        """Delete ``instance`` from the DB within the current transaction."""
        await self._session.delete(instance)
        await self._session.flush()
