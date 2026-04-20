"""ORM model for recurring specialist weekly availability rules."""

from __future__ import annotations

import uuid
from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, SmallInteger, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.specialist import Specialist


class SpecialistAvailabilityRule(Base, TimestampMixin):
    """Represent a recurring weekly availability window for a specialist."""

    __tablename__ = "specialist_availability_rules"
    __table_args__ = (
        CheckConstraint("weekday >= 0 AND weekday <= 6", name="ck_specialist_availability_weekday"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    specialist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("specialists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    weekday: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    specialist: Mapped[Specialist] = relationship("Specialist", back_populates="availability_rules")
