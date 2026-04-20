"""Unit tests for mood-analysis parsing and fallback behavior."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.enums import MoodLabel, RiskLevel, SenderType, UserRole
from app.models.user import User
from app.services.mood_analysis_service import (
    MoodAnalysisConfigurationError,
    MoodAnalysisGenerationError,
    MoodAnalysisService,
    run_best_effort_mood_analysis,
)
from app.services.openai_client import OpenAIConfigurationError


def _user() -> User:
    user = User(email=f"{uuid4().hex[:12]}@example.com", full_name="Mood Test User", role=UserRole.USER)
    user.id = uuid4()
    return user


def _session(user: User) -> ChatSession:
    session = ChatSession(user_id=user.id, summary="Mood analysis session")
    session.id = uuid4()
    return session


def _message(session: ChatSession, *, content: str = "I feel down.", created_at: datetime | None = None) -> ChatMessage:
    message = ChatMessage(session_id=session.id, sender=SenderType.USER, content=content)
    message.id = uuid4()
    message.created_at = created_at or datetime(2026, 4, 20, 10, tzinfo=UTC)
    return message


@pytest.mark.unit
def test_init_raises_configuration_error_when_openai_client_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Wrap OpenAI client configuration errors in the mood-analysis specific exception."""

    monkeypatch.setattr(
        "app.services.mood_analysis_service.build_openai_client",
        Mock(side_effect=OpenAIConfigurationError("OPENAI_API_KEY is required.")),
    )

    with pytest.raises(MoodAnalysisConfigurationError, match="OPENAI_API_KEY is required."):
        MoodAnalysisService(Mock())


@pytest.mark.unit
def test_parse_result_accepts_json_wrapped_in_markdown() -> None:
    """Parse valid JSON even when the model wraps it in a fenced code block."""

    service = object.__new__(MoodAnalysisService)
    raw_output = """```json
    {"primary_mood":"sad","secondary_mood":"tired","intensity":4,"confidence":0.91,"risk":"high","possible_triggers":["work"]}
    ```"""

    result = service._parse_result(raw_output)

    assert result.primary_mood == MoodLabel.SAD
    assert result.secondary_mood == MoodLabel.TIRED
    assert result.intensity == 4
    assert result.confidence == pytest.approx(0.91)
    assert result.risk == RiskLevel.HIGH
    assert result.possible_triggers == ["work"]


@pytest.mark.unit
def test_parse_result_rejects_invalid_json_payloads() -> None:
    """Raise a domain error when the model response is not parseable JSON."""

    service = object.__new__(MoodAnalysisService)

    with pytest.raises(MoodAnalysisGenerationError, match="Mood analysis output was not valid JSON."):
        service._parse_result("not-json-at-all")


@pytest.mark.unit
def test_extract_response_text_reads_nested_output_content() -> None:
    """Extract response text from nested response content items when output_text is empty."""

    service = object.__new__(MoodAnalysisService)
    response = SimpleNamespace(
        output_text="",
        output=[SimpleNamespace(content=[SimpleNamespace(text=" First line "), SimpleNamespace(text="Second line")])],
    )

    text = service._extract_response_text(response)

    assert text == "First line\nSecond line"


@pytest.mark.unit
def test_build_heuristic_fallback_result_detects_stress_signals() -> None:
    """Map stress language into the deterministic fallback analysis."""

    service = object.__new__(MoodAnalysisService)

    result = service._build_heuristic_fallback_result("I feel stressed, anxious, and overwhelmed by work today.")

    assert result.primary_mood == MoodLabel.STRESSED
    assert result.secondary_mood == MoodLabel.OVERWHELMED
    assert result.risk == RiskLevel.LOW
    assert result.confidence == pytest.approx(0.25)


@pytest.mark.unit
def test_upsert_daily_summary_creates_new_summary_and_formats_text() -> None:
    """Create a daily summary when none exists for the analyzed date."""

    service = object.__new__(MoodAnalysisService)
    service.logger = Mock()
    service.daily_summary_repository = Mock()
    service.daily_summary_repository.get_by_user_and_date.return_value = None
    user = _user()
    analyses = [
        SimpleNamespace(primary_mood=MoodLabel.SAD, intensity=4, risk=RiskLevel.MEDIUM, trigger_notes="work, sleep"),
        SimpleNamespace(primary_mood=MoodLabel.SAD, intensity=2, risk=RiskLevel.LOW, trigger_notes="work"),
    ]
    service.analysis_repository = Mock()
    service.analysis_repository.list_for_user_on_date.return_value = analyses

    summary = service._upsert_daily_summary(user, date(2026, 4, 20))

    assert summary.user_id == user.id
    assert summary.summary_date == date(2026, 4, 20)
    assert summary.dominant_mood == MoodLabel.SAD
    assert summary.average_intensity == pytest.approx(3.0)
    assert summary.risk == RiskLevel.MEDIUM
    assert summary.summary_text is not None
    assert "Common triggers: work, sleep." in summary.summary_text
    assert "Highest observed risk was medium." in summary.summary_text
    service.daily_summary_repository.add.assert_called_once_with(summary)


@pytest.mark.unit
def test_upsert_daily_summary_updates_existing_summary() -> None:
    """Update the persisted daily summary when one already exists for the date."""

    service = object.__new__(MoodAnalysisService)
    service.logger = Mock()
    existing_summary = SimpleNamespace(
        dominant_mood=MoodLabel.CALM,
        average_intensity=1.0,
        risk=RiskLevel.LOW,
        summary_text="Old",
    )
    service.daily_summary_repository = Mock()
    service.daily_summary_repository.get_by_user_and_date.return_value = existing_summary
    analyses = [SimpleNamespace(primary_mood=MoodLabel.HAPPY, intensity=5, risk=RiskLevel.HIGH, trigger_notes="exercise")]
    service.analysis_repository = Mock()
    service.analysis_repository.list_for_user_on_date.return_value = analyses
    user = _user()

    summary = service._upsert_daily_summary(user, date(2026, 4, 20))

    assert summary is existing_summary
    assert summary.dominant_mood == MoodLabel.HAPPY
    assert summary.average_intensity == pytest.approx(5.0)
    assert summary.risk == RiskLevel.HIGH
    assert summary.summary_text is not None
    assert "Dominant mood was happy" in summary.summary_text
    service.daily_summary_repository.add.assert_not_called()


@pytest.mark.unit
def test_analyze_message_uses_fallback_when_model_output_is_empty() -> None:
    """Persist an analysis using the heuristic fallback when the model returns no text."""

    service = object.__new__(MoodAnalysisService)
    service.uow = Mock()
    service.client = cast(Any, SimpleNamespace(responses=SimpleNamespace(create=Mock(return_value=SimpleNamespace(output_text="")))))
    service.prompt_builder = cast(Any, SimpleNamespace(build_messages=Mock(return_value=[{"role": "user"}])))
    service.analysis_repository = Mock()
    service.daily_summary_repository = Mock()
    service.risk_event_service = Mock()
    service.logger = Mock()
    service._upsert_daily_summary = Mock()
    service._extract_response_text = Mock(return_value="")
    service._build_heuristic_fallback_result = Mock(
        return_value=SimpleNamespace(
            primary_mood=MoodLabel.SAD,
            secondary_mood=MoodLabel.TIRED,
            intensity=3,
            confidence=0.25,
            risk=RiskLevel.LOW,
            possible_triggers=["low mood"],
        )
    )
    user = _user()
    session = _session(user)
    message = _message(session)

    analysis = service.analyze_message(user, session, message)

    assert analysis.user_id == user.id
    assert analysis.session_id == session.id
    assert analysis.message_id == message.id
    assert analysis.primary_mood == MoodLabel.SAD
    assert analysis.confidence == Decimal("0.250")
    assert analysis.trigger_notes == "low mood"
    service.analysis_repository.add.assert_called_once_with(analysis)
    service._upsert_daily_summary.assert_called_once_with(user, message.created_at.date())
    service.risk_event_service.create_from_mood_analysis.assert_called_once_with(user, session, message, analysis)
    service.uow.commit.assert_called_once()
    service.uow.refresh.assert_called_once_with(analysis)


@pytest.mark.unit
def test_run_best_effort_mood_analysis_returns_none_on_runtime_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Protect the chat flow by swallowing runtime analysis failures."""

    db = Mock()
    user = _user()
    session = _session(user)
    message = _message(session)

    class FailingMoodAnalysisService:
        def __init__(self, bound_db) -> None:
            self.db = bound_db

        def analyze_message(self, current_user, current_session, current_message):
            raise MoodAnalysisGenerationError("schema mismatch")

    monkeypatch.setattr("app.services.mood_analysis_service.MoodAnalysisService", FailingMoodAnalysisService)

    result = run_best_effort_mood_analysis(db, user, session, message)

    assert result is None
