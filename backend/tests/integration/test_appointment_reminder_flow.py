"""Integration tests for appointment reminder notification delivery."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus, NotificationType
from app.models.notification import Notification
from app.models.specialist import Specialist
from app.models.user import User
from app.services.appointment_reminder_service import AppointmentReminderService


@pytest.mark.integration
def test_send_due_reminders_creates_notifications_and_marks_appointment(
    db_session: Session,
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
    appointment_factory: Callable[..., Appointment],
) -> None:
    """Create one reminder per participant and mark the appointment as reminded."""

    # Arrange
    user = user_factory()
    specialist = specialist_factory(full_name="Dr. Reminder")
    appointment = appointment_factory(
        user=user,
        specialist=specialist,
        preferred_datetime=datetime.now(UTC) + timedelta(hours=6),
        status=AppointmentStatus.CONFIRMED,
    )
    service = AppointmentReminderService(db_session)

    # Act
    sent_count = service.send_due_reminders(lead_time=timedelta(hours=24))

    # Assert
    assert sent_count == 1
    db_session.refresh(appointment)
    assert appointment.reminder_sent_at is not None

    notifications = db_session.scalars(
        select(Notification)
        .where(Notification.appointment_id == appointment.id)
        .order_by(Notification.created_at.asc())
    ).all()
    assert len(notifications) == 2
    assert {notification.user_id for notification in notifications} == {
        user.id,
        specialist.user_id,
    }
    assert {notification.type for notification in notifications} == {
        NotificationType.APPOINTMENT_REMINDER,
    }


@pytest.mark.integration
def test_send_due_reminders_is_idempotent_for_already_marked_appointments(
    db_session: Session,
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
    appointment_factory: Callable[..., Appointment],
) -> None:
    """Skip appointments that were already marked as reminded."""

    # Arrange
    user = user_factory()
    specialist = specialist_factory(full_name="Dr. Idempotent")
    appointment = appointment_factory(
        user=user,
        specialist=specialist,
        preferred_datetime=datetime.now(UTC) + timedelta(hours=8),
        status=AppointmentStatus.CONFIRMED,
    )
    appointment.reminder_sent_at = datetime.now(UTC)
    db_session.flush()
    service = AppointmentReminderService(db_session)

    # Act
    sent_count = service.send_due_reminders(lead_time=timedelta(hours=24))

    # Assert
    assert sent_count == 0
    notifications = db_session.scalars(
        select(Notification).where(Notification.appointment_id == appointment.id)
    ).all()
    assert notifications == []
