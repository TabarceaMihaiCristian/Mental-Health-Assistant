"""Application service for specialist-managed scheduling configuration."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, time
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.unit_of_work import UnitOfWork
from app.repositories.appointment_repository import AppointmentRepository
from app.models.specialist import Specialist
from app.models.specialist_availability_rule import SpecialistAvailabilityRule
from app.models.specialist_break import SpecialistBreak
from app.models.specialist_time_off import SpecialistTimeOff
from app.models.user import User
from app.repositories.specialist_repository import SpecialistRepository
from app.repositories.specialist_schedule_repository import SpecialistScheduleRepository
from app.schemas.specialist_schedule import (
    AvailabilityRuleUpsertRequest,
    BreakCreateRequest,
    BreakUpdateRequest,
    TimeOffCreateRequest,
    TimeOffUpdateRequest,
)
from app.services.availability_service import AvailabilityService
from app.utils.logging import get_app_logger, log_event
from app.utils.validation import normalize_future_datetime, normalize_optional_comment


class SpecialistScheduleValidationError(ValueError):
    """Raised when schedule input is structurally invalid."""


class SpecialistProfileNotFoundError(ValueError):
    """Raised when a specialist user has no linked specialist profile."""


class SpecialistScheduleItemNotFoundError(ValueError):
    """Raised when a schedule item does not belong to the current specialist."""


class SpecialistScheduleService:
    """Manage specialist availability rules, breaks, and time off."""

    def __init__(self, db: Session) -> None:
        """Bind specialist scheduling workflows to one SQLAlchemy session."""

        self.db = db
        self.uow = UnitOfWork(db)
        self.specialist_repository = SpecialistRepository(db)
        self.schedule_repository = SpecialistScheduleRepository(db)
        self.appointment_repository = AppointmentRepository(db)
        self.availability_service = AvailabilityService(db)
        self.logger = get_app_logger(__name__)

    def list_availability_rules(self, current_user: User) -> list[SpecialistAvailabilityRule]:
        """Return recurring weekly availability rules for the current specialist."""

        specialist = self._get_specialist_for_user(current_user)
        return self.schedule_repository.list_availability_rules(specialist.id)

    def replace_availability_rules(
        self,
        current_user: User,
        payload: list[AvailabilityRuleUpsertRequest],
    ) -> list[SpecialistAvailabilityRule]:
        """Replace all recurring weekly availability rules for the current specialist."""

        specialist = self._get_specialist_for_user(current_user)
        self._validate_weekly_windows(payload)
        rules = [
            SpecialistAvailabilityRule(
                specialist_id=specialist.id,
                weekday=item.weekday,
                start_time=item.start_time,
                end_time=item.end_time,
                is_enabled=item.is_enabled,
            )
            for item in payload
        ]
        self.schedule_repository.replace_availability_rules(specialist.id, rules)
        self.uow.commit()
        log_event(
            self.logger,
            "specialist.schedule.availability_replaced",
            user_id=current_user.id,
            specialist_id=specialist.id,
            rule_count=len(rules),
        )
        return self.schedule_repository.list_availability_rules(specialist.id)

    def list_breaks(self, current_user: User) -> list[SpecialistBreak]:
        """Return recurring break windows for the current specialist."""

        specialist = self._get_specialist_for_user(current_user)
        return self.schedule_repository.list_breaks(specialist.id)

    def create_break(self, current_user: User, payload: BreakCreateRequest) -> SpecialistBreak:
        """Create a recurring break window for the current specialist."""

        specialist = self._get_specialist_for_user(current_user)
        self._ensure_valid_time_window(payload.start_time, payload.end_time, "Break")
        existing_breaks = self.schedule_repository.list_breaks(specialist.id)
        self._ensure_no_overlap(
            payload.weekday,
            payload.start_time,
            payload.end_time,
            [(item.weekday, item.start_time, item.end_time) for item in existing_breaks],
            "Break",
        )
        specialist_break = SpecialistBreak(
            specialist_id=specialist.id,
            weekday=payload.weekday,
            start_time=payload.start_time,
            end_time=payload.end_time,
            label=normalize_optional_comment(payload.label),
        )
        self.schedule_repository.add_break(specialist_break)
        self.uow.commit()
        self.uow.refresh(specialist_break)
        return specialist_break

    def update_break(
        self,
        current_user: User,
        break_id: UUID,
        payload: BreakUpdateRequest,
    ) -> SpecialistBreak:
        """Update one recurring break for the current specialist."""

        specialist = self._get_specialist_for_user(current_user)
        specialist_break = self.schedule_repository.get_break(specialist.id, break_id)
        if specialist_break is None:
            raise SpecialistScheduleItemNotFoundError("Break not found.")

        self._ensure_valid_time_window(payload.start_time, payload.end_time, "Break")
        other_breaks = [
            item
            for item in self.schedule_repository.list_breaks(specialist.id)
            if item.id != break_id
        ]
        self._ensure_no_overlap(
            payload.weekday,
            payload.start_time,
            payload.end_time,
            [(item.weekday, item.start_time, item.end_time) for item in other_breaks],
            "Break",
        )
        specialist_break.weekday = payload.weekday
        specialist_break.start_time = payload.start_time
        specialist_break.end_time = payload.end_time
        specialist_break.label = normalize_optional_comment(payload.label)
        self.uow.commit()
        self.uow.refresh(specialist_break)
        return specialist_break

    def delete_break(self, current_user: User, break_id: UUID) -> None:
        """Delete one recurring break for the current specialist."""

        specialist = self._get_specialist_for_user(current_user)
        specialist_break = self.schedule_repository.get_break(specialist.id, break_id)
        if specialist_break is None:
            raise SpecialistScheduleItemNotFoundError("Break not found.")
        self.db.delete(specialist_break)
        self.uow.commit()

    def list_time_off(self, current_user: User) -> list[SpecialistTimeOff]:
        """Return time-off windows for the current specialist."""

        specialist = self._get_specialist_for_user(current_user)
        return self.schedule_repository.list_time_off(specialist.id)

    def create_time_off(
        self,
        current_user: User,
        payload: TimeOffCreateRequest,
    ) -> SpecialistTimeOff:
        """Create a specific future time-off window for the current specialist."""

        specialist = self._get_specialist_for_user(current_user)
        start_datetime = normalize_future_datetime(payload.start_datetime)
        end_datetime = normalize_future_datetime(payload.end_datetime)
        if end_datetime <= start_datetime:
            raise SpecialistScheduleValidationError("Time off end must be after start.")
        time_off = SpecialistTimeOff(
            specialist_id=specialist.id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            reason=normalize_optional_comment(payload.reason),
        )
        self.schedule_repository.add_time_off(time_off)
        self.uow.commit()
        self.uow.refresh(time_off)
        return time_off

    def update_time_off(
        self,
        current_user: User,
        time_off_id: UUID,
        payload: TimeOffUpdateRequest,
    ) -> SpecialistTimeOff:
        """Update one time-off window for the current specialist."""

        specialist = self._get_specialist_for_user(current_user)
        time_off = self.schedule_repository.get_time_off(specialist.id, time_off_id)
        if time_off is None:
            raise SpecialistScheduleItemNotFoundError("Time off not found.")

        start_datetime = normalize_future_datetime(payload.start_datetime)
        end_datetime = normalize_future_datetime(payload.end_datetime)
        if end_datetime <= start_datetime:
            raise SpecialistScheduleValidationError("Time off end must be after start.")

        time_off.start_datetime = start_datetime
        time_off.end_datetime = end_datetime
        time_off.reason = normalize_optional_comment(payload.reason)
        self.uow.commit()
        self.uow.refresh(time_off)
        return time_off

    def delete_time_off(self, current_user: User, time_off_id: UUID) -> None:
        """Delete one time-off window for the current specialist."""

        specialist = self._get_specialist_for_user(current_user)
        time_off = self.schedule_repository.get_time_off(specialist.id, time_off_id)
        if time_off is None:
            raise SpecialistScheduleItemNotFoundError("Time off not found.")
        self.db.delete(time_off)
        self.uow.commit()

    def get_calendar(
        self,
        current_user: User,
        date_from: date,
        date_to: date,
    ) -> tuple[list, list, list[SpecialistBreak], list[SpecialistTimeOff], UUID]:
        """Return appointments, available slots, breaks, and time off for a date window."""

        specialist = self._get_specialist_for_user(current_user)
        appointments = self.appointment_repository.list_for_specialist_calendar(
            specialist.id,
            date_from,
            date_to,
        )
        available_slots = self.availability_service.get_available_slots(
            specialist.id,
            date_from,
            date_to,
        )
        breaks = self.schedule_repository.list_breaks(specialist.id)
        time_off_periods = self.schedule_repository.list_time_off_in_window(
            specialist.id,
            date_from,
            date_to,
        )
        return appointments, available_slots, breaks, time_off_periods, specialist.id

    def _get_specialist_for_user(self, current_user: User) -> Specialist:
        """Resolve the specialist profile linked to the authenticated specialist user."""

        specialist = self.specialist_repository.get_by_user_id(current_user.id)
        if specialist is None:
            raise SpecialistProfileNotFoundError("Specialist profile not found.")
        return specialist

    def _validate_weekly_windows(self, payload: list[AvailabilityRuleUpsertRequest]) -> None:
        """Validate that recurring weekly availability windows do not overlap."""

        grouped_windows: dict[int, list[tuple[time, time]]] = defaultdict(list)
        for item in payload:
            self._ensure_valid_time_window(item.start_time, item.end_time, "Availability")
            grouped_windows[item.weekday].append((item.start_time, item.end_time))

        for weekday, windows in grouped_windows.items():
            sorted_windows = sorted(windows, key=lambda item: item[0])
            for index in range(1, len(sorted_windows)):
                if sorted_windows[index][0] < sorted_windows[index - 1][1]:
                    raise SpecialistScheduleValidationError(
                        f"Availability windows cannot overlap on weekday {weekday}."
                    )

    def _ensure_valid_time_window(self, start_time: time, end_time: time, label: str) -> None:
        """Ensure a scheduling time window has a strictly increasing range."""

        if start_time >= end_time:
            raise SpecialistScheduleValidationError(
                f"{label} start time must be earlier than end time."
            )

    def _ensure_no_overlap(
        self,
        weekday: int,
        start_time: time,
        end_time: time,
        windows: list[tuple[int, time, time]],
        label: str,
    ) -> None:
        """Ensure a new break window does not overlap existing windows on the same weekday."""

        relevant_windows = [(start, end) for day, start, end in windows if day == weekday]
        relevant_windows.append((start_time, end_time))
        relevant_windows.sort(key=lambda item: item[0])
        for index in range(1, len(relevant_windows)):
            if relevant_windows[index][0] < relevant_windows[index - 1][1]:
                raise SpecialistScheduleValidationError(
                    f"{label} windows cannot overlap on the same weekday."
                )
