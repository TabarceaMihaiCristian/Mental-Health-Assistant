"""Specialist and scheduling fixtures for backend tests."""

from __future__ import annotations

from collections.abc import Callable
from datetime import time
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models.enums import SpecialistStatus, UserRole
from app.models.specialist import Specialist
from app.models.specialist_availability_rule import SpecialistAvailabilityRule
from app.models.user import User


@pytest.fixture()
def specialist_factory(
    db_session: Session,
    user_factory: Callable[..., User],
) -> Callable[..., Specialist]:
    """Return a factory that creates active specialists linked to specialist users."""

    def create_specialist(
        *,
        full_name: str = "Dr. Specialist",
        specialty: str = "Psychology",
        city: str | None = "Bucharest",
        consultation_modes: list[str] | None = None,
        status: SpecialistStatus = SpecialistStatus.ACTIVE,
        with_user: bool = True,
    ) -> Specialist:
        """Create and flush one specialist profile, optionally linked to a user account."""

        specialist_user = (
            user_factory(
                email=f"{uuid4().hex[:12]}@example.com",
                full_name=full_name,
                role=UserRole.SPECIALIST,
            )
            if with_user
            else None
        )
        specialist = Specialist(
            user_id=None if specialist_user is None else specialist_user.id,
            full_name=full_name,
            specialty=specialty,
            bio="Test specialist profile",
            consultation_modes=consultation_modes or ["online"],
            city=city,
            status=status,
        )
        if specialist_user is not None:
            specialist.user = specialist_user
        db_session.add(specialist)
        db_session.flush()
        return specialist

    return create_specialist


@pytest.fixture()
def availability_rule_factory(
    db_session: Session,
) -> Callable[..., SpecialistAvailabilityRule]:
    """Return a factory for recurring weekly specialist availability rules."""

    def create_availability_rule(
        *,
        specialist_id,
        weekday: int,
        start_time: time = time(hour=9),
        end_time: time = time(hour=17),
        is_enabled: bool = True,
    ) -> SpecialistAvailabilityRule:
        """Create and flush one recurring availability rule."""

        availability_rule = SpecialistAvailabilityRule(
            specialist_id=specialist_id,
            weekday=weekday,
            start_time=start_time,
            end_time=end_time,
            is_enabled=is_enabled,
        )
        db_session.add(availability_rule)
        db_session.flush()
        return availability_rule

    return create_availability_rule
