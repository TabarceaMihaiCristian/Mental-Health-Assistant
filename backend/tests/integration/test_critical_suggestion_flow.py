"""Integration tests for critical-alert appointment suggestion endpoints."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, time, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.enums import RiskLevel, SenderType
from app.models.risk_event import RiskEvent
from app.models.user import User
from app.models.specialist import Specialist


@pytest.mark.integration
def test_list_critical_appointment_suggestions_requires_recent_alert(
    client: TestClient,
    auth_headers_factory: Callable[[User], dict[str, str]],
    user_factory: Callable[..., User],
) -> None:
    """Reject suggestion requests when the user has no recent critical risk event."""

    # Arrange
    user = user_factory()

    # Act
    response = client.get(
        "/api/v1/appointments/suggestions/critical",
        headers=auth_headers_factory(user),
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "No recent critical alert was found for appointment suggestions."


@pytest.mark.integration
def test_list_critical_appointment_suggestions_returns_live_slots(
    client: TestClient,
    db_session: Session,
    auth_headers_factory: Callable[[User], dict[str, str]],
    user_factory: Callable[..., User],
    specialist_factory: Callable[..., Specialist],
    availability_rule_factory: Callable[..., object],
) -> None:
    """Return live specialist availability when a recent critical alert exists."""

    # Arrange
    user = user_factory()
    specialist = specialist_factory(full_name="Dr. Escalation", specialty="Psychology")
    future_date = (datetime.now(UTC) + timedelta(days=1)).date()
    availability_rule_factory(
        specialist_id=specialist.id,
        weekday=future_date.weekday(),
        start_time=time(hour=9),
        end_time=time(hour=17),
    )

    session = ChatSession(user_id=user.id, summary="Risk escalation session")
    db_session.add(session)
    db_session.flush()

    message = ChatMessage(
        session_id=session.id,
        sender=SenderType.USER,
        content="I am in crisis and need urgent help.",
    )
    db_session.add(message)
    db_session.flush()

    db_session.add(
        RiskEvent(
            user_id=user.id,
            session_id=session.id,
            message_id=message.id,
            risk=RiskLevel.CRITICAL,
            action_taken="flagged_for_urgent_follow_up",
        )
    )
    db_session.flush()

    # Act
    response = client.get(
        "/api/v1/appointments/suggestions/critical",
        headers=auth_headers_factory(user),
    )

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_suggestions"] >= 1
    assert payload["suggestions"][0]["specialist_id"] == str(specialist.id)
    assert payload["suggestions"][0]["specialist_name"] == "Dr. Escalation"
