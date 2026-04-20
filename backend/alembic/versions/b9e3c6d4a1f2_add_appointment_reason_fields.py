"""Add appointment cancellation, rejection, and reschedule reason fields."""

# pylint: disable=no-member,invalid-name

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "b9e3c6d4a1f2"
down_revision = "a4c1b2e3f567"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add reason fields used for clearer appointment audit trails."""

    op.add_column(
        "appointments",
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column("rejection_reason", sa.Text(), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column("reschedule_note", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Remove reason fields from appointments."""

    op.drop_column("appointments", "reschedule_note")
    op.drop_column("appointments", "rejection_reason")
    op.drop_column("appointments", "cancellation_reason")
