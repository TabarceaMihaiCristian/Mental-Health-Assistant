"""ORM model for in-app notifications delivered to users."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin
from app.models.enums import NOTIFICATION_TYPE_ENUM, NotificationType

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.user import User


class Notification(Base, CreatedAtMixin):
    """Persist an in-app notification targeted at a single user."""

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    appointment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="CASCADE"),
        index=True,
    )
    type: Mapped[NotificationType] = mapped_column(
        NOTIFICATION_TYPE_ENUM,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship("User", back_populates="notifications")
    appointment: Mapped[Appointment | None] = relationship("Appointment")
