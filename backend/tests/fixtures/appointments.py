"""Appointment fixtures for backend tests."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.enums import AppointmentMode, AppointmentStatus
from app.models.specialist import Specialist
from app.models.user import User


@pytest.fixture()
def appointment_factory(
    db_session: Session,
) -> Callable[..., Appointment]:
    """Return a factory for persisted appointment rows."""

    def create_appointment(
        *,
        user: User,
        specialist: Specialist,
        preferred_datetime: datetime,
        end_datetime: datetime | None = None,
        mode: AppointmentMode = AppointmentMode.ONLINE,
        status: AppointmentStatus = AppointmentStatus.REQUESTED,
    ) -> Appointment:
        """Create and flush a persisted appointment for test setup."""

        appointment = Appointment(
            user_id=user.id,
            specialist_id=specialist.id,
            mode=mode,
            status=status,
            preferred_datetime=preferred_datetime,
            end_datetime=end_datetime or preferred_datetime + timedelta(hours=2),
            status_updated_by_user_id=user.id,
        )
        db_session.add(appointment)
        db_session.flush()
        return appointment

    return create_appointment
