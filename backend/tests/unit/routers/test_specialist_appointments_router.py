"""Unit tests for specialist appointment router branches."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.v1.routers import specialist_appointments as router
from app.models.enums import AppointmentMode, AppointmentStatus, UserRole
from app.models.user import User
from app.schemas.appointment import (
    AppointmentRejectionRequest,
    AppointmentRescheduleRequest,
    SpecialistAppointmentCreateRequest,
)
from app.services.appointment_service import (
    AppointmentCompletionNotAllowedError,
    AppointmentDecisionNotAllowedError,
    AppointmentNotFoundError,
    AppointmentRescheduleNotAllowedError,
    AppointmentSlotUnavailableError,
    AppointmentUserNotFoundError,
    InvalidAppointmentDateError,
    SpecialistProfileNotFoundError,
)


def _current_user() -> User:
    return User(email=f"{uuid4().hex[:12]}@example.com", full_name="Specialist Router User", role=UserRole.SPECIALIST)


def _appointment_row() -> SimpleNamespace:
    return SimpleNamespace(id=uuid4(), status=AppointmentStatus.REQUESTED)


@pytest.mark.unit
def test_list_and_get_specialist_appointments_map_not_found_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    appointment = _appointment_row()
    current_user = _current_user()
    monkeypatch.setattr(router.AppointmentResponse, "model_validate", classmethod(lambda cls, item: item))
    service = SimpleNamespace(
        list_specialist_appointments=Mock(return_value=[appointment]),
        get_specialist_appointment=Mock(return_value=appointment),
    )
    monkeypatch.setattr(router, "AppointmentService", Mock(return_value=service))

    assert router.list_specialist_appointments(current_user, Mock()) == [appointment]
    assert router.get_specialist_appointment(appointment.id, current_user, Mock()) is appointment

    for method_name, exc in [
        ("list_specialist_appointments", SpecialistProfileNotFoundError("No profile")),
        ("get_specialist_appointment", SpecialistProfileNotFoundError("No profile")),
        ("get_specialist_appointment", AppointmentNotFoundError("Missing appointment")),
    ]:
        failing_service = SimpleNamespace(**{method_name: Mock(side_effect=exc)})
        monkeypatch.setattr(router, "AppointmentService", Mock(return_value=failing_service))
        with pytest.raises(HTTPException) as error:
            if method_name == "list_specialist_appointments":
                router.list_specialist_appointments(current_user, Mock())
            else:
                router.get_specialist_appointment(appointment.id, current_user, Mock())
        assert error.value.status_code == 404
        assert error.value.detail == str(exc)


@pytest.mark.unit
def test_create_specialist_appointment_maps_create_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = SpecialistAppointmentCreateRequest(
        user_id=uuid4(),
        preferred_datetime=datetime(2026, 4, 25, 9, tzinfo=UTC),
        mode=AppointmentMode.ONLINE,
    )
    current_user = _current_user()
    appointment = _appointment_row()
    monkeypatch.setattr(router.AppointmentResponse, "model_validate", classmethod(lambda cls, item: item))
    service = SimpleNamespace(create_specialist_appointment=Mock(return_value=appointment))
    monkeypatch.setattr(router, "AppointmentService", Mock(return_value=service))

    assert router.create_specialist_appointment(payload, current_user, Mock()) is appointment

    for exc, status_code in [
        (SpecialistProfileNotFoundError("No profile"), 404),
        (AppointmentUserNotFoundError("Missing user"), 404),
        (InvalidAppointmentDateError("Bad datetime"), 400),
        (AppointmentSlotUnavailableError("Taken slot"), 409),
    ]:
        failing_service = SimpleNamespace(create_specialist_appointment=Mock(side_effect=exc))
        monkeypatch.setattr(router, "AppointmentService", Mock(return_value=failing_service))
        with pytest.raises(HTTPException) as error:
            router.create_specialist_appointment(payload, current_user, Mock())
        assert error.value.status_code == status_code
        assert error.value.detail == str(exc)


@pytest.mark.unit
def test_specialist_decision_routes_map_conflicts_and_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    appointment = _appointment_row()
    current_user = _current_user()
    rejection_payload = AppointmentRejectionRequest(reason="Cannot take this slot")
    reschedule_payload = AppointmentRescheduleRequest(
        preferred_datetime=datetime(2026, 4, 26, 9, tzinfo=UTC),
        note="Move it",
    )
    monkeypatch.setattr(router.AppointmentResponse, "model_validate", classmethod(lambda cls, item: item))
    service = SimpleNamespace(
        confirm_specialist_appointment=Mock(return_value=appointment),
        reject_specialist_appointment=Mock(return_value=appointment),
        reschedule_specialist_appointment=Mock(return_value=appointment),
        complete_specialist_appointment=Mock(return_value=appointment),
    )
    monkeypatch.setattr(router, "AppointmentService", Mock(return_value=service))

    assert router.confirm_specialist_appointment(appointment.id, current_user, Mock()) is appointment
    assert router.reject_specialist_appointment(appointment.id, rejection_payload, current_user, Mock()) is appointment
    assert router.reschedule_specialist_appointment(appointment.id, reschedule_payload, current_user, Mock()) is appointment
    assert router.complete_specialist_appointment(appointment.id, current_user, Mock()) is appointment

    cases = [
        ("confirm_specialist_appointment", SpecialistProfileNotFoundError("No profile"), 404),
        ("confirm_specialist_appointment", AppointmentNotFoundError("Missing appointment"), 404),
        ("confirm_specialist_appointment", AppointmentDecisionNotAllowedError("Cannot confirm"), 409),
        ("reject_specialist_appointment", AppointmentDecisionNotAllowedError("Cannot reject"), 409),
        ("reschedule_specialist_appointment", AppointmentRescheduleNotAllowedError("Cannot reschedule"), 409),
        ("reschedule_specialist_appointment", InvalidAppointmentDateError("Bad datetime"), 400),
        ("reschedule_specialist_appointment", AppointmentSlotUnavailableError("Taken slot"), 409),
        ("complete_specialist_appointment", AppointmentCompletionNotAllowedError("Cannot complete"), 409),
    ]

    for method_name, exc, status_code in cases:
        failing_service = SimpleNamespace(**{method_name: Mock(side_effect=exc)})
        monkeypatch.setattr(router, "AppointmentService", Mock(return_value=failing_service))
        with pytest.raises(HTTPException) as error:
            if method_name == "reject_specialist_appointment":
                router.reject_specialist_appointment(appointment.id, rejection_payload, current_user, Mock())
            elif method_name == "reschedule_specialist_appointment":
                router.reschedule_specialist_appointment(appointment.id, reschedule_payload, current_user, Mock())
            elif method_name == "complete_specialist_appointment":
                router.complete_specialist_appointment(appointment.id, current_user, Mock())
            else:
                router.confirm_specialist_appointment(appointment.id, current_user, Mock())
        assert error.value.status_code == status_code
        assert error.value.detail == str(exc)
