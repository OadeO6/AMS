# alembic/env.py
"""
Alembic migration environment — async SQLAlchemy 2.x edition.

How it works
------------
1. ``sqlalchemy.url`` in alembic.ini is a placeholder only.
2. This file overrides it with ``settings.DATABASE_URL`` at runtime.
3. ``target_metadata`` is set to ``Base.metadata`` so that
   ``alembic revision --autogenerate`` can diff the live DB against the ORM.
4. All ORM models MUST be imported (via ``app.models``) before the metadata
   is read, otherwise Alembic won't detect their tables.

Running migrations
------------------
    # Apply all pending migrations
    uv run alembic upgrade head

    # Generate a new migration from ORM changes
    uv run alembic revision --autogenerate -m "describe your change"

    # Roll back one migration
    uv run alembic downgrade -1
"""

from __future__ import annotations

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------------------------------------------------------------------------
# Make ``src/`` importable when running alembic from the project root.
# ``prepend_sys_path = .`` in alembic.ini adds "." not "src/", so we add
# "src/" explicitly here.
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# ---------------------------------------------------------------------------
# Import settings and all ORM models.
# Models MUST be imported (even if unused) so their tables appear in
# Base.metadata before autogenerate runs.
# ---------------------------------------------------------------------------
from typing import TYPE_CHECKING

from app.config import settings
from app.models import Base

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection

# ---------------------------------------------------------------------------
# Alembic Config object — provides access to values in alembic.ini.
# ---------------------------------------------------------------------------
alembic_cfg = context.config

# Override the placeholder URL with the real one from environment / .env.
alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Attach Python logging config from alembic.ini (if present).
if alembic_cfg.config_file_name is not None:
    fileConfig(alembic_cfg.config_file_name)

# The metadata object that autogenerate will diff against.
target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline mode — generate SQL without a live DB connection.
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Useful for generating a SQL script to review before applying.
    """
    url = alembic_cfg.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online mode — requires a live async DB connection.
# ---------------------------------------------------------------------------
def do_run_migrations(connection: Connection) -> None:
    """Execute pending migrations within an existing connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # detect column type changes
        compare_server_default=True,  # detect server_default changes
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations through a sync proxy."""
    connectable = async_engine_from_config(
        alembic_cfg.get_section(alembic_cfg.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # no persistent pool needed for migrations
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online migration mode."""
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
