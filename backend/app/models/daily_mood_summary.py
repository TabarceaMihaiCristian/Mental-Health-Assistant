"""ORM model for per-day aggregated mood summaries."""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin
from app.models.enums import MOOD_LABEL_ENUM, RISK_LEVEL_ENUM, MoodLabel, RiskLevel

if TYPE_CHECKING:
    from app.models.user import User


class DailyMoodSummary(Base, CreatedAtMixin):
    """Store one aggregated emotional summary per user per day."""

    __tablename__ = "daily_mood_summaries"
    __table_args__ = (
        UniqueConstraint("user_id", "summary_date", name="uq_daily_mood_user_date"),
        CheckConstraint(
            "average_intensity >= 1 AND average_intensity <= 5",
            name="ck_daily_mood_average_intensity_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    summary_date: Mapped[date] = mapped_column(Date, nullable=False)
    dominant_mood: Mapped[MoodLabel] = mapped_column(MOOD_LABEL_ENUM, nullable=False)
    average_intensity: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    risk: Mapped[RiskLevel] = mapped_column(RISK_LEVEL_ENUM, nullable=False, default=RiskLevel.LOW)
    summary_text: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship("User", back_populates="daily_summaries")
