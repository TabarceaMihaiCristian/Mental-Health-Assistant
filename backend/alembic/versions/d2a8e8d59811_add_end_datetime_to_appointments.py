"""add end datetime to appointments

Revision ID: d2a8e8d59811
Revises: c3d7fa4b8e21
Create Date: 2026-04-02 14:15:00.000000
"""
# pylint: disable=no-member,invalid-name

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "d2a8e8d59811"
down_revision = "c3d7fa4b8e21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add explicit end times for fixed-duration appointments."""

    op.add_column(
        "appointments",
        sa.Column("end_datetime", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        """
        UPDATE appointments
        SET end_datetime = preferred_datetime + INTERVAL '2 hours'
        WHERE end_datetime IS NULL
        """
    )
    op.alter_column("appointments", "end_datetime", nullable=False)


def downgrade() -> None:
    """Remove the explicit appointment end-time column."""

    op.drop_column("appointments", "end_datetime")
