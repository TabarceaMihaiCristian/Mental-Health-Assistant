"""ORM model for individual chat messages within a session."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin
from app.models.enums import SENDER_TYPE_ENUM, SenderType

if TYPE_CHECKING:
    from app.models.mood_analysis import MoodAnalysis
    from app.models.risk_event import RiskEvent
    from app.models.chat_session import ChatSession


class ChatMessage(Base, CreatedAtMixin):
    """Store one message sent by the user, assistant, or system."""

    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender: Mapped[SenderType] = mapped_column(SENDER_TYPE_ENUM, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    mood_analyses: Mapped[list[MoodAnalysis]] = relationship(
        "MoodAnalysis",
        back_populates="message",
        cascade="all, delete-orphan",
    )
    risk_events: Mapped[list[RiskEvent]] = relationship(
        "RiskEvent",
        back_populates="message",
        cascade="all, delete-orphan",
    )
    session: Mapped[ChatSession] = relationship("ChatSession", back_populates="messages")
