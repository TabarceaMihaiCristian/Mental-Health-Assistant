"""Validation helpers for authentication and account-related input."""

from __future__ import annotations


def normalize_email(email: str) -> str:
    """Normalize an email address for lookup and storage."""

    return email.strip().lower()


def normalize_full_name(full_name: str) -> str:
    """Normalize a full name while preserving internal spacing."""

    return " ".join(full_name.strip().split())
