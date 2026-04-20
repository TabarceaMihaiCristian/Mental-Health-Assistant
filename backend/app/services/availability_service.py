"""Compute public bookable specialist availability from schedule rules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.specialist_availability_rule import SpecialistAvailabilityRule
from app.models.specialist_break import SpecialistBreak
from app.models.specialist_time_off import SpecialistTimeOff
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.specialist_repository import SpecialistRepository
from app.repositories.specialist_schedule_repository import SpecialistScheduleRepository


SLOT_DURATION = timedelta(hours=2)


@dataclass(slots=True)
class AvailabilitySlot:
    """Computed 2-hour availability slot."""

    start_datetime: datetime
    end_datetime: datetime


class AvailabilityWindowError(ValueError):
    """Raised when the requested availability range is invalid."""


class SpecialistAvailabilityNotFoundError(ValueError):
    """Raised when availability is requested for a missing or inactive specialist."""


class AvailabilityService:
    """Build specialist bookable 2-hour slots from recurring schedule rules."""

    def __init__(self, db: Session) -> None:
        """Bind availability computation to one SQLAlchemy session."""

        self.specialist_repository = SpecialistRepository(db)
        self.schedule_repository = SpecialistScheduleRepository(db)
        self.appointment_repository = AppointmentRepository(db)

    def get_available_slots(
        self,
        specialist_id: UUID,
        date_from: date,
        date_to: date,
    ) -> list[AvailabilitySlot]:
        """Return bookable 2-hour slots for a specialist within a date range."""

        if date_to < date_from:
            raise AvailabilityWindowError("date_to must be on or after date_from.")

        specialist = self.specialist_repository.get_active_specialist_by_id(specialist_id)
        if specialist is None:
            raise SpecialistAvailabilityNotFoundError("Specialist not found or unavailable.")

        rules = self.schedule_repository.list_availability_rules(specialist_id)
        breaks = self.schedule_repository.list_breaks(specialist_id)
        time_off_periods = self.schedule_repository.list_time_off_in_window(
            specialist_id, date_from, date_to
        )
        appointments = self.appointment_repository.list_for_specialist_in_window(
            specialist_id, date_from, date_to
        )

        slots: list[AvailabilitySlot] = []
        current_date = date_from
        while current_date <= date_to:
            weekday_rules = [
                rule
                for rule in rules
                if rule.weekday == current_date.weekday() and rule.is_enabled
            ]
            weekday_breaks = [
                specialist_break
                for specialist_break in breaks
                if specialist_break.weekday == current_date.weekday()
            ]
            for rule in weekday_rules:
                slots.extend(
                    self._build_rule_slots(
                        current_date,
                        rule,
                        weekday_breaks,
                        time_off_periods,
                        appointments,
                    )
                )
            current_date += timedelta(days=1)
        return slots

    def is_bookable_slot(
        self,
        specialist_id: UUID,
        start_datetime: datetime,
    ) -> bool:
        """Return whether a datetime matches an available 2-hour slot start."""

        normalized_start = start_datetime.astimezone(UTC)
        slots = self.get_available_slots(
            specialist_id,
            normalized_start.date(),
            normalized_start.date(),
        )
        return any(slot.start_datetime == normalized_start for slot in slots)

    def _build_rule_slots(
        self,
        current_date: date,
        rule: SpecialistAvailabilityRule,
        breaks: list[SpecialistBreak],
        time_off_periods: list[SpecialistTimeOff],
        appointments: list[Appointment],
    ) -> list[AvailabilitySlot]:
        """Build valid 2-hour slots for one recurring availability rule on one day."""

        rule_start = datetime.combine(current_date, rule.start_time, tzinfo=UTC)
        rule_end = datetime.combine(current_date, rule.end_time, tzinfo=UTC)
        slots: list[AvailabilitySlot] = []
        cursor = rule_start
        while cursor + SLOT_DURATION <= rule_end:
            slot_end = cursor + SLOT_DURATION
            if not self._slot_is_blocked(
                cursor,
                slot_end,
                current_date,
                breaks,
                time_off_periods,
                appointments,
            ):
                slots.append(AvailabilitySlot(start_datetime=cursor, end_datetime=slot_end))
            cursor = slot_end
        return slots

    def _slot_is_blocked(
        self,
        slot_start: datetime,
        slot_end: datetime,
        current_date: date,
        breaks: list[SpecialistBreak],
        time_off_periods: list[SpecialistTimeOff],
        appointments: list[Appointment],
    ) -> bool:
        """Return whether a slot is blocked by breaks, time off, or appointments."""

        return (
            self._slot_overlaps_break(slot_start, slot_end, current_date, breaks)
            or self._slot_overlaps_time_off(slot_start, slot_end, time_off_periods)
            or self._slot_overlaps_appointment(slot_start, slot_end, appointments)
        )

    def _slot_overlaps_break(
        self,
        slot_start: datetime,
        slot_end: datetime,
        current_date: date,
        breaks: list[SpecialistBreak],
    ) -> bool:
        """Return whether a slot overlaps any recurring break on the same weekday."""

        for specialist_break in breaks:
            break_start = datetime.combine(current_date, specialist_break.start_time, tzinfo=UTC)
            break_end = datetime.combine(current_date, specialist_break.end_time, tzinfo=UTC)
            if self._intervals_overlap(slot_start, slot_end, break_start, break_end):
                return True
        return False

    def _slot_overlaps_time_off(
        self,
        slot_start: datetime,
        slot_end: datetime,
        time_off_periods: list[SpecialistTimeOff],
    ) -> bool:
        """Return whether a slot overlaps any specific time-off window."""

        return any(
            self._intervals_overlap(
                slot_start,
                slot_end,
                time_off.start_datetime,
                time_off.end_datetime,
            )
            for time_off in time_off_periods
        )

    def _slot_overlaps_appointment(
        self,
        slot_start: datetime,
        slot_end: datetime,
        appointments: list[Appointment],
    ) -> bool:
        """Return whether a slot overlaps any existing active appointment."""

        return any(
            self._intervals_overlap(
                slot_start,
                slot_end,
                appointment.preferred_datetime,
                appointment.end_datetime,
            )
            for appointment in appointments
        )

    def _intervals_overlap(
        self,
        start_a: datetime,
        end_a: datetime,
        start_b: datetime,
        end_b: datetime,
    ) -> bool:
        """Return whether two half-open datetime intervals overlap."""

        return start_a < end_b and start_b < end_a
