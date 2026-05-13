# src/app/models/base.py
"""
Shared SQLAlchemy base and mixins inherited by all ORM models.

All models MUST:
    class MyModel(Base, TimestampMixin):
        __tablename__ = "my_table"
        ...

Never use the legacy Column() API — always use Mapped[T] + mapped_column().
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models.

    Alembic's autogenerate reads ``Base.metadata`` to detect schema changes.
    All models must be imported in ``src/app/models/__init__.py`` so their
    tables are registered before any migration runs.
    """


class TimestampMixin:
    """Mixin that adds server-managed ``created_at`` / ``updated_at`` columns.

    * ``created_at`` is set once by the DB server on INSERT.
    * ``updated_at`` is set by the DB server on INSERT and refreshed on UPDATE.

    Both columns are timezone-aware and non-nullable.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="UTC timestamp of row creation (set by the DB server).",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="UTC timestamp of last update (refreshed by the DB server on UPDATE).",
    )
