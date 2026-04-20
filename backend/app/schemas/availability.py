"""Schemas for specialist availability and calendar responses."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.appointment import AppointmentResponse
from app.schemas.specialist_schedule import BreakResponse, TimeOffResponse


class SpecialistAvailabilitySlotResponse(BaseModel):
    """Single bookable specialist slot."""

    start_datetime: datetime
    end_datetime: datetime
    is_available: bool = True


class SpecialistAvailabilityResponse(BaseModel):
    """Availability response for a specialist within a date range."""

    specialist_id: UUID
    slot_duration_minutes: int = 120
    date_from: date
    date_to: date
    slots: list[SpecialistAvailabilitySlotResponse]


class SpecialistCalendarResponse(BaseModel):
    """Calendar view for a specialist across a date window."""

    specialist_id: UUID
    date_from: date
    date_to: date
    appointments: list[AppointmentResponse]
    available_slots: list[SpecialistAvailabilitySlotResponse]
    breaks: list[BreakResponse]
    time_off_periods: list[TimeOffResponse]
