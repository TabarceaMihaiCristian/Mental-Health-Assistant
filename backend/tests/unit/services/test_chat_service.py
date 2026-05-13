"""Unit tests for chat session service workflows."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.models.chat_session import ChatSession
from app.models.enums import ChatSessionStatus, ReportPeriod, RiskLevel, SenderType, UserRole
from app.models.user import User
from app.schemas.assistant import ChatInteractionRequest
from app.schemas.chat import ChatMessageCreateRequest, ChatSessionCreateRequest
from app.services.chat_service import (
    AssistantInteractionError,
    ChatService,
    ChatSessionClosedError,
    ChatSessionNotFoundError,
    InvalidChatSenderError,
)


def _user() -> User:
    user = User(email=f"{uuid4().hex[:12]}@example.com", full_name="Chat Test User", role=UserRole.USER)
    user.id = uuid4()
    return user


def _session(*, status: ChatSessionStatus) -> ChatSession:
    session = ChatSession(user_id=uuid4(), summary="Chat service test")
    session.id = uuid4()
    session.status = status
    session.messages = []
    return session


@pytest.mark.unit
def test_create_session_persists_open_session() -> None:
    """Create an open chat session, commit it, and refresh the persisted row."""

    service = object.__new__(ChatService)
    service.uow = Mock()
    service.session_repository = Mock()
    service.message_repository = Mock()
    service.logger = Mock()
    user = _user()
    created_session: ChatSession | None = None

    def add_session(session) -> None:
        nonlocal created_session
        created_session = session
        session.id = uuid4()

    service.session_repository.add.side_effect = add_session

    result = service.create_session(user, ChatSessionCreateRequest(summary="Support session"))

    assert created_session
    assert result is created_session
    assert created_session.user_id == user.id
    assert created_session.status == ChatSessionStatus.OPEN
    service.uow.commit.assert_called_once()
    service.uow.refresh.assert_called_once_with(created_session)


@pytest.mark.unit
def test_get_session_raises_when_owned_session_is_missing() -> None:
    """Reject session lookups that do not belong to the current user."""

    service = object.__new__(ChatService)
    service.session_repository = Mock()
    service.session_repository.get_owned_session.return_value = None
    user = _user()

    with pytest.raises(ChatSessionNotFoundError, match="Chat session not found."):
        service.get_session(user, uuid4())


@pytest.mark.unit
def test_close_session_marks_open_session_closed_and_generates_reports(monkeypatch: pytest.MonkeyPatch) -> None:
    """Close an open session and regenerate the current weekly and monthly reports."""

    service = object.__new__(ChatService)
    service.db = Mock()
    service.uow = Mock()
    service.session_repository = Mock()
    service.message_repository = Mock()
    service.logger = Mock()
    session = _session(status=ChatSessionStatus.OPEN)
    user = _user()
    service.get_session = Mock(return_value=session)
    report_service = SimpleNamespace(generate_report=Mock())
    monkeypatch.setattr("app.services.chat_service.ReportService", Mock(return_value=report_service))

    result = service.close_session(user, session.id)

    assert result is session
    assert session.status == ChatSessionStatus.CLOSED
    assert session.ended_at is not None
    service.session_repository.add.assert_called_once_with(session)
    service.uow.commit.assert_called_once()
    service.uow.refresh.assert_called_once_with(session)
    report_service.generate_report.assert_any_call(user, ReportPeriod.WEEKLY, session.ended_at.date())
    report_service.generate_report.assert_any_call(user, ReportPeriod.MONTHLY, session.ended_at.date())
    assert report_service.generate_report.call_count == 2


@pytest.mark.unit
def test_close_session_keeps_closure_when_report_sync_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """Do not undo session closure when report materialization fails after close."""

    service = object.__new__(ChatService)
    service.db = Mock()
    service.uow = Mock()
    service.session_repository = Mock()
    service.message_repository = Mock()
    service.logger = Mock()
    session = _session(status=ChatSessionStatus.OPEN)
    user = _user()
    service.get_session = Mock(return_value=session)
    report_service = SimpleNamespace(generate_report=Mock(side_effect=RuntimeError("report store unavailable")))
    monkeypatch.setattr("app.services.chat_service.ReportService", Mock(return_value=report_service))

    result = service.close_session(user, session.id)

    assert result is session
    assert session.status == ChatSessionStatus.CLOSED
    assert session.ended_at is not None
    service.uow.commit.assert_called_once()
    service.uow.refresh.assert_called_once_with(session)


@pytest.mark.unit
def test_add_message_rejects_invalid_sender(monkeypatch: pytest.MonkeyPatch) -> None:
    """Translate sender validation errors into the chat-specific exception."""

    service = object.__new__(ChatService)
    monkeypatch.setattr("app.services.chat_service.ensure_user_sender", Mock(side_effect=ValueError("Sender must be user.")))

    with pytest.raises(InvalidChatSenderError, match="Sender must be user."):
        service.add_message(
            _user(),
            uuid4(),
            ChatMessageCreateRequest(content="Hello", sender=SenderType.USER),
        )


@pytest.mark.unit
def test_add_message_rejects_closed_session() -> None:
    """Reject writes against closed chat sessions."""

    service = object.__new__(ChatService)
    service.get_session = Mock(return_value=_session(status=ChatSessionStatus.CLOSED))

    with pytest.raises(ChatSessionClosedError, match="Cannot add messages to a closed chat session."):
        service.add_message(
            _user(),
            uuid4(),
            ChatMessageCreateRequest(content="Hello", sender=SenderType.USER),
        )


@pytest.mark.unit
def test_add_message_normalizes_content_and_persists_message(monkeypatch: pytest.MonkeyPatch) -> None:
    """Persist a normalized user message on an open session and refresh it."""

    service = object.__new__(ChatService)
    service.uow = Mock()
    service.session_repository = Mock()
    service.message_repository = Mock()
    service.logger = Mock()
    monkeypatch.setattr("app.services.chat_service.ensure_user_sender", Mock())
    monkeypatch.setattr("app.services.chat_service.normalize_message_content", lambda value: value.strip())
    open_session = _session(status=ChatSessionStatus.OPEN)
    service.get_session = Mock(return_value=open_session)
    user = _user()
    created_message = None

    def add_message(message) -> None:
        nonlocal created_message
        created_message = message
        message.id = uuid4()

    service.message_repository.add.side_effect = add_message
    service.session_repository.add.side_effect = lambda session: session

    result = service.add_message(
        user,
        open_session.id,
        ChatMessageCreateRequest(content="  Hello there  ", sender=SenderType.USER),
    )

    assert created_message
    assert result is created_message
    assert created_message.content == "Hello there"
    assert created_message.sender == SenderType.USER
    service.uow.commit.assert_called_once()
    service.uow.refresh.assert_called_once_with(created_message)


@pytest.mark.unit
def test_create_interaction_rolls_back_when_assistant_generation_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """Rollback and wrap assistant errors without persisting an interaction."""

    service = object.__new__(ChatService)
    service.db = Mock()
    service.uow = Mock()
    service.session_repository = Mock()
    service.message_repository = Mock()
    service.logger = Mock()
    session = _session(status=ChatSessionStatus.OPEN)
    service.get_session = Mock(return_value=session)
    monkeypatch.setattr(
        "app.services.chat_service.AssistantService",
        Mock(return_value=SimpleNamespace(generate_reply=Mock(side_effect=RuntimeError("OpenAI down")))),
    )

    with pytest.raises(AssistantInteractionError, match="OpenAI down"):
        service.create_interaction(
            _user(),
            session.id,
            ChatInteractionRequest(content="I need help"),
        )

    service.uow.rollback.assert_called_once()
    service.uow.commit.assert_not_called()


@pytest.mark.unit
def test_create_interaction_returns_suggestions_for_critical_analysis(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return appointment suggestions when best-effort analysis marks the message critical."""

    service = object.__new__(ChatService)
    service.db = Mock()
    service.uow = Mock()
    service.session_repository = Mock()
    service.message_repository = Mock()
    service.logger = Mock()
    session = _session(status=ChatSessionStatus.OPEN)
    service.get_session = Mock(return_value=session)

    monkeypatch.setattr(
        "app.services.chat_service.AssistantService",
        Mock(return_value=SimpleNamespace(generate_reply=Mock(return_value="Assistant reply"))),
    )
    monkeypatch.setattr("app.services.chat_service.normalize_message_content", lambda value: value.strip())
    monkeypatch.setattr(
        "app.services.chat_service.run_best_effort_mood_analysis",
        Mock(return_value=SimpleNamespace(risk=RiskLevel.CRITICAL)),
    )
    suggestions = SimpleNamespace(total_suggestions=1)
    suggestion_service = SimpleNamespace(get_critical_appointment_suggestions=Mock(return_value=suggestions))
    monkeypatch.setattr("app.services.chat_service.SuggestionService", Mock(return_value=suggestion_service))

    created_messages: list[object] = []

    def add_message(message) -> None:
        created_messages.append(message)
        message.id = uuid4()

    service.message_repository.add.side_effect = add_message
    service.session_repository.add.side_effect = lambda persisted_session: persisted_session
    user = _user()

    user_message, assistant_message, persisted_session, returned_suggestions = service.create_interaction(
        user,
        session.id,
        ChatInteractionRequest(content="  I am in crisis  "),
    )

    assert persisted_session is session
    assert user_message.content == "I am in crisis"
    assert user_message.sender == SenderType.USER
    assert assistant_message.content == "Assistant reply"
    assert assistant_message.sender == SenderType.ASSISTANT
    assert returned_suggestions is suggestions
    assert len(created_messages) == 2
    service.uow.commit.assert_called_once()
    assert service.uow.refresh.call_count == 4
    suggestion_service.get_critical_appointment_suggestions.assert_called_once_with(user, require_recent_critical_alert=False)


