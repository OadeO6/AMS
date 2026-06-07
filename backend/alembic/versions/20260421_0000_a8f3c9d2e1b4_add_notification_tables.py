"""Add notification and user_device_tokens tables.

Revision ID: a8f3c9d2e1b4
Revises: 3f7e2a91c4d5
Create Date: 2026-04-21 00:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a8f3c9d2e1b4"
down_revision: Union[str, None] = "3f7e2a91c4d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # notifications
    # ------------------------------------------------------------------
    # Drop existing notifications table from initial schema
    op.drop_table("notifications")
    
    op.create_table(
        "notifications",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="Surrogate PK — UUID generated application-side.",
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="Owner of this notification.",
        ),
        sa.Column(
            "event",
            sa.String(length=100),
            nullable=False,
            comment="Dot-notated event name, e.g. grade.published.",
        ),
        sa.Column(
            "channel",
            sa.String(length=20),
            nullable=False,
            comment="Delivery channel: inapp | email | push | sms.",
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Arbitrary JSON payload for deep-linking.",
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
            comment="pending | sent | failed | read.",
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_event", "notifications", ["event"])
    op.create_index("ix_notifications_status", "notifications", ["status"])
    # Composite index for the most common query: user's unread in-app notifications
    op.create_index(
        "ix_notifications_user_channel_status",
        "notifications",
        ["user_id", "channel", "status"],
    )

    # ------------------------------------------------------------------
    # user_device_tokens
    # ------------------------------------------------------------------
    op.create_table(
        "user_device_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "token",
            sa.Text(),
            nullable=False,
            comment="Raw FCM token or JSON-serialised Web Push subscription.",
        ),
        sa.Column(
            "platform",
            sa.String(length=20),
            nullable=False,
            comment="fcm | web",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token", name="uq_user_device_tokens_token"),
    )
    op.create_index("ix_user_device_tokens_user_id", "user_device_tokens", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_device_tokens_user_id", table_name="user_device_tokens")
    op.drop_table("user_device_tokens")

    op.drop_index("ix_notifications_user_channel_status", table_name="notifications")
    op.drop_index("ix_notifications_status", table_name="notifications")
    op.drop_index("ix_notifications_event", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
