"""Application service for sending appointment reminder notifications."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.db.unit_of_work import UnitOfWork
from app.models.appointment import Appointment
from app.models.enums import NotificationType
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.specialist_repository import SpecialistRepository
from app.services.notification_service import NotificationService
from app.utils.logging import get_app_logger, log_event


class AppointmentReminderService:
    """Create in-app reminders for upcoming confirmed appointments."""

    def __init__(self, db: Session) -> None:
        """Bind reminder workflows to one SQLAlchemy session."""

        self.db = db
        self.uow = UnitOfWork(db)
        self.appointment_repository = AppointmentRepository(db)
        self.specialist_repository = SpecialistRepository(db)
        self.notification_service = NotificationService(db)
        self.logger = get_app_logger(__name__)

    def send_due_reminders(self, lead_time: timedelta = timedelta(days=1)) -> int:
        """Send reminders for confirmed appointments starting within the lead window."""

        now = datetime.now(UTC)
        window_end = now + lead_time
        appointments = self.appointment_repository.list_confirmed_starting_between(
            now,
            window_end,
        )

        sent_count = 0
        for appointment in appointments:
            self._send_reminders_for_appointment(appointment)
            appointment.reminder_sent_at = now
            sent_count += 1

        if sent_count:
            self.uow.commit()
        log_event(
            self.logger,
            "appointments.reminders.sent",
            count=sent_count,
            window_end=window_end.isoformat(),
        )
        return sent_count

    def _send_reminders_for_appointment(self, appointment: Appointment) -> None:
        """Send user and specialist reminders for a single appointment."""

        self.notification_service.create_unique_notification(
            user_id=appointment.user_id,
            notification_type=NotificationType.APPOINTMENT_REMINDER,
            title="Appointment reminder",
            message="You have an appointment scheduled within the next 24 hours.",
            appointment_id=appointment.id,
        )

        specialist = self.specialist_repository.get_by_id(appointment.specialist_id)
        if specialist is not None and specialist.user_id is not None:
            self.notification_service.create_unique_notification(
                user_id=specialist.user_id,
                notification_type=NotificationType.APPOINTMENT_REMINDER,
                title="Appointment reminder",
                message="You have a specialist appointment scheduled within the next 24 hours.",
                appointment_id=appointment.id,
            )
