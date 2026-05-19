"""Unit tests for appointment service lifecycle and conflict handling."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.appointment import Appointment
from app.models.enums import AppointmentActorRole, AppointmentMode, AppointmentStatus, NotificationType, UserRole
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCancellationRequest,
    AppointmentRescheduleRequest,
    SpecialistAppointmentCreateRequest,
)
from app.services.appointment_service import (
    APPOINTMENT_OVERLAP_CONSTRAINT_NAME,
    AppointmentCancellationNotAllowedError,
    AppointmentService,
    AppointmentSlotUnavailableError,
    AppointmentUserNotFoundError,
    InvalidAppointmentDateError,
    SLOT_UNAVAILABLE_MESSAGE,
    SpecialistProfileNotFoundError,
    SpecialistUnavailableError,
)


def _user(*, role: UserRole = UserRole.USER, active: bool = True) -> User:
    user = User(email=f"{uuid4().hex[:12]}@example.com", full_name="Appointment Test User", role=role, is_active=active)
    user.id = uuid4()
    return user


def _build_appointment(*, status: AppointmentStatus, preferred_datetime: datetime) -> Appointment:
    appointment = Appointment(
        user_id=uuid4(),
        specialist_id=uuid4(),
        mode=AppointmentMode.ONLINE,
        status=status,
        preferred_datetime=preferred_datetime,
        end_datetime=preferred_datetime + timedelta(hours=2),
        status_updated_by_user_id=uuid4(),
    )
    appointment.id = uuid4()
    return appointment


@pytest.mark.unit
def test_ensure_slot_still_available_raises_for_overlapping_active_appointment() -> None:
    service = object.__new__(AppointmentService)
    service.repository = Mock()
    service.repository.has_overlapping_active_appointment.return_value = True

    with pytest.raises(AppointmentSlotUnavailableError):
        service._ensure_slot_still_available(specialist_id=uuid4(), start_datetime=Mock(), end_datetime=Mock())


@pytest.mark.unit
def test_commit_appointment_write_translates_overlap_constraint_error() -> None:
    service = object.__new__(AppointmentService)
    service.uow = Mock()
    overlap_error = IntegrityError(
        statement="insert into appointments ...",
        params={},
        orig=Exception(f'constraint "{APPOINTMENT_OVERLAP_CONSTRAINT_NAME}" violated'),
    )
    service.uow.commit.side_effect = overlap_error

    with pytest.raises(AppointmentSlotUnavailableError):
        service._commit_appointment_write()
    service.uow.rollback.assert_called_once()


@pytest.mark.unit
def test_get_specialist_profile_raises_when_profile_missing() -> None:
    service = object.__new__(AppointmentService)
    service.specialist_repository = Mock()
    service.specialist_repository.get_by_user_id.return_value = None

    with pytest.raises(SpecialistProfileNotFoundError, match="Specialist profile not found."):
        service._get_specialist_profile(_user(role=UserRole.SPECIALIST))


@pytest.mark.unit
def test_create_specialist_appointment_rejects_missing_target_user() -> None:
    service = object.__new__(AppointmentService)
    service.user_repository = Mock()
    service.user_repository.get_by_id.return_value = None
    service._get_specialist_profile = Mock(return_value=SimpleNamespace(id=uuid4()))
    payload = SpecialistAppointmentCreateRequest(user_id=uuid4(), mode=AppointmentMode.ONLINE, preferred_datetime=datetime.now(UTC), notes=None)

    with pytest.raises(AppointmentUserNotFoundError, match="Target user not found."):
        service.create_specialist_appointment(_user(role=UserRole.SPECIALIST), payload)


@pytest.mark.unit
def test_create_specialist_appointment_confirms_and_notifies_user() -> None:
    service = object.__new__(AppointmentService)
    service.user_repository = Mock()
    target_user = _user(active=True)
    specialist = SimpleNamespace(id=uuid4())
    appointment = _build_appointment(status=AppointmentStatus.CONFIRMED, preferred_datetime=datetime.now(UTC) + timedelta(days=2))
    service.user_repository.get_by_id.return_value = target_user
    service._get_specialist_profile = Mock(return_value=specialist)
    service._create_appointment_record = Mock(return_value=appointment)
    service._notify_user = Mock()
    service.logger = Mock()
    payload = SpecialistAppointmentCreateRequest(user_id=target_user.id, mode=AppointmentMode.ONLINE, preferred_datetime=appointment.preferred_datetime, notes="Focus")

    result = service.create_specialist_appointment(_user(role=UserRole.SPECIALIST), payload)

    assert result is appointment
    service._create_appointment_record.assert_called_once()
    service._notify_user.assert_called_once()


@pytest.mark.unit
def test_cancel_appointment_updates_state_and_notifies_specialist() -> None:
    service = object.__new__(AppointmentService)
    service.get_appointment = Mock()
    appointment = _build_appointment(status=AppointmentStatus.CONFIRMED, preferred_datetime=datetime.now(UTC) + timedelta(days=2))
    service.get_appointment.return_value = appointment
    service.uow = Mock()
    service._notify_specialist = Mock()
    service.logger = Mock()
    user = _user()

    result = service.cancel_appointment(user, appointment.id, AppointmentCancellationRequest(reason="Changed plans"))

    assert result.status == AppointmentStatus.CANCELLED
    assert result.cancellation_reason == "Changed plans"
    assert result.cancelled_at is not None
    service._notify_specialist.assert_called_once()
    service.uow.refresh.assert_called_once_with(appointment)


@pytest.mark.unit
def test_cancel_appointment_rejects_cutoff_violations() -> None:
    service = object.__new__(AppointmentService)
    appointment = _build_appointment(status=AppointmentStatus.CONFIRMED, preferred_datetime=datetime.now(UTC) + timedelta(minutes=30))
    service.get_appointment = Mock(return_value=appointment)

    with pytest.raises(AppointmentCancellationNotAllowedError):
        service.cancel_appointment(_user(), appointment.id)


@pytest.mark.unit
def test_reschedule_appointment_updates_requested_state_and_actor() -> None:
    service = object.__new__(AppointmentService)
    appointment = _build_appointment(status=AppointmentStatus.CONFIRMED, preferred_datetime=datetime.now(UTC) + timedelta(days=2))
    service.get_appointment = Mock(return_value=appointment)
    service.availability_service = Mock()
    service.availability_service.is_bookable_slot.return_value = True
    service._ensure_slot_still_available = Mock()
    service._commit_appointment_write = Mock()
    service._notify_both_sides_rescheduled = Mock()
    service.uow = Mock()
    service.logger = Mock()
    user = _user()
    new_start = datetime.now(UTC) + timedelta(days=3)

    result = service.reschedule_appointment(user, appointment.id, AppointmentRescheduleRequest(preferred_datetime=new_start, note="Move it"))

    assert result.status == AppointmentStatus.REQUESTED
    assert result.preferred_datetime == new_start
    assert result.reschedule_note == "Move it"
    assert result.last_rescheduled_by_role == AppointmentActorRole.USER
    service._notify_both_sides_rescheduled.assert_called_once_with(appointment, actor_role=AppointmentActorRole.USER)


@pytest.mark.unit
def test_reschedule_appointment_rejects_invalid_datetime_and_unavailable_slot(monkeypatch: pytest.MonkeyPatch) -> None:
    appointment = _build_appointment(status=AppointmentStatus.CONFIRMED, preferred_datetime=datetime.now(UTC) + timedelta(days=2))
    service = object.__new__(AppointmentService)
    service.get_appointment = Mock(return_value=appointment)
    service.availability_service = Mock()
    user = _user()

    monkeypatch.setattr("app.services.appointment_service.normalize_future_datetime", Mock(side_effect=ValueError("Bad datetime")))
    with pytest.raises(InvalidAppointmentDateError, match="Bad datetime"):
        service.reschedule_appointment(user, appointment.id, AppointmentRescheduleRequest(preferred_datetime=datetime.now(UTC), note=None))

    monkeypatch.setattr("app.services.appointment_service.normalize_future_datetime", lambda value: value)
    service.availability_service.is_bookable_slot.return_value = False
    with pytest.raises(AppointmentSlotUnavailableError, match=SLOT_UNAVAILABLE_MESSAGE):
        service.reschedule_appointment(user, appointment.id, AppointmentRescheduleRequest(preferred_datetime=datetime.now(UTC) + timedelta(days=5), note=None))


@pytest.mark.unit
def test_create_appointment_record_handles_missing_specialist_invalid_datetime_and_slot(monkeypatch: pytest.MonkeyPatch) -> None:
    service = object.__new__(AppointmentService)
    service.specialist_repository = Mock()
    service.specialist_repository.get_active_specialist_by_id.return_value = None
    service.availability_service = Mock()
    service.repository = Mock()
    service.uow = Mock()

    with pytest.raises(SpecialistUnavailableError):
        service._create_appointment_record(
            user_id=uuid4(), specialist_id=uuid4(), mode=AppointmentMode.ONLINE,
            preferred_datetime=datetime.now(UTC), notes=None, created_by_user_id=uuid4(),
            initial_status=AppointmentStatus.REQUESTED,
        )

    service.specialist_repository.get_active_specialist_by_id.return_value = SimpleNamespace(id=uuid4())
    monkeypatch.setattr("app.services.appointment_service.normalize_future_datetime", Mock(side_effect=ValueError("Bad datetime")))
    with pytest.raises(InvalidAppointmentDateError, match="Bad datetime"):
        service._create_appointment_record(
            user_id=uuid4(), specialist_id=uuid4(), mode=AppointmentMode.ONLINE,
            preferred_datetime=datetime.now(UTC), notes=None, created_by_user_id=uuid4(),
            initial_status=AppointmentStatus.REQUESTED,
        )

    future = datetime.now(UTC) + timedelta(days=5)
    monkeypatch.setattr("app.services.appointment_service.normalize_future_datetime", lambda value: value)
    monkeypatch.setattr("app.services.appointment_service.ensure_minimum_appointment_notice", Mock())
    service.availability_service.is_bookable_slot.return_value = False
    with pytest.raises(AppointmentSlotUnavailableError, match=SLOT_UNAVAILABLE_MESSAGE):
        service._create_appointment_record(
            user_id=uuid4(), specialist_id=uuid4(), mode=AppointmentMode.ONLINE,
            preferred_datetime=future, notes=None, created_by_user_id=uuid4(),
            initial_status=AppointmentStatus.REQUESTED,
        )


@pytest.mark.unit
def test_create_appointment_record_persists_confirmed_appointment(monkeypatch: pytest.MonkeyPatch) -> None:
    service = object.__new__(AppointmentService)
    service.specialist_repository = Mock()
    service.specialist_repository.get_active_specialist_by_id.return_value = SimpleNamespace(id=uuid4())
    service.availability_service = Mock()
    service.availability_service.is_bookable_slot.return_value = True
    service.repository = Mock()
    service.uow = Mock()
    service._ensure_slot_still_available = Mock()
    service._commit_appointment_write = Mock()
    monkeypatch.setattr("app.services.appointment_service.normalize_future_datetime", lambda value: value)
    monkeypatch.setattr("app.services.appointment_service.ensure_minimum_appointment_notice", Mock())
    future = datetime.now(UTC) + timedelta(days=4)

    added: Appointment | None = None
    def add_appointment(appointment):
        nonlocal added
        added = appointment
        appointment.id = uuid4()
    service.repository.add.side_effect = add_appointment

    result = service._create_appointment_record(
        user_id=uuid4(), specialist_id=uuid4(), mode=AppointmentMode.ONLINE,
        preferred_datetime=future, notes=" Keep note ", created_by_user_id=uuid4(),
        initial_status=AppointmentStatus.CONFIRMED,
    )

    assert added
    assert result is added
    assert added.notes == "Keep note"
    assert added.status == AppointmentStatus.CONFIRMED
    assert added.confirmed_at is not None
    service._commit_appointment_write.assert_called_once()
    service.uow.refresh.assert_called_once_with(added)


@pytest.mark.unit
def test_notify_specialist_uses_safe_notification_delivery() -> None:
    service = object.__new__(AppointmentService)
    service.specialist_repository = Mock()
    service._create_notification_safely = Mock()
    appointment = _build_appointment(
        status=AppointmentStatus.REQUESTED,
        preferred_datetime=datetime.now(UTC) + timedelta(days=2),
    )
    specialist_user_id = uuid4()
    service.specialist_repository.get_by_id.return_value = SimpleNamespace(user_id=specialist_user_id)

    service._notify_specialist(
        appointment,
        NotificationType.APPOINTMENT_REQUESTED,
        "Title",
        "Message",
    )

    service._create_notification_safely.assert_called_once_with(
        user_id=specialist_user_id,
        notification_type=NotificationType.APPOINTMENT_REQUESTED,
        title="Title",
        message="Message",
        appointment_id=appointment.id,
    )


@pytest.mark.unit
def test_create_notification_safely_rolls_back_and_suppresses_failures() -> None:
    service = object.__new__(AppointmentService)
    service.notification_service = Mock()
    service.notification_service.create_notification.side_effect = RuntimeError("blocked")
    service.uow = Mock()
    service.logger = Mock()

    service._create_notification_safely(
        user_id=uuid4(),
        notification_type=NotificationType.APPOINTMENT_REQUESTED,
        title="Title",
        message="Message",
        appointment_id=uuid4(),
    )

    service.uow.rollback.assert_called_once()
    service.logger.exception.assert_called_once()


@pytest.mark.unit
def test_notify_specialist_skips_missing_profile_or_user() -> None:
    service = object.__new__(AppointmentService)
    service.specialist_repository = Mock()
    service.notification_service = Mock()
    appointment = _build_appointment(status=AppointmentStatus.REQUESTED, preferred_datetime=datetime.now(UTC) + timedelta(days=2))

    service.specialist_repository.get_by_id.return_value = None
    service._notify_specialist(appointment, NotificationType.APPOINTMENT_REQUESTED, "Title", "Message")
    service.specialist_repository.get_by_id.return_value = SimpleNamespace(user_id=None)
    service._notify_specialist(appointment, NotificationType.APPOINTMENT_REQUESTED, "Title", "Message")

    service.notification_service.create_notification.assert_not_called()


@pytest.mark.unit
def test_build_notification_message_uses_utc_timestamp() -> None:
    service = object.__new__(AppointmentService)
    appointment = _build_appointment(status=AppointmentStatus.REQUESTED, preferred_datetime=datetime(2026, 4, 25, 9, tzinfo=UTC))

    message = service._build_notification_message("Appointment updated", appointment)

    assert message == "Appointment updated. Scheduled for 2026-04-25 09:00 UTC."





