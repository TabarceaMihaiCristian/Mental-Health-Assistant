"""Unit tests for specialist availability computation."""

from __future__ import annotations

from datetime import UTC, date, datetime, time
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.models.appointment import Appointment
from app.models.enums import AppointmentMode, AppointmentStatus, SpecialistStatus
from app.models.specialist_availability_rule import SpecialistAvailabilityRule
from app.models.specialist_break import SpecialistBreak
from app.repositories.specialist_repository import SpecialistDirectoryRow
from app.services.availability_service import (
    AvailabilityService,
    AvailabilityWindowError,
)


@pytest.mark.unit
def test_get_available_slots_excludes_break_and_existing_appointment() -> None:
    """Exclude blocked 2-hour windows caused by recurring breaks and appointments."""

    # Arrange
    specialist_id = uuid4()
    service = object.__new__(AvailabilityService)
    service.specialist_repository = Mock()
    service.schedule_repository = Mock()
    service.appointment_repository = Mock()
    service.specialist_repository.get_active_specialist_by_id.return_value = SpecialistDirectoryRow(
        id=specialist_id,
        full_name="Dr. Test",
        specialty="Psychology",
        bio=None,
        consultation_modes=["online"],
        city="Bucharest",
        status=SpecialistStatus.ACTIVE,
        average_rating=4.8,
        review_count=12,
    )
    service.schedule_repository.list_availability_rules.return_value = [
        SpecialistAvailabilityRule(
            specialist_id=specialist_id,
            weekday=0,
            start_time=time(hour=9),
            end_time=time(hour=17),
            is_enabled=True,
        )
    ]
    service.schedule_repository.list_breaks.return_value = [
        SpecialistBreak(
            specialist_id=specialist_id,
            weekday=0,
            start_time=time(hour=13),
            end_time=time(hour=14),
            label="Lunch",
        )
    ]
    service.schedule_repository.list_time_off_in_window.return_value = []
    service.appointment_repository.list_for_specialist_in_window.return_value = [
        Appointment(
            user_id=uuid4(),
            specialist_id=specialist_id,
            mode=AppointmentMode.ONLINE,
            status=AppointmentStatus.CONFIRMED,
            preferred_datetime=datetime(2026, 4, 20, 9, 0, tzinfo=UTC),
            end_datetime=datetime(2026, 4, 20, 11, 0, tzinfo=UTC),
        )
    ]

    # Act
    slots = service.get_available_slots(
        specialist_id,
        date(2026, 4, 20),
        date(2026, 4, 20),
    )

    # Assert
    assert [slot.start_datetime for slot in slots] == [
        datetime(2026, 4, 20, 11, 0, tzinfo=UTC),
        datetime(2026, 4, 20, 15, 0, tzinfo=UTC),
    ]


@pytest.mark.unit
def test_get_available_slots_rejects_inverted_date_windows() -> None:
    """Reject availability requests where the end date is before the start date."""

    # Arrange
    service = object.__new__(AvailabilityService)

    # Act / Assert
    with pytest.raises(AvailabilityWindowError):
        service.get_available_slots(
            uuid4(),
            date(2026, 4, 21),
            date(2026, 4, 20),
        )
