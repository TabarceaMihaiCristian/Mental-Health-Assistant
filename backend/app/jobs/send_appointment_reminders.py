"""Job entrypoint for sending appointment reminder notifications."""

from __future__ import annotations

from app.db.session import SessionLocal
from app.services.appointment_reminder_service import AppointmentReminderService


def main() -> None:
    """Run the appointment reminder job once and print the reminder count."""

    db = SessionLocal()
    try:
        sent_count = AppointmentReminderService(db).send_due_reminders()
        print(f"Sent {sent_count} appointment reminder(s).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
