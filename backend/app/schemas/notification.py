"""Schemas for in-app notification reads, updates, and pagination."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import NotificationType


class NotificationBulkActionResponse(BaseModel):
    """Result payload for bulk notification inbox actions."""

    affected_count: int


class NotificationBulkMarkRequest(BaseModel):
    """Request payload for bulk notification read-state updates."""

    mark_as_read: bool = Field(
        ...,
        description="Whether matching notifications should be marked as read.",
    )


class NotificationUnreadCountResponse(BaseModel):
    """Unread notification badge count for the authenticated user."""

    unread_count: int


class NotificationResponse(BaseModel):
    """Serialized notification record for the authenticated user."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    appointment_id: UUID | None
    type: NotificationType
    title: str
    message: str
    is_read: bool
    read_at: datetime | None
    created_at: datetime


class NotificationPageResponse(BaseModel):
    """Paginated notification response for inbox views."""

    items: list[NotificationResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
