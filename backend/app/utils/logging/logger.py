"""Centralized logger construction and event formatting."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from uuid import UUID

from app.utils.logging.masking import mask_email, mask_uuid
from app.utils.logging.request_context import get_request_id


LOGGER_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def get_app_logger(name: str) -> logging.Logger:
    """Return a configured logger for the application."""

    logger = logging.getLogger(name)
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format=LOGGER_FORMAT)
    return logger


def log_event(logger: logging.Logger, event: str, **context: object) -> None:
    """Log a compact structured event with flattened key/value context."""

    enriched_context = _attach_request_id(context)
    serialized_context = _serialize_context(enriched_context)
    message = event if not serialized_context else f"{event} | {serialized_context}"
    logger.info(message)


def _attach_request_id(context: Mapping[str, object]) -> dict[str, object]:
    """Attach the active request identifier unless the caller already set one."""

    request_id = get_request_id()
    if request_id is None or "request_id" in context:
        return dict(context)

    return {"request_id": request_id, **context}


def _serialize_context(context: Mapping[str, object]) -> str:
    """Serialize context fields into a compact log fragment."""

    return " ".join(f"{key}={_sanitize_value(key, value)}" for key, value in context.items())


def _sanitize_value(key: str, value: object) -> object:
    """Mask sensitive identifiers consistently before logging."""

    if value is None:
        return value

    lowered_key = key.lower()
    if lowered_key.endswith("email") or lowered_key == "email":
        return mask_email(str(value))

    if isinstance(value, UUID):
        return mask_uuid(value)

    if lowered_key.endswith("_id") or lowered_key == "id":
        return mask_uuid(str(value))

    return value
