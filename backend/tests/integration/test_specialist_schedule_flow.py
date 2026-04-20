"""Integration tests for specialist-owned schedule endpoints."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, time, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.models.specialist import Specialist


@pytest.mark.integration
def test_replace_my_availability_persists_rules(
    client: TestClient,
    specialist_factory: Callable[..., Specialist],
    auth_headers_factory,
) -> None:
    """Allow a specialist to replace their recurring availability rules."""

    # Arrange
    specialist = specialist_factory(full_name="Dr. Schedule")
    headers = auth_headers_factory(specialist.user)

    # Act
    response = client.put(
        "/api/v1/specialists/me/availability",
        json=[
            {
                "weekday": 1,
                "start_time": "09:00:00",
                "end_time": "13:00:00",
                "is_enabled": True,
            },
            {
                "weekday": 3,
                "start_time": "14:00:00",
                "end_time": "18:00:00",
                "is_enabled": True,
            },
        ],
        headers=headers,
    )

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["weekday"] == 1
    assert payload[1]["weekday"] == 3


@pytest.mark.integration
def test_create_my_break_rejects_overlapping_windows(
    client: TestClient,
    specialist_factory: Callable[..., Specialist],
    auth_headers_factory,
) -> None:
    """Reject overlapping break windows for the same weekday."""

    # Arrange
    specialist = specialist_factory(full_name="Dr. Break")
    headers = auth_headers_factory(specialist.user)
    first_response = client.post(
        "/api/v1/specialists/me/breaks",
        json={
            "weekday": 2,
            "start_time": "12:00:00",
            "end_time": "13:00:00",
            "label": "Lunch",
        },
        headers=headers,
    )
    assert first_response.status_code == 201

    # Act
    response = client.post(
        "/api/v1/specialists/me/breaks",
        json={
            "weekday": 2,
            "start_time": "12:30:00",
            "end_time": "13:30:00",
            "label": "Overlap",
        },
        headers=headers,
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Break windows cannot overlap on the same weekday."


@pytest.mark.integration
def test_create_my_time_off_persists_future_window(
    client: TestClient,
    specialist_factory: Callable[..., Specialist],
    auth_headers_factory,
) -> None:
    """Allow a specialist to create a future time-off window."""

    # Arrange
    specialist = specialist_factory(full_name="Dr. Time Off")
    headers = auth_headers_factory(specialist.user)
    start_datetime = datetime.now(UTC) + timedelta(days=2)
    end_datetime = start_datetime + timedelta(hours=6)

    # Act
    response = client.post(
        "/api/v1/specialists/me/time-off",
        json={
            "start_datetime": start_datetime.isoformat(),
            "end_datetime": end_datetime.isoformat(),
            "reason": "Conference",
        },
        headers=headers,
    )

    # Assert
    assert response.status_code == 201
    payload = response.json()
    assert payload["reason"] == "Conference"


@pytest.mark.integration
def test_get_my_calendar_returns_appointments_breaks_and_time_off(
    client: TestClient,
    db_session: Session,
    specialist_factory: Callable[..., Specialist],
    user_factory,
    auth_headers_factory,
    availability_rule_factory,
    appointment_factory: Callable[..., Appointment],
) -> None:
    """Return assembled calendar data for the current specialist."""

    # Arrange
    specialist = specialist_factory(full_name="Dr. Calendar")
    headers = auth_headers_factory(specialist.user)
    user = user_factory()
    future_day = (datetime.now(UTC) + timedelta(days=2)).date()
    availability_rule_factory(
        specialist_id=specialist.id,
        weekday=future_day.weekday(),
        start_time=time(hour=9),
        end_time=time(hour=17),
    )
    appointment_factory(
        user=user,
        specialist=specialist,
        preferred_datetime=datetime.combine(future_day, time(hour=9), tzinfo=UTC),
        status=AppointmentStatus.CONFIRMED,
    )
    break_response = client.post(
        "/api/v1/specialists/me/breaks",
        json={
            "weekday": future_day.weekday(),
            "start_time": "12:00:00",
            "end_time": "13:00:00",
            "label": "Lunch",
        },
        headers=headers,
    )
    assert break_response.status_code == 201
    start_datetime = datetime.combine(future_day, time(hour=15), tzinfo=UTC)
    end_datetime = start_datetime + timedelta(hours=2)
    time_off_response = client.post(
        "/api/v1/specialists/me/time-off",
        json={
            "start_datetime": start_datetime.isoformat(),
            "end_datetime": end_datetime.isoformat(),
            "reason": "Personal",
        },
        headers=headers,
    )
    assert time_off_response.status_code == 201

    # Act
    response = client.get(
        f"/api/v1/specialists/me/calendar?date_from={future_day.isoformat()}&date_to={future_day.isoformat()}",
        headers=headers,
    )

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["specialist_id"] == str(specialist.id)
    assert len(payload["appointments"]) == 1
    assert len(payload["breaks"]) == 1
    assert len(payload["time_off_periods"]) == 1
