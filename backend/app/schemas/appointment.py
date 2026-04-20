"""Schemas for appointment booking, lifecycle metadata, and read models."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AppointmentActorRole, AppointmentMode, AppointmentStatus


class AppointmentUserSummary(BaseModel):
    """Compact user information embedded in appointment responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: str


class AppointmentSpecialistSummary(BaseModel):
    """Compact specialist information embedded in appointment responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    specialty: str
    city: str | None


class AppointmentCreateRequest(BaseModel):
    """Request payload for creating a new appointment booking."""

    specialist_id: UUID
    mode: AppointmentMode
    preferred_datetime: datetime
    notes: str | None = Field(default=None, max_length=1000)


class SpecialistAppointmentCreateRequest(BaseModel):
    """Request payload for a specialist creating an appointment for a user."""

    user_id: UUID
    mode: AppointmentMode
    preferred_datetime: datetime
    notes: str | None = Field(default=None, max_length=1000)


class AppointmentRescheduleRequest(BaseModel):
    """Request payload for rescheduling an existing appointment."""

    preferred_datetime: datetime
    note: str | None = Field(default=None, max_length=1000)


class AppointmentCancellationRequest(BaseModel):
    """Request payload for cancelling an existing appointment."""

    reason: str | None = Field(default=None, max_length=1000)


class AppointmentRejectionRequest(BaseModel):
    """Request payload for rejecting an existing appointment."""

    reason: str | None = Field(default=None, max_length=1000)


class AppointmentResponse(BaseModel):
    """Serialized appointment row."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    specialist_id: UUID
    user: AppointmentUserSummary | None = None
    specialist: AppointmentSpecialistSummary | None = None
    mode: AppointmentMode
    status: AppointmentStatus
    preferred_datetime: datetime
    end_datetime: datetime
    notes: str | None
    cancellation_reason: str | None
    rejection_reason: str | None
    reschedule_note: str | None
    confirmed_at: datetime | None
    rejected_at: datetime | None
    cancelled_at: datetime | None
    completed_at: datetime | None
    last_rescheduled_at: datetime | None
    reminder_sent_at: datetime | None
    last_rescheduled_by_role: AppointmentActorRole | None
    status_updated_by_user_id: UUID | None
    created_at: datetime
    updated_at: datetime


class AppointmentPageResponse(BaseModel):
    """Paginated appointment response for admin oversight views."""

    items: list[AppointmentResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
