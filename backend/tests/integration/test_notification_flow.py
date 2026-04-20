"""Integration tests for notification inbox endpoints."""

from __future__ import annotations

from collections.abc import Callable

from fastapi.testclient import TestClient

from app.models.enums import NotificationType
from app.models.user import User
from app.services.notification_service import NotificationService


def test_notification_inbox_supports_read_unread_and_unread_count(
    client: TestClient,
    db_session,
    user_factory: Callable[..., User],
    auth_headers_factory: Callable[[User], dict[str, str]],
) -> None:
    """Allow a user to inspect and update notification read state."""

    # Arrange
    user = user_factory()
    notification = NotificationService(db_session).create_notification(
        user_id=user.id,
        notification_type=NotificationType.APPOINTMENT_REQUESTED,
        title="New appointment request",
        message="A new appointment request is waiting for your review.",
    )
    headers = auth_headers_factory(user)

    # Act
    unread_count_response = client.get("/api/v1/notifications/unread-count", headers=headers)
    mark_read_response = client.patch(
        f"/api/v1/notifications/{notification.id}/read",
        headers=headers,
    )
    mark_unread_response = client.patch(
        f"/api/v1/notifications/{notification.id}/unread",
        headers=headers,
    )

    # Assert
    assert unread_count_response.status_code == 200
    assert unread_count_response.json()["unread_count"] == 1
    assert mark_read_response.status_code == 200
    assert mark_read_response.json()["is_read"] is True
    assert mark_unread_response.status_code == 200
    assert mark_unread_response.json()["is_read"] is False


def test_notification_listing_supports_filters_and_bulk_mark(
    client: TestClient,
    db_session,
    user_factory: Callable[..., User],
    auth_headers_factory: Callable[[User], dict[str, str]],
) -> None:
    """Support inbox filtering and bulk read-state updates."""

    # Arrange
    user = user_factory()
    notification_service = NotificationService(db_session)
    notification_service.create_notification(
        user_id=user.id,
        notification_type=NotificationType.APPOINTMENT_REMINDER,
        title="Reminder",
        message="You have an appointment tomorrow.",
    )
    notification_service.create_notification(
        user_id=user.id,
        notification_type=NotificationType.APPOINTMENT_CONFIRMED,
        title="Confirmed",
        message="Your appointment has been confirmed.",
    )
    headers = auth_headers_factory(user)

    # Act
    filtered_response = client.get(
        "/api/v1/notifications?type=appointment_reminder&page=1&page_size=10",
        headers=headers,
    )
    bulk_mark_response = client.patch(
        "/api/v1/notifications/mark?type=appointment_reminder",
        json={"mark_as_read": True},
        headers=headers,
    )

    # Assert
    assert filtered_response.status_code == 200
    body = filtered_response.json()
    assert body["total"] == 1
    assert body["items"][0]["type"] == "appointment_reminder"
    assert bulk_mark_response.status_code == 200
    assert bulk_mark_response.json()["affected_count"] == 1


def test_notification_bulk_delete_uses_filters(
    client: TestClient,
    db_session,
    user_factory: Callable[..., User],
    auth_headers_factory: Callable[[User], dict[str, str]],
) -> None:
    """Delete only the notifications matching the requested inbox filters."""

    # Arrange
    user = user_factory()
    notification_service = NotificationService(db_session)
    notification_service.create_notification(
        user_id=user.id,
        notification_type=NotificationType.APPOINTMENT_REMINDER,
        title="Reminder A",
        message="First reminder.",
    )
    notification_service.create_notification(
        user_id=user.id,
        notification_type=NotificationType.APPOINTMENT_REMINDER,
        title="Reminder B",
        message="Second reminder.",
    )
    notification_service.create_notification(
        user_id=user.id,
        notification_type=NotificationType.APPOINTMENT_CONFIRMED,
        title="Confirmed",
        message="This should remain.",
    )
    headers = auth_headers_factory(user)

    # Act
    delete_response = client.delete(
        "/api/v1/notifications?type=appointment_reminder",
        headers=headers,
    )
    list_response = client.get("/api/v1/notifications?page=1&page_size=10", headers=headers)

    # Assert
    assert delete_response.status_code == 200
    assert delete_response.json()["affected_count"] == 2
    assert list_response.status_code == 200
    body = list_response.json()
    assert body["total"] == 1
    assert body["items"][0]["type"] == "appointment_confirmed"
