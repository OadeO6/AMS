"""Add offering_lecturers junction table and migrate existing lecturer_id data.

Revision ID: 3f7e2a91c4d5
Revises: 62bd1310aaef
Create Date: 2026-04-19 18:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3f7e2a91c4d5"
down_revision: str | None = "62bd1310aaef"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create the new junction table
    op.create_table(
        "offering_lecturers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        ),
        sa.Column(
            "offering_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("course_offerings.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "lecturer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # 2. Data migration: copy existing offering.lecturer_id → offering_lecturers rows
    conn = op.get_bind()
    results = conn.execute(
        sa.text(
            "SELECT id, lecturer_id FROM course_offerings WHERE lecturer_id IS NOT NULL"
        )
    )
    rows = results.fetchall()
    for offering_id, lecturer_id in rows:
        conn.execute(
            sa.text(
                "INSERT INTO offering_lecturers (id, offering_id, lecturer_id) "
                "VALUES (:id, :offering_id, :lecturer_id)"
            ),
            {"id": str(uuid.uuid4()), "offering_id": str(offering_id), "lecturer_id": str(lecturer_id)},
        )

    # 3. Drop the lecturer_id column from course_offerings
    op.drop_column("course_offerings", "lecturer_id")


def downgrade() -> None:
    # 1. Re-add lecturer_id column (nullable)
    op.add_column(
        "course_offerings",
        sa.Column(
            "lecturer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    # 2. Data migration back: take the first lecturer per offering (arbitrary if multiple)
    conn = op.get_bind()
    results = conn.execute(
        sa.text(
            "SELECT DISTINCT ON (offering_id) offering_id, lecturer_id "
            "FROM offering_lecturers ORDER BY offering_id, created_at"
        )
    )
    for offering_id, lecturer_id in results.fetchall():
        conn.execute(
            sa.text(
                "UPDATE course_offerings SET lecturer_id = :lecturer_id WHERE id = :offering_id"
            ),
            {"lecturer_id": str(lecturer_id), "offering_id": str(offering_id)},
        )

    # 3. Drop the junction table
    op.drop_table("offering_lecturers")
