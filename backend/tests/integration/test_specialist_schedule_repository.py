"""Repository tests for specialist scheduling persistence helpers."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, date, datetime, time

import pytest
from sqlalchemy.orm import Session

from app.models.specialist import Specialist
from app.models.specialist_availability_rule import SpecialistAvailabilityRule
from app.models.specialist_break import SpecialistBreak
from app.models.specialist_time_off import SpecialistTimeOff
from app.repositories.specialist_schedule_repository import SpecialistScheduleRepository


@pytest.mark.integration
def test_specialist_schedule_repository_replaces_rules_and_lists_breaks(
    db_session: Session,
    specialist_factory: Callable[..., Specialist],
) -> None:
    """Replace recurring rules and return sorted breaks for a specialist."""

    specialist = specialist_factory(full_name="Dr. Schedule Repo")
    repository = SpecialistScheduleRepository(db_session)
    first_rules = [
        SpecialistAvailabilityRule(
            specialist_id=specialist.id,
            weekday=1,
            start_time=time(hour=9),
            end_time=time(hour=12),
            is_enabled=True,
        ),
        SpecialistAvailabilityRule(
            specialist_id=specialist.id,
            weekday=3,
            start_time=time(hour=13),
            end_time=time(hour=17),
            is_enabled=True,
        ),
    ]

    repository.replace_availability_rules(specialist.id, first_rules)
    replacement_rules = [
        SpecialistAvailabilityRule(
            specialist_id=specialist.id,
            weekday=4,
            start_time=time(hour=10),
            end_time=time(hour=14),
            is_enabled=True,
        ),
    ]
    repository.replace_availability_rules(specialist.id, replacement_rules)
    morning_break = repository.add_break(
        SpecialistBreak(
            specialist_id=specialist.id,
            weekday=4,
            start_time=time(hour=11),
            end_time=time(hour=11, minute=30),
            label="Coffee",
        )
    )
    afternoon_break = repository.add_break(
        SpecialistBreak(
            specialist_id=specialist.id,
            weekday=4,
            start_time=time(hour=15),
            end_time=time(hour=15, minute=30),
            label="Tea",
        )
    )

    availability_rules = repository.list_availability_rules(specialist.id)
    breaks = repository.list_breaks(specialist.id)
    stored_break = repository.get_break(specialist.id, morning_break.id)

    assert [item.weekday for item in availability_rules] == [4]
    assert [item.id for item in breaks] == [morning_break.id, afternoon_break.id]
    assert stored_break is not None
    assert stored_break.label == "Coffee"


@pytest.mark.integration
def test_specialist_schedule_repository_filters_time_off_window(
    db_session: Session,
    specialist_factory: Callable[..., Specialist],
) -> None:
    """Return only time-off periods that overlap the requested date window."""

    specialist = specialist_factory(full_name="Dr. Time Off Repo")
    repository = SpecialistScheduleRepository(db_session)
    inside_window = repository.add_time_off(
        SpecialistTimeOff(
            specialist_id=specialist.id,
            start_datetime=datetime(2026, 4, 22, 9, tzinfo=UTC),
            end_datetime=datetime(2026, 4, 22, 12, tzinfo=UTC),
            reason="Inside",
        )
    )
    repository.add_time_off(
        SpecialistTimeOff(
            specialist_id=specialist.id,
            start_datetime=datetime(2026, 4, 25, 9, tzinfo=UTC),
            end_datetime=datetime(2026, 4, 25, 12, tzinfo=UTC),
            reason="Outside",
        )
    )

    listed_time_off = repository.list_time_off(specialist.id)
    window_matches = repository.list_time_off_in_window(
        specialist.id,
        date(2026, 4, 21),
        date(2026, 4, 23),
    )
    stored_time_off = repository.get_time_off(specialist.id, inside_window.id)

    assert len(listed_time_off) == 2
    assert [item.id for item in window_matches] == [inside_window.id]
    assert stored_time_off is not None
    assert stored_time_off.reason == "Inside"
