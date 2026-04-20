"""Validation helpers for chat-related input."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.models.enums import AppointmentStatus
from app.models.enums import SenderType


def normalize_message_content(content: str) -> str:
    """Trim and validate free-form chat content."""

    normalized = content.strip()
    if not normalized:
        raise ValueError("Message content cannot be blank.")
    return normalized


def ensure_user_sender(sender: SenderType) -> None:
    """Ensure a public chat request only uses the user sender type."""

    if sender != SenderType.USER:
        raise ValueError("Only user-authored messages are accepted.")


def normalize_optional_comment(comment: str | None) -> str | None:
    """Trim optional free-form comments and collapse blanks to None."""

    if comment is None:
        return None
    normalized = comment.strip()
    return normalized or None


def normalize_future_datetime(value: datetime) -> datetime:
    """Ensure a datetime is timezone-aware and in the future."""

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Appointment datetime must include timezone information.")
    normalized = value.astimezone(UTC)
    if normalized <= datetime.now(UTC):
        raise ValueError("Appointment datetime must be in the future.")
    return normalized


def ensure_minimum_appointment_notice(value: datetime, minimum_hours: int) -> None:
    """Ensure an appointment is scheduled with enough advance notice."""

    minimum_allowed = datetime.now(UTC) + timedelta(hours=minimum_hours)
    if value < minimum_allowed:
        raise ValueError(
            f"Appointments must be scheduled at least {minimum_hours} hours in advance."
        )


def ensure_appointment_mutable(status: AppointmentStatus) -> None:
    """Ensure an appointment can still be canceled or rescheduled."""

    if status not in {AppointmentStatus.REQUESTED, AppointmentStatus.CONFIRMED}:
        raise ValueError("Only requested or confirmed appointments can be modified.")


def ensure_appointment_cancellation_allowed(
    status: AppointmentStatus,
    start_datetime: datetime,
    cutoff_hours: int,
) -> None:
    """Ensure an appointment can still be cancelled before the configured cutoff."""

    ensure_appointment_mutable(status)
    cancellation_deadline = start_datetime - timedelta(hours=cutoff_hours)
    if datetime.now(UTC) >= cancellation_deadline:
        raise ValueError(
            f"Appointments can only be cancelled at least {cutoff_hours} hours before they start."
        )


def ensure_appointment_reschedule_allowed(
    status: AppointmentStatus,
    start_datetime: datetime,
    cutoff_hours: int,
) -> None:
    """Ensure an appointment can still be rescheduled before the configured cutoff."""

    ensure_appointment_mutable(status)
    reschedule_deadline = start_datetime - timedelta(hours=cutoff_hours)
    if datetime.now(UTC) >= reschedule_deadline:
        raise ValueError(
            f"Appointments can only be rescheduled at least {cutoff_hours} hours before they start."
        )


def ensure_specialist_decision_allowed(
    status: AppointmentStatus,
    start_datetime: datetime,
) -> None:
    """Ensure a specialist can still confirm or reject a pending appointment."""

    if status != AppointmentStatus.REQUESTED:
        raise ValueError("Only requested appointments can be updated by the specialist.")
    if datetime.now(UTC) >= start_datetime:
        raise ValueError("Appointments cannot be confirmed or rejected after they start.")


def ensure_appointment_completion_allowed(
    status: AppointmentStatus,
    end_datetime: datetime,
) -> None:
    """Ensure an appointment can only be completed after its scheduled end time."""

    if status != AppointmentStatus.CONFIRMED:
        raise ValueError("Only confirmed appointments can be completed.")
    if datetime.now(UTC) < end_datetime:
        raise ValueError("Appointments can only be completed after they end.")
