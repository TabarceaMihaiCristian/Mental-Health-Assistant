"""Repositories for notification persistence and ownership-scoped lookup."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import NotificationType
from app.models.notification import Notification


class NotificationRepository:
    """Database access helpers for in-app notifications."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to one SQLAlchemy session."""

        self.db = db

    def add(self, notification: Notification) -> Notification:
        """Persist a notification row."""

        self.db.add(notification)
        self.db.flush()
        return notification

    def delete(self, notification: Notification) -> None:
        """Delete a notification row."""

        self.db.delete(notification)
        self.db.flush()

    def list_for_user(
        self,
        user_id: UUID,
        *,
        is_read: bool | None = None,
        notification_type: NotificationType | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> list[Notification]:
        """Return notifications for a user with optional read-state and type filters."""

        statement = select(Notification).where(Notification.user_id == user_id)
        if is_read is not None:
            statement = statement.where(Notification.is_read.is_(is_read))
        if notification_type is not None:
            statement = statement.where(Notification.type == notification_type)
        offset = (page - 1) * page_size
        statement = statement.order_by(
            Notification.is_read.asc(),
            Notification.created_at.desc(),
        ).offset(offset).limit(page_size)
        return list(self.db.scalars(statement).all())

    def count_for_user(
        self,
        user_id: UUID,
        *,
        is_read: bool | None = None,
        notification_type: NotificationType | None = None,
    ) -> int:
        """Return the notification count for a user with optional filters."""

        statement = select(Notification.id).where(Notification.user_id == user_id)
        if is_read is not None:
            statement = statement.where(Notification.is_read.is_(is_read))
        if notification_type is not None:
            statement = statement.where(Notification.type == notification_type)
        return len(list(self.db.scalars(statement).all()))

    def get_for_user_type_and_appointment(
        self,
        user_id: UUID,
        notification_type,
        appointment_id: UUID,
    ) -> Notification | None:
        """Return one notification matching a user/type/appointment combination."""

        statement = select(Notification).where(
            Notification.user_id == user_id,
            Notification.type == notification_type,
            Notification.appointment_id == appointment_id,
        )
        return self.db.scalar(statement)

    def get_for_user(self, user_id: UUID, notification_id: UUID) -> Notification | None:
        """Return one notification only if it belongs to the given user."""

        statement = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        return self.db.scalar(statement)

    def list_unread_for_user(self, user_id: UUID) -> list[Notification]:
        """Return unread notifications for a user."""

        statement = (
            select(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .order_by(Notification.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def count_unread_for_user(self, user_id: UUID) -> int:
        """Return the unread notification count for a user."""

        statement = select(Notification.id).where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        return len(list(self.db.scalars(statement).all()))

    def delete_many_for_user(
        self,
        user_id: UUID,
        *,
        is_read: bool | None = None,
        notification_type: NotificationType | None = None,
    ) -> int:
        """Delete notifications for a user matching the provided optional filters."""

        notifications = self.list_for_user(
            user_id,
            is_read=is_read,
            notification_type=notification_type,
            page=1,
            page_size=10_000,
        )
        for notification in notifications:
            self.db.delete(notification)
        self.db.flush()
        return len(notifications)

    def list_many_for_user(
        self,
        user_id: UUID,
        *,
        is_read: bool | None = None,
        notification_type: NotificationType | None = None,
    ) -> list[Notification]:
        """Return all notifications for a user matching the provided optional filters."""

        return self.list_for_user(
            user_id,
            is_read=is_read,
            notification_type=notification_type,
            page=1,
            page_size=10_000,
        )
