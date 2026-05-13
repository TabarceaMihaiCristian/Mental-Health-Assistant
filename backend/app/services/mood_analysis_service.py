"""Structured mood analysis and daily summary generation."""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from decimal import Decimal
from typing import Any, cast

from openai.types.responses.response_input_param import ResponseInputParam
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.unit_of_work import UnitOfWork
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.daily_mood_summary import DailyMoodSummary
from app.models.enums import MoodLabel, RiskLevel
from app.models.mood_analysis import MoodAnalysis
from app.models.user import User
from app.repositories.mood_repository import DailyMoodSummaryRepository, MoodAnalysisRepository
from app.schemas.mood_analysis import MoodAnalysisResult
from app.services.openai_client import OpenAIConfigurationError, build_openai_client
from app.services.prompt_builders.mood_analysis_prompt_builder import MoodAnalysisPromptBuilder
from app.services.risk_event_service import RiskEventService
from app.utils.logging import get_app_logger, log_event, mask_uuid


CRISIS_MARKERS = (
    "kill myself",
    "want to die",
    "end my life",
    "suicide",
    "suicidal",
    "self harm",
    "self-harm",
    "don't want to live",
)

HIGH_RISK_MARKERS = (
    "hurt myself",
    "can't go on",
    "life is ruined",
    "no reason to live",
    "wish i was dead",
)

RISK_PRIORITY = {
    RiskLevel.LOW: 0,
    RiskLevel.MEDIUM: 1,
    RiskLevel.HIGH: 2,
    RiskLevel.CRITICAL: 3,
}


class MoodAnalysisConfigurationError(RuntimeError):
    """Raised when mood analysis is attempted without required configuration."""


class MoodAnalysisGenerationError(RuntimeError):
    """Raised when the AI analysis output cannot be parsed or validated."""


class MoodAnalysisService:
    """Analyze user messages and maintain derived daily summaries."""

    def __init__(self, db: Session) -> None:
        """Bind mood-analysis workflows to one SQLAlchemy session."""

        self.db = db
        self.uow = UnitOfWork(db)
        try:
            self.client = build_openai_client()
        except OpenAIConfigurationError as exc:
            raise MoodAnalysisConfigurationError(str(exc)) from exc
        self.prompt_builder = MoodAnalysisPromptBuilder()
        self.analysis_repository = MoodAnalysisRepository(db)
        self.daily_summary_repository = DailyMoodSummaryRepository(db)
        self.risk_event_service = RiskEventService(db)
        self.logger = get_app_logger(__name__)

    def analyze_message(
        self,
        user: User,
        session: ChatSession,
        user_message: ChatMessage,
    ) -> MoodAnalysis:
        """Persist structured analysis for a single user-authored message."""

        prompt_messages = cast(
            ResponseInputParam,
            self.prompt_builder.build_messages(user, session, user_message),
        )
        response = self.client.responses.create(
            model=settings.openai_model,
            input=prompt_messages,
            max_output_tokens=180,
        )

        raw_output = self._extract_response_text(response)
        if not raw_output:
            result = self._build_heuristic_fallback_result(user_message.content)
            log_event(
                self.logger,
                "mood.analysis.fallback_used",
                user_id=mask_uuid(user.id),
                session_id=mask_uuid(session.id),
                message_id=mask_uuid(user_message.id),
                reason="empty_response_text",
            )
        else:
            result = self._parse_result(raw_output)

        analysis = MoodAnalysis(
            session_id=session.id,
            message_id=user_message.id,
            user_id=user.id,
            primary_mood=result.primary_mood,
            secondary_mood=result.secondary_mood,
            intensity=result.intensity,
            confidence=Decimal(f"{result.confidence:.3f}"),
            risk=result.risk,
            trigger_notes=", ".join(result.possible_triggers) if result.possible_triggers else None,
        )
        self.analysis_repository.add(analysis)
        self._upsert_daily_summary(user, user_message.created_at.date())
        self.risk_event_service.create_from_mood_analysis(user, session, user_message, analysis)
        self.uow.commit()
        self.uow.refresh(analysis)
        log_event(
            self.logger,
            "mood.analysis.created",
            user_id=mask_uuid(user.id),
            session_id=mask_uuid(session.id),
            message_id=mask_uuid(user_message.id),
            analysis_id=mask_uuid(analysis.id),
            primary_mood=analysis.primary_mood.value,
            risk=analysis.risk.value,
        )
        return analysis

    def list_user_analyses(self, user: User, limit: int = 50) -> list[MoodAnalysis]:
        """Return recent analyses for the authenticated user."""

        return self.analysis_repository.list_recent_for_user(user.id, limit)

    def _upsert_daily_summary(self, user: User, summary_date: date) -> DailyMoodSummary:
        """Recompute and upsert the aggregated summary for a single day."""

        analyses = self.analysis_repository.list_for_user_on_date(user.id, summary_date)
        if not analyses:
            raise MoodAnalysisGenerationError("Cannot build a daily summary without analyses.")

        dominant_mood = self._pick_dominant_mood(analyses)
        average_intensity = sum(item.intensity for item in analyses) / len(analyses)
        highest_risk = self._pick_highest_risk(analyses)
        summary_text = self._build_daily_summary_text(analyses, dominant_mood, highest_risk)

        existing_summary = self.daily_summary_repository.get_by_user_and_date(user.id, summary_date)
        if existing_summary is None:
            existing_summary = DailyMoodSummary(
                user_id=user.id,
                summary_date=summary_date,
                dominant_mood=dominant_mood,
                average_intensity=round(average_intensity, 2),
                risk=highest_risk,
                summary_text=summary_text,
            )
            self.daily_summary_repository.add(existing_summary)
        else:
            existing_summary.dominant_mood = dominant_mood
            existing_summary.average_intensity = round(average_intensity, 2)
            existing_summary.risk = highest_risk
            existing_summary.summary_text = summary_text

        log_event(
            self.logger,
            "mood.daily_summary.upserted",
            user_id=mask_uuid(user.id),
            summary_date=summary_date.isoformat(),
            dominant_mood=dominant_mood.value,
            risk=highest_risk.value,
        )
        return existing_summary

    def _extract_response_text(self, response: Any) -> str:
        """Extract usable text from the OpenAI response object."""

        output_text = (getattr(response, "output_text", "") or "").strip()
        if output_text:
            return output_text

        collected_parts: list[str] = []
        for item in getattr(response, "output", []) or []:
            for content_item in getattr(item, "content", []) or []:
                text_value = getattr(content_item, "text", None)
                if isinstance(text_value, str) and text_value.strip():
                    collected_parts.append(text_value.strip())

        return "\n".join(collected_parts).strip()

    def _parse_result(self, raw_output: str) -> MoodAnalysisResult:
        """Parse and validate the raw JSON output returned by the model."""

        normalized_output = raw_output.strip()
        if normalized_output.startswith("```"):
            normalized_output = normalized_output.strip("`")
            normalized_output = normalized_output.removeprefix("json").strip()

        try:
            payload = json.loads(normalized_output)
        except json.JSONDecodeError as exc:
            raise MoodAnalysisGenerationError("Mood analysis output was not valid JSON.") from exc

        try:
            return MoodAnalysisResult.model_validate(payload)
        except Exception as exc:
            raise MoodAnalysisGenerationError("Mood analysis output did" +
                                              " not match the expected schema.") from exc

    def _build_heuristic_fallback_result(self, user_message: str) -> MoodAnalysisResult:
        """Build a low-confidence deterministic fallback analysis."""

        message = user_message.lower()

        if any(token in message for token in CRISIS_MARKERS):
            return MoodAnalysisResult(
                primary_mood=MoodLabel.SAD,
                secondary_mood=MoodLabel.OVERWHELMED,
                intensity=5,
                confidence=0.35,
                risk=RiskLevel.CRITICAL,
                possible_triggers=["self-harm language", "acute crisis"],
            )

        if any(token in message for token in HIGH_RISK_MARKERS):
            return MoodAnalysisResult(
                primary_mood=MoodLabel.SAD,
                secondary_mood=MoodLabel.OVERWHELMED,
                intensity=4,
                confidence=0.3,
                risk=RiskLevel.HIGH,
                possible_triggers=["acute distress"],
            )

        positive_tokens = (
            "good",
            "great",
            "happy",
            "better",
            "proud",
            "excited",
        )
        if any(token in message for token in positive_tokens):
            return MoodAnalysisResult(
                primary_mood=MoodLabel.HAPPY,
                secondary_mood=MoodLabel.HOPEFUL,
                intensity=3,
                confidence=0.25,
                risk=RiskLevel.LOW,
                possible_triggers=["positive routine", "self-care"],
            )

        if any(token in message for token in ("down", "sad", "low")):
            return MoodAnalysisResult(
                primary_mood=MoodLabel.SAD,
                secondary_mood=MoodLabel.TIRED,
                intensity=3,
                confidence=0.25,
                risk=RiskLevel.LOW,
                possible_triggers=["low mood"],
            )

        if any(token in message for token in ("stress", "stressed", "overwhelmed", "anxious")):
            return MoodAnalysisResult(
                primary_mood=MoodLabel.STRESSED,
                secondary_mood=MoodLabel.OVERWHELMED,
                intensity=3,
                confidence=0.25,
                risk=RiskLevel.LOW,
                possible_triggers=["work stress"],
            )

        return MoodAnalysisResult(
            primary_mood=MoodLabel.CALM,
            secondary_mood=None,
            intensity=2,
            confidence=0.2,
            risk=RiskLevel.LOW,
            possible_triggers=[],
        )

    def _pick_dominant_mood(self, analyses: list[MoodAnalysis]) -> MoodLabel:
        """Return the most frequent primary mood for the given analyses."""

        counts = Counter(item.primary_mood for item in analyses)
        return counts.most_common(1)[0][0]

    def _pick_highest_risk(self, analyses: list[MoodAnalysis]) -> RiskLevel:
        """Return the most severe risk label present in the analyses."""

        return max(analyses, key=lambda item: RISK_PRIORITY[item.risk]).risk

    def _build_daily_summary_text(
        self,
        analyses: list[MoodAnalysis],
        dominant_mood: MoodLabel,
        highest_risk: RiskLevel,
    ) -> str:
        """Create a compact deterministic daily summary sentence."""

        triggers: list[str] = []
        for item in analyses:
            if item.trigger_notes:
                triggers.extend(
                    trigger.strip()
                    for trigger in item.trigger_notes.split(",")
                    if trigger.strip()
                )

        trigger_counts = Counter(triggers)
        top_triggers = ", ".join(trigger for trigger, _ in trigger_counts.most_common(3))
        summary = (
            f"Dominant mood was {dominant_mood.value} across {len(analyses)} analyzed message"
            f"{'' if len(analyses) == 1 else 's'}."
        )
        if top_triggers:
            summary += f" Common triggers: {top_triggers}."
        if highest_risk != RiskLevel.LOW:
            summary += f" Highest observed risk was {highest_risk.value}."
        return summary


def run_best_effort_mood_analysis(
    db: Session,
    user: User,
    session: ChatSession,
    user_message: ChatMessage,
) -> MoodAnalysis | None:
    """Run mood analysis without breaking the user-facing chat flow on failure."""

    try:
        return MoodAnalysisService(db).analyze_message(user, session, user_message)
    except RuntimeError as exc:
        UnitOfWork(db).rollback()
        logger = get_app_logger(__name__)
        log_event(
            logger,
            "mood.analysis.failed",
            user_id=mask_uuid(user.id),
            session_id=mask_uuid(session.id),
            message_id=mask_uuid(user_message.id),
            reason=str(exc),
        )
        return None
