"""ORM model for generated weekly and monthly reports."""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin
from app.models.enums import REPORT_PERIOD_ENUM, ReportPeriod

if TYPE_CHECKING:
    from app.models.user import User


class Report(Base, CreatedAtMixin):
    """Persist serialized report output for a defined reporting window."""

    __tablename__ = "reports"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "period",
            "period_start",
            "period_end",
            name="uq_report_user_period_window",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period: Mapped[ReportPeriod] = mapped_column(REPORT_PERIOD_ENUM, nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    report_data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="reports")
