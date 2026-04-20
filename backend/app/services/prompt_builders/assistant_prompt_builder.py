"""Build OpenAI-ready messages for the mental health assistant."""

from __future__ import annotations

from typing import Literal

from openai.types.responses.easy_input_message_param import EasyInputMessageParam

from app.core.config import settings
from app.models.chat_session import ChatSession
from app.models.enums import SenderType
from app.models.user import User


class AssistantPromptBuilder:
    """Assemble system instructions and chat context for assistant replies."""

    def build_messages(self, user: User, session: ChatSession) -> list[EasyInputMessageParam]:
        """Build the message sequence sent to the OpenAI Responses API."""

        messages: list[EasyInputMessageParam] = [
            {
                "role": "system",
                "content": self._build_system_prompt(),
                "type": "message",
            }
        ]

        user_context = self._build_user_context(user)
        if user_context:
            messages.append(
                {
                    "role": "system",
                    "content": user_context,
                    "type": "message",
                }
            )

        recent_messages = session.messages[-settings.assistant_max_context_messages :]
        for message in recent_messages:
            role = self._map_sender_to_role(message.sender)
            messages.append(
                {
                    "role": role,
                    "content": message.content,
                    "type": "message",
                }
            )

        return messages

    def _build_system_prompt(self) -> str:
        """Return the assistant's stable behavioral and safety instructions."""

        return (
            "You are a supportive mental wellness assistant. "
            "Be calm, empathetic, warm, and natural. "
            "You are not a doctor, psychologist, or psychiatrist and must "
            "not diagnose medical or psychiatric conditions. "
            "Do not claim certainty about a user's mental health state. "
            "Respond like a thoughtful human supporter, not like a checklist or triage bot. "
            "Respond primarily to the latest user message. "
            "If the latest message differs in tone from earlier conversation "
            "context, prioritize the latest message. "
            "Keep replies short but complete: no more than 4 sentences, "
            "usually 2 short paragraphs, "
            "and avoid bullet lists unless the user explicitly asks for options. "
            "Ask at most one follow-up question, and only if it genuinely "
            "helps the conversation move forward. "
            "Do not abruptly ask direct self-harm or suicide-screening "
            "questions just because the user sounds sad, low, "
            "stressed, or overwhelmed. "
            "Only move into direct safety-check language if the user clearly "
            "mentions wanting to die, self-harm, suicide, "
            "or immediate danger. "
            "When the user sounds low or emotionally tired, first respond with "
            "gentle validation, emotional presence, and one small grounding or "
            "supportive next step if appropriate. "
            "Avoid sounding clinical, scripted, alarmist, or overly formal. "
            "End with a complete sentence."
        )

    def _build_user_context(self, user: User) -> str:
        """Build a compact personalization summary from the user's profile."""

        profile = user.profile
        if profile is None:
            return ""

        parts: list[str] = []
        if profile.occupation:
            parts.append(f"Occupation: {profile.occupation}.")
        if profile.goals:
            parts.append(f"Goals: {profile.goals}.")
        if profile.preferred_activities:
            activities = ", ".join(profile.preferred_activities)
            parts.append(f"Preferred calming activities: {activities}.")

        return " ".join(parts)

    def _map_sender_to_role(
        self, sender: SenderType
    ) -> Literal["user", "assistant", "system", "developer"]:
        """Translate internal sender types to OpenAI message roles."""

        if sender == SenderType.ASSISTANT:
            return "assistant"
        return "user"
