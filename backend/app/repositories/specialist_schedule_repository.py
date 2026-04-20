"""Repositories for specialist-owned scheduling configuration."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, UTC
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.specialist_availability_rule import SpecialistAvailabilityRule
from app.models.specialist_break import SpecialistBreak
from app.models.specialist_time_off import SpecialistTimeOff


class SpecialistScheduleRepository:
    """Database access helpers for specialist scheduling records."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to one SQLAlchemy session."""

        self.db = db

    def replace_availability_rules(
        self,
        specialist_id: UUID,
        rules: list[SpecialistAvailabilityRule],
    ) -> list[SpecialistAvailabilityRule]:
        """Replace a specialist's recurring availability rules."""

        self.db.execute(
            delete(SpecialistAvailabilityRule).where(
                SpecialistAvailabilityRule.specialist_id == specialist_id
            )
        )
        for rule in rules:
            self.db.add(rule)
        self.db.flush()
        return rules

    def list_availability_rules(self, specialist_id: UUID) -> list[SpecialistAvailabilityRule]:
        """Return recurring availability rules for a specialist."""

        statement = (
            select(SpecialistAvailabilityRule)
            .where(SpecialistAvailabilityRule.specialist_id == specialist_id)
            .order_by(
                SpecialistAvailabilityRule.weekday.asc(),
                SpecialistAvailabilityRule.start_time.asc(),
            )
        )
        return list(self.db.scalars(statement).all())

    def add_break(self, specialist_break: SpecialistBreak) -> SpecialistBreak:
        """Persist a recurring break."""

        self.db.add(specialist_break)
        self.db.flush()
        return specialist_break

    def list_breaks(self, specialist_id: UUID) -> list[SpecialistBreak]:
        """Return recurring breaks for a specialist."""

        statement = (
            select(SpecialistBreak)
            .where(SpecialistBreak.specialist_id == specialist_id)
            .order_by(SpecialistBreak.weekday.asc(), SpecialistBreak.start_time.asc())
        )
        return list(self.db.scalars(statement).all())

    def get_break(self, specialist_id: UUID, break_id: UUID) -> SpecialistBreak | None:
        """Return one recurring break if it belongs to the specialist."""

        statement = select(SpecialistBreak).where(
            SpecialistBreak.id == break_id,
            SpecialistBreak.specialist_id == specialist_id,
        )
        return self.db.scalar(statement)

    def add_time_off(self, time_off: SpecialistTimeOff) -> SpecialistTimeOff:
        """Persist a time-off window."""

        self.db.add(time_off)
        self.db.flush()
        return time_off

    def list_time_off(self, specialist_id: UUID) -> list[SpecialistTimeOff]:
        """Return time-off windows for a specialist."""

        statement = (
            select(SpecialistTimeOff)
            .where(SpecialistTimeOff.specialist_id == specialist_id)
            .order_by(SpecialistTimeOff.start_datetime.asc())
        )
        return list(self.db.scalars(statement).all())

    def get_time_off(
        self,
        specialist_id: UUID,
        time_off_id: UUID,
    ) -> SpecialistTimeOff | None:
        """Return one time-off window if it belongs to the specialist."""

        statement = select(SpecialistTimeOff).where(
            SpecialistTimeOff.id == time_off_id,
            SpecialistTimeOff.specialist_id == specialist_id,
        )
        return self.db.scalar(statement)

    def list_time_off_in_window(
        self,
        specialist_id: UUID,
        date_from: date,
        date_to: date,
    ) -> list[SpecialistTimeOff]:
        """Return time-off windows overlapping the requested date range."""

        window_start = datetime.combine(date_from, time.min, tzinfo=UTC)
        window_end = datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=UTC)
        statement = (
            select(SpecialistTimeOff)
            .where(
                SpecialistTimeOff.specialist_id == specialist_id,
                SpecialistTimeOff.start_datetime < window_end,
                SpecialistTimeOff.end_datetime > window_start,
            )
            .order_by(SpecialistTimeOff.start_datetime.asc())
        )
        return list(self.db.scalars(statement).all())
