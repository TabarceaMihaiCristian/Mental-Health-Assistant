"""Repositories for chat sessions and messages."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.enums import ChatSessionStatus


class ChatSessionRepository:
    """Database access helpers for chat sessions."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to one SQLAlchemy session."""

        self.db = db

    def add(self, session: ChatSession) -> ChatSession:
        """Persist a chat session."""

        self.db.add(session)
        self.db.flush()
        return session

    def get_open_session_for_user(self, user_id: UUID) -> ChatSession | None:
        """Return the latest open chat session for a user."""

        statement = (
            select(ChatSession)
            .where(
                ChatSession.user_id == user_id,
                ChatSession.status == ChatSessionStatus.OPEN,
            )
            .order_by(ChatSession.last_message_at.desc())
        )
        return self.db.scalar(statement)

    def list_sessions_for_user(self, user_id: UUID) -> list[ChatSession]:
        """List all chat sessions for a user."""

        statement = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.started_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def get_owned_session(self, user_id: UUID, session_id: UUID) -> ChatSession | None:
        """Return a single owned session with messages loaded."""

        statement = (
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
            )
        )
        return self.db.scalar(statement)


class ChatMessageRepository:
    """Database access helpers for chat messages."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to one SQLAlchemy session."""

        self.db = db

    def add(self, message: ChatMessage) -> ChatMessage:
        """Persist a chat message."""

        self.db.add(message)
        self.db.flush()
        return message
