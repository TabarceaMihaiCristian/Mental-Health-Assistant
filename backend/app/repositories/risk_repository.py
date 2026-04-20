"""Repositories for risk event persistence and lookup."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.risk_event import RiskEvent


class RiskEventRepository:
    """Database access helpers for risk events."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to one SQLAlchemy session."""

        self.db = db

    def add(self, risk_event: RiskEvent) -> RiskEvent:
        """Persist a risk event row."""

        self.db.add(risk_event)
        self.db.flush()
        return risk_event

    def get_by_message_id(self, message_id: UUID) -> RiskEvent | None:
        """Return the stored risk event associated with a specific message."""

        statement = select(RiskEvent).where(RiskEvent.message_id == message_id)
        return self.db.scalar(statement)

    def list_for_user(self, user_id: UUID) -> list[RiskEvent]:
        """Return risk events for a user ordered from newest to oldest."""

        statement = (
            select(RiskEvent)
            .where(RiskEvent.user_id == user_id)
            .order_by(RiskEvent.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def list_for_user_in_window(
        self,
        user_id: UUID,
        date_from: date,
        date_to: date,
    ) -> list[RiskEvent]:
        """Return risk events for a user within an inclusive date window."""

        window_start = datetime.combine(date_from, time.min, tzinfo=UTC)
        window_end = datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=UTC)
        statement = (
            select(RiskEvent)
            .where(
                RiskEvent.user_id == user_id,
                RiskEvent.created_at >= window_start,
                RiskEvent.created_at < window_end,
            )
            .order_by(RiskEvent.created_at.desc())
        )
        return list(self.db.scalars(statement).all())
