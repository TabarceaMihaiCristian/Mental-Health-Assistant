"""Integration tests for admin specialist and appointment oversight endpoints."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus, SpecialistStatus, UserRole
from app.models.specialist import Specialist
from app.models.user import User
from tests.fixtures.auth import TEST_AUTH_SECRET

PASSWORD_FIELD = "password"


@pytest.mark.integration
def test_admin_can_create_list_and_update_specialists(
    client: TestClient,
    user_factory: Callable[..., User],
    auth_headers_factory,
) -> None:
    """Allow admins to onboard, list, and update specialist profiles."""

    # Arrange
    admin_user = user_factory(role=UserRole.ADMIN, email="admin-flow@example.com")
    headers = auth_headers_factory(admin_user)

    # Act
    create_response = client.post(
        "/api/v1/admin/specialists",
        json={
            "email": "new-specialist@example.com",
            "full_name": "Dr. Admin Created",
            PASSWORD_FIELD: TEST_AUTH_SECRET,
            "specialty": "Psychology",
            "bio": "Focused on stress support.",
            "consultation_modes": ["online"],
            "city": "Bucharest",
        },
        headers=headers,
    )
    specialist_id = create_response.json()["id"]
    list_response = client.get(
        "/api/v1/admin/specialists?page=1&page_size=10",
        headers=headers,
    )
    status_response = client.patch(
        f"/api/v1/admin/specialists/{specialist_id}/status",
        json={"status": SpecialistStatus.INACTIVE.value},
        headers=headers,
    )

    # Assert
    assert create_response.status_code == 201
    assert create_response.json()["full_name"] == "Dr. Admin Created"
    assert list_response.status_code == 200
    assert list_response.json()["total"] >= 1
    created_item = next(item for item in list_response.json()["items"] if item["id"] == specialist_id)
    assert created_item["email"] == "new-specialist@example.com"
    assert status_response.status_code == 200
    assert status_response.json()["status"] == SpecialistStatus.INACTIVE.value


@pytest.mark.integration
def test_admin_can_filter_and_fetch_appointments(
    client: TestClient,
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
    appointment_factory: Callable[..., Appointment],
    auth_headers_factory,
) -> None:
    """Allow admins to filter appointments and fetch one by id."""

    # Arrange
    admin_user = user_factory(role=UserRole.ADMIN, email="admin-appointments@example.com")
    normal_user = user_factory()
    specialist = specialist_factory(full_name="Dr. Oversight")
    appointment = appointment_factory(
        user=normal_user,
        specialist=specialist,
        preferred_datetime=datetime.now(UTC) + timedelta(days=3),
        status=AppointmentStatus.CONFIRMED,
    )
    headers = auth_headers_factory(admin_user)

    # Act
    list_response = client.get(
        f"/api/v1/admin/appointments?status={AppointmentStatus.CONFIRMED.value}&page=1&page_size=10",
        headers=headers,
    )
    detail_response = client.get(
        f"/api/v1/admin/appointments/{appointment.id}",
        headers=headers,
    )

    # Assert
    assert list_response.status_code == 200
    assert list_response.json()["total"] >= 1
    assert any(item["id"] == str(appointment.id) for item in list_response.json()["items"])
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == str(appointment.id)
    assert detail_response.json()["status"] == AppointmentStatus.CONFIRMED.value
