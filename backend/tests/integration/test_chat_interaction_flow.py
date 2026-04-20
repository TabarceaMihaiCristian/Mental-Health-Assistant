"""Integration tests for chat interactions and critical-escalation responses."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.enums import MoodLabel, RiskLevel, SenderType
from app.models.mood_analysis import MoodAnalysis
from app.models.user import User
from app.schemas.suggestion import (
    AppointmentSuggestionItemResponse,
    CriticalAppointmentSuggestionsResponse,
)


@pytest.mark.integration
def test_create_chat_interaction_persists_user_and_assistant_messages(
    client: TestClient,
    db_session: Session,
    auth_headers_factory: Callable[[User], dict[str, str]],
    user_factory: Callable[..., User],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Create a deterministic interaction and persist both sides of the conversation."""

    # Arrange
    user = user_factory()
    headers = auth_headers_factory(user)
    session_response = client.post(
        "/api/v1/chat/sessions",
        json={"summary": "Need support today."},
        headers=headers,
    )
    session_id = UUID(session_response.json()["id"])
    monkeypatch.setattr(
        "app.services.chat_service.AssistantService.generate_reply",
        lambda self, current_user, session: "I am here to help.",
    )
    monkeypatch.setattr(
        "app.services.chat_service.run_best_effort_mood_analysis",
        lambda db, current_user, session, user_message: None,
    )

    # Act
    response = client.post(
        f"/api/v1/chat/sessions/{session_id}/interactions",
        json={"content": "I feel tense and need to talk."},
        headers=headers,
    )

    # Assert
    assert response.status_code == 201
    payload = response.json()
    assert payload["user_message"]["sender"] == SenderType.USER.value
    assert payload["assistant_message"]["sender"] == SenderType.ASSISTANT.value
    assert payload["assistant_message"]["content"] == "I am here to help."
    assert payload["appointment_suggestions"] is None

    stored_messages = db_session.scalars(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    ).all()
    assert len(stored_messages) == 2
    assert [message.sender for message in stored_messages] == [
        SenderType.USER,
        SenderType.ASSISTANT,
    ]


@pytest.mark.integration
def test_create_chat_interaction_includes_critical_appointment_suggestions(
    client: TestClient,
    auth_headers_factory: Callable[[User], dict[str, str]],
    user_factory: Callable[..., User],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Attach appointment suggestions when the best-effort analysis flags critical risk."""

    # Arrange
    user = user_factory()
    headers = auth_headers_factory(user)
    session_response = client.post(
        "/api/v1/chat/sessions",
        json={"summary": "Escalation path."},
        headers=headers,
    )
    session_id = UUID(session_response.json()["id"])
    monkeypatch.setattr(
        "app.services.chat_service.AssistantService.generate_reply",
        lambda self, current_user, session: "You are not alone right now.",
    )

    def build_analysis(db, current_user, session, user_message):
        return MoodAnalysis(
            session_id=session.id,
            message_id=user_message.id,
            user_id=current_user.id,
            primary_mood=MoodLabel.OVERWHELMED,
            secondary_mood=MoodLabel.ANXIOUS,
            intensity=5,
            confidence=Decimal("0.950"),
            risk=RiskLevel.CRITICAL,
            trigger_notes="urgent distress",
        )

    monkeypatch.setattr(
        "app.services.chat_service.run_best_effort_mood_analysis",
        build_analysis,
    )
    suggestion_start = datetime.now(UTC) + timedelta(days=1)
    suggestion_end = suggestion_start + timedelta(hours=2)
    monkeypatch.setattr(
        "app.services.chat_service.SuggestionService.get_critical_appointment_suggestions",
        lambda self, current_user, require_recent_critical_alert=False: CriticalAppointmentSuggestionsResponse(
            generated_at=datetime.now(UTC),
            lookahead_days=7,
            total_suggestions=1,
            suggestions=[
                AppointmentSuggestionItemResponse(
                    specialist_id=UUID("11111111-1111-1111-1111-111111111111"),
                    specialist_name="Dr. Support",
                    specialty="Psychology",
                    city="Bucharest",
                    consultation_modes=["online"],
                    average_rating=4.9,
                    review_count=18,
                    start_datetime=suggestion_start,
                    end_datetime=suggestion_end,
                )
            ],
        ),
    )

    # Act
    response = client.post(
        f"/api/v1/chat/sessions/{session_id}/interactions",
        json={"content": "I feel like I am in crisis."},
        headers=headers,
    )

    # Assert
    assert response.status_code == 201
    payload = response.json()
    assert payload["appointment_suggestions"] is not None
    assert payload["appointment_suggestions"]["total_suggestions"] == 1
    assert payload["appointment_suggestions"]["suggestions"][0]["specialist_name"] == "Dr. Support"
