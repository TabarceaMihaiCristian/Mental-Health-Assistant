"""ORM model for AI-generated mood and risk analysis results."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, SmallInteger, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin
from app.models.enums import MOOD_LABEL_ENUM, RISK_LEVEL_ENUM, MoodLabel, RiskLevel

if TYPE_CHECKING:
    from app.models.chat_message import ChatMessage
    from app.models.chat_session import ChatSession
    from app.models.user import User


class MoodAnalysis(Base, CreatedAtMixin):
    """Persist emotional classification output for a chat session."""

    __tablename__ = "mood_analyses"
    __table_args__ = (
        CheckConstraint("intensity BETWEEN 1 AND 5",
                        name="ck_mood_analysis_intensity_range"),
        CheckConstraint("confidence >= 0 AND confidence <= 1",
                        name="ck_mood_analysis_confidence_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    primary_mood: Mapped[MoodLabel] = mapped_column(MOOD_LABEL_ENUM, nullable=False)
    secondary_mood: Mapped[MoodLabel | None] = mapped_column(MOOD_LABEL_ENUM)
    intensity: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    risk: Mapped[RiskLevel] = mapped_column(RISK_LEVEL_ENUM, nullable=False, default=RiskLevel.LOW)
    trigger_notes: Mapped[str | None] = mapped_column(Text)

    message: Mapped[ChatMessage] = relationship("ChatMessage", back_populates="mood_analyses")
    user: Mapped[User] = relationship("User", back_populates="mood_analyses")
    session: Mapped[ChatSession] = relationship("ChatSession", back_populates="mood_analyses")
