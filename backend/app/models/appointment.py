"""ORM model for specialist appointment booking requests."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import (
    APPOINTMENT_ACTOR_ROLE_ENUM,
    APPOINTMENT_MODE_ENUM,
    APPOINTMENT_STATUS_ENUM,
    AppointmentActorRole,
    AppointmentMode,
    AppointmentStatus,
)

if TYPE_CHECKING:
    from app.models.specialist import Specialist
    from app.models.user import User


class Appointment(Base, TimestampMixin):
    """Represent a requested or scheduled consultation between a user and specialist."""

    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    specialist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("specialists.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    mode: Mapped[AppointmentMode] = mapped_column(APPOINTMENT_MODE_ENUM, nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        APPOINTMENT_STATUS_ENUM,
        nullable=False,
        default=AppointmentStatus.REQUESTED,
    )
    preferred_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    cancellation_reason: Mapped[str | None] = mapped_column(Text)
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    reschedule_note: Mapped[str | None] = mapped_column(Text)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_rescheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reminder_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_rescheduled_by_role: Mapped[AppointmentActorRole | None] = mapped_column(
        APPOINTMENT_ACTOR_ROLE_ENUM
    )
    status_updated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )

    user: Mapped[User] = relationship("User", back_populates="appointments")
    specialist: Mapped[Specialist] = relationship("Specialist", back_populates="appointments")
