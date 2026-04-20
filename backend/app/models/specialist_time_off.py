"""ORM model for one-off specialist time-off windows."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.specialist import Specialist


class SpecialistTimeOff(Base, TimestampMixin):
    """Represent a specific time-off period during which a specialist is unavailable."""

    __tablename__ = "specialist_time_off"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    specialist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("specialists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255))

    specialist: Mapped[Specialist] = relationship("Specialist", back_populates="time_off_periods")
