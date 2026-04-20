"""Shared OpenAI client construction helpers."""

from __future__ import annotations

from openai import OpenAI

from app.core.config import settings


class OpenAIConfigurationError(RuntimeError):
    """Raised when OpenAI-backed features are used without configuration."""


def build_openai_client() -> OpenAI:
    """Build a configured OpenAI client or raise a configuration error."""

    if not settings.openai_api_key:
        raise OpenAIConfigurationError("OPENAI_API_KEY is not configured.")
    return OpenAI(api_key=settings.openai_api_key)
