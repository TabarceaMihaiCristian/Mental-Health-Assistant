"""Unit tests for mood-analysis prompt construction."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.enums import SenderType, UserRole
from app.models.user import User
from app.models.user_profile import UserProfile
from app.services.prompt_builders.mood_analysis_prompt_builder import MoodAnalysisPromptBuilder


def _user_with_profile(*, occupation: str | None = "Designer", goals: str | None = "Reduce anxiety") -> User:
    user = User(email=f"{uuid4().hex[:12]}@example.com", full_name="Mood Prompt User", role=UserRole.USER)
    user.id = uuid4()
    user.profile = UserProfile(user_id=user.id, occupation=occupation, goals=goals)
    return user


def _session() -> ChatSession:
    session = ChatSession(user_id=uuid4(), summary="Mood prompt session")
    session.id = uuid4()
    session.messages = [
        ChatMessage(session_id=session.id, sender=SenderType.USER, content="I feel tense."),
        ChatMessage(session_id=session.id, sender=SenderType.ASSISTANT, content="Tell me more."),
    ]
    return session


@pytest.mark.unit
def test_build_messages_includes_context_and_transcript() -> None:
    """Build a strict analysis prompt with profile context and recent transcript lines."""

    builder = MoodAnalysisPromptBuilder()
    user = _user_with_profile()
    session = _session()
    user_message = ChatMessage(session_id=session.id, sender=SenderType.USER, content="I am overwhelmed today.")

    messages = builder.build_messages(user, session, user_message)

    assert messages[0]["role"] == "system"
    assert "Return only a compact JSON object" in messages[0]["content"]
    assert messages[1]["role"] == "system"
    assert messages[1]["content"] == "Occupation: Designer. Stated goals: Reduce anxiety."
    assert messages[2]["role"] == "user"
    assert "Latest user message:\nI am overwhelmed today." in messages[2]["content"]
    assert "user: I feel tense." in messages[2]["content"]
    assert "assistant: Tell me more." in messages[2]["content"]


@pytest.mark.unit
def test_build_user_context_returns_empty_string_without_profile() -> None:
    """Skip optional profile context when no user profile exists."""

    builder = MoodAnalysisPromptBuilder()
    user = User(email=f"{uuid4().hex[:12]}@example.com", full_name="No Profile", role=UserRole.USER)

    assert builder._build_user_context(user) == ""


@pytest.mark.unit
def test_build_user_context_omits_missing_profile_fields() -> None:
    """Include only profile values that are actually present."""

    builder = MoodAnalysisPromptBuilder()
    user = _user_with_profile(occupation=None, goals="Stay grounded")

    assert builder._build_user_context(user) == "Stated goals: Stay grounded."
