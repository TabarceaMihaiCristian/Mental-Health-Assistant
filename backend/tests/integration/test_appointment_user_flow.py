"""Integration tests for the user-facing appointment booking flow."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta, time

import pytest
from fastapi.testclient import TestClient

from app.models.enums import AppointmentMode
from app.models.specialist import Specialist
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


@pytest.mark.integration
def test_user_can_book_available_specialist_slot(
    client: TestClient,
    auth_headers_factory: Callable[[User], dict[str, str]],
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
    availability_rule_factory: Callable[..., object],
) -> None:
    """Create a requested appointment when the chosen slot is currently bookable."""

    # Arrange
    user = user_factory()
    specialist = specialist_factory()
    slot_start = _next_weekday_datetime(target_weekday=1, hour=9)
    availability_rule_factory(
        specialist_id=specialist.id,
        weekday=slot_start.weekday(),
        start_time=time(hour=9),
        end_time=time(hour=17),
    )
    payload = {
        "specialist_id": str(specialist.id),
        "mode": AppointmentMode.ONLINE.value,
        "preferred_datetime": slot_start.isoformat(),
        "notes": "Need support this week.",
    }

    # Act
    response = client.post(
        "/api/v1/appointments",
        json=payload,
        headers=auth_headers_factory(user),
    )

    # Assert
    assert response.status_code == 201
    body = response.json()
    assert body["specialist_id"] == str(specialist.id)
    assert body["user_id"] == str(user.id)
    assert body["status"] == "requested"
    assert body["mode"] == "online"
    assert body["notes"] == "Need support this week."
    assert body["preferred_datetime"] == slot_start.isoformat().replace("+00:00", "Z")
    assert body["end_datetime"] == (
        slot_start + timedelta(hours=2)
    ).isoformat().replace("+00:00", "Z")


@pytest.mark.integration
def test_user_cannot_book_slot_outside_specialist_availability(
    client: TestClient,
    auth_headers_factory: Callable[[User], dict[str, str]],
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
    availability_rule_factory: Callable[..., object],
) -> None:
    """Reject an appointment request when the chosen slot is not part of the schedule."""

    # Arrange
    user = user_factory()
    specialist = specialist_factory()
    slot_start = _next_weekday_datetime(target_weekday=2, hour=15)
    availability_rule_factory(
        specialist_id=specialist.id,
        weekday=slot_start.weekday(),
        start_time=time(hour=9),
        end_time=time(hour=11),
    )
    payload = {
        "specialist_id": str(specialist.id),
        "mode": AppointmentMode.ONLINE.value,
        "preferred_datetime": slot_start.isoformat(),
        "notes": "This should fail.",
    }

    # Act
    response = client.post(
        "/api/v1/appointments",
        json=payload,
        headers=auth_headers_factory(user),
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "The requested appointment slot is not available."
