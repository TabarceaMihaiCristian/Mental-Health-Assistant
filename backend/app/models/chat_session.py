"""ORM model for a single resumable conversation session."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, utc_now
from app.models.enums import CHAT_SESSION_STATUS_ENUM, ChatSessionStatus

if TYPE_CHECKING:
    from app.models.chat_message import ChatMessage
    from app.models.mood_analysis import MoodAnalysis
    from app.models.risk_event import RiskEvent
    from app.models.user import User


class ChatSession(Base, TimestampMixin):
    """Track the lifecycle and metadata of a user conversation."""

    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ChatSessionStatus] = mapped_column(
        CHAT_SESSION_STATUS_ENUM,
        nullable=False,
        default=ChatSessionStatus.OPEN,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    summary: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship("User", back_populates="chat_sessions")
    messages: Mapped[list[ChatMessage]] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )
    mood_analyses: Mapped[list[MoodAnalysis]] = relationship(
        "MoodAnalysis",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    risk_events: Mapped[list[RiskEvent]] = relationship(
        "RiskEvent",
        back_populates="session",
    )
