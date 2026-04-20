"""Validation and normalization helpers shared across the application."""

from app.utils.validation.auth_validation import normalize_email, normalize_full_name
from app.utils.validation.chat_validation import (
    ensure_appointment_cancellation_allowed,
    ensure_appointment_completion_allowed,
    ensure_appointment_mutable,
    ensure_appointment_reschedule_allowed,
    ensure_minimum_appointment_notice,
    ensure_specialist_decision_allowed,
    ensure_user_sender,
    normalize_message_content,
    normalize_future_datetime,
    normalize_optional_comment,
)

__all__ = [
    "ensure_appointment_mutable",
    "ensure_appointment_cancellation_allowed",
    "ensure_appointment_completion_allowed",
    "ensure_appointment_reschedule_allowed",
    "ensure_minimum_appointment_notice",
    "ensure_specialist_decision_allowed",
    "ensure_user_sender",
    "normalize_future_datetime",
    "normalize_email",
    "normalize_full_name",
    "normalize_message_content",
    "normalize_optional_comment",
]
