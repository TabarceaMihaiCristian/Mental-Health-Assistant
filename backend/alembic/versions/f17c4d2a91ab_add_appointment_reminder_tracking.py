"""Add reminder tracking metadata to appointments and notifications."""

# pylint: disable=no-member,invalid-name

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f17c4d2a91ab"
down_revision = "e8d93f2f4b12"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add appointment-linked notification support and reminder timestamps."""

    op.add_column(
        "appointments",
        sa.Column("reminder_sent_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "notifications",
        sa.Column("appointment_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_notifications_appointment_id_appointments",
        "notifications",
        "appointments",
        ["appointment_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        op.f("ix_notifications_appointment_id"),
        "notifications",
        ["appointment_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove appointment-linked notification support and reminder timestamps."""

    op.drop_index(op.f("ix_notifications_appointment_id"), table_name="notifications")
    op.drop_constraint(
        "fk_notifications_appointment_id_appointments",
        "notifications",
        type_="foreignkey",
    )
    op.drop_column("notifications", "appointment_id")
    op.drop_column("appointments", "reminder_sent_at")
