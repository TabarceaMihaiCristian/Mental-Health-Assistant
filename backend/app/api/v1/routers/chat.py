"""Chat session and message API endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.assistant import ChatInteractionRequest, ChatInteractionResponse
from app.schemas.chat import (
    ChatMessageCreateRequest,
    ChatMessageResponse,
    ChatSessionCreateRequest,
    ChatSessionDetailResponse,
    ChatSessionResponse,
    ChatSessionStatusUpdateResponse,
)
from app.services.chat_service import (
    AssistantInteractionError,
    ChatService,
    ChatSessionClosedError,
    ChatSessionNotFoundError,
    InvalidChatSenderError,
)


router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
def create_chat_session(
    payload: ChatSessionCreateRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> ChatSessionResponse:
    """Create a new chat session for the authenticated user."""
    service = ChatService(db)
    session = service.create_session(current_user, payload)
    return ChatSessionResponse.model_validate(session)


@router.get("/sessions")
def list_chat_sessions(current_user: CurrentUser, db: DbSession) -> list[ChatSessionResponse]:
    """List all chat sessions owned by the authenticated user."""
    service = ChatService(db)
    sessions = service.list_sessions(current_user)
    return [ChatSessionResponse.model_validate(session) for session in sessions]


@router.get("/sessions/open")
def get_open_chat_session(current_user: CurrentUser, db: DbSession) -> ChatSessionResponse | None:
    """Return the current open chat session for the authenticated user, if one exists."""
    service = ChatService(db)
    session = service.get_open_session(current_user)
    if session is None:
        return None
    return ChatSessionResponse.model_validate(session)


@router.get("/sessions/{session_id}")
def get_chat_session(
    session_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> ChatSessionDetailResponse:
    """Return one owned chat session by identifier."""
    service = ChatService(db)
    try:
        session = service.get_session(current_user, session_id)
    except ChatSessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return ChatSessionDetailResponse.model_validate(session)


@router.patch("/sessions/{session_id}/close")
def close_chat_session(
    session_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> ChatSessionStatusUpdateResponse:
    """Close an owned open chat session."""
    service = ChatService(db)
    try:
        session = service.close_session(current_user, session_id)
    except ChatSessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ChatSessionStatusUpdateResponse(session=ChatSessionResponse.model_validate(session))


@router.patch("/sessions/{session_id}/archive")
def archive_chat_session(
    session_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> ChatSessionStatusUpdateResponse:
    """Archive an owned chat session."""
    service = ChatService(db)
    try:
        session = service.archive_session(current_user, session_id)
    except ChatSessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ChatSessionStatusUpdateResponse(session=ChatSessionResponse.model_validate(session))


@router.post(
    "/sessions/{session_id}/messages",
    status_code=status.HTTP_201_CREATED,
)
def add_chat_message(
    session_id: UUID,
    payload: ChatMessageCreateRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> ChatMessageResponse:
    """Persist a direct user message into an open chat session."""
    service = ChatService(db)
    try:
        message = service.add_message(current_user, session_id, payload)
    except ChatSessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ChatSessionClosedError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except InvalidChatSenderError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ChatMessageResponse.model_validate(message)


@router.post("/sessions/{session_id}/interactions", status_code=status.HTTP_201_CREATED)
def create_chat_interaction(
    session_id: UUID,
    payload: ChatInteractionRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> ChatInteractionResponse:
    """Create a user-assistant interaction inside an open chat session."""
    service = ChatService(db)
    try:
        (
            user_message,
            assistant_message,
            session,
            appointment_suggestions,
        ) = service.create_interaction(
            current_user,
            session_id,
            payload,
        )
    except ChatSessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ChatSessionClosedError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except AssistantInteractionError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return ChatInteractionResponse(
        user_message=ChatMessageResponse.model_validate(user_message),
        assistant_message=ChatMessageResponse.model_validate(assistant_message),
        session=ChatSessionResponse.model_validate(session),
        appointment_suggestions=appointment_suggestions,
    )
