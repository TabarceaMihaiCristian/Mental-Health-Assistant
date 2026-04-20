"""Add appointment audit metadata and in-app notifications."""

# pylint: disable=no-member,invalid-name

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e8d93f2f4b12"
down_revision = "d2a8e8d59811"
branch_labels = None
depends_on = None

USERS_TABLE_ID = "users.id"


def upgrade() -> None:
    """Add appointment audit metadata and create notifications."""

    op.execute("ALTER TYPE appointment_status ADD VALUE IF NOT EXISTS 'rejected'")

    appointment_actor_role_enum = postgresql.ENUM(
        "user",
        "specialist",
        "admin",
        name="appointment_actor_role",
    )
    notification_type_enum = postgresql.ENUM(
        "appointment_requested",
        "appointment_confirmed",
        "appointment_rejected",
        "appointment_rescheduled",
        "appointment_cancelled",
        "appointment_reminder",
        name="notification_type",
    )
    appointment_actor_role_enum.create(op.get_bind(), checkfirst=True)
    notification_type_enum.create(op.get_bind(), checkfirst=True)
    notification_type_existing_enum = postgresql.ENUM(
        "appointment_requested",
        "appointment_confirmed",
        "appointment_rejected",
        "appointment_rescheduled",
        "appointment_cancelled",
        "appointment_reminder",
        name="notification_type",
        create_type=False,
    )

    op.add_column(
        "appointments",
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column("last_rescheduled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column(
            "last_rescheduled_by_role",
            appointment_actor_role_enum,
            nullable=True,
        ),
    )
    op.add_column(
        "appointments",
        sa.Column("status_updated_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_appointments_status_updated_by_user_id_users",
        "appointments",
        "users",
        ["status_updated_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_appointments_status_updated_by_user_id"),
        "appointments",
        ["status_updated_by_user_id"],
        unique=False,
    )

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", notification_type_existing_enum, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_notifications_user_id"),
        "notifications",
        ["user_id"],
        unique=False,
    )
    op.alter_column("notifications", "is_read", server_default=None)


def downgrade() -> None:
    """Remove appointment audit metadata and drop notifications."""

    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_table("notifications")

    op.drop_index(
        op.f("ix_appointments_status_updated_by_user_id"),
        table_name="appointments",
    )
    op.drop_constraint(
        "fk_appointments_status_updated_by_user_id_users",
        "appointments",
        type_="foreignkey",
    )
    op.drop_column("appointments", "status_updated_by_user_id")
    op.drop_column("appointments", "last_rescheduled_by_role")
    op.drop_column("appointments", "last_rescheduled_at")
    op.drop_column("appointments", "completed_at")
    op.drop_column("appointments", "cancelled_at")
    op.drop_column("appointments", "rejected_at")
    op.drop_column("appointments", "confirmed_at")

    notification_type_enum = postgresql.ENUM(name="notification_type")
    appointment_actor_role_enum = postgresql.ENUM(name="appointment_actor_role")
    notification_type_enum.drop(op.get_bind(), checkfirst=True)
    appointment_actor_role_enum.drop(op.get_bind(), checkfirst=True)
