"""Application service for in-app notification delivery and read state."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.unit_of_work import UnitOfWork
from app.models.enums import NotificationType
from app.models.notification import Notification
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository
from app.utils.logging import get_app_logger, log_event


class NotificationNotFoundError(ValueError):
    """Raised when a notification does not belong to the current user."""


NOTIFICATION_NOT_FOUND_MESSAGE = "Notification not found."


class NotificationService:
    """Create and manage in-app notifications."""

    def __init__(self, db: Session) -> None:
        """Bind notification workflows to one SQLAlchemy session."""

        self.db = db
        self.uow = UnitOfWork(db)
        self.repository = NotificationRepository(db)
        self.logger = get_app_logger(__name__)

    def create_notification(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        message: str,
        appointment_id: UUID | None = None,
    ) -> Notification:
        """Persist a new notification for a target user."""

        notification = Notification(
            user_id=user_id,
            appointment_id=appointment_id,
            type=notification_type,
            title=title,
            message=message,
        )
        self.repository.add(notification)
        self.uow.commit()
        self.uow.refresh(notification)
        log_event(
            self.logger,
            "notifications.created",
            user_id=user_id,
            notification_id=notification.id,
            appointment_id=notification.appointment_id,
            type=notification.type.value,
        )
        return notification

    def create_unique_notification(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        message: str,
        appointment_id: UUID,
    ) -> Notification:
        """Create one appointment-linked notification unless it already exists."""

        existing = self.repository.get_for_user_type_and_appointment(
            user_id,
            notification_type,
            appointment_id,
        )
        if existing is not None:
            return existing
        return self.create_notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            appointment_id=appointment_id,
        )

    def list_notifications(self, user: User) -> list[Notification]:
        """Return all notifications visible to the authenticated user."""

        return self.repository.list_for_user(user.id)

    def list_filtered_notifications(
        self,
        user: User,
        *,
        is_read: bool | None = None,
        notification_type: NotificationType | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Notification], int]:
        """Return paginated notifications and the total count for the authenticated user."""

        notifications = self.repository.list_for_user(
            user.id,
            is_read=is_read,
            notification_type=notification_type,
            page=page,
            page_size=page_size,
        )
        total = self.repository.count_for_user(
            user.id,
            is_read=is_read,
            notification_type=notification_type,
        )
        return notifications, total

    def get_unread_count(self, user: User) -> int:
        """Return the unread notification count for the authenticated user."""

        return self.repository.count_unread_for_user(user.id)

    def mark_as_read(self, user: User, notification_id: UUID) -> Notification:
        """Mark a single notification as read for the authenticated user."""

        notification = self.repository.get_for_user(user.id, notification_id)
        if notification is None:
            raise NotificationNotFoundError(NOTIFICATION_NOT_FOUND_MESSAGE)
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now(UTC)
            self.uow.commit()
            self.uow.refresh(notification)
            log_event(
                self.logger,
                "notifications.read",
                user_id=user.id,
                notification_id=notification.id,
            )
        return notification

    def mark_as_unread(self, user: User, notification_id: UUID) -> Notification:
        """Mark a single notification as unread for the authenticated user."""

        notification = self.repository.get_for_user(user.id, notification_id)
        if notification is None:
            raise NotificationNotFoundError(NOTIFICATION_NOT_FOUND_MESSAGE)
        if notification.is_read:
            notification.is_read = False
            notification.read_at = None
            self.uow.commit()
            self.uow.refresh(notification)
            log_event(
                self.logger,
                "notifications.unread",
                user_id=user.id,
                notification_id=notification.id,
            )
        return notification

    def mark_all_as_read(self, user: User) -> list[Notification]:
        """Mark every unread notification as read for the authenticated user."""

        notifications = self.repository.list_unread_for_user(user.id)
        if not notifications:
            return []

        read_at = datetime.now(UTC)
        for notification in notifications:
            notification.is_read = True
            notification.read_at = read_at

        self.uow.commit()
        for notification in notifications:
            self.uow.refresh(notification)
        log_event(
            self.logger,
            "notifications.read_all",
            user_id=user.id,
            count=len(notifications),
        )
        return notifications

    def delete_notification(self, user: User, notification_id: UUID) -> None:
        """Delete a single notification belonging to the authenticated user."""

        notification = self.repository.get_for_user(user.id, notification_id)
        if notification is None:
            raise NotificationNotFoundError(NOTIFICATION_NOT_FOUND_MESSAGE)
        self.repository.delete(notification)
        self.uow.commit()
        log_event(
            self.logger,
            "notifications.deleted",
            user_id=user.id,
            notification_id=notification_id,
        )

    def delete_filtered_notifications(
        self,
        user: User,
        *,
        is_read: bool | None = None,
        notification_type: NotificationType | None = None,
    ) -> int:
        """Delete notifications matching the provided inbox filters for one user."""

        affected_count = self.repository.delete_many_for_user(
            user.id,
            is_read=is_read,
            notification_type=notification_type,
        )
        if affected_count > 0:
            self.uow.commit()
            log_event(
                self.logger,
                "notifications.deleted_many",
                user_id=user.id,
                count=affected_count,
                is_read=is_read,
                type=None if notification_type is None else notification_type.value,
            )
        return affected_count

    def mark_filtered_notifications(
        self,
        user: User,
        *,
        mark_as_read: bool,
        is_read: bool | None = None,
        notification_type: NotificationType | None = None,
    ) -> int:
        """Bulk update notification read state for one user's inbox filters."""

        notifications = self.repository.list_many_for_user(
            user.id,
            is_read=is_read,
            notification_type=notification_type,
        )
        affected_notifications = [
            notification
            for notification in notifications
            if notification.is_read != mark_as_read
        ]
        if not affected_notifications:
            return 0

        read_at = datetime.now(UTC) if mark_as_read else None
        for notification in affected_notifications:
            notification.is_read = mark_as_read
            notification.read_at = read_at

        self.uow.commit()
        event_name = (
            "notifications.marked_read_many"
            if mark_as_read
            else "notifications.marked_unread_many"
        )
        log_event(
            self.logger,
            event_name,
            user_id=user.id,
            count=len(affected_notifications),
            is_read=is_read,
            type=None if notification_type is None else notification_type.value,
        )
        return len(affected_notifications)
