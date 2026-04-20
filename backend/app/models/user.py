"""ORM model representing application users."""

from __future__ import annotations

import uuid
from typing import Final, TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import USER_ROLE_ENUM, UserRole

if TYPE_CHECKING:
    from app.models.auth_identity import AuthIdentity
    from app.models.appointment import Appointment
    from app.models.chat_session import ChatSession
    from app.models.daily_mood_summary import DailyMoodSummary
    from app.models.mood_analysis import MoodAnalysis
    from app.models.notification import Notification
    from app.models.report import Report
    from app.models.risk_event import RiskEvent
    from app.models.specialist_review import SpecialistReview
    from app.models.user_profile import UserProfile


DELETE_ORPHAN_CASCADE: Final[str] = "all, delete-orphan"


class User(Base, TimestampMixin):
    """Persist authentication and high-level account information for a user."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(USER_ROLE_ENUM, nullable=False, default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    auth_identities: Mapped[list[AuthIdentity]] = relationship(
        "AuthIdentity",
        back_populates="user",
        cascade=DELETE_ORPHAN_CASCADE,
    )
    profile: Mapped[UserProfile | None] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade=DELETE_ORPHAN_CASCADE,
    )
    chat_sessions: Mapped[list[ChatSession]] = relationship(
        "ChatSession",
        back_populates="user",
        cascade=DELETE_ORPHAN_CASCADE,
    )
    mood_analyses: Mapped[list[MoodAnalysis]] = relationship(
        "MoodAnalysis",
        back_populates="user",
        cascade=DELETE_ORPHAN_CASCADE,
    )
    daily_summaries: Mapped[list[DailyMoodSummary]] = relationship(
        "DailyMoodSummary",
        back_populates="user",
        cascade=DELETE_ORPHAN_CASCADE,
    )
    reports: Mapped[list[Report]] = relationship(
        "Report",
        back_populates="user",
        cascade=DELETE_ORPHAN_CASCADE,
    )
    appointments: Mapped[list[Appointment]] = relationship(
        "Appointment",
        back_populates="user",
        cascade=DELETE_ORPHAN_CASCADE,
    )
    specialist_reviews: Mapped[list[SpecialistReview]] = relationship(
        "SpecialistReview",
        back_populates="user",
        cascade=DELETE_ORPHAN_CASCADE,
    )
    risk_events: Mapped[list[RiskEvent]] = relationship(
        "RiskEvent",
        back_populates="user",
        cascade=DELETE_ORPHAN_CASCADE,
    )
    notifications: Mapped[list[Notification]] = relationship(
        "Notification",
        back_populates="user",
        cascade=DELETE_ORPHAN_CASCADE,
    )
