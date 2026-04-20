"""Per-request logging context helpers."""

from __future__ import annotations

from contextvars import ContextVar, Token
from uuid import uuid4


_request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)


def generate_request_id() -> str:
    """Generate a new request identifier for correlation and tracing."""

    return uuid4().hex


def get_request_id() -> str | None:
    """Return the active request identifier from the current context."""

    return _request_id_context.get()


def set_request_id(request_id: str) -> Token[str | None]:
    """Store a request identifier in the current execution context."""

    return _request_id_context.set(request_id)


def reset_request_id(token: Token[str | None]) -> None:
    """Restore the previous request identifier after request completion."""

    _request_id_context.reset(token)
