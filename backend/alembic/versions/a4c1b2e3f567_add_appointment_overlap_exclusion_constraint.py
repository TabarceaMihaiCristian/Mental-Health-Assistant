"""Add a database-level overlap guard for active specialist appointments."""

# pylint: disable=no-member,invalid-name

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "a4c1b2e3f567"
down_revision = "f17c4d2a91ab"
branch_labels = None
depends_on = None

OVERLAP_CONSTRAINT_NAME = "appointments_no_active_overlap"


def upgrade() -> None:
    """Prevent overlapping requested and confirmed appointments per specialist."""

    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute(
        f"""
        ALTER TABLE appointments
        ADD CONSTRAINT {OVERLAP_CONSTRAINT_NAME}
        EXCLUDE USING gist (
            specialist_id WITH =,
            tstzrange(preferred_datetime, end_datetime, '[)') WITH &&
        )
        WHERE (
            status IN (
                'REQUESTED'::appointment_status,
                'CONFIRMED'::appointment_status
            )
        )
        """
    )


def downgrade() -> None:
    """Remove the database-level overlap guard for active appointments."""

    op.execute(
        f"""
        ALTER TABLE appointments
        DROP CONSTRAINT IF EXISTS {OVERLAP_CONSTRAINT_NAME}
        """
    )
