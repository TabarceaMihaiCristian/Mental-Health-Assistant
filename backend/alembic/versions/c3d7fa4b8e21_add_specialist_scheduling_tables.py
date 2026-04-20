"""add specialist scheduling tables

Revision ID: c3d7fa4b8e21
Revises: b5f6a36ebd3b
Create Date: 2026-04-02 11:30:00.000000
"""
# pylint: disable=no-member,invalid-name

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "c3d7fa4b8e21"
down_revision = "b5f6a36ebd3b"
branch_labels = None
depends_on = None
SPECIALISTS_TABLE_ID = "specialists.id"


def upgrade() -> None:
    """Create the specialist scheduling tables and indexes."""

    op.create_table(
        "specialist_availability_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("specialist_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("weekday", sa.SmallInteger(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "weekday >= 0 AND weekday <= 6",
            name="ck_specialist_availability_weekday",
        ),
        sa.ForeignKeyConstraint(["specialist_id"], [SPECIALISTS_TABLE_ID], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_specialist_availability_rules_specialist_id"),
        "specialist_availability_rules",
        ["specialist_id"],
        unique=False,
    )

    op.create_table(
        "specialist_breaks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("specialist_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("weekday", sa.SmallInteger(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "weekday >= 0 AND weekday <= 6",
            name="ck_specialist_breaks_weekday",
        ),
        sa.ForeignKeyConstraint(["specialist_id"], [SPECIALISTS_TABLE_ID], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_specialist_breaks_specialist_id"),
        "specialist_breaks",
        ["specialist_id"],
        unique=False,
    )

    op.create_table(
        "specialist_time_off",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("specialist_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["specialist_id"], [SPECIALISTS_TABLE_ID], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_specialist_time_off_specialist_id"),
        "specialist_time_off",
        ["specialist_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the specialist scheduling tables and indexes."""

    op.drop_index(
        op.f("ix_specialist_time_off_specialist_id"),
        table_name="specialist_time_off",
    )
    op.drop_table("specialist_time_off")
    op.drop_index(
        op.f("ix_specialist_breaks_specialist_id"),
        table_name="specialist_breaks",
    )
    op.drop_table("specialist_breaks")
    op.drop_index(
        op.f("ix_specialist_availability_rules_specialist_id"),
        table_name="specialist_availability_rules",
    )
    op.drop_table("specialist_availability_rules")
