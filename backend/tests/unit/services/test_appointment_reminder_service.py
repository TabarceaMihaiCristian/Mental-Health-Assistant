"""Unit tests for appointment reminder delivery."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.models.appointment import Appointment
from app.models.enums import AppointmentMode, AppointmentStatus, NotificationType
from app.services.appointment_reminder_service import AppointmentReminderService


def _appointment() -> Appointment:
    appointment = Appointment(
        user_id=uuid4(),
        specialist_id=uuid4(),
        mode=AppointmentMode.ONLINE,
        status=AppointmentStatus.CONFIRMED,
        preferred_datetime=datetime(2026, 4, 21, 9, tzinfo=UTC),
        end_datetime=datetime(2026, 4, 21, 10, tzinfo=UTC),
        status_updated_by_user_id=uuid4(),
    )
    appointment.id = uuid4()
    return appointment


@pytest.mark.unit
def test_send_due_reminders_marks_appointments_and_commits() -> None:
    """Mark due appointments as reminded and commit once after processing."""

    service = object.__new__(AppointmentReminderService)
    service.uow = Mock()
    service.logger = Mock()
    service.appointment_repository = Mock()
    service.specialist_repository = Mock()
    service.notification_service = Mock()
    first_appointment = _appointment()
    second_appointment = _appointment()
    service.appointment_repository.list_confirmed_starting_between.return_value = [
        first_appointment,
        second_appointment,
    ]
    service._send_reminders_for_appointment = Mock()

    sent_count = service.send_due_reminders(timedelta(hours=12))

    assert sent_count == 2
    assert first_appointment.reminder_sent_at is not None
    assert second_appointment.reminder_sent_at is not None
    service._send_reminders_for_appointment.assert_any_call(first_appointment)
    service._send_reminders_for_appointment.assert_any_call(second_appointment)
    service.uow.commit.assert_called_once()


@pytest.mark.unit
def test_send_due_reminders_skips_commit_when_nothing_is_due() -> None:
    """Avoid unnecessary writes when the reminder window is empty."""

    service = object.__new__(AppointmentReminderService)
    service.uow = Mock()
    service.logger = Mock()
    service.appointment_repository = Mock()
    service.specialist_repository = Mock()
    service.notification_service = Mock()
    service.appointment_repository.list_confirmed_starting_between.return_value = []

    sent_count = service.send_due_reminders()

    assert sent_count == 0
    service.uow.commit.assert_not_called()


@pytest.mark.unit
def test_send_reminders_for_appointment_creates_user_and_specialist_notifications() -> None:
    """Create reminder notifications for both participants when the specialist has a user account."""

    service = object.__new__(AppointmentReminderService)
    service.uow = Mock()
    service.logger = Mock()
    service.appointment_repository = Mock()
    service.specialist_repository = Mock()
    service.notification_service = Mock()
    appointment = _appointment()
    specialist_user_id = uuid4()
    service.specialist_repository.get_by_id.return_value = SimpleNamespace(user_id=specialist_user_id)

    service._send_reminders_for_appointment(appointment)

    assert service.notification_service.create_unique_notification.call_count == 2
    first_call = service.notification_service.create_unique_notification.call_args_list[0]
    second_call = service.notification_service.create_unique_notification.call_args_list[1]
    assert first_call.kwargs["user_id"] == appointment.user_id
    assert first_call.kwargs["notification_type"] == NotificationType.APPOINTMENT_REMINDER
    assert second_call.kwargs["user_id"] == specialist_user_id
    assert second_call.kwargs["appointment_id"] == appointment.id


@pytest.mark.unit
def test_send_reminders_for_appointment_skips_specialist_notification_without_linked_user() -> None:
    """Skip the specialist-side reminder when the specialist profile is not linked to a user."""

    service = object.__new__(AppointmentReminderService)
    service.uow = Mock()
    service.logger = Mock()
    service.appointment_repository = Mock()
    service.specialist_repository = Mock()
    service.notification_service = Mock()
    appointment = _appointment()
    service.specialist_repository.get_by_id.return_value = SimpleNamespace(user_id=None)

    service._send_reminders_for_appointment(appointment)

    service.notification_service.create_unique_notification.assert_called_once()
    assert service.notification_service.create_unique_notification.call_args.kwargs["user_id"] == appointment.user_id
