"""Repository tests for notification persistence helpers."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

import pytest
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus, NotificationType
from app.models.notification import Notification
from app.models.specialist import Specialist
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository


@pytest.mark.integration
def test_notification_repository_orders_unread_first_and_scopes_lookups(
    db_session: Session,
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
    appointment_factory: Callable[..., Appointment],
) -> None:
    """Order unread notifications first and scope appointment/type lookups to the owner."""

    # Arrange
    user = user_factory()
    other_user = user_factory()
    specialist = specialist_factory(full_name="Dr. Notification Repo")
    appointment = appointment_factory(
        user=user,
        specialist=specialist,
        preferred_datetime=datetime(2026, 4, 20, 14, tzinfo=UTC),
        status=AppointmentStatus.CONFIRMED,
    )
    unread_old = Notification(
        user_id=user.id,
        appointment_id=appointment.id,
        type=NotificationType.APPOINTMENT_CONFIRMED,
        title="Older unread",
        message="Older unread message",
        is_read=False,
    )
    unread_new = Notification(
        user_id=user.id,
        appointment_id=appointment.id,
        type=NotificationType.APPOINTMENT_REMINDER,
        title="Newer unread",
        message="Newer unread message",
        is_read=False,
    )
    read_latest = Notification(
        user_id=user.id,
        appointment_id=appointment.id,
        type=NotificationType.APPOINTMENT_CANCELLED,
        title="Read latest",
        message="Read latest message",
        is_read=True,
        read_at=datetime(2026, 4, 20, 11, tzinfo=UTC),
    )
    foreign = Notification(
        user_id=other_user.id,
        type=NotificationType.APPOINTMENT_CONFIRMED,
        title="Foreign",
        message="Foreign message",
        is_read=False,
    )
    db_session.add_all([unread_old, unread_new, read_latest, foreign])
    db_session.flush()
    unread_old.created_at = datetime(2026, 4, 20, 8, tzinfo=UTC)
    unread_new.created_at = datetime(2026, 4, 20, 10, tzinfo=UTC)
    read_latest.created_at = datetime(2026, 4, 20, 12, tzinfo=UTC)
    foreign.created_at = datetime(2026, 4, 20, 13, tzinfo=UTC)
    db_session.flush()
    repository = NotificationRepository(db_session)

    # Act
    listed = repository.list_for_user(user.id)
    unread_only = repository.list_unread_for_user(user.id)
    owned_notification = repository.get_for_user(user.id, unread_old.id)
    matching_notification = repository.get_for_user_type_and_appointment(
        user.id,
        NotificationType.APPOINTMENT_REMINDER,
        appointment.id,
    )

    # Assert
    assert [item.id for item in listed] == [unread_new.id, unread_old.id, read_latest.id]
    assert [item.id for item in unread_only] == [unread_new.id, unread_old.id]
    assert repository.count_for_user(user.id) == 3
    assert repository.count_unread_for_user(user.id) == 2
    assert owned_notification is not None
    assert owned_notification.id == unread_old.id
    assert repository.get_for_user(other_user.id, unread_old.id) is None
    assert matching_notification is not None
    assert matching_notification.id == unread_new.id
    assert (
        repository.get_for_user_type_and_appointment(
            user.id,
            NotificationType.APPOINTMENT_REJECTED,
            appointment.id,
        )
        is None
    )


@pytest.mark.integration
def test_notification_repository_bulk_helpers_respect_filters(
    db_session: Session,
    user_factory: Callable[..., User],
) -> None:
    """Return and delete only notifications matching the provided bulk filter criteria."""

    # Arrange
    user = user_factory()
    db_session.add_all(
        [
            Notification(
                user_id=user.id,
                type=NotificationType.APPOINTMENT_REMINDER,
                title="Unread reminder",
                message="Unread reminder message",
                is_read=False,
            ),
            Notification(
                user_id=user.id,
                type=NotificationType.APPOINTMENT_REMINDER,
                title="Read reminder",
                message="Read reminder message",
                is_read=True,
                read_at=datetime(2026, 4, 20, 9, tzinfo=UTC),
            ),
            Notification(
                user_id=user.id,
                type=NotificationType.APPOINTMENT_CONFIRMED,
                title="Unread confirmed",
                message="Unread confirmed message",
                is_read=False,
            ),
        ]
    )
    db_session.flush()
    repository = NotificationRepository(db_session)

    # Act
    matched = repository.list_many_for_user(
        user.id,
        notification_type=NotificationType.APPOINTMENT_REMINDER,
    )
    deleted = repository.delete_many_for_user(
        user.id,
        is_read=True,
        notification_type=NotificationType.APPOINTMENT_REMINDER,
    )

    # Assert
    assert len(matched) == 2
    assert deleted == 1
    remaining = repository.list_for_user(user.id, page=1, page_size=10)
    assert len(remaining) == 2
    assert all(item.title != "Read reminder" for item in remaining)
