"""Pydantic schemas for chat sessions and chat messages."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ChatSessionStatus, SenderType


class ChatSessionCreateRequest(BaseModel):
    """Payload used to create a new chat session."""

    summary: str | None = Field(default=None, max_length=1000)


class ChatMessageCreateRequest(BaseModel):
    """Payload used to append a user message to a chat session."""

    content: str = Field(min_length=1, max_length=5000)
    sender: SenderType = SenderType.USER


class ChatMessageResponse(BaseModel):
    """Serialized chat message returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    sender: SenderType
    content: str
    created_at: datetime


class ChatSessionResponse(BaseModel):
    """Serialized chat session returned by session list endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    status: ChatSessionStatus
    started_at: datetime
    last_message_at: datetime
    ended_at: datetime | None
    summary: str | None
    created_at: datetime
    updated_at: datetime


class ChatSessionDetailResponse(ChatSessionResponse):
    """Detailed chat session response that includes the message history."""

    messages: list[ChatMessageResponse] = Field(default_factory=list)
