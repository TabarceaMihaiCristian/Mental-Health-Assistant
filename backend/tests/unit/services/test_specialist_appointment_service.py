"""Unit tests for specialist-side appointment lifecycle transitions."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.models.appointment import Appointment
from app.models.enums import AppointmentActorRole, AppointmentMode, AppointmentStatus
from app.services.appointment_service import (
    AppointmentCompletionNotAllowedError,
    AppointmentDecisionNotAllowedError,
    AppointmentRescheduleNotAllowedError,
    AppointmentService,
)


def _build_appointment(
    *,
    status: AppointmentStatus,
    preferred_datetime: datetime,
) -> Appointment:
    """Create an in-memory appointment entity for service-level tests."""

    return Appointment(
        user_id=uuid4(),
        specialist_id=uuid4(),
        mode=AppointmentMode.ONLINE,
        status=status,
        preferred_datetime=preferred_datetime,
        end_datetime=preferred_datetime + timedelta(hours=2),
        status_updated_by_user_id=uuid4(),
    )


@pytest.mark.unit
def test_confirm_specialist_appointment_sets_confirmed_metadata() -> None:
    """Confirm a requested appointment and update audit metadata."""

    # Arrange
    current_user = Mock(id=uuid4())
    appointment = _build_appointment(
        status=AppointmentStatus.REQUESTED,
        preferred_datetime=datetime.now(UTC) + timedelta(days=2),
    )
    service = object.__new__(AppointmentService)
    service.get_specialist_appointment = Mock(return_value=appointment)
    service.uow = Mock()
    service._notify_user = Mock()
    service._log_specialist_transition = Mock()
    service.uow.refresh = Mock()

    # Act
    result = service.confirm_specialist_appointment(current_user, appointment.id)

    # Assert
    assert result.status == AppointmentStatus.CONFIRMED
    assert result.confirmed_at is not None
    assert result.status_updated_by_user_id == current_user.id
    service._notify_user.assert_called_once()
    service._log_specialist_transition.assert_called_once()


@pytest.mark.unit
def test_reject_specialist_appointment_stores_reason() -> None:
    """Reject a requested appointment and persist the provided reason."""

    # Arrange
    current_user = Mock(id=uuid4())
    payload = Mock(reason="Schedule conflict")
    appointment = _build_appointment(
        status=AppointmentStatus.REQUESTED,
        preferred_datetime=datetime.now(UTC) + timedelta(days=2),
    )
    service = object.__new__(AppointmentService)
    service.get_specialist_appointment = Mock(return_value=appointment)
    service.uow = Mock()
    service.uow.refresh = Mock()
    service._notify_user = Mock()
    service._log_specialist_transition = Mock()

    # Act
    result = service.reject_specialist_appointment(current_user, appointment.id, payload)

    # Assert
    assert result.status == AppointmentStatus.REJECTED
    assert result.rejection_reason == "Schedule conflict"
    assert result.rejected_at is not None
    assert result.status_updated_by_user_id == current_user.id


@pytest.mark.unit
def test_reschedule_specialist_appointment_updates_requested_state_and_actor() -> None:
    """Reschedule a specialist-owned appointment back to requested state."""

    # Arrange
    current_user = Mock(id=uuid4())
    new_start = datetime.now(UTC) + timedelta(days=3)
    payload = Mock(preferred_datetime=new_start, note="Moved by specialist")
    appointment = _build_appointment(
        status=AppointmentStatus.CONFIRMED,
        preferred_datetime=datetime.now(UTC) + timedelta(days=2),
    )
    service = object.__new__(AppointmentService)
    service.get_specialist_appointment = Mock(return_value=appointment)
    service.availability_service = Mock()
    service.availability_service.is_bookable_slot.return_value = True
    service._ensure_slot_still_available = Mock()
    service._commit_appointment_write = Mock()
    service.uow = Mock()
    service.uow.refresh = Mock()
    service._notify_both_sides_rescheduled = Mock()
    service._log_specialist_transition = Mock()

    # Act
    result = service.reschedule_specialist_appointment(current_user, appointment.id, payload)

    # Assert
    assert result.status == AppointmentStatus.REQUESTED
    assert result.preferred_datetime == new_start
    assert result.end_datetime == new_start + timedelta(hours=2)
    assert result.reschedule_note == "Moved by specialist"
    assert result.last_rescheduled_by_role == AppointmentActorRole.SPECIALIST
    assert result.status_updated_by_user_id == current_user.id


@pytest.mark.unit
def test_complete_specialist_appointment_rejects_non_confirmed_status() -> None:
    """Reject completion attempts for appointments that are not confirmed."""

    # Arrange
    current_user = Mock(id=uuid4())
    appointment = _build_appointment(
        status=AppointmentStatus.REQUESTED,
        preferred_datetime=datetime.now(UTC) - timedelta(days=1),
    )
    service = object.__new__(AppointmentService)
    service.get_specialist_appointment = Mock(return_value=appointment)

    # Act / Assert
    with pytest.raises(AppointmentCompletionNotAllowedError):
        service.complete_specialist_appointment(current_user, appointment.id)


@pytest.mark.unit
def test_confirm_specialist_appointment_rejects_started_appointments() -> None:
    """Reject confirmation when the appointment has already started."""

    # Arrange
    current_user = Mock(id=uuid4())
    appointment = _build_appointment(
        status=AppointmentStatus.REQUESTED,
        preferred_datetime=datetime.now(UTC) - timedelta(minutes=5),
    )
    service = object.__new__(AppointmentService)
    service.get_specialist_appointment = Mock(return_value=appointment)

    # Act / Assert
    with pytest.raises(AppointmentDecisionNotAllowedError):
        service.confirm_specialist_appointment(current_user, appointment.id)


@pytest.mark.unit
def test_reschedule_specialist_appointment_rejects_cutoff_violations() -> None:
    """Reject specialist reschedules that fall inside the configured cutoff window."""

    # Arrange
    current_user = Mock(id=uuid4())
    payload = Mock(
        preferred_datetime=datetime.now(UTC) + timedelta(days=1),
        note=None,
    )
    appointment = _build_appointment(
        status=AppointmentStatus.CONFIRMED,
        preferred_datetime=datetime.now(UTC) + timedelta(hours=1),
    )
    service = object.__new__(AppointmentService)
    service.get_specialist_appointment = Mock(return_value=appointment)

    # Act / Assert
    with pytest.raises(AppointmentRescheduleNotAllowedError):
        service.reschedule_specialist_appointment(current_user, appointment.id, payload)
