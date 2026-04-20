"""Unit tests for user-facing appointment router branches."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.v1.routers import appointments as router
from app.models.enums import AppointmentMode, AppointmentStatus, UserRole
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCancellationRequest,
    AppointmentCreateRequest,
    AppointmentRescheduleRequest,
)
from app.services.appointment_service import (
    AppointmentCancellationNotAllowedError,
    AppointmentNotFoundError,
    AppointmentRescheduleNotAllowedError,
    AppointmentSlotUnavailableError,
    InvalidAppointmentDateError,
    SpecialistUnavailableError,
)
from app.services.suggestion_service import NoRecentCriticalAlertError


def _current_user() -> User:
    return User(email=f"{uuid4().hex[:12]}@example.com", full_name="Appointment Router User", role=UserRole.USER)


def _appointment_row() -> SimpleNamespace:
    return SimpleNamespace(id=uuid4(), status=AppointmentStatus.REQUESTED)


@pytest.mark.unit
def test_create_appointment_maps_domain_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = AppointmentCreateRequest(
        specialist_id=uuid4(),
        preferred_datetime=datetime(2026, 4, 25, 9, tzinfo=UTC),
        mode=AppointmentMode.ONLINE,
    )
    current_user = _current_user()

    for exc, status_code in [
        (SpecialistUnavailableError("Missing specialist"), 404),
        (InvalidAppointmentDateError("Bad datetime"), 400),
        (AppointmentSlotUnavailableError("Taken slot"), 400),
    ]:
        service = SimpleNamespace(create_appointment=Mock(side_effect=exc))
        monkeypatch.setattr(router, "AppointmentService", Mock(return_value=service))
        with pytest.raises(HTTPException) as error:
            router.create_appointment(payload, current_user, Mock())
        assert error.value.status_code == status_code
        assert error.value.detail == str(exc)


@pytest.mark.unit
def test_list_get_cancel_and_reschedule_appointment_routes(monkeypatch: pytest.MonkeyPatch) -> None:
    appointment = _appointment_row()
    current_user = _current_user()
    cancel_payload = AppointmentCancellationRequest(reason="Need to cancel")
    reschedule_payload = AppointmentRescheduleRequest(
        preferred_datetime=datetime(2026, 4, 26, 9, tzinfo=UTC),
        note="Need a different time",
    )
    monkeypatch.setattr(router.AppointmentResponse, "model_validate", classmethod(lambda cls, item: item))
    service = SimpleNamespace(
        list_appointments=Mock(return_value=[appointment]),
        get_appointment=Mock(return_value=appointment),
        cancel_appointment=Mock(return_value=appointment),
        reschedule_appointment=Mock(return_value=appointment),
    )
    monkeypatch.setattr(router, "AppointmentService", Mock(return_value=service))

    listed = router.list_appointments(current_user, Mock())
    fetched = router.get_appointment(appointment.id, current_user, Mock())
    cancelled = router.cancel_appointment(appointment.id, cancel_payload, current_user, Mock())
    rescheduled = router.reschedule_appointment(appointment.id, reschedule_payload, current_user, Mock())

    assert listed == [appointment]
    assert fetched is appointment
    assert cancelled is appointment
    assert rescheduled is appointment

    for method_name, exc, status_code in [
        ("get_appointment", AppointmentNotFoundError("Not found"), 404),
        ("cancel_appointment", AppointmentNotFoundError("Not found"), 404),
        ("cancel_appointment", AppointmentCancellationNotAllowedError("Cannot cancel"), 409),
        ("reschedule_appointment", AppointmentNotFoundError("Not found"), 404),
        ("reschedule_appointment", AppointmentRescheduleNotAllowedError("Cannot reschedule"), 409),
        ("reschedule_appointment", InvalidAppointmentDateError("Bad datetime"), 400),
        ("reschedule_appointment", AppointmentSlotUnavailableError("Taken slot"), 409),
    ]:
        failing_service = SimpleNamespace(**{method_name: Mock(side_effect=exc)})
        monkeypatch.setattr(router, "AppointmentService", Mock(return_value=failing_service))
        with pytest.raises(HTTPException) as error:
            if method_name == "get_appointment":
                router.get_appointment(appointment.id, current_user, Mock())
            elif method_name == "cancel_appointment":
                router.cancel_appointment(appointment.id, None, current_user, Mock())
            else:
                router.reschedule_appointment(appointment.id, reschedule_payload, current_user, Mock())
        assert error.value.status_code == status_code
        assert error.value.detail == str(exc)


@pytest.mark.unit
def test_list_critical_appointment_suggestions_maps_missing_alert(monkeypatch: pytest.MonkeyPatch) -> None:
    current_user = _current_user()
    service = SimpleNamespace(get_critical_appointment_suggestions=Mock(side_effect=NoRecentCriticalAlertError("No recent alert")))
    monkeypatch.setattr(router, "SuggestionService", Mock(return_value=service))

    with pytest.raises(HTTPException) as error:
        router.list_critical_appointment_suggestions(current_user, Mock())

    assert error.value.status_code == 404
    assert error.value.detail == "No recent alert"
