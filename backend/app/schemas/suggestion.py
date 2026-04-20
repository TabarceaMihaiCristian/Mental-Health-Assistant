"""Schemas for appointment suggestions triggered by critical risk alerts."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AppointmentSuggestionItemResponse(BaseModel):
    """One suggested appointment slot paired with a specialist summary."""

    specialist_id: UUID
    specialist_name: str
    specialty: str
    city: str | None
    consultation_modes: list[str]
    average_rating: float | None
    review_count: int
    start_datetime: datetime
    end_datetime: datetime


class CriticalAppointmentSuggestionsResponse(BaseModel):
    """Recommended specialist appointment slots for a recent critical alert."""

    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    lookahead_days: int
    total_suggestions: int
    suggestions: list[AppointmentSuggestionItemResponse]
