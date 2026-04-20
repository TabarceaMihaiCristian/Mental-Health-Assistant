"""Unit tests for specialist schedule management."""

from __future__ import annotations

from datetime import UTC, datetime, time, timedelta
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.models.enums import UserRole
from app.models.user import User
from app.schemas.specialist_schedule import (
    AvailabilityRuleUpsertRequest,
    BreakCreateRequest,
    BreakUpdateRequest,
    TimeOffCreateRequest,
    TimeOffUpdateRequest,
)
from app.services.specialist_schedule_service import (
    SpecialistProfileNotFoundError,
    SpecialistScheduleItemNotFoundError,
    SpecialistScheduleService,
    SpecialistScheduleValidationError,
)


def _specialist_user() -> User:
    return User(email=f"{uuid4().hex[:12]}@example.com", full_name="Schedule Test Specialist", role=UserRole.SPECIALIST)


@pytest.mark.unit
def test_validate_weekly_windows_rejects_overlaps_on_same_weekday() -> None:
    """Reject overlapping weekly availability windows on the same weekday."""

    service = object.__new__(SpecialistScheduleService)
    payload = [
        AvailabilityRuleUpsertRequest(weekday=1, start_time=time(hour=9), end_time=time(hour=12), is_enabled=True),
        AvailabilityRuleUpsertRequest(weekday=1, start_time=time(hour=11), end_time=time(hour=15), is_enabled=True),
    ]

    with pytest.raises(SpecialistScheduleValidationError, match="Availability windows cannot overlap on weekday 1."):
        service._validate_weekly_windows(payload)


@pytest.mark.unit
def test_ensure_no_overlap_rejects_break_collisions() -> None:
    """Reject overlapping break windows on the same weekday."""

    service = object.__new__(SpecialistScheduleService)
    existing_windows = [(2, time(hour=12), time(hour=13)), (2, time(hour=15), time(hour=16))]

    with pytest.raises(SpecialistScheduleValidationError, match="Break windows cannot overlap on the same weekday."):
        service._ensure_no_overlap(2, time(hour=12, minute=30), time(hour=13, minute=30), existing_windows, "Break")


@pytest.mark.unit
def test_ensure_valid_time_window_rejects_start_after_end() -> None:
    """Reject time windows whose start is not strictly earlier than the end."""

    service = object.__new__(SpecialistScheduleService)

    with pytest.raises(SpecialistScheduleValidationError, match="Break start time must be earlier than end time."):
        service._ensure_valid_time_window(time(hour=12), time(hour=12), "Break")


@pytest.mark.unit
def test_replace_availability_rules_commits_and_returns_current_rules() -> None:
    """Replace recurring availability and return the repository's current rule list."""

    service = object.__new__(SpecialistScheduleService)
    service.uow = Mock()
    service.schedule_repository = Mock()
    service.logger = Mock()
    specialist = SimpleNamespace(id=uuid4())
    current_user = _specialist_user()
    service._get_specialist_for_user = Mock(return_value=specialist)
    service._validate_weekly_windows = Mock()
    payload = [AvailabilityRuleUpsertRequest(weekday=1, start_time=time(hour=9), end_time=time(hour=12), is_enabled=True)]
    returned_rules = [SimpleNamespace(id=uuid4())]
    service.schedule_repository.list_availability_rules.return_value = returned_rules

    result = service.replace_availability_rules(current_user, payload)

    assert result == returned_rules
    service.schedule_repository.replace_availability_rules.assert_called_once()
    service.uow.commit.assert_called_once()


@pytest.mark.unit
def test_create_break_rejects_overlapping_existing_windows() -> None:
    """Reject break creation when the requested slot overlaps an existing break."""

    service = object.__new__(SpecialistScheduleService)
    service.uow = Mock()
    service.schedule_repository = Mock()
    service.logger = Mock()
    service._get_specialist_for_user = Mock(return_value=SimpleNamespace(id=uuid4()))
    service.schedule_repository.list_breaks.return_value = [SimpleNamespace(weekday=2, start_time=time(hour=12), end_time=time(hour=13))]
    payload = BreakCreateRequest(weekday=2, start_time=time(hour=12, minute=30), end_time=time(hour=13, minute=30), label="Lunch")

    with pytest.raises(SpecialistScheduleValidationError, match="Break windows cannot overlap on the same weekday."):
        service.create_break(_specialist_user(), payload)


@pytest.mark.unit
def test_update_break_and_delete_break_handle_missing_rows() -> None:
    """Update breaks in place and reject delete or update operations for unknown ids."""

    service = object.__new__(SpecialistScheduleService)
    service.db = Mock()
    service.uow = Mock()
    service.schedule_repository = Mock()
    service.logger = Mock()
    specialist = SimpleNamespace(id=uuid4())
    service._get_specialist_for_user = Mock(return_value=specialist)
    current_user = _specialist_user()
    specialist_break = SimpleNamespace(id=uuid4(), weekday=1, start_time=time(hour=9), end_time=time(hour=10), label="Old")
    service.schedule_repository.get_break.side_effect = [specialist_break, None, None]
    service.schedule_repository.list_breaks.return_value = [specialist_break]
    payload = BreakUpdateRequest(weekday=2, start_time=time(hour=14), end_time=time(hour=15), label=" Updated label ")

    updated = service.update_break(current_user, specialist_break.id, payload)

    assert updated is specialist_break
    assert specialist_break.weekday == 2
    assert specialist_break.start_time == time(hour=14)
    assert specialist_break.end_time == time(hour=15)
    assert specialist_break.label == "Updated label"
    service.uow.commit.assert_called_once()
    service.uow.refresh.assert_called_once_with(specialist_break)

    with pytest.raises(SpecialistScheduleItemNotFoundError, match="Break not found."):
        service.update_break(current_user, uuid4(), payload)

    with pytest.raises(SpecialistScheduleItemNotFoundError, match="Break not found."):
        service.delete_break(current_user, uuid4())


@pytest.mark.unit
def test_create_time_off_rejects_end_before_start() -> None:
    """Reject invalid time-off windows whose end is not after the start."""

    service = object.__new__(SpecialistScheduleService)
    service.uow = Mock()
    service.specialist_repository = Mock()
    service.schedule_repository = Mock()
    service.appointment_repository = Mock()
    service.availability_service = Mock()
    service.logger = Mock()
    specialist = SimpleNamespace(id=uuid4())
    current_user = _specialist_user()
    service._get_specialist_for_user = Mock(return_value=specialist)
    future_start = datetime.now(UTC) + timedelta(days=1)
    payload = TimeOffCreateRequest(start_datetime=future_start, end_datetime=future_start, reason="Vacation")

    with pytest.raises(SpecialistScheduleValidationError, match="Time off end must be after start."):
        service.create_time_off(current_user, payload)


@pytest.mark.unit
def test_update_and_delete_time_off_handle_success_and_missing_rows() -> None:
    """Update time-off rows in place and reject unknown ids."""

    service = object.__new__(SpecialistScheduleService)
    service.db = Mock()
    service.uow = Mock()
    service.schedule_repository = Mock()
    service.logger = Mock()
    specialist = SimpleNamespace(id=uuid4())
    service._get_specialist_for_user = Mock(return_value=specialist)
    current_user = _specialist_user()
    existing_time_off = SimpleNamespace(
        id=uuid4(),
        start_datetime=datetime.now(UTC) + timedelta(days=2),
        end_datetime=datetime.now(UTC) + timedelta(days=3),
        reason="Old",
    )
    service.schedule_repository.get_time_off.side_effect = [existing_time_off, None, None]
    payload = TimeOffUpdateRequest(
        start_datetime=datetime.now(UTC) + timedelta(days=5),
        end_datetime=datetime.now(UTC) + timedelta(days=6),
        reason=" Updated reason ",
    )

    updated = service.update_time_off(current_user, existing_time_off.id, payload)

    assert updated is existing_time_off
    assert updated.reason == "Updated reason"
    service.uow.commit.assert_called_once()
    service.uow.refresh.assert_called_once_with(existing_time_off)

    with pytest.raises(SpecialistScheduleItemNotFoundError, match="Time off not found."):
        service.update_time_off(current_user, uuid4(), payload)

    with pytest.raises(SpecialistScheduleItemNotFoundError, match="Time off not found."):
        service.delete_time_off(current_user, uuid4())


@pytest.mark.unit
def test_get_specialist_for_user_raises_when_profile_missing() -> None:
    """Reject schedule operations for specialist users without linked profiles."""

    service = object.__new__(SpecialistScheduleService)
    service.specialist_repository = Mock()
    service.specialist_repository.get_by_user_id.return_value = None

    with pytest.raises(SpecialistProfileNotFoundError, match="Specialist profile not found."):
        service._get_specialist_for_user(_specialist_user())


@pytest.mark.unit
def test_get_calendar_aggregates_schedule_components() -> None:
    """Assemble the specialist calendar payload from repository and availability data."""

    service = object.__new__(SpecialistScheduleService)
    service.uow = Mock()
    service.specialist_repository = Mock()
    service.schedule_repository = Mock()
    service.appointment_repository = Mock()
    service.availability_service = Mock()
    service.logger = Mock()
    specialist = SimpleNamespace(id=uuid4())
    current_user = _specialist_user()
    service._get_specialist_for_user = Mock(return_value=specialist)
    appointments = [SimpleNamespace(id=uuid4())]
    slots = [SimpleNamespace(start_datetime=datetime.now(UTC), end_datetime=datetime.now(UTC) + timedelta(hours=2))]
    breaks = [SimpleNamespace(id=uuid4())]
    time_off = [SimpleNamespace(id=uuid4())]
    service.appointment_repository.list_for_specialist_calendar.return_value = appointments
    service.availability_service.get_available_slots.return_value = slots
    service.schedule_repository.list_breaks.return_value = breaks
    service.schedule_repository.list_time_off_in_window.return_value = time_off

    result = service.get_calendar(current_user, datetime.now(UTC).date(), (datetime.now(UTC) + timedelta(days=2)).date())

    assert result == (appointments, slots, breaks, time_off, specialist.id)
