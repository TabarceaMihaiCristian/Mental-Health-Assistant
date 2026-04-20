"""Helpers for masking sensitive identifiers in logs."""

from __future__ import annotations

from uuid import UUID


def mask_uuid(value: UUID | str | None) -> str:
    """Mask the middle of a UUID while preserving the start and end for debugging."""

    if value is None:
        return "none"

    normalized = str(value)
    parts = normalized.split("-")
    if len(parts) == 5:
        return f"{parts[0]}-****-****-****-{parts[4]}"
    if len(normalized) <= 8:
        return normalized
    return f"{normalized[:4]}****{normalized[-4:]}"


def mask_email(email: str | None) -> str:
    """Mask an email address for logs while keeping basic debugging context."""

    if not email:
        return "none"

    local_part, separator, domain = email.partition("@")
    if not separator:
        return f"{email[:2]}***"
    visible_local = local_part[:2] if len(local_part) > 2 else local_part[:1]
    return f"{visible_local}***@{domain}"
