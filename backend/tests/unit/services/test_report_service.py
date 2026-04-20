"""Unit tests for mood report generation."""

from __future__ import annotations

from collections import Counter
from datetime import date
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.models.daily_mood_summary import DailyMoodSummary
from app.models.enums import MoodLabel, ReportPeriod, RiskLevel, UserRole
from app.models.user import User
from app.services.report_service import ReportService


def _summary(
    *,
    dominant_mood: MoodLabel,
    average_intensity: float,
    risk: RiskLevel,
    summary_text: str,
) -> DailyMoodSummary:
    return DailyMoodSummary(
        user_id=uuid4(),
        summary_date=date(2026, 4, 20),
        dominant_mood=dominant_mood,
        average_intensity=average_intensity,
        risk=risk,
        summary_text=summary_text,
    )


def _user() -> User:
    user = User(email=f"{uuid4().hex[:12]}@example.com", full_name="Report Test User", role=UserRole.USER)
    user.id = uuid4()
    return user


@pytest.mark.unit
def test_resolve_period_window_for_weekly_and_monthly_reports() -> None:
    """Translate weekly and monthly references into deterministic date windows."""

    service = object.__new__(ReportService)

    weekly_start, weekly_end = service._resolve_period_window(
        ReportPeriod.WEEKLY,
        date(2026, 4, 22),
    )
    monthly_start, monthly_end = service._resolve_period_window(
        ReportPeriod.MONTHLY,
        date(2026, 2, 16),
    )

    assert weekly_start == date(2026, 4, 20)
    assert weekly_end == date(2026, 4, 26)
    assert monthly_start == date(2026, 2, 1)
    assert monthly_end == date(2026, 2, 28)


@pytest.mark.unit
def test_build_report_data_aggregates_daily_summaries() -> None:
    """Aggregate summary rows into stable report data fields."""

    service = object.__new__(ReportService)
    summaries = [
        _summary(dominant_mood=MoodLabel.SAD, average_intensity=3.0, risk=RiskLevel.MEDIUM, summary_text="A hard day with low energy."),
        _summary(dominant_mood=MoodLabel.SAD, average_intensity=4.0, risk=RiskLevel.HIGH, summary_text="Stress was elevated today."),
        _summary(dominant_mood=MoodLabel.HOPEFUL, average_intensity=2.0, risk=RiskLevel.LOW, summary_text="Improvement appeared later in the day."),
    ]

    report_data = service._build_report_data(
        ReportPeriod.WEEKLY,
        date(2026, 4, 20),
        date(2026, 4, 26),
        summaries,
    )

    assert report_data["days_with_data"] == 3
    assert report_data["average_intensity"] == pytest.approx(3.0)
    assert report_data["highest_risk"] == RiskLevel.HIGH.value
    assert report_data["dominant_mood_distribution"] == {
        MoodLabel.SAD.value: 2,
        MoodLabel.HOPEFUL.value: 1,
    }
    assert report_data["risk_distribution"] == {
        RiskLevel.MEDIUM.value: 1,
        RiskLevel.HIGH.value: 1,
        RiskLevel.LOW.value: 1,
    }
    assert len(report_data["highlights"]) == 3
    assert "most common dominant mood was sad" in report_data["generated_summary"]


@pytest.mark.unit
def test_generate_report_replaces_window_and_refreshes_result() -> None:
    """Persist a generated report using the resolved reporting window."""

    service = object.__new__(ReportService)
    service.uow = Mock()
    service.daily_summary_repository = Mock()
    service.report_repository = Mock()
    user = _user()
    persisted_report = Mock(id=uuid4())
    service.report_repository.replace_for_window.return_value = persisted_report
    service.list_daily_summaries = Mock(return_value=[])
    service._build_report_data = Mock(return_value={"period": "weekly"})

    report = service.generate_report(user, ReportPeriod.WEEKLY, date(2026, 4, 22))

    assert report is persisted_report
    service.report_repository.replace_for_window.assert_called_once()
    replace_call = service.report_repository.replace_for_window.call_args
    assert replace_call.args[0] == user.id
    assert replace_call.args[1] == ReportPeriod.WEEKLY
    assert replace_call.args[2] == date(2026, 4, 20)
    assert replace_call.args[3] == date(2026, 4, 26)
    assert replace_call.kwargs["report_data"] == {"period": "weekly"}
    service.uow.commit.assert_called_once()
    service.uow.refresh.assert_called_once_with(persisted_report)


@pytest.mark.unit
def test_build_generated_summary_handles_empty_windows() -> None:
    """Return the empty-data explanation when no summaries exist."""

    service = object.__new__(ReportService)

    summary = service._build_generated_summary(
        ReportPeriod.MONTHLY,
        0,
        Counter(),
        RiskLevel.LOW.value,
        0.0,
    )

    assert "No mood data is available yet for this monthly window." in summary
