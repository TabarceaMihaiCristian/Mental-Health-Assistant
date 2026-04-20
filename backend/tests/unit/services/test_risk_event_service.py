"""Unit tests for elevated-risk event creation."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.enums import MoodLabel, RiskLevel, SenderType, UserRole
from app.models.mood_analysis import MoodAnalysis
from app.models.user import User
from app.services.risk_event_service import RiskEventService


def _user() -> User:
    user = User(email=f"{uuid4().hex[:12]}@example.com", full_name="Risk Test User", role=UserRole.USER)
    user.id = uuid4()
    return user


def _session(user: User) -> ChatSession:
    session = ChatSession(user_id=user.id, summary="Risk flow")
    session.id = uuid4()
    return session


def _message(session: ChatSession) -> ChatMessage:
    message = ChatMessage(session_id=session.id, sender=SenderType.USER, content="Help")
    message.id = uuid4()
    return message


def _analysis(*, user: User, session: ChatSession, message: ChatMessage, risk: RiskLevel) -> MoodAnalysis:
    analysis = MoodAnalysis(
        session_id=session.id,
        message_id=message.id,
        user_id=user.id,
        primary_mood=MoodLabel.SAD,
        secondary_mood=None,
        intensity=4,
        confidence=Decimal("0.900"),
        risk=risk,
        trigger_notes="Escalation test",
    )
    analysis.id = uuid4()
    return analysis


@pytest.mark.unit
def test_create_from_mood_analysis_ignores_low_risk() -> None:
    """Skip persistence when the analysis does not indicate elevated risk."""

    # Arrange
    service = object.__new__(RiskEventService)
    service.repository = Mock()
    service.logger = Mock()
    user = _user()
    session = _session(user)
    message = _message(session)
    analysis = _analysis(user=user, session=session, message=message, risk=RiskLevel.LOW)

    # Act
    result = service.create_from_mood_analysis(user, session, message, analysis)

    # Assert
    assert result is None
    service.repository.get_by_message_id.assert_not_called()
    service.repository.add.assert_not_called()


@pytest.mark.unit
def test_create_from_mood_analysis_creates_critical_event_once() -> None:
    """Persist a critical event and reuse the existing one on duplicate processing."""

    # Arrange
    service = object.__new__(RiskEventService)
    service.repository = Mock()
    service.logger = Mock()
    service.repository.get_by_message_id.side_effect = [None, "existing-event"]
    user = _user()
    session = _session(user)
    message = _message(session)
    analysis = _analysis(user=user, session=session, message=message, risk=RiskLevel.CRITICAL)

    # Act
    created_event = service.create_from_mood_analysis(user, session, message, analysis)
    duplicate_event = service.create_from_mood_analysis(user, session, message, analysis)

    # Assert
    assert created_event is not None
    assert created_event.user_id == user.id
    assert created_event.session_id == session.id
    assert created_event.message_id == message.id
    assert created_event.risk == RiskLevel.CRITICAL
    assert created_event.action_taken == "flagged_for_urgent_follow_up"
    assert duplicate_event == "existing-event"
    service.repository.add.assert_called_once_with(created_event)
