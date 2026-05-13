"""Generate assistant replies using the OpenAI Responses API."""

from __future__ import annotations

from typing import Any, cast

from openai.types.responses.response_input_param import ResponseInputParam

from app.core.config import settings
from app.models.chat_session import ChatSession
from app.models.user import User
from app.services.openai_client import OpenAIConfigurationError, build_openai_client
from app.services.prompt_builders.assistant_prompt_builder import AssistantPromptBuilder


CRISIS_MARKERS = (
    "kill myself",
    "want to die",
    "end my life",
    "suicide",
    "suicidal",
    "self harm",
    "self-harm",
    "don't want to live",
)


class AssistantConfigurationError(RuntimeError):
    """Raised when assistant generation is attempted without required configuration."""


class AssistantGenerationError(RuntimeError):
    """Raised when the OpenAI API does not return usable assistant output."""


class AssistantService:
    """Handle assistant reply generation for chat interactions."""

    def __init__(self) -> None:
        """Create the OpenAI client and prompt builder for assistant replies."""

        try:
            self.client = build_openai_client()
        except OpenAIConfigurationError as exc:
            raise AssistantConfigurationError(str(exc)) from exc
        self.prompt_builder = AssistantPromptBuilder()

    def generate_reply(self, user: User, session: ChatSession) -> str:
        """Generate a text reply for the latest session context."""

        prompt_messages = cast(ResponseInputParam,
                                self.prompt_builder.build_messages(user, session))
        response = self.client.responses.create(
            model=settings.openai_model,
            input=prompt_messages,
            max_output_tokens=settings.openai_max_output_tokens,
        )

        reply = self._extract_response_text(response)
        if not reply:
            latest_user_message = self._get_latest_user_message(session)
            reply = self._build_fallback_reply(latest_user_message)

        return reply

    def _extract_response_text(self, response: Any) -> str:
        """Extract usable assistant text from the OpenAI response object."""

        output_text = (getattr(response, "output_text", "") or "").strip()
        if output_text:
            return output_text

        collected_parts: list[str] = []
        for item in getattr(response, "output", []) or []:
            for content_item in getattr(item, "content", []) or []:
                text_value = getattr(content_item, "text", None)
                if isinstance(text_value, str) and text_value.strip():
                    collected_parts.append(text_value.strip())

        return "\n".join(collected_parts).strip()

    def _build_fallback_reply(self, latest_user_message: str) -> str:
        """Return a safe fallback reply when the model response is empty."""

        lower_message = latest_user_message.lower()
        if any(marker in lower_message for marker in CRISIS_MARKERS):
            return (
                "I'm really glad you said that out loud. If you might act on these thoughts or you feel unsafe, "
                "call emergency services now or go to the nearest emergency department. If you can, contact a trusted "
                "person and stay with them while you get immediate human support."
            )

        positive_markers = (
            "good",
            "great",
            "happy",
            "better",
            "proud",
            "excited",
            "calm",
            "thankful",
        )
        if any(marker in lower_message for marker in positive_markers):
            return (
                "That sounds like a meaningful positive moment. "
                "It's good to notice the habits and choices that are helping you feel better today."
            )

        return (
            "I'm here with you. Thank you for sharing that. "
            "If you want, tell me a bit more about what this has felt like for you today."
        )

    def _get_latest_user_message(self, session: ChatSession) -> str:
        """Return the latest user-authored message content from the session context."""

        for message in reversed(session.messages):
            if message.sender.value == "user":
                return message.content
        return ""
