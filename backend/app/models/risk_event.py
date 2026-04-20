"""ORM model for recorded safety escalations and risk events."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin
from app.models.enums import RISK_LEVEL_ENUM, RiskLevel

if TYPE_CHECKING:
    from app.models.chat_message import ChatMessage
    from app.models.chat_session import ChatSession
    from app.models.user import User


class RiskEvent(Base, CreatedAtMixin):
    """Store notable risk detections and the action taken in response."""

    __tablename__ = "risk_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="SET NULL")
    )
    risk: Mapped[RiskLevel] = mapped_column(RISK_LEVEL_ENUM, nullable=False)
    action_taken: Mapped[str] = mapped_column(Text, nullable=False)

    message: Mapped[ChatMessage] = relationship("ChatMessage", back_populates="risk_events")
    user: Mapped[User] = relationship("User", back_populates="risk_events")
    session: Mapped[ChatSession | None] = relationship("ChatSession", back_populates="risk_events")
