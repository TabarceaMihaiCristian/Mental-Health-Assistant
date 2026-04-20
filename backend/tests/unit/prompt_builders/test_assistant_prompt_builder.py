"""Unit tests for assistant prompt construction."""

from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.enums import SenderType, UserRole
from app.models.user import User
from app.models.user_profile import UserProfile
from app.services.prompt_builders.assistant_prompt_builder import AssistantPromptBuilder


def _user_with_profile() -> User:
    user = User(email=f"{uuid4().hex[:12]}@example.com", full_name="Prompt Test User", role=UserRole.USER)
    user.id = uuid4()
    user.profile = UserProfile(
        user_id=user.id,
        occupation="Engineer",
        goals="Sleep better",
        preferred_activities=["walking", "journaling"],
    )
    return user


def _session() -> ChatSession:
    session = ChatSession(user_id=uuid4(), summary="Prompt session")
    session.id = uuid4()
    session.messages = [
        ChatMessage(session_id=session.id, sender=SenderType.USER, content="first"),
        ChatMessage(session_id=session.id, sender=SenderType.ASSISTANT, content="second"),
        ChatMessage(session_id=session.id, sender=SenderType.USER, content="third"),
    ]
    return session


@pytest.mark.unit
def test_build_messages_includes_system_context_and_recent_history(monkeypatch: pytest.MonkeyPatch) -> None:
    """Build prompt messages with profile context and only the configured recent history."""

    monkeypatch.setattr(
        "app.services.prompt_builders.assistant_prompt_builder.settings",
        SimpleNamespace(assistant_max_context_messages=2),
    )
    builder = AssistantPromptBuilder()
    user = _user_with_profile()
    session = _session()

    messages = builder.build_messages(user, session)

    assert messages[0]["role"] == "system"
    assert "supportive mental wellness assistant" in messages[0]["content"]
    assert messages[1]["role"] == "system"
    assert "Occupation: Engineer." in messages[1]["content"]
    assert "Goals: Sleep better." in messages[1]["content"]
    assert "Preferred calming activities: walking, journaling." in messages[1]["content"]
    assert [item["content"] for item in messages[2:]] == ["second", "third"]
    assert [item["role"] for item in messages[2:]] == ["assistant", "user"]


@pytest.mark.unit
def test_build_user_context_returns_empty_string_without_profile() -> None:
    """Skip user-context messages when the user has no profile."""

    builder = AssistantPromptBuilder()
    user = User(email=f"{uuid4().hex[:12]}@example.com", full_name="No Profile", role=UserRole.USER)

    assert builder._build_user_context(user) == ""


@pytest.mark.unit
def test_map_sender_to_role_defaults_non_assistant_to_user() -> None:
    """Map assistant senders explicitly and treat the rest as user messages."""

    builder = AssistantPromptBuilder()

    assert builder._map_sender_to_role(SenderType.ASSISTANT) == "assistant"
    assert builder._map_sender_to_role(SenderType.USER) == "user"
