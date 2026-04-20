"""Schemas for admin-driven specialist onboarding and updates."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import SpecialistStatus


class AdminSpecialistCreateRequest(BaseModel):
    """Request payload used by admins to onboard a specialist."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    specialty: str = Field(min_length=1, max_length=255)
    bio: str | None = Field(default=None, max_length=2000)
    consultation_modes: list[str] = Field(min_length=1)
    city: str | None = Field(default=None, max_length=255)


class AdminSpecialistUpdateRequest(BaseModel):
    """Request payload used by admins to update specialist profile details."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    specialty: str | None = Field(default=None, min_length=1, max_length=255)
    bio: str | None = Field(default=None, max_length=2000)
    consultation_modes: list[str] | None = None
    city: str | None = Field(default=None, max_length=255)


class AdminSpecialistStatusUpdateRequest(BaseModel):
    """Request payload for updating specialist status."""

    status: SpecialistStatus


class AdminSpecialistResponse(BaseModel):
    """Serialized specialist admin response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None
    full_name: str
    specialty: str
    bio: str | None
    consultation_modes: list[str]
    city: str | None
    status: SpecialistStatus
    email: str | None = None
    user_is_active: bool | None = None
    average_rating: float | None = None
    review_count: int = 0


class AdminSpecialistPageResponse(BaseModel):
    """Paginated specialist response for admin oversight views."""

    items: list[AdminSpecialistResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
