"""Normalize enum labels to the SQLAlchemy enum contract."""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "f2c7e9b4a1d3"
down_revision = "b9e3c6d4a1f2"
branch_labels = None
depends_on = None


def _rename_enum_value(type_name: str, old_value: str, new_value: str) -> None:
    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_enum enum
                JOIN pg_type typ ON enum.enumtypid = typ.oid
                WHERE typ.typname = '{type_name}' AND enum.enumlabel = '{old_value}'
            ) THEN
                ALTER TYPE {type_name} RENAME VALUE '{old_value}' TO '{new_value}';
            END IF;
        END $$;
        """
    )


def upgrade() -> None:
    """Rename drifted lowercase enum labels to the model-backed uppercase names."""

    _rename_enum_value("appointment_status", "rejected", "REJECTED")

    _rename_enum_value("appointment_actor_role", "user", "USER")
    _rename_enum_value("appointment_actor_role", "specialist", "SPECIALIST")
    _rename_enum_value("appointment_actor_role", "admin", "ADMIN")

    _rename_enum_value("notification_type", "appointment_requested", "APPOINTMENT_REQUESTED")
    _rename_enum_value("notification_type", "appointment_confirmed", "APPOINTMENT_CONFIRMED")
    _rename_enum_value("notification_type", "appointment_rejected", "APPOINTMENT_REJECTED")
    _rename_enum_value("notification_type", "appointment_rescheduled", "APPOINTMENT_RESCHEDULED")
    _rename_enum_value("notification_type", "appointment_cancelled", "APPOINTMENT_CANCELLED")
    _rename_enum_value("notification_type", "appointment_reminder", "APPOINTMENT_REMINDER")


def downgrade() -> None:
    """Restore the lowercase enum labels used by the drifted schema."""

    _rename_enum_value("appointment_status", "REJECTED", "rejected")

    _rename_enum_value("appointment_actor_role", "USER", "user")
    _rename_enum_value("appointment_actor_role", "SPECIALIST", "specialist")
    _rename_enum_value("appointment_actor_role", "ADMIN", "admin")

    _rename_enum_value("notification_type", "APPOINTMENT_REQUESTED", "appointment_requested")
    _rename_enum_value("notification_type", "APPOINTMENT_CONFIRMED", "appointment_confirmed")
    _rename_enum_value("notification_type", "APPOINTMENT_REJECTED", "appointment_rejected")
    _rename_enum_value("notification_type", "APPOINTMENT_RESCHEDULED", "appointment_rescheduled")
    _rename_enum_value("notification_type", "APPOINTMENT_CANCELLED", "appointment_cancelled")
    _rename_enum_value("notification_type", "APPOINTMENT_REMINDER", "appointment_reminder")
