"""Schemas for specialist directory and review-related responses."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import SpecialistStatus


class SpecialistResponse(BaseModel):
    """Serialized specialist directory entry with computed rating fields."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    specialty: str
    bio: str | None
    consultation_modes: list[str]
    city: str | None
    status: SpecialistStatus
    average_rating: float | None
    review_count: int


class SpecialistReviewUpsertRequest(BaseModel):
    """Request body used to create or update a specialist review."""

    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=1000)


class SpecialistReviewResponse(BaseModel):
    """Serialized specialist review."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    specialist_id: UUID
    user_id: UUID
    rating: int
    comment: str | None
    created_at: datetime
    updated_at: datetime
