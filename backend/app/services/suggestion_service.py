"""Appointment suggestion workflows for critical-risk support escalation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.enums import RiskLevel
from app.models.user import User
from app.repositories.risk_repository import RiskEventRepository
from app.repositories.specialist_repository import (
    SpecialistDirectoryRow,
    SpecialistRepository,
)
from app.schemas.suggestion import (
    AppointmentSuggestionItemResponse,
    CriticalAppointmentSuggestionsResponse,
)
from app.services.availability_service import AvailabilityService
from app.utils.logging import get_app_logger, log_event


class NoRecentCriticalAlertError(ValueError):
    """Raised when critical-alert suggestions are requested without a recent trigger."""


@dataclass(slots=True)
class _SuggestionCandidate:
    """Internal sortable suggestion candidate."""

    specialist: SpecialistDirectoryRow
    start_datetime: datetime
    end_datetime: datetime


class SuggestionService:
    """Build appointment suggestions for users after critical-risk detections."""

    def __init__(self, db: Session) -> None:
        """Bind suggestion workflows to one SQLAlchemy session."""

        self.db = db
        self.logger = get_app_logger(__name__)
        self.specialist_repository = SpecialistRepository(db)
        self.risk_repository = RiskEventRepository(db)
        self.availability_service = AvailabilityService(db)

    def get_critical_appointment_suggestions(
        self,
        user: User,
        *,
        require_recent_critical_alert: bool = True,
    ) -> CriticalAppointmentSuggestionsResponse:
        """Return live specialist slot suggestions for a user's recent critical alert."""

        if require_recent_critical_alert and not self._has_recent_critical_alert(user):
            raise NoRecentCriticalAlertError(
                "No recent critical alert was found for appointment suggestions."
            )

        now = datetime.now(UTC)
        minimum_start = now + timedelta(hours=settings.appointment_booking_min_notice_hours)
        date_from = minimum_start.date()
        date_to = date_from + timedelta(days=settings.critical_alert_suggestion_lookahead_days - 1)

        candidates: list[_SuggestionCandidate] = []
        for specialist in self.specialist_repository.list_active_specialists():
            slots = self.availability_service.get_available_slots(
                specialist.id,
                date_from,
                date_to,
            )
            specialist_candidates = [
                _SuggestionCandidate(
                    specialist=specialist,
                    start_datetime=slot.start_datetime,
                    end_datetime=slot.end_datetime,
                )
                for slot in slots
                if slot.start_datetime >= minimum_start
            ]
            candidates.extend(
                specialist_candidates[: settings.critical_alert_slots_per_specialist]
            )

        ordered_candidates = sorted(
            candidates,
            key=lambda candidate: (
                candidate.start_datetime,
                -(candidate.specialist.average_rating or 0.0),
                candidate.specialist.full_name.lower(),
            ),
        )
        suggestions = [
            self._to_response_item(candidate)
            for candidate in ordered_candidates[: settings.critical_alert_suggestion_limit]
        ]
        log_event(
            self.logger,
            "suggestions.critical_appointments.generated",
            user_id=user.id,
            suggestion_count=len(suggestions),
            require_recent_alert=require_recent_critical_alert,
        )
        return CriticalAppointmentSuggestionsResponse(
            lookahead_days=settings.critical_alert_suggestion_lookahead_days,
            total_suggestions=len(suggestions),
            suggestions=suggestions,
        )

    def _has_recent_critical_alert(self, user: User) -> bool:
        """Return whether the user has a recent critical risk event."""

        cutoff = datetime.now(UTC) - timedelta(hours=settings.critical_alert_recent_window_hours)
        events = self.risk_repository.list_for_user(user.id)
        return any(
            event.risk == RiskLevel.CRITICAL and event.created_at >= cutoff
            for event in events
        )

    def _to_response_item(
        self,
        candidate: _SuggestionCandidate,
    ) -> AppointmentSuggestionItemResponse:
        """Map an internal suggestion candidate into its API response shape."""

        specialist = candidate.specialist
        return AppointmentSuggestionItemResponse(
            specialist_id=specialist.id,
            specialist_name=specialist.full_name,
            specialty=specialist.specialty,
            city=specialist.city,
            consultation_modes=specialist.consultation_modes,
            average_rating=specialist.average_rating,
            review_count=specialist.review_count,
            start_datetime=candidate.start_datetime,
            end_datetime=candidate.end_datetime,
        )
