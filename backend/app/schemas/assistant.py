"""Pydantic schemas for assistant-driven chat interactions."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.chat import ChatMessageResponse, ChatSessionResponse
from app.schemas.suggestion import CriticalAppointmentSuggestionsResponse


class ChatInteractionRequest(BaseModel):
    """Payload used to create a user message and request an assistant reply."""

    content: str = Field(min_length=1, max_length=5000)


class ChatInteractionResponse(BaseModel):
    """Response containing both sides of an assistant interaction."""

    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse
    session: ChatSessionResponse
    appointment_suggestions: CriticalAppointmentSuggestionsResponse | None = None
