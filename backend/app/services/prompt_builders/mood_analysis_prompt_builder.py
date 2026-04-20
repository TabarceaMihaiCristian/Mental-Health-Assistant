"""Build prompts for structured mood analysis."""

from __future__ import annotations

from openai.types.responses.easy_input_message_param import EasyInputMessageParam

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.user import User


class MoodAnalysisPromptBuilder:
    """Assemble strict analysis prompts for structured mood extraction."""

    def build_messages(
        self,
        user: User,
        session: ChatSession,
        user_message: ChatMessage,
    ) -> list[EasyInputMessageParam]:
        """Build the message sequence sent to the OpenAI Responses API."""

        messages: list[EasyInputMessageParam] = [
            {
                "role": "system",
                "type": "message",
                "content": self._build_system_prompt(),
            }
        ]

        user_context = self._build_user_context(user)
        if user_context:
            messages.append(
                {
                    "role": "system",
                    "type": "message",
                    "content": user_context,
                }
            )

        recent_messages = session.messages[-6:]
        transcript_lines: list[str] = []
        for message in recent_messages:
            speaker = "assistant" if message.sender.value == "assistant" else "user"
            transcript_lines.append(f"{speaker}: {message.content}")

        messages.append(
            {
                "role": "user",
                "type": "message",
                "content": (
                    "Analyze the user's emotional state from the "
                    "latest user message, using the recent "
                    "conversation only as supporting context.\n\n"
                    f"Latest user message:\n{user_message.content}\n\n"
                    "Recent conversation context:\n"
                    + "\n".join(transcript_lines)
                ),
            }
        )

        return messages

    def _build_system_prompt(self) -> str:
        """Return strict instructions for structured emotion analysis."""

        return (
            "You are an emotion-analysis component for a mental wellness application. "
            "You are not writing a conversational reply. "
            "Infer cautiously from the user's own words. "
            "Do not overstate risk or certainty. "
            "Only classify risk as high or critical when the user's language clearly indicates "
            "serious danger, "
            "self-harm intent, suicidal intent, or immediate safety concerns. "
            "Possible triggers should be short phrases, not sentences. "
            "Return only a compact JSON object with these keys: "
            "primary_mood, secondary_mood, intensity, confidence, risk, possible_triggers."
        )

    def _build_user_context(self, user: User) -> str:
        """Return compact optional profile context for analysis."""

        profile = user.profile
        if profile is None:
            return ""

        parts: list[str] = []
        if profile.occupation:
            parts.append(f"Occupation: {profile.occupation}.")
        if profile.goals:
            parts.append(f"Stated goals: {profile.goals}.")
        return " ".join(parts)
