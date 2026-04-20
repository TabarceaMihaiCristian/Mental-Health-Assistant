"""Repository tests for chat session and message persistence helpers."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

import pytest
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.enums import ChatSessionStatus, SenderType
from app.models.user import User
from app.repositories.chat_repository import ChatMessageRepository, ChatSessionRepository


@pytest.mark.integration
def test_chat_session_repository_returns_latest_open_and_orders_sessions(
    db_session: Session,
    user_factory: Callable[..., User],
) -> None:
    """Select the latest open session and list sessions from newest start time to oldest."""

    # Arrange
    user = user_factory()
    other_user = user_factory()
    oldest_open = ChatSession(
        user_id=user.id,
        status=ChatSessionStatus.OPEN,
        summary="Old open",
    )
    closed = ChatSession(
        user_id=user.id,
        status=ChatSessionStatus.CLOSED,
        summary="Closed",
    )
    latest_open = ChatSession(
        user_id=user.id,
        status=ChatSessionStatus.OPEN,
        summary="Latest open",
    )
    foreign_open = ChatSession(
        user_id=other_user.id,
        status=ChatSessionStatus.OPEN,
        summary="Foreign open",
    )
    db_session.add_all([oldest_open, closed, latest_open, foreign_open])
    db_session.flush()
    oldest_open.started_at = datetime(2026, 4, 20, 8, tzinfo=UTC)
    oldest_open.last_message_at = datetime(2026, 4, 20, 8, tzinfo=UTC)
    closed.started_at = datetime(2026, 4, 20, 9, tzinfo=UTC)
    closed.last_message_at = datetime(2026, 4, 20, 9, tzinfo=UTC)
    latest_open.started_at = datetime(2026, 4, 20, 10, tzinfo=UTC)
    latest_open.last_message_at = datetime(2026, 4, 20, 11, tzinfo=UTC)
    foreign_open.started_at = datetime(2026, 4, 20, 12, tzinfo=UTC)
    foreign_open.last_message_at = datetime(2026, 4, 20, 12, tzinfo=UTC)
    db_session.flush()
    repository = ChatSessionRepository(db_session)

    # Act
    open_session = repository.get_open_session_for_user(user.id)
    sessions = repository.list_sessions_for_user(user.id)

    # Assert
    assert open_session is not None
    assert open_session.id == latest_open.id
    assert [item.id for item in sessions] == [latest_open.id, closed.id, oldest_open.id]


@pytest.mark.integration
def test_chat_repository_adds_messages_and_scopes_owned_session(
    db_session: Session,
    user_factory: Callable[..., User],
) -> None:
    """Persist chat messages and return only owned sessions with ordered messages loaded."""

    # Arrange
    user = user_factory()
    other_user = user_factory()
    session = ChatSession(user_id=user.id, summary="Owned session")
    db_session.add(session)
    db_session.flush()
    message_repository = ChatMessageRepository(db_session)
    first_message = message_repository.add(
        ChatMessage(session_id=session.id, sender=SenderType.USER, content="Hello")
    )
    second_message = message_repository.add(
        ChatMessage(session_id=session.id, sender=SenderType.ASSISTANT, content="Hi there")
    )
    repository = ChatSessionRepository(db_session)

    # Act
    owned_session = repository.get_owned_session(user.id, session.id)
    foreign_session = repository.get_owned_session(other_user.id, session.id)

    # Assert
    assert first_message.id is not None
    assert second_message.id is not None
    assert owned_session is not None
    assert [item.id for item in owned_session.messages] == [first_message.id, second_message.id]
    assert foreign_session is None
