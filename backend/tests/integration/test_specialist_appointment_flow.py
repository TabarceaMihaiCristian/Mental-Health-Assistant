"""Integration tests for specialist-managed appointment lifecycle flows."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, time, timedelta

import pytest
from fastapi.testclient import TestClient

from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.models.specialist import Specialist
from app.models.specialist_availability_rule import SpecialistAvailabilityRule
from app.models.user import User


def _next_weekday_datetime(
    *,
    target_weekday: int,
    hour: int,
) -> datetime:
    """Return the next future UTC datetime matching a weekday and hour."""

    now = datetime.now(UTC)
    candidate = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    days_ahead = (target_weekday - candidate.weekday()) % 7
    if days_ahead == 0 and candidate <= now:
        days_ahead = 7
    return candidate + timedelta(days=days_ahead)


def _future_datetime_at_hour(*, days_ahead: int, hour: int) -> datetime:
    """Return a UTC datetime at least a fixed number of days in the future."""

    now = datetime.now(UTC)
    return (now + timedelta(days=days_ahead)).replace(
        hour=hour,
        minute=0,
        second=0,
        microsecond=0,
    )


@pytest.mark.integration
def test_specialist_can_confirm_requested_appointment(
    client: TestClient,
    auth_headers_factory: Callable[[User], dict[str, str]],
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
    availability_rule_factory: Callable[..., SpecialistAvailabilityRule],
    appointment_factory: Callable[..., Appointment],
) -> None:
    """Allow a specialist to confirm a requested future appointment."""

    # Arrange
    user = user_factory()
    specialist = specialist_factory()
    specialist_user = specialist.user
    assert specialist_user is not None
    slot_start = _next_weekday_datetime(target_weekday=1, hour=9)
    availability_rule_factory(
        specialist_id=specialist.id,
        weekday=slot_start.weekday(),
        start_time=time(hour=9),
        end_time=time(hour=17),
    )
    appointment = appointment_factory(
        user=user,
        specialist=specialist,
        preferred_datetime=slot_start,
        status=AppointmentStatus.REQUESTED,
    )

    # Act
    response = client.patch(
        f"/api/v1/specialist/appointments/{appointment.id}/confirm",
        headers=auth_headers_factory(specialist_user),
    )

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "confirmed"
    assert body["confirmed_at"] is not None


@pytest.mark.integration
def test_specialist_can_reject_requested_appointment_with_reason(
    client: TestClient,
    auth_headers_factory: Callable[[User], dict[str, str]],
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
    appointment_factory: Callable[..., Appointment],
) -> None:
    """Allow a specialist to reject a requested appointment and store the reason."""

    # Arrange
    user = user_factory()
    specialist = specialist_factory()
    specialist_user = specialist.user
    assert specialist_user is not None
    appointment = appointment_factory(
        user=user,
        specialist=specialist,
        preferred_datetime=datetime.now(UTC) + timedelta(days=2),
        status=AppointmentStatus.REQUESTED,
    )

    # Act
    response = client.patch(
        f"/api/v1/specialist/appointments/{appointment.id}/reject",
        json={"reason": "Unavailable at that time"},
        headers=auth_headers_factory(specialist_user),
    )

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["rejection_reason"] == "Unavailable at that time"
    assert body["rejected_at"] is not None


@pytest.mark.integration
def test_specialist_can_reschedule_to_a_valid_available_slot(
    client: TestClient,
    auth_headers_factory: Callable[[User], dict[str, str]],
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
    availability_rule_factory: Callable[..., SpecialistAvailabilityRule],
    appointment_factory: Callable[..., Appointment],
) -> None:
    """Allow a specialist to reschedule a future appointment to a valid slot."""

    # Arrange
    user = user_factory()
    specialist = specialist_factory()
    specialist_user = specialist.user
    assert specialist_user is not None
    original_start = _future_datetime_at_hour(days_ahead=3, hour=9)
    new_start = original_start.replace(hour=11)
    availability_rule_factory(
        specialist_id=specialist.id,
        weekday=original_start.weekday(),
        start_time=time(hour=9),
        end_time=time(hour=17),
    )
    appointment = appointment_factory(
        user=user,
        specialist=specialist,
        preferred_datetime=original_start,
        status=AppointmentStatus.CONFIRMED,
    )

    # Act
    response = client.patch(
        f"/api/v1/specialist/appointments/{appointment.id}/reschedule",
        json={
            "preferred_datetime": new_start.isoformat(),
            "note": "Please use the next available slot.",
        },
        headers=auth_headers_factory(specialist_user),
    )

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "requested"
    assert body["reschedule_note"] == "Please use the next available slot."
    assert body["last_rescheduled_by_role"] == "specialist"
    assert body["preferred_datetime"] == new_start.isoformat().replace("+00:00", "Z")


@pytest.mark.integration
def test_specialist_cannot_reschedule_to_an_unavailable_slot(
    client: TestClient,
    auth_headers_factory: Callable[[User], dict[str, str]],
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
    availability_rule_factory: Callable[..., SpecialistAvailabilityRule],
    appointment_factory: Callable[..., Appointment],
) -> None:
    """Reject specialist reschedules that target a slot outside availability."""

    # Arrange
    user = user_factory()
    specialist = specialist_factory()
    specialist_user = specialist.user
    assert specialist_user is not None
    original_start = _future_datetime_at_hour(days_ahead=3, hour=9)
    invalid_start = original_start.replace(hour=15)
    availability_rule_factory(
        specialist_id=specialist.id,
        weekday=original_start.weekday(),
        start_time=time(hour=9),
        end_time=time(hour=11),
    )
    appointment = appointment_factory(
        user=user,
        specialist=specialist,
        preferred_datetime=original_start,
        status=AppointmentStatus.CONFIRMED,
    )

    # Act
    response = client.patch(
        f"/api/v1/specialist/appointments/{appointment.id}/reschedule",
        json={"preferred_datetime": invalid_start.isoformat(), "note": None},
        headers=auth_headers_factory(specialist_user),
    )

    # Assert
    assert response.status_code == 409
    assert response.json()["detail"] == "The requested appointment slot is not available."


@pytest.mark.integration
def test_specialist_can_complete_confirmed_finished_appointment(
    client: TestClient,
    auth_headers_factory: Callable[[User], dict[str, str]],
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
    appointment_factory: Callable[..., Appointment],
) -> None:
    """Allow completion when the confirmed appointment has already ended."""

    # Arrange
    user = user_factory()
    specialist = specialist_factory()
    specialist_user = specialist.user
    assert specialist_user is not None
    past_start = datetime.now(UTC) - timedelta(days=1, hours=3)
    appointment = appointment_factory(
        user=user,
        specialist=specialist,
        preferred_datetime=past_start,
        end_datetime=past_start + timedelta(hours=2),
        status=AppointmentStatus.CONFIRMED,
    )

    # Act
    response = client.patch(
        f"/api/v1/specialist/appointments/{appointment.id}/complete",
        headers=auth_headers_factory(specialist_user),
    )

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["completed_at"] is not None
