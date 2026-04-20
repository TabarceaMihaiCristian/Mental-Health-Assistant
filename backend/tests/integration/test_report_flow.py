"""Integration tests for daily mood summaries and generated reports."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.daily_mood_summary import DailyMoodSummary
from app.models.enums import MoodLabel, ReportPeriod, RiskLevel
from app.models.report import Report
from app.models.user import User


@pytest.mark.integration
def test_list_daily_mood_summaries_returns_user_owned_summaries(
    client: TestClient,
    db_session: Session,
    auth_headers_factory: Callable[[User], dict[str, str]],
    user_factory: Callable[..., User],
) -> None:
    """Return only the authenticated user's stored daily summaries."""

    # Arrange
    user = user_factory()
    other_user = user_factory()
    db_session.add_all(
        [
            DailyMoodSummary(
                user_id=user.id,
                summary_date=date(2026, 4, 20),
                dominant_mood=MoodLabel.SAD,
                average_intensity=3.20,
                risk=RiskLevel.MEDIUM,
                summary_text="Hard Monday.",
            ),
            DailyMoodSummary(
                user_id=other_user.id,
                summary_date=date(2026, 4, 20),
                dominant_mood=MoodLabel.HAPPY,
                average_intensity=2.10,
                risk=RiskLevel.LOW,
                summary_text="Different user data.",
            ),
        ]
    )
    db_session.flush()

    # Act
    response = client.get(
        "/api/v1/reports/daily-summaries",
        headers=auth_headers_factory(user),
    )

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["summary_text"] == "Hard Monday."
    assert payload[0]["dominant_mood"] == MoodLabel.SAD.value


@pytest.mark.integration
def test_generate_and_fetch_weekly_report_flow(
    client: TestClient,
    db_session: Session,
    auth_headers_factory: Callable[[User], dict[str, str]],
    user_factory: Callable[..., User],
) -> None:
    """Generate a weekly report from stored summaries and fetch it back."""

    # Arrange
    user = user_factory()
    db_session.add_all(
        [
            DailyMoodSummary(
                user_id=user.id,
                summary_date=date(2026, 4, 20),
                dominant_mood=MoodLabel.SAD,
                average_intensity=3.50,
                risk=RiskLevel.MEDIUM,
                summary_text="Monday was difficult.",
            ),
            DailyMoodSummary(
                user_id=user.id,
                summary_date=date(2026, 4, 21),
                dominant_mood=MoodLabel.HOPEFUL,
                average_intensity=2.50,
                risk=RiskLevel.LOW,
                summary_text="Tuesday improved slightly.",
            ),
        ]
    )
    db_session.flush()
    headers = auth_headers_factory(user)

    # Act
    generate_response = client.post(
        "/api/v1/reports/weekly?reference_date=2026-04-22",
        headers=headers,
    )
    fetch_response = client.get(
        "/api/v1/reports/weekly?reference_date=2026-04-22",
        headers=headers,
    )

    # Assert
    assert generate_response.status_code == 201
    generate_payload = generate_response.json()
    assert generate_payload["period"] == ReportPeriod.WEEKLY.value
    assert generate_payload["period_start"] == "2026-04-20"
    assert generate_payload["period_end"] == "2026-04-26"
    assert generate_payload["report_data"]["days_with_data"] == 2
    assert generate_payload["report_data"]["highest_risk"] == RiskLevel.MEDIUM.value
    assert "sad" in generate_payload["report_data"]["dominant_mood_distribution"]

    assert fetch_response.status_code == 200
    fetch_payload = fetch_response.json()
    assert fetch_payload["id"] == generate_payload["id"]

    stored_reports = db_session.query(Report).filter(Report.user_id == user.id).all()
    assert len(stored_reports) == 1
