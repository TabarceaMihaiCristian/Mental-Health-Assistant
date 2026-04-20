"""Repository tests for appointment persistence helpers."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, date, datetime

import pytest
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.models.specialist import Specialist
from app.models.user import User
from app.repositories.appointment_repository import AppointmentRepository


@pytest.mark.integration
def test_appointment_repository_scopes_ordering_and_overlap_queries(
    db_session: Session,
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
    appointment_factory: Callable[..., Appointment],
) -> None:
    """Return appointments with the expected ownership, ordering, and overlap behavior."""

    # Arrange
    user = user_factory()
    other_user = user_factory()
    specialist = specialist_factory(full_name="Dr. Repository")
    other_specialist = specialist_factory(full_name="Dr. Elsewhere")
    requested = appointment_factory(
        user=user,
        specialist=specialist,
        preferred_datetime=datetime(2026, 4, 20, 9, tzinfo=UTC),
        status=AppointmentStatus.REQUESTED,
    )
    confirmed = appointment_factory(
        user=user,
        specialist=specialist,
        preferred_datetime=datetime(2026, 4, 21, 9, tzinfo=UTC),
        status=AppointmentStatus.CONFIRMED,
    )
    cancelled = appointment_factory(
        user=user,
        specialist=specialist,
        preferred_datetime=datetime(2026, 4, 22, 9, tzinfo=UTC),
        status=AppointmentStatus.CANCELLED,
    )
    specialist_owned_by_other_user = appointment_factory(
        user=other_user,
        specialist=specialist,
        preferred_datetime=datetime(2026, 4, 23, 9, tzinfo=UTC),
        status=AppointmentStatus.REQUESTED,
    )
    user_with_other_specialist = appointment_factory(
        user=user,
        specialist=other_specialist,
        preferred_datetime=datetime(2026, 4, 24, 9, tzinfo=UTC),
        status=AppointmentStatus.REQUESTED,
    )
    repository = AppointmentRepository(db_session)

    # Act
    user_appointments = repository.list_for_user(user.id)
    specialist_appointments = repository.list_for_specialist(specialist.id)
    blocking_window = repository.list_for_specialist_in_window(
        specialist.id,
        date(2026, 4, 21),
        date(2026, 4, 22),
    )
    calendar_window = repository.list_for_specialist_calendar(
        specialist.id,
        date(2026, 4, 22),
        date(2026, 4, 22),
    )
    owned_appointment = repository.get_owned_appointment(user.id, requested.id)
    specialist_appointment = repository.get_for_specialist(specialist.id, requested.id)

    # Assert
    assert [item.id for item in user_appointments] == [
        user_with_other_specialist.id,
        cancelled.id,
        confirmed.id,
        requested.id,
    ]
    assert [item.id for item in specialist_appointments] == [
        requested.id,
        confirmed.id,
        cancelled.id,
        specialist_owned_by_other_user.id,
    ]
    assert owned_appointment is not None
    assert owned_appointment.id == requested.id
    assert repository.get_owned_appointment(other_user.id, requested.id) is None
    assert specialist_appointment is not None
    assert specialist_appointment.id == requested.id
    assert repository.get_for_specialist(other_specialist.id, requested.id) is None
    assert [item.id for item in blocking_window] == [confirmed.id]
    assert [item.id for item in calendar_window] == [cancelled.id]
    assert repository.has_overlapping_active_appointment(
        specialist.id,
        start_datetime=datetime(2026, 4, 21, 10, tzinfo=UTC),
        end_datetime=datetime(2026, 4, 21, 11, tzinfo=UTC),
    )
    assert not repository.has_overlapping_active_appointment(
        specialist.id,
        start_datetime=datetime(2026, 4, 21, 10, tzinfo=UTC),
        end_datetime=datetime(2026, 4, 21, 11, tzinfo=UTC),
        exclude_appointment_id=confirmed.id,
    )


@pytest.mark.integration
def test_appointment_repository_admin_filters_counts_and_reminder_window(
    db_session: Session,
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
    appointment_factory: Callable[..., Appointment],
) -> None:
    """Keep filtered admin queries, counts, and reminder selection consistent."""

    # Arrange
    user = user_factory()
    specialist = specialist_factory(full_name="Dr. Admin Repo")
    first = appointment_factory(
        user=user,
        specialist=specialist,
        preferred_datetime=datetime(2026, 4, 25, 9, tzinfo=UTC),
        status=AppointmentStatus.CONFIRMED,
    )
    second = appointment_factory(
        user=user,
        specialist=specialist,
        preferred_datetime=datetime(2026, 4, 25, 13, tzinfo=UTC),
        status=AppointmentStatus.CONFIRMED,
    )
    third = appointment_factory(
        user=user,
        specialist=specialist,
        preferred_datetime=datetime(2026, 4, 26, 9, tzinfo=UTC),
        status=AppointmentStatus.REQUESTED,
    )
    second.reminder_sent_at = datetime(2026, 4, 24, 12, tzinfo=UTC)
    first.created_at = datetime(2026, 4, 20, 8, tzinfo=UTC)
    second.created_at = datetime(2026, 4, 20, 9, tzinfo=UTC)
    third.created_at = datetime(2026, 4, 20, 10, tzinfo=UTC)
    db_session.flush()
    repository = AppointmentRepository(db_session)

    # Act
    filtered_page = repository.list_all_filtered(
        status=AppointmentStatus.CONFIRMED,
        specialist_id=specialist.id,
        user_id=user.id,
        date_from=date(2026, 4, 25),
        date_to=date(2026, 4, 25),
        page=1,
        page_size=1,
    )
    filtered_count = repository.count_all_filtered(
        status=AppointmentStatus.CONFIRMED,
        specialist_id=specialist.id,
        user_id=user.id,
        date_from=date(2026, 4, 25),
        date_to=date(2026, 4, 25),
    )
    reminders = repository.list_confirmed_starting_between(
        window_start=datetime(2026, 4, 25, 9, tzinfo=UTC),
        window_end=datetime(2026, 4, 25, 10, tzinfo=UTC),
    )
    stored_first = repository.get_by_id(first.id)

    # Assert
    assert filtered_count == 2
    assert [item.id for item in filtered_page] == [second.id]
    assert stored_first is not None
    assert stored_first.id == first.id
    assert repository.count_all_filtered(status=AppointmentStatus.CANCELLED) == 0
    assert [item.id for item in reminders] == [first.id]
    assert [item.id for item in repository.list_all()[:2]] == [third.id, second.id]
