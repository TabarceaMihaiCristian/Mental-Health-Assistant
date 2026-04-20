"""Application service for creating auditable risk escalation records."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.enums import RiskLevel
from app.models.mood_analysis import MoodAnalysis
from app.models.risk_event import RiskEvent
from app.models.user import User
from app.repositories.risk_repository import RiskEventRepository
from app.utils.logging import get_app_logger, log_event


ELEVATED_RISK_LEVELS = {RiskLevel.HIGH, RiskLevel.CRITICAL}


class RiskEventService:
    """Create risk events from elevated mood-analysis results."""

    def __init__(self, db: Session) -> None:
        """Bind risk-event workflows to one SQLAlchemy session."""

        self.db = db
        self.repository = RiskEventRepository(db)
        self.logger = get_app_logger(__name__)

    def create_from_mood_analysis(
        self,
        user: User,
        session: ChatSession,
        user_message: ChatMessage,
        analysis: MoodAnalysis,
    ) -> RiskEvent | None:
        """Create a risk event for a message if the analysis indicates elevated risk."""

        if analysis.risk not in ELEVATED_RISK_LEVELS:
            return None

        existing_event = self.repository.get_by_message_id(user_message.id)
        if existing_event is not None:
            return existing_event

        risk_event = RiskEvent(
            user_id=user.id,
            session_id=session.id,
            message_id=user_message.id,
            risk=analysis.risk,
            action_taken=self._resolve_action_taken(analysis.risk),
        )
        self.repository.add(risk_event)
        log_event(
            self.logger,
            "risk.event.created",
            user_id=user.id,
            session_id=session.id,
            message_id=user_message.id,
            risk_event_id=risk_event.id,
            risk=analysis.risk.value,
            action_taken=risk_event.action_taken,
        )
        return risk_event

    def _resolve_action_taken(self, risk: RiskLevel) -> str:
        """Return the deterministic action label associated with an elevated risk level."""

        if risk == RiskLevel.CRITICAL:
            return "flagged_for_urgent_follow_up"
        return "flagged_for_follow_up"
