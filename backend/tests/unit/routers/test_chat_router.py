"""Unit tests for chat router branches."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.v1.routers import chat as router
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.assistant import ChatInteractionRequest
from app.schemas.chat import ChatMessageCreateRequest, ChatSessionCreateRequest
from app.schemas.suggestion import CriticalAppointmentSuggestionsResponse
from app.services.chat_service import (
    AssistantInteractionError,
    ChatSessionClosedError,
    ChatSessionNotFoundError,
    InvalidChatSenderError,
)


def _current_user() -> User:
    return User(email=f"{uuid4().hex[:12]}@example.com", full_name="Chat Router User", role=UserRole.USER)


def _session_row() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        user_id=uuid4(),
        status="open",
        started_at=datetime(2026, 4, 20, 9, tzinfo=UTC),
        last_message_at=datetime(2026, 4, 20, 10, tzinfo=UTC),
        ended_at=None,
        summary="Support session",
        created_at=datetime(2026, 4, 20, 9, tzinfo=UTC),
        updated_at=datetime(2026, 4, 20, 10, tzinfo=UTC),
        messages=[],
    )


def _message_row() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        session_id=uuid4(),
        sender="user",
        content="Hello",
        created_at=datetime(2026, 4, 20, 10, tzinfo=UTC),
    )


@pytest.mark.unit
def test_chat_session_routes_cover_success_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    """Serialize session routes for create, list, open, and owned-session detail."""

    session = _session_row()
    current_user = _current_user()
    monkeypatch.setattr(router.ChatSessionResponse, "model_validate", classmethod(lambda cls, item: item))
    monkeypatch.setattr(router.ChatSessionDetailResponse, "model_validate", classmethod(lambda cls, item: item))
    service = SimpleNamespace(
        create_session=Mock(return_value=session),
        list_sessions=Mock(return_value=[session]),
        get_open_session=Mock(return_value=session),
        get_session=Mock(return_value=session),
    )
    monkeypatch.setattr(router, "ChatService", Mock(return_value=service))

    assert router.create_chat_session(ChatSessionCreateRequest(summary="Support session"), current_user, Mock()) is session
    assert router.list_chat_sessions(current_user, Mock()) == [session]
    assert router.get_open_chat_session(current_user, Mock()) is session
    assert router.get_chat_session(session.id, current_user, Mock()) is session


@pytest.mark.unit
def test_get_open_and_get_chat_session_map_missing_session(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return `None` for no open session and map owned-session misses to 404."""

    current_user = _current_user()
    monkeypatch.setattr(router.ChatSessionResponse, "model_validate", classmethod(lambda cls, item: item))
    service = SimpleNamespace(
        get_open_session=Mock(return_value=None),
        get_session=Mock(side_effect=ChatSessionNotFoundError("Chat session not found.")),
    )
    monkeypatch.setattr(router, "ChatService", Mock(return_value=service))

    assert router.get_open_chat_session(current_user, Mock()) is None
    with pytest.raises(HTTPException) as error:
        router.get_chat_session(uuid4(), current_user, Mock())
    assert error.value.status_code == 404
    assert error.value.detail == "Chat session not found."


@pytest.mark.unit
def test_add_chat_message_maps_not_found_closed_and_sender_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Serialize successful message writes and map known chat write failures."""

    message = _message_row()
    payload = ChatMessageCreateRequest(content="Hello")
    current_user = _current_user()
    monkeypatch.setattr(router.ChatMessageResponse, "model_validate", classmethod(lambda cls, item: item))
    service = SimpleNamespace(add_message=Mock(return_value=message))
    monkeypatch.setattr(router, "ChatService", Mock(return_value=service))

    assert router.add_chat_message(message.session_id, payload, current_user, Mock()) is message

    for exc in [
        ChatSessionNotFoundError("Chat session not found."),
        ChatSessionClosedError("Cannot add messages to a closed chat session."),
        InvalidChatSenderError("Sender must be user."),
    ]:
        failing = SimpleNamespace(add_message=Mock(side_effect=exc))
        monkeypatch.setattr(router, "ChatService", Mock(return_value=failing))
        with pytest.raises(HTTPException) as error:
            router.add_chat_message(message.session_id, payload, current_user, Mock())
        expected_status = 404 if isinstance(exc, ChatSessionNotFoundError) else 400
        assert error.value.status_code == expected_status
        assert error.value.detail == str(exc)


@pytest.mark.unit
def test_create_chat_interaction_maps_service_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    """Serialize successful interactions and map chat interaction failures."""

    user_message = _message_row()
    assistant_message = _message_row()
    session = _session_row()
    suggestions = CriticalAppointmentSuggestionsResponse(lookahead_days=7, total_suggestions=0, suggestions=[])
    payload = ChatInteractionRequest(content="Help")
    current_user = _current_user()
    monkeypatch.setattr(router.ChatMessageResponse, "model_validate", classmethod(lambda cls, item: item))
    monkeypatch.setattr(router.ChatSessionResponse, "model_validate", classmethod(lambda cls, item: item))
    monkeypatch.setattr(router, "ChatInteractionResponse", lambda **kwargs: SimpleNamespace(**kwargs))
    service = SimpleNamespace(create_interaction=Mock(return_value=(user_message, assistant_message, session, suggestions)))
    monkeypatch.setattr(router, "ChatService", Mock(return_value=service))

    response = router.create_chat_interaction(session.id, payload, current_user, Mock())
    assert response.user_message is user_message
    assert response.assistant_message is assistant_message
    assert response.session is session
    assert response.appointment_suggestions is suggestions

    for exc in [
        ChatSessionNotFoundError("Chat session not found."),
        ChatSessionClosedError("Cannot add messages to a closed chat session."),
        AssistantInteractionError("Assistant unavailable"),
    ]:
        failing = SimpleNamespace(create_interaction=Mock(side_effect=exc))
        monkeypatch.setattr(router, "ChatService", Mock(return_value=failing))
        with pytest.raises(HTTPException) as error:
            router.create_chat_interaction(session.id, payload, current_user, Mock())
        if isinstance(exc, ChatSessionNotFoundError):
            expected_status = 404
        elif isinstance(exc, ChatSessionClosedError):
            expected_status = 400
        else:
            expected_status = 502
        assert error.value.status_code == expected_status
        assert error.value.detail == str(exc)
