"""Repository tests for mood-analysis and risk-event queries."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.daily_mood_summary import DailyMoodSummary
from app.models.enums import MoodLabel, RiskLevel, SenderType
from app.models.mood_analysis import MoodAnalysis
from app.models.risk_event import RiskEvent
from app.models.user import User
from app.repositories.mood_repository import DailyMoodSummaryRepository, MoodAnalysisRepository
from app.repositories.risk_repository import RiskEventRepository


@pytest.mark.integration
def test_mood_analysis_repository_lists_recent_and_by_date(
    db_session: Session,
    user_factory: Callable[..., User],
) -> None:
    """Return recent analyses in descending order and per-day analyses in ascending order."""

    # Arrange
    user = user_factory()
    session = ChatSession(user_id=user.id, summary="Mood repository session")
    db_session.add(session)
    db_session.flush()
    first_message = ChatMessage(session_id=session.id, sender=SenderType.USER, content="first")
    second_message = ChatMessage(session_id=session.id, sender=SenderType.USER, content="second")
    db_session.add_all([first_message, second_message])
    db_session.flush()

    first_analysis = MoodAnalysis(
        session_id=session.id,
        message_id=first_message.id,
        user_id=user.id,
        primary_mood=MoodLabel.SAD,
        secondary_mood=None,
        intensity=3,
        confidence=Decimal("0.700"),
        risk=RiskLevel.LOW,
        trigger_notes="low mood",
    )
    second_analysis = MoodAnalysis(
        session_id=session.id,
        message_id=second_message.id,
        user_id=user.id,
        primary_mood=MoodLabel.HOPEFUL,
        secondary_mood=None,
        intensity=2,
        confidence=Decimal("0.800"),
        risk=RiskLevel.MEDIUM,
        trigger_notes="improvement",
    )
    db_session.add_all([first_analysis, second_analysis])
    db_session.flush()
    first_analysis.created_at = datetime.now(UTC) - timedelta(hours=2)
    second_analysis.created_at = datetime.now(UTC) - timedelta(hours=1)
    db_session.flush()
    repository = MoodAnalysisRepository(db_session)

    # Act
    recent = repository.list_recent_for_user(user.id, limit=10)
    same_day = repository.list_for_user_on_date(user.id, date.today())

    # Assert
    assert [item.id for item in recent] == [second_analysis.id, first_analysis.id]
    assert [item.id for item in same_day] == [first_analysis.id, second_analysis.id]


@pytest.mark.integration
def test_daily_mood_summary_repository_filters_window_descending(
    db_session: Session,
    user_factory: Callable[..., User],
) -> None:
    """Return daily summaries within a date window in descending date order."""

    # Arrange
    user = user_factory()
    older = DailyMoodSummary(
        user_id=user.id,
        summary_date=date(2026, 4, 18),
        dominant_mood=MoodLabel.SAD,
        average_intensity=3.0,
        risk=RiskLevel.LOW,
        summary_text="Older summary",
    )
    newer = DailyMoodSummary(
        user_id=user.id,
        summary_date=date(2026, 4, 20),
        dominant_mood=MoodLabel.HAPPY,
        average_intensity=2.0,
        risk=RiskLevel.LOW,
        summary_text="Newer summary",
    )
    db_session.add_all([older, newer])
    db_session.flush()
    repository = DailyMoodSummaryRepository(db_session)
    stored_summary = repository.get_by_user_and_date(user.id, date(2026, 4, 18))

    # Act
    summaries = repository.list_for_user(
        user.id,
        date_from=date(2026, 4, 19),
        date_to=date(2026, 4, 20),
    )

    # Assert
    assert [item.id for item in summaries] == [newer.id]
    assert stored_summary is not None
    assert stored_summary.id == older.id


@pytest.mark.integration
def test_risk_event_repository_filters_by_message_and_window(
    db_session: Session,
    user_factory: Callable[..., User],
) -> None:
    """Return risk events by message id and inclusive date window in descending order."""

    # Arrange
    user = user_factory()
    session = ChatSession(user_id=user.id, summary="Risk repository session")
    db_session.add(session)
    db_session.flush()
    first_message = ChatMessage(session_id=session.id, sender=SenderType.USER, content="high risk")
    second_message = ChatMessage(session_id=session.id, sender=SenderType.USER, content="critical risk")
    db_session.add_all([first_message, second_message])
    db_session.flush()

    first_event = RiskEvent(
        user_id=user.id,
        session_id=session.id,
        message_id=first_message.id,
        risk=RiskLevel.HIGH,
        action_taken="flagged_for_follow_up",
    )
    second_event = RiskEvent(
        user_id=user.id,
        session_id=session.id,
        message_id=second_message.id,
        risk=RiskLevel.CRITICAL,
        action_taken="flagged_for_urgent_follow_up",
    )
    db_session.add_all([first_event, second_event])
    db_session.flush()
    first_event.created_at = datetime(2026, 4, 18, 10, tzinfo=UTC)
    second_event.created_at = datetime(2026, 4, 20, 12, tzinfo=UTC)
    db_session.flush()
    repository = RiskEventRepository(db_session)

    # Act
    by_message = repository.get_by_message_id(second_message.id)
    all_events = repository.list_for_user(user.id)
    window_events = repository.list_for_user_in_window(
        user.id,
        date(2026, 4, 19),
        date(2026, 4, 20),
    )

    # Assert
    assert by_message is not None
    assert by_message.id == second_event.id
    assert [item.id for item in all_events] == [second_event.id, first_event.id]
    assert [item.id for item in window_events] == [second_event.id]
