"""Repositories for appointment persistence and ownership-scoped lookup."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, UTC
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus


class AppointmentRepository:
    """Database access helpers for specialist appointments."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to one SQLAlchemy session."""

        self.db = db

    def add(self, appointment: Appointment) -> Appointment:
        """Persist an appointment row."""

        self.db.add(appointment)
        self.db.flush()
        return appointment

    def list_for_user(self, user_id: UUID) -> list[Appointment]:
        """Return all appointments owned by a user from newest to oldest."""

        statement = (
            select(Appointment)
            .options(
                selectinload(Appointment.specialist),
                selectinload(Appointment.user),
            )
            .where(Appointment.user_id == user_id)
            .order_by(Appointment.preferred_datetime.desc(), Appointment.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def get_owned_appointment(self, user_id: UUID, appointment_id: UUID) -> Appointment | None:
        """Return a specific appointment only if it belongs to the given user."""

        statement = (
            select(Appointment)
            .options(
                selectinload(Appointment.specialist),
                selectinload(Appointment.user),
            )
            .where(
                Appointment.id == appointment_id,
                Appointment.user_id == user_id,
            )
        )
        return self.db.scalar(statement)

    def list_for_specialist(self, specialist_id: UUID) -> list[Appointment]:
        """Return all appointments assigned to a specialist from soonest to latest."""

        statement = (
            select(Appointment)
            .options(
                selectinload(Appointment.specialist),
                selectinload(Appointment.user),
            )
            .where(Appointment.specialist_id == specialist_id)
            .order_by(Appointment.preferred_datetime.asc(), Appointment.created_at.asc())
        )
        return list(self.db.scalars(statement).all())

    def get_for_specialist(
        self,
        specialist_id: UUID,
        appointment_id: UUID,
    ) -> Appointment | None:
        """Return a specific appointment only if it belongs to the given specialist."""

        statement = (
            select(Appointment)
            .options(
                selectinload(Appointment.specialist),
                selectinload(Appointment.user),
            )
            .where(
                Appointment.id == appointment_id,
                Appointment.specialist_id == specialist_id,
            )
        )
        return self.db.scalar(statement)

    def list_for_specialist_in_window(
        self,
        specialist_id: UUID,
        date_from: date,
        date_to: date,
    ) -> list[Appointment]:
        """Return blocking appointments for a specialist within a date window."""

        window_start = datetime.combine(date_from, time.min, tzinfo=UTC)
        window_end = datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=UTC)
        statement = (
            select(Appointment)
            .where(
                Appointment.specialist_id == specialist_id,
                Appointment.status.in_(
                    [AppointmentStatus.REQUESTED, AppointmentStatus.CONFIRMED]
                ),
                Appointment.preferred_datetime < window_end,
                Appointment.end_datetime > window_start,
            )
            .order_by(Appointment.preferred_datetime.asc())
        )
        return list(self.db.scalars(statement).all())

    def has_overlapping_active_appointment(
        self,
        specialist_id: UUID,
        start_datetime: datetime,
        end_datetime: datetime,
        exclude_appointment_id: UUID | None = None,
    ) -> bool:
        """Return whether an active appointment overlaps the given slot."""

        statement = select(Appointment.id).where(
            Appointment.specialist_id == specialist_id,
            Appointment.status.in_(
                [AppointmentStatus.REQUESTED, AppointmentStatus.CONFIRMED]
            ),
            Appointment.preferred_datetime < end_datetime,
            Appointment.end_datetime > start_datetime,
        )
        if exclude_appointment_id is not None:
            statement = statement.where(Appointment.id != exclude_appointment_id)
        return self.db.scalar(statement.limit(1)) is not None

    def list_all(self) -> list[Appointment]:
        """Return all appointments with user and specialist relations loaded."""

        statement = (
            select(Appointment)
            .options(
                selectinload(Appointment.specialist),
                selectinload(Appointment.user),
            )
            .order_by(Appointment.preferred_datetime.desc(), Appointment.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def list_all_filtered(
        self,
        *,
        status: AppointmentStatus | None = None,
        specialist_id: UUID | None = None,
        user_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> list[Appointment]:
        """Return admin-visible appointments filtered by lifecycle and ownership fields."""

        statement = self._filtered_admin_statement(
            status=status,
            specialist_id=specialist_id,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        ).options(
            selectinload(Appointment.specialist),
            selectinload(Appointment.user),
        ).order_by(
            Appointment.preferred_datetime.desc(),
            Appointment.created_at.desc(),
        )
        offset = (page - 1) * page_size
        statement = statement.offset(offset).limit(page_size)
        return list(self.db.scalars(statement).all())

    def count_all_filtered(
        self,
        *,
        status: AppointmentStatus | None = None,
        specialist_id: UUID | None = None,
        user_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> int:
        """Return the admin-visible appointment count for the provided filters."""

        statement = self._filtered_admin_statement(
            status=status,
            specialist_id=specialist_id,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        ).with_only_columns(func.count(Appointment.id)).order_by(None)
        count = self.db.scalar(statement)
        return 0 if count is None else int(count)

    def get_by_id(self, appointment_id: UUID) -> Appointment | None:
        """Return one appointment by id with user and specialist relations loaded."""

        statement = (
            select(Appointment)
            .options(
                selectinload(Appointment.specialist),
                selectinload(Appointment.user),
            )
            .where(Appointment.id == appointment_id)
        )
        return self.db.scalar(statement)

    def list_confirmed_starting_between(
        self,
        window_start: datetime,
        window_end: datetime,
    ) -> list[Appointment]:
        """Return confirmed appointments starting in a window that still need reminders."""

        statement = (
            select(Appointment)
            .options(
                selectinload(Appointment.specialist),
                selectinload(Appointment.user),
            )
            .where(
                Appointment.status == AppointmentStatus.CONFIRMED,
                Appointment.preferred_datetime >= window_start,
                Appointment.preferred_datetime <= window_end,
                Appointment.reminder_sent_at.is_(None),
            )
            .order_by(Appointment.preferred_datetime.asc())
        )
        return list(self.db.scalars(statement).all())

    def list_for_specialist_calendar(
        self,
        specialist_id: UUID,
        date_from: date,
        date_to: date,
    ) -> list[Appointment]:
        """Return all appointments overlapping a specialist calendar window."""

        window_start = datetime.combine(date_from, time.min, tzinfo=UTC)
        window_end = datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=UTC)
        statement = (
            select(Appointment)
            .options(
                selectinload(Appointment.specialist),
                selectinload(Appointment.user),
            )
            .where(
                Appointment.specialist_id == specialist_id,
                Appointment.preferred_datetime < window_end,
                Appointment.end_datetime > window_start,
            )
            .order_by(Appointment.preferred_datetime.asc())
        )
        return list(self.db.scalars(statement).all())

    def _filtered_admin_statement(
        self,
        *,
        status: AppointmentStatus | None = None,
        specialist_id: UUID | None = None,
        user_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ):
        """Build the shared base statement for filtered admin appointment queries."""

        statement = select(Appointment)
        if status is not None:
            statement = statement.where(Appointment.status == status)
        if specialist_id is not None:
            statement = statement.where(Appointment.specialist_id == specialist_id)
        if user_id is not None:
            statement = statement.where(Appointment.user_id == user_id)
        if date_from is not None:
            window_start = datetime.combine(date_from, time.min, tzinfo=UTC)
            statement = statement.where(Appointment.preferred_datetime >= window_start)
        if date_to is not None:
            window_end = datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=UTC)
            statement = statement.where(Appointment.preferred_datetime < window_end)
        return statement
