"""add message id to risk events

Revision ID: b5f6a36ebd3b
Revises: e1d4c0b4f1a2
Create Date: 2026-04-01 15:05:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "b5f6a36ebd3b"
down_revision = "e1d4c0b4f1a2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add the triggering-message foreign key to risk events."""

    op.add_column(
        "risk_events",
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.create_index(op.f("ix_risk_events_message_id"), "risk_events", ["message_id"], unique=False)
    op.create_foreign_key(
        "fk_risk_events_message_id_chat_messages",
        "risk_events",
        "chat_messages",
        ["message_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Remove the triggering-message foreign key from risk events."""

    op.drop_constraint("fk_risk_events_message_id_chat_messages", "risk_events", type_="foreignkey")
    op.drop_index(op.f("ix_risk_events_message_id"), table_name="risk_events")
    op.drop_column("risk_events", "message_id")
