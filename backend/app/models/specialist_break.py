"""ORM model for recurring specialist break windows within a weekday."""

from __future__ import annotations

import uuid
from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.specialist import Specialist


class SpecialistBreak(Base, TimestampMixin):
    """Represent a recurring blocked break window for a specialist."""

    __tablename__ = "specialist_breaks"
    __table_args__ = (
        CheckConstraint("weekday >= 0 AND weekday <= 6", name="ck_specialist_breaks_weekday"),
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
    label: Mapped[str | None] = mapped_column(String(100))

    specialist: Mapped[Specialist] = relationship("Specialist", back_populates="breaks")
