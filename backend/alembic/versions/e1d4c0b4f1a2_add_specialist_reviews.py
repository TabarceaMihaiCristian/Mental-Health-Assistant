"""add specialist reviews

Revision ID: e1d4c0b4f1a2
Revises: 8456358a93e0
Create Date: 2026-04-01 14:40:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "e1d4c0b4f1a2"
down_revision = "8456358a93e0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create specialist reviews and supporting indexes."""

    op.create_table(
        "specialist_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("specialist_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rating", sa.SmallInteger(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_specialist_reviews_rating_range"),
        sa.ForeignKeyConstraint(["specialist_id"], ["specialists.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("specialist_id", "user_id", name="uq_specialist_reviews_specialist_user"),
    )
    op.create_index(
        op.f("ix_specialist_reviews_specialist_id"),
        "specialist_reviews",
        ["specialist_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_specialist_reviews_user_id"),
        "specialist_reviews",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop specialist reviews and supporting indexes."""

    op.drop_index(op.f("ix_specialist_reviews_user_id"), table_name="specialist_reviews")
    op.drop_index(op.f("ix_specialist_reviews_specialist_id"), table_name="specialist_reviews")
    op.drop_table("specialist_reviews")
