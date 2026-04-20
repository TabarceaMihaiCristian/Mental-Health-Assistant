"""ORM model for specialists available through the platform."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import SPECIALIST_STATUS_ENUM, SpecialistStatus

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.specialist_availability_rule import SpecialistAvailabilityRule
    from app.models.specialist_break import SpecialistBreak
    from app.models.specialist_review import SpecialistReview
    from app.models.specialist_time_off import SpecialistTimeOff
    from app.models.user import User


DELETE_ORPHAN_CASCADE = "all, delete-orphan"


class Specialist(Base, TimestampMixin):
    """Store specialist profile data exposed to users for booking."""

    __tablename__ = "specialists"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        unique=True,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    specialty: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text)
    consultation_modes: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    city: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[SpecialistStatus] = mapped_column(
        SPECIALIST_STATUS_ENUM,
        nullable=False,
        default=SpecialistStatus.ACTIVE,
    )

    appointments: Mapped[list[Appointment]] = relationship(
        "Appointment",
        back_populates="specialist",
    )
    user: Mapped[User | None] = relationship("User")
    reviews: Mapped[list[SpecialistReview]] = relationship(
        "SpecialistReview",
        back_populates="specialist",
        cascade=DELETE_ORPHAN_CASCADE,
    )
    availability_rules: Mapped[list[SpecialistAvailabilityRule]] = relationship(
        "SpecialistAvailabilityRule",
        back_populates="specialist",
        cascade=DELETE_ORPHAN_CASCADE,
    )
    breaks: Mapped[list[SpecialistBreak]] = relationship(
        "SpecialistBreak",
        back_populates="specialist",
        cascade=DELETE_ORPHAN_CASCADE,
    )
    time_off_periods: Mapped[list[SpecialistTimeOff]] = relationship(
        "SpecialistTimeOff",
        back_populates="specialist",
        cascade=DELETE_ORPHAN_CASCADE,
    )
