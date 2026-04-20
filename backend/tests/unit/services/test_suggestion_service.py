"""Unit tests for critical appointment suggestion generation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.models.enums import SpecialistStatus, UserRole
from app.models.user import User
from app.repositories.specialist_repository import SpecialistDirectoryRow
from app.schemas.availability import SpecialistAvailabilitySlotResponse
from app.services.suggestion_service import NoRecentCriticalAlertError, SuggestionService


def _user() -> User:
    return User(email=f"{uuid4().hex[:12]}@example.com", full_name="Suggestion Test User", role=UserRole.USER)


@pytest.mark.unit
def test_get_critical_appointment_suggestions_requires_recent_alert() -> None:
    """Reject explicit critical suggestions when no recent alert exists."""

    # Arrange
    service = object.__new__(SuggestionService)
    service.logger = Mock()
    service.specialist_repository = Mock()
    service.risk_repository = Mock()
    service.availability_service = Mock()
    service._has_recent_critical_alert = Mock(return_value=False)
    user = _user()

    # Act / Assert
    with pytest.raises(
        NoRecentCriticalAlertError,
        match="No recent critical alert was found for appointment suggestions.",
    ):
        service.get_critical_appointment_suggestions(user)


@pytest.mark.unit
def test_get_critical_appointment_suggestions_orders_by_time_then_rating() -> None:
    """Return the earliest viable slots first and break ties by stronger ratings."""

    # Arrange
    service = object.__new__(SuggestionService)
    service.logger = Mock()
    service.specialist_repository = Mock()
    service.risk_repository = Mock()
    service.availability_service = Mock()
    user = _user()

    specialist_a = SpecialistDirectoryRow(
        id=uuid4(),
        full_name="Dr. Alpha",
        specialty="Psychology",
        bio=None,
        consultation_modes=["online"],
        city="Bucharest",
        status=SpecialistStatus.ACTIVE,
        average_rating=4.6,
        review_count=12,
    )
    specialist_b = SpecialistDirectoryRow(
        id=uuid4(),
        full_name="Dr. Beta",
        specialty="Psychiatry",
        bio=None,
        consultation_modes=["onsite"],
        city="Cluj",
        status=SpecialistStatus.ACTIVE,
        average_rating=4.9,
        review_count=20,
    )
    service.specialist_repository.list_active_specialists.return_value = [specialist_a, specialist_b]

    now = datetime.now(UTC)
    same_start = now + timedelta(days=1, hours=3)
    later_start = same_start + timedelta(hours=2)
    service.availability_service.get_available_slots.side_effect = [
        [
            SpecialistAvailabilitySlotResponse(
                start_datetime=same_start,
                end_datetime=same_start + timedelta(hours=2),
            ),
        ],
        [
            SpecialistAvailabilitySlotResponse(
                start_datetime=same_start,
                end_datetime=same_start + timedelta(hours=2),
            ),
            SpecialistAvailabilitySlotResponse(
                start_datetime=later_start,
                end_datetime=later_start + timedelta(hours=2),
            ),
        ],
    ]

    # Act
    response = service.get_critical_appointment_suggestions(
        user,
        require_recent_critical_alert=False,
    )

    # Assert
    assert response.total_suggestions == 3
    assert response.suggestions[0].specialist_id == specialist_b.id
    assert response.suggestions[0].start_datetime == same_start
    assert response.suggestions[1].specialist_id == specialist_a.id
    assert response.suggestions[2].start_datetime == later_start
