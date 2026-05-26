"""Remove Playwright-generated demo data from the local database."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import delete, false, or_, select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.appointment import Appointment
from app.models.auth_identity import AuthIdentity
from app.models.chat_session import ChatSession
from app.models.daily_mood_summary import DailyMoodSummary
from app.models.mood_analysis import MoodAnalysis
from app.models.notification import Notification
from app.models.report import Report
from app.models.risk_event import RiskEvent
from app.models.specialist import Specialist
from app.models.specialist_availability_rule import SpecialistAvailabilityRule
from app.models.specialist_break import SpecialistBreak
from app.models.specialist_review import SpecialistReview
from app.models.specialist_time_off import SpecialistTimeOff
from app.models.user import User
from app.models.user_profile import UserProfile


PLAYWRIGHT_USER_PREFIX = "Playwright "
PLAYWRIGHT_SPECIALIST_BIO = "Playwright-owned specialist profile for E2E isolation."
PLAYWRIGHT_ADMIN_SPECIALIST_BIO = "Playwright created specialist for E2E verification."
PLAYWRIGHT_TEXT_PREFIX = "Playwright "


@dataclass(frozen=True, slots=True)
class CleanupSummary:
    """Track the number of removed records per entity."""

    appointments: int = 0
    availability_rules: int = 0
    breaks: int = 0
    chat_sessions: int = 0
    daily_summaries: int = 0
    mood_analyses: int = 0
    notifications: int = 0
    reports: int = 0
    reviews: int = 0
    risk_events: int = 0
    specialists: int = 0
    time_off_periods: int = 0
    users: int = 0
    user_profiles: int = 0
    auth_identities: int = 0


def main() -> None:
    """Delete Playwright-created users, specialists, and their derived records."""

    with SessionLocal() as session:
        summary = cleanup_playwright_data(session)
        session.commit()

    print("Playwright cleanup complete.")
    for field_name in CleanupSummary.__dataclass_fields__:
        print(f"- {field_name}: {getattr(summary, field_name)}")


def cleanup_playwright_data(session: Session) -> CleanupSummary:
    """Remove records created by the Playwright suite."""

    playwright_users = list(
        session.scalars(
            select(User).where(User.full_name.startswith(PLAYWRIGHT_USER_PREFIX))
        )
    )
    playwright_specialists = list(
        session.scalars(
            select(Specialist).where(
                or_(
                    Specialist.bio == PLAYWRIGHT_SPECIALIST_BIO,
                    Specialist.bio == PLAYWRIGHT_ADMIN_SPECIALIST_BIO,
                )
            )
        )
    )

    user_ids = [user.id for user in playwright_users]
    specialist_ids = [specialist.id for specialist in playwright_specialists]
    specialist_user_ids = [specialist.user_id for specialist in playwright_specialists if specialist.user_id]
    all_user_ids = sorted({*user_ids, *specialist_user_ids})

    appointment_ids = list(
        session.scalars(
            select(Appointment.id).where(
                or_(
                    Appointment.user_id.in_(all_user_ids) if all_user_ids else false(),
                    Appointment.specialist_id.in_(specialist_ids) if specialist_ids else false(),
                    Appointment.notes.startswith(PLAYWRIGHT_TEXT_PREFIX),
                    Appointment.cancellation_reason.startswith(PLAYWRIGHT_TEXT_PREFIX),
                    Appointment.rejection_reason.startswith(PLAYWRIGHT_TEXT_PREFIX),
                    Appointment.reschedule_note.startswith(PLAYWRIGHT_TEXT_PREFIX),
                )
            )
        )
    )

    counts: dict[str, int] = {}

    def delete_count(model_name: str, statement) -> None:
        result = session.execute(statement)
        counts[model_name] = int(getattr(result, "rowcount", 0) or 0)

    if appointment_ids:
        delete_count(
            "notifications",
            delete(Notification).where(
                or_(
                    Notification.appointment_id.in_(appointment_ids),
                    Notification.user_id.in_(all_user_ids) if all_user_ids else false(),
                )
            ),
        )
    elif all_user_ids:
        delete_count(
            "notifications",
            delete(Notification).where(Notification.user_id.in_(all_user_ids)),
        )
    else:
        counts["notifications"] = 0

    if all_user_ids:
        delete_count("reports", delete(Report).where(Report.user_id.in_(all_user_ids)))
        delete_count(
            "daily_summaries",
            delete(DailyMoodSummary).where(DailyMoodSummary.user_id.in_(all_user_ids)),
        )
        delete_count(
            "mood_analyses",
            delete(MoodAnalysis).where(MoodAnalysis.user_id.in_(all_user_ids)),
        )
        delete_count(
            "risk_events",
            delete(RiskEvent).where(RiskEvent.user_id.in_(all_user_ids)),
        )
        delete_count(
            "chat_sessions",
            delete(ChatSession).where(ChatSession.user_id.in_(all_user_ids)),
        )
        delete_count(
            "user_profiles",
            delete(UserProfile).where(UserProfile.user_id.in_(all_user_ids)),
        )
        delete_count(
            "auth_identities",
            delete(AuthIdentity).where(AuthIdentity.user_id.in_(all_user_ids)),
        )
    else:
        counts.update(
            reports=0,
            daily_summaries=0,
            mood_analyses=0,
            risk_events=0,
            chat_sessions=0,
            user_profiles=0,
            auth_identities=0,
        )

    if specialist_ids:
        delete_count(
            "availability_rules",
            delete(SpecialistAvailabilityRule).where(
                SpecialistAvailabilityRule.specialist_id.in_(specialist_ids)
            ),
        )
        delete_count(
            "breaks",
            delete(SpecialistBreak).where(SpecialistBreak.specialist_id.in_(specialist_ids)),
        )
        delete_count(
            "time_off_periods",
            delete(SpecialistTimeOff).where(
                or_(
                    SpecialistTimeOff.specialist_id.in_(specialist_ids),
                    SpecialistTimeOff.reason.startswith(PLAYWRIGHT_TEXT_PREFIX),
                )
            ),
        )
        delete_count(
            "reviews",
            delete(SpecialistReview).where(SpecialistReview.specialist_id.in_(specialist_ids)),
        )
    else:
        counts.update(availability_rules=0, breaks=0, time_off_periods=0, reviews=0)

    if appointment_ids:
        delete_count("appointments", delete(Appointment).where(Appointment.id.in_(appointment_ids)))
    else:
        counts["appointments"] = 0

    if specialist_ids:
        delete_count("specialists", delete(Specialist).where(Specialist.id.in_(specialist_ids)))
    else:
        counts["specialists"] = 0

    if all_user_ids:
        delete_count("users", delete(User).where(User.id.in_(all_user_ids)))
    else:
        counts["users"] = 0

    return CleanupSummary(**counts)


if __name__ == "__main__":
    main()
