"""Seed deterministic demo data for local UI and flow validation."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.appointment import Appointment
from app.models.auth_identity import AuthIdentity
from app.models.enums import (
    AppointmentMode,
    AppointmentStatus,
    AuthProvider,
    SpecialistStatus,
    UserRole,
)
from app.models.specialist import Specialist
from app.models.specialist_availability_rule import SpecialistAvailabilityRule
from app.models.specialist_break import SpecialistBreak
from app.models.specialist_review import SpecialistReview
from app.models.specialist_time_off import SpecialistTimeOff
from app.models.user import User
from app.models.user_profile import UserProfile
from app.services.availability_service import SLOT_DURATION


@dataclass(frozen=True, slots=True)
class DemoAccountSpec:
    """Credentials and base identity data for deterministic local accounts."""

    label: str
    env_email: str
    env_password: str
    default_email: str
    default_password: str
    full_name: str
    role: UserRole


@dataclass(frozen=True, slots=True)
class DemoSpecialistSpec:
    """Public specialist directory data used to populate the UI."""

    key: str
    email: str
    password: str | None
    full_name: str
    specialty: str
    bio: str
    consultation_modes: list[str]
    city: str
    status: SpecialistStatus


@dataclass(frozen=True, slots=True)
class ReviewSpec:
    """One deterministic specialist review entry."""

    reviewer_email: str
    rating: int
    comment: str


@dataclass(frozen=True, slots=True)
class AvailabilityRuleSpec:
    """One recurring weekly availability window."""

    weekday: int
    start_time: time
    end_time: time
    is_enabled: bool = True


@dataclass(frozen=True, slots=True)
class BreakSpec:
    """One recurring weekly break window."""

    weekday: int
    start_time: time
    end_time: time
    label: str


@dataclass(frozen=True, slots=True)
class TimeOffSpec:
    """One specific time-off period for a seeded specialist."""

    start_datetime: datetime
    end_datetime: datetime
    reason: str


ACCOUNT_SPECS = (
    DemoAccountSpec(
        label="AdminTest",
        env_email="SEED_ADMIN_EMAIL",
        env_password="SEED_ADMIN_PASSWORD",
        default_email="admin.test@mentalhealthapp.com",
        default_password="AdminTest123!",
        full_name="Admin Test",
        role=UserRole.ADMIN,
    ),
    DemoAccountSpec(
        label="SpecialistTest",
        env_email="SEED_SPECIALIST_EMAIL",
        env_password="SEED_SPECIALIST_PASSWORD",
        default_email="specialist.test@mentalhealthapp.com",
        default_password="SpecialistTest123!",
        full_name="Dr. Ana Pavel",
        role=UserRole.SPECIALIST,
    ),
    DemoAccountSpec(
        label="UserTest",
        env_email="SEED_USER_EMAIL",
        env_password="SEED_USER_PASSWORD",
        default_email="user.test@mentalhealthapp.com",
        default_password="UserTest123!",
        full_name="Alex Marin",
        role=UserRole.USER,
    ),
)

REVIEWER_SPECS = (
    ("reviewer.one@mentalhealthapp.com", "Bianca Georgescu"),
    ("reviewer.two@mentalhealthapp.com", "Mihnea Stan"),
    ("reviewer.three@mentalhealthapp.com", "Oana Ilie"),
)

SPECIALIST_SPECS = (
    DemoSpecialistSpec(
        key="specialist_test",
        email="specialist.test@mentalhealthapp.com",
        password="SpecialistTest123!",
        full_name="Dr. Ana Pavel",
        specialty="Clinical Psychology",
        bio="Clinical psychologist with 11 years of experience supporting adults through anxiety, loss, and major life transitions. Known for a structured, grounded style that balances emotional safety with practical coping work.",
        consultation_modes=["online", "onsite"],
        city="Bucharest",
        status=SpecialistStatus.ACTIVE,
    ),
    DemoSpecialistSpec(
        key="elena_ionescu",
        email="elena.ionescu@mentalhealthapp.com",
        password=None,
        full_name="Dr. Elena Ionescu",
        specialty="CBT for Anxiety",
        bio="Focused on generalized anxiety, panic symptoms, and burnout recovery. 9 years of CBT practice with a strong emphasis on routines, sleep regulation, and work-life stabilisation.",
        consultation_modes=["online"],
        city="Cluj-Napoca",
        status=SpecialistStatus.ACTIVE,
    ),
    DemoSpecialistSpec(
        key="mara_dumitrescu",
        email="mara.dumitrescu@mentalhealthapp.com",
        password=None,
        full_name="Dr. Mara Dumitrescu",
        specialty="Trauma and Stress",
        bio="Trauma-informed therapist working with chronic stress, grief, and difficult relationship histories. 13 years of experience in longer-form therapeutic support for adults.",
        consultation_modes=["online", "onsite"],
        city="Iasi",
        status=SpecialistStatus.ACTIVE,
    ),
    DemoSpecialistSpec(
        key="radu_marinescu",
        email="radu.marinescu@mentalhealthapp.com",
        password=None,
        full_name="Dr. Radu Marinescu",
        specialty="Depression and Mood Disorders",
        bio="Psychotherapist with 12 years of work around depressive episodes, motivation collapse, and recovery planning. Calm, methodical, and well suited for users who want a steady pace.",
        consultation_modes=["onsite"],
        city="Timisoara",
        status=SpecialistStatus.ACTIVE,
    ),
    DemoSpecialistSpec(
        key="ioana_petrescu",
        email="ioana.petrescu@mentalhealthapp.com",
        password=None,
        full_name="Dr. Ioana Petrescu",
        specialty="Relationships and Family Systems",
        bio="Works with conflict, separation, communication breakdowns, and emotional boundaries. 10 years of clinical work across couples, individuals, and family-system patterns.",
        consultation_modes=["online", "onsite"],
        city="Brasov",
        status=SpecialistStatus.ACTIVE,
    ),
    DemoSpecialistSpec(
        key="sorin_vasilescu",
        email="sorin.vasilescu@mentalhealthapp.com",
        password=None,
        full_name="Dr. Sorin Vasilescu",
        specialty="Career Stress and Burnout",
        bio="Specialist in exhaustion, perfectionism, and decision fatigue. 8 years of experience helping professionals rebuild healthy structure and emotional bandwidth.",
        consultation_modes=["online"],
        city="Sibiu",
        status=SpecialistStatus.INACTIVE,
    ),
)

SPECIALIST_REVIEWS: dict[str, tuple[ReviewSpec, ...]] = {
    "specialist_test": (
        ReviewSpec("reviewer.one@mentalhealthapp.com", 5, "Very grounded, calm, and easy to talk to. I left each session with a concrete plan."),
        ReviewSpec("reviewer.two@mentalhealthapp.com", 4, "Clear structure and practical advice. Good fit for anxiety and difficult transitions."),
        ReviewSpec("reviewer.three@mentalhealthapp.com", 5, "Supportive without being vague. Helped me stabilise after a difficult breakup."),
    ),
    "elena_ionescu": (
        ReviewSpec("reviewer.one@mentalhealthapp.com", 5, "Excellent for anxiety management. The exercises were practical and not overwhelming."),
        ReviewSpec("reviewer.two@mentalhealthapp.com", 4, "Professional and focused. I appreciated the strong CBT structure."),
        ReviewSpec("reviewer.three@mentalhealthapp.com", 5, "Helped me reduce panic symptoms and get back into daily routines."),
    ),
    "mara_dumitrescu": (
        ReviewSpec("reviewer.one@mentalhealthapp.com", 5, "Very thoughtful and trauma-informed. I felt safe without feeling pushed."),
        ReviewSpec("reviewer.two@mentalhealthapp.com", 5, "Deeply attentive therapist. Strong at helping connect stress reactions to past events."),
        ReviewSpec("reviewer.three@mentalhealthapp.com", 4, "A serious and steady presence. Sessions felt meaningful and well paced."),
    ),
    "radu_marinescu": (
        ReviewSpec("reviewer.one@mentalhealthapp.com", 4, "Careful and realistic approach to depression recovery."),
        ReviewSpec("reviewer.two@mentalhealthapp.com", 4, "Good at setting achievable steps when everything feels heavy."),
        ReviewSpec("reviewer.three@mentalhealthapp.com", 5, "Balanced empathy with practical structure. Very helpful during a low period."),
    ),
    "ioana_petrescu": (
        ReviewSpec("reviewer.one@mentalhealthapp.com", 5, "Strong perspective on relationship patterns and boundaries."),
        ReviewSpec("reviewer.two@mentalhealthapp.com", 4, "Clear communicator. Helped me handle family tension better."),
        ReviewSpec("reviewer.three@mentalhealthapp.com", 5, "Insightful and direct in a good way. Sessions were both warm and useful."),
    ),
}


def main() -> None:
    """Seed deterministic demo accounts, specialists, schedules, and dashboard data."""

    with SessionLocal() as session:
        now = datetime.now(UTC)
        accounts = ensure_demo_accounts(session)
        reviewers = ensure_reviewer_accounts(session)
        specialists = ensure_specialists(session, accounts, now)
        seed_user_profile(session, accounts["UserTest"])
        seed_specialist_schedules(session, specialists, now)
        seed_specialist_reviews(session, specialists, reviewers)
        seed_demo_appointments(session, accounts, specialists, now)
        session.commit()

    print("Demo seed complete.")
    for spec in ACCOUNT_SPECS:
        email = os.getenv(spec.env_email, spec.default_email)
        password = os.getenv(spec.env_password, spec.default_password)
        print(f"- {spec.label}: {email} / {password}")


def ensure_demo_accounts(session: Session) -> dict[str, User]:
    """Create or update the deterministic login accounts used for flow testing."""

    accounts: dict[str, User] = {}
    for spec in ACCOUNT_SPECS:
        email = os.getenv(spec.env_email, spec.default_email)
        password = os.getenv(spec.env_password, spec.default_password)
        user = ensure_user(session, email=email, full_name=spec.full_name, role=spec.role)
        ensure_local_identity(session, user=user, email=email, password=password)
        accounts[spec.label] = user
    return accounts


def ensure_reviewer_accounts(session: Session) -> dict[str, User]:
    """Create deterministic reviewer users used only to support realistic ratings."""

    reviewers: dict[str, User] = {}
    for email, full_name in REVIEWER_SPECS:
        reviewers[email] = ensure_user(
            session,
            email=email,
            full_name=full_name,
            role=UserRole.USER,
        )
    return reviewers


def ensure_specialists(
    session: Session,
    accounts: dict[str, User],
    now: datetime,
) -> dict[str, Specialist]:
    """Create or update the seeded specialist directory entries."""

    specialists: dict[str, Specialist] = {}
    for spec in SPECIALIST_SPECS:
        if spec.key == "specialist_test":
            user = accounts["SpecialistTest"]
            user.full_name = spec.full_name
        else:
            user = ensure_user(
                session,
                email=spec.email,
                full_name=spec.full_name,
                role=UserRole.SPECIALIST,
            )

        specialist = session.scalar(select(Specialist).where(Specialist.user_id == user.id))
        if specialist is None:
            specialist = Specialist(user_id=user.id)
            session.add(specialist)
        specialist.full_name = spec.full_name
        specialist.specialty = spec.specialty
        specialist.bio = spec.bio
        specialist.consultation_modes = spec.consultation_modes
        specialist.city = spec.city
        specialist.status = spec.status
        specialists[spec.key] = specialist

    session.flush()
    return specialists


def seed_user_profile(session: Session, user: User) -> None:
    """Ensure the main demo user has profile data that makes settings look populated."""

    profile = session.get(UserProfile, user.id)
    if profile is None:
        profile = UserProfile(user_id=user.id)
        session.add(profile)
    profile.age_range = "25-34"
    profile.occupation = "Product designer"
    profile.goals = "Reduce anxiety spikes, improve consistency, and rebuild routines after a difficult breakup."
    profile.preferred_activities = ["walking", "journaling", "breathing exercises"]
    profile.timezone = "Europe/Bucharest"


def seed_specialist_schedules(
    session: Session,
    specialists: dict[str, Specialist],
    now: datetime,
) -> None:
    """Replace schedule data for seeded specialists so reruns stay deterministic."""

    specialist_ids = [specialist.id for specialist in specialists.values()]
    session.execute(delete(SpecialistAvailabilityRule).where(SpecialistAvailabilityRule.specialist_id.in_(specialist_ids)))
    session.execute(delete(SpecialistBreak).where(SpecialistBreak.specialist_id.in_(specialist_ids)))
    session.execute(delete(SpecialistTimeOff).where(SpecialistTimeOff.specialist_id.in_(specialist_ids)))

    weekday_rules = [
        AvailabilityRuleSpec(weekday=0, start_time=time(hour=9), end_time=time(hour=17)),
        AvailabilityRuleSpec(weekday=1, start_time=time(hour=9), end_time=time(hour=17)),
        AvailabilityRuleSpec(weekday=2, start_time=time(hour=9), end_time=time(hour=17)),
        AvailabilityRuleSpec(weekday=3, start_time=time(hour=9), end_time=time(hour=17)),
        AvailabilityRuleSpec(weekday=4, start_time=time(hour=9), end_time=time(hour=17)),
    ]
    lunch_break = BreakSpec(weekday=2, start_time=time(hour=13), end_time=time(hour=15), label="Midweek admin break")
    time_off = TimeOffSpec(
        start_datetime=next_weekday_at(now, weekday=4, hour=9),
        end_datetime=next_weekday_at(now, weekday=4, hour=13),
        reason="Conference and supervision block",
    )

    for key, specialist in specialists.items():
        if specialist.status != SpecialistStatus.ACTIVE:
            continue

        for rule in weekday_rules:
            session.add(
                SpecialistAvailabilityRule(
                    specialist_id=specialist.id,
                    weekday=rule.weekday,
                    start_time=rule.start_time,
                    end_time=rule.end_time,
                    is_enabled=rule.is_enabled,
                )
            )

        session.add(
            SpecialistBreak(
                specialist_id=specialist.id,
                weekday=lunch_break.weekday,
                start_time=lunch_break.start_time,
                end_time=lunch_break.end_time,
                label=lunch_break.label,
            )
        )

        if key in {"specialist_test", "mara_dumitrescu"}:
            session.add(
                SpecialistTimeOff(
                    specialist_id=specialist.id,
                    start_datetime=time_off.start_datetime,
                    end_datetime=time_off.end_datetime,
                    reason=time_off.reason,
                )
            )


def seed_specialist_reviews(
    session: Session,
    specialists: dict[str, Specialist],
    reviewers: dict[str, User],
) -> None:
    """Replace reviews for the seeded public specialists to produce stable ratings."""

    specialist_ids = [specialist.id for specialist in specialists.values()]
    session.execute(delete(SpecialistReview).where(SpecialistReview.specialist_id.in_(specialist_ids)))

    for key, review_specs in SPECIALIST_REVIEWS.items():
        specialist = specialists[key]
        for review_spec in review_specs:
            session.add(
                SpecialistReview(
                    specialist_id=specialist.id,
                    user_id=reviewers[review_spec.reviewer_email].id,
                    rating=review_spec.rating,
                    comment=review_spec.comment,
                )
            )


def seed_demo_appointments(
    session: Session,
    accounts: dict[str, User],
    specialists: dict[str, Specialist],
    now: datetime,
) -> dict[str, Appointment]:
    """Create a small deterministic appointment set for user and specialist dashboards."""

    user_test = accounts["UserTest"]
    specialist_test = specialists["specialist_test"]
    elena = specialists["elena_ionescu"]

    session.execute(
        delete(Appointment).where(
            (Appointment.user_id == user_test.id)
            | (Appointment.specialist_id.in_([specialist_test.id, elena.id]))
        )
    )

    requested_start = next_weekday_at(now, weekday=next_business_weekday(now, min_days=1), hour=9)
    confirmed_start = next_weekday_at(now, weekday=next_business_weekday(now, min_days=2), hour=15)
    completed_start = previous_weekday_at(now, weekday=previous_business_weekday(now, min_days=2), hour=9)

    requested = Appointment(
        user_id=user_test.id,
        specialist_id=specialist_test.id,
        mode=AppointmentMode.ONLINE,
        status=AppointmentStatus.REQUESTED,
        preferred_datetime=requested_start,
        end_datetime=requested_start + SLOT_DURATION,
        notes="Recent breakup, insomnia, and strong rumination.",
        status_updated_by_user_id=user_test.id,
    )
    confirmed = Appointment(
        user_id=user_test.id,
        specialist_id=specialist_test.id,
        mode=AppointmentMode.ONLINE,
        status=AppointmentStatus.CONFIRMED,
        preferred_datetime=confirmed_start,
        end_datetime=confirmed_start + SLOT_DURATION,
        notes="Follow-up session focused on grounding routines and emotional regulation.",
        confirmed_at=now,
        status_updated_by_user_id=specialist_test.user_id,
    )
    completed = Appointment(
        user_id=user_test.id,
        specialist_id=elena.id,
        mode=AppointmentMode.ONLINE,
        status=AppointmentStatus.COMPLETED,
        preferred_datetime=completed_start,
        end_datetime=completed_start + SLOT_DURATION,
        notes="Initial assessment and plan for anxiety management.",
        confirmed_at=completed_start - timedelta(days=1),
        completed_at=completed_start + SLOT_DURATION + timedelta(minutes=15),
        status_updated_by_user_id=elena.user_id,
    )

    session.add_all([requested, confirmed, completed])
    session.flush()
    return {
        "requested": requested,
        "confirmed": confirmed,
        "completed": completed,
    }



def ensure_user(session: Session, *, email: str, full_name: str, role: UserRole) -> User:
    """Create or update one deterministic user row by email."""

    user = session.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email, full_name=full_name, role=role, is_active=True)
        session.add(user)
    user.email = email
    user.full_name = full_name
    user.role = role
    user.is_active = True
    session.flush()
    return user


def ensure_local_identity(session: Session, *, user: User, email: str, password: str) -> AuthIdentity:
    """Create or update the local credential row for a deterministic login account."""

    identity = session.scalar(
        select(AuthIdentity).where(
            AuthIdentity.provider == AuthProvider.LOCAL,
            AuthIdentity.email == email,
        )
    )
    if identity is None:
        identity = AuthIdentity(
            user_id=user.id,
            provider=AuthProvider.LOCAL,
            provider_user_id=email,
            email=email,
            is_primary=True,
            password_hash=hash_password(password),
        )
        session.add(identity)
    identity.user_id = user.id
    identity.provider = AuthProvider.LOCAL
    identity.provider_user_id = email
    identity.email = email
    identity.is_primary = True
    identity.password_hash = hash_password(password)
    session.flush()
    return identity


def next_weekday_at(base: datetime, *, weekday: int, hour: int) -> datetime:
    """Return the next UTC datetime at the given weekday and hour."""

    candidate = base.astimezone(UTC).replace(minute=0, second=0, microsecond=0)
    days_ahead = (weekday - candidate.weekday()) % 7
    if days_ahead == 0 and candidate.hour >= hour:
        days_ahead = 7
    candidate = (candidate + timedelta(days=days_ahead)).replace(hour=hour)
    return candidate


def previous_weekday_at(base: datetime, *, weekday: int, hour: int) -> datetime:
    """Return the previous UTC datetime at the given weekday and hour."""

    candidate = base.astimezone(UTC).replace(minute=0, second=0, microsecond=0)
    days_back = (candidate.weekday() - weekday) % 7
    if days_back == 0 and candidate.hour <= hour:
        days_back = 7
    candidate = (candidate - timedelta(days=days_back)).replace(hour=hour)
    return candidate


def next_business_weekday(base: datetime, *, min_days: int) -> int:
    """Return the weekday for the next business day offset."""

    target = base.astimezone(UTC).date() + timedelta(days=min_days)
    while target.weekday() >= 5:
        target += timedelta(days=1)
    return target.weekday()


def previous_business_weekday(base: datetime, *, min_days: int) -> int:
    """Return the weekday for the previous business day offset."""

    target = base.astimezone(UTC).date() - timedelta(days=min_days)
    while target.weekday() >= 5:
        target -= timedelta(days=1)
    return target.weekday()


if __name__ == "__main__":
    main()
