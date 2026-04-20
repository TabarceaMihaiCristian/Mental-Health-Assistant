"""Unit tests for assistant reply generation."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.enums import SenderType, UserRole
from app.models.user import User
from app.services.assistant_service import AssistantConfigurationError, AssistantService
from app.services.openai_client import OpenAIConfigurationError


def _user() -> User:
    user = User(email=f"{uuid4().hex[:12]}@example.com", full_name="Assistant Test User", role=UserRole.USER)
    user.id = uuid4()
    return user


def _session(messages: list[ChatMessage] | None = None) -> ChatSession:
    session = ChatSession(user_id=uuid4(), summary="Assistant session")
    session.id = uuid4()
    session.messages = messages or []
    return session


@pytest.mark.unit
def test_init_raises_configuration_error_when_openai_client_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Wrap OpenAI client configuration errors in the assistant-specific exception."""

    monkeypatch.setattr(
        "app.services.assistant_service.build_openai_client",
        Mock(side_effect=OpenAIConfigurationError("OPENAI_API_KEY is required.")),
    )

    with pytest.raises(AssistantConfigurationError, match="OPENAI_API_KEY is required."):
        AssistantService()


@pytest.mark.unit
def test_generate_reply_returns_model_output(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return trimmed model output when the OpenAI response contains text."""

    client = SimpleNamespace(
        responses=SimpleNamespace(create=Mock(return_value=SimpleNamespace(output_text="  Generated reply.  ")))
    )
    prompt_builder = SimpleNamespace(build_messages=Mock(return_value=[{"role": "user", "content": "Hello"}]))
    monkeypatch.setattr("app.services.assistant_service.build_openai_client", Mock(return_value=client))
    monkeypatch.setattr("app.services.assistant_service.AssistantPromptBuilder", Mock(return_value=prompt_builder))
    service = AssistantService()

    reply = service.generate_reply(_user(), _session())

    assert reply == "Generated reply."
    prompt_builder.build_messages.assert_called_once()
    client.responses.create.assert_called_once()


@pytest.mark.unit
def test_generate_reply_uses_positive_fallback_for_empty_model_output(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fallback to the positive-tone helper when the model returns no usable text."""

    client = SimpleNamespace(
        responses=SimpleNamespace(create=Mock(return_value=SimpleNamespace(output_text="   ")))
    )
    prompt_builder = SimpleNamespace(build_messages=Mock(return_value=[]))
    monkeypatch.setattr("app.services.assistant_service.build_openai_client", Mock(return_value=client))
    monkeypatch.setattr("app.services.assistant_service.AssistantPromptBuilder", Mock(return_value=prompt_builder))
    service = AssistantService()
    session = _session(
        [
            ChatMessage(session_id=uuid4(), sender=SenderType.ASSISTANT, content="Older"),
            ChatMessage(session_id=uuid4(), sender=SenderType.USER, content="I feel good and proud today."),
        ]
    )

    reply = service.generate_reply(_user(), session)

    assert "meaningful positive moment" in reply


@pytest.mark.unit
def test_get_latest_user_message_returns_empty_string_without_user_messages() -> None:
    """Return an empty string when the session contains no user-authored messages."""

    service = object.__new__(AssistantService)
    session = _session([ChatMessage(session_id=uuid4(), sender=SenderType.ASSISTANT, content="Hello")])

    latest = service._get_latest_user_message(session)

    assert latest == ""
