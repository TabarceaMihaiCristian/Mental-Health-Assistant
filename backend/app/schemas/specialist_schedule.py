"""Schemas for specialist-managed availability, breaks, and time off."""

from __future__ import annotations

from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AvailabilityRuleUpsertRequest(BaseModel):
    """Recurring weekly availability rule."""

    weekday: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    is_enabled: bool = True


class AvailabilityRuleResponse(BaseModel):
    """Serialized availability rule."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    specialist_id: UUID
    weekday: int
    start_time: time
    end_time: time
    is_enabled: bool


class BreakCreateRequest(BaseModel):
    """Recurring specialist break."""

    weekday: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    label: str | None = Field(default=None, max_length=100)


class BreakUpdateRequest(BaseModel):
    """Recurring specialist break update payload."""

    weekday: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    label: str | None = Field(default=None, max_length=100)


class BreakResponse(BaseModel):
    """Serialized specialist break."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    specialist_id: UUID
    weekday: int
    start_time: time
    end_time: time
    label: str | None


class TimeOffCreateRequest(BaseModel):
    """Specific specialist time-off window."""

    start_datetime: datetime
    end_datetime: datetime
    reason: str | None = Field(default=None, max_length=255)


class TimeOffUpdateRequest(BaseModel):
    """Specific specialist time-off update payload."""

    start_datetime: datetime
    end_datetime: datetime
    reason: str | None = Field(default=None, max_length=255)


class TimeOffResponse(BaseModel):
    """Serialized time-off window."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    specialist_id: UUID
    start_datetime: datetime
    end_datetime: datetime
    reason: str | None
