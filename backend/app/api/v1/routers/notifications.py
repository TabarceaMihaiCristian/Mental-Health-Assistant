"""Notification read endpoints for authenticated users."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.enums import NotificationType
from app.models.user import User
from app.schemas.notification import (
    NotificationBulkActionResponse,
    NotificationBulkMarkRequest,
    NotificationPageResponse,
    NotificationResponse,
    NotificationUnreadCountResponse,
)
from app.services.notification_service import (
    NotificationNotFoundError,
    NotificationService,
)

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("")
def list_notifications(
    current_user: CurrentUser,
    db: DbSession,
    is_read: Annotated[bool | None, Query()] = None,
    notification_type: Annotated[NotificationType | None, Query(alias="type")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> NotificationPageResponse:
    """List notifications visible to the authenticated user."""

    notifications, total = NotificationService(db).list_filtered_notifications(
        current_user,
        is_read=is_read,
        notification_type=notification_type,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return NotificationPageResponse(
        items=[NotificationResponse.model_validate(item) for item in notifications],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get("/unread-count")
def get_unread_notification_count(
    current_user: CurrentUser,
    db: DbSession,
) -> NotificationUnreadCountResponse:
    """Return the unread notification badge count for the authenticated user."""

    unread_count = NotificationService(db).get_unread_count(current_user)
    return NotificationUnreadCountResponse(unread_count=unread_count)


@router.patch("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> NotificationResponse:
    """Mark a single notification as read for the authenticated user."""

    try:
        notification = NotificationService(db).mark_as_read(current_user, notification_id)
    except NotificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return NotificationResponse.model_validate(notification)


@router.patch("/{notification_id}/unread")
def mark_notification_as_unread(
    notification_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> NotificationResponse:
    """Mark a single notification as unread for the authenticated user."""

    try:
        notification = NotificationService(db).mark_as_unread(current_user, notification_id)
    except NotificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return NotificationResponse.model_validate(notification)


@router.patch("/read-all")
def mark_all_notifications_as_read(
    current_user: CurrentUser,
    db: DbSession,
) -> list[NotificationResponse]:
    """Mark all unread notifications as read for the authenticated user."""

    notifications = NotificationService(db).mark_all_as_read(current_user)
    return [NotificationResponse.model_validate(item) for item in notifications]


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    """Delete a single notification from the authenticated user's inbox."""

    try:
        NotificationService(db).delete_notification(current_user, notification_id)
    except NotificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("")
def bulk_delete_notifications(
    current_user: CurrentUser,
    db: DbSession,
    is_read: Annotated[bool | None, Query()] = None,
    notification_type: Annotated[NotificationType | None, Query(alias="type")] = None,
) -> NotificationBulkActionResponse:
    """Delete notifications in bulk using the same optional inbox filters."""

    affected_count = NotificationService(db).delete_filtered_notifications(
        current_user,
        is_read=is_read,
        notification_type=notification_type,
    )
    return NotificationBulkActionResponse(affected_count=affected_count)


@router.patch("/mark")
def bulk_mark_notifications(
    payload: NotificationBulkMarkRequest,
    current_user: CurrentUser,
    db: DbSession,
    is_read: Annotated[bool | None, Query()] = None,
    notification_type: Annotated[NotificationType | None, Query(alias="type")] = None,
) -> NotificationBulkActionResponse:
    """Mark notifications in bulk as read or unread using the same inbox filters."""

    affected_count = NotificationService(db).mark_filtered_notifications(
        current_user,
        mark_as_read=payload.mark_as_read,
        is_read=is_read,
        notification_type=notification_type,
    )
    return NotificationBulkActionResponse(affected_count=affected_count)
