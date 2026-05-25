"""Create a past confirmed appointment for E2E isolation."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.appointment import Appointment
from app.models.enums import AppointmentActorRole, AppointmentMode, AppointmentStatus
from app.models.specialist import Specialist
from app.models.user import User


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user-email", required=True)
    parser.add_argument("--specialist-email", required=True)
    parser.add_argument("--notes", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    session = SessionLocal()

    try:
        user = session.scalar(select(User).where(User.email == args.user_email))
        specialist_user = session.scalar(select(User).where(User.email == args.specialist_email))
        if user is None:
            raise ValueError(f"User not found: {args.user_email}")
        if specialist_user is None:
            raise ValueError(f"Specialist user not found: {args.specialist_email}")

        specialist = session.scalar(select(Specialist).where(Specialist.user_id == specialist_user.id))
        if specialist is None:
            raise ValueError(f"Specialist profile not found for: {args.specialist_email}")

        start_datetime = datetime.now(UTC) - timedelta(days=1, hours=2)
        end_datetime = start_datetime + timedelta(hours=2)

        appointment = Appointment(
            user_id=user.id,
            specialist_id=specialist.id,
            mode=AppointmentMode.ONLINE,
            status=AppointmentStatus.CONFIRMED,
            preferred_datetime=start_datetime,
            end_datetime=end_datetime,
            notes=args.notes,
            confirmed_at=start_datetime - timedelta(hours=1),
            last_rescheduled_by_role=AppointmentActorRole.SPECIALIST,
            status_updated_by_user_id=specialist_user.id,
        )
        session.add(appointment)
        session.commit()
        print(str(appointment.id))
    finally:
        session.close()


if __name__ == "__main__":
    main()
