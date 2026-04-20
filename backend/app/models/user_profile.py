"""ORM model for user onboarding details and preferences."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class UserProfile(Base, TimestampMixin):
    """Store optional profile data associated with a single user account."""

    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    age_range: Mapped[str | None] = mapped_column(String(50))
    occupation: Mapped[str | None] = mapped_column(String(255))
    goals: Mapped[str | None] = mapped_column(Text)
    preferred_activities: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    timezone: Mapped[str] = mapped_column(String(100), nullable=False, default="UTC")

    user: Mapped[User] = relationship("User", back_populates="profile")
