"""Application service for chat session and message persistence."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.db.unit_of_work import UnitOfWork
from app.models.base import utc_now
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.enums import ChatSessionStatus, ReportPeriod, RiskLevel, SenderType
from app.models.user import User
from app.repositories.chat_repository import ChatMessageRepository, ChatSessionRepository
from app.schemas.assistant import ChatInteractionRequest
from app.schemas.chat import ChatMessageCreateRequest, ChatSessionCreateRequest
from app.schemas.suggestion import CriticalAppointmentSuggestionsResponse
from app.services.assistant_service import AssistantService
from app.services.mood_analysis_service import run_best_effort_mood_analysis
from app.services.report_service import ReportService
from app.services.suggestion_service import SuggestionService
from app.utils.logging import get_app_logger, log_event, mask_uuid
from app.utils.validation import ensure_user_sender, normalize_message_content


class ChatSessionNotFoundError(ValueError):
    """Raised when the requested chat session does not exist for the user."""


class ChatSessionClosedError(ValueError):
    """Raised when attempting to add a message to a closed chat session."""


class InvalidChatSenderError(ValueError):
    """Raised when an external request tries to use an unsupported sender type."""


class AssistantInteractionError(RuntimeError):
    """Raised when assistant reply generation fails during a chat interaction."""


class ChatService:
    """Handle chat session lifecycle operations for authenticated users."""

    def __init__(self, db: Session) -> None:
        """Bind chat workflows to one SQLAlchemy session."""

        self.db = db
        self.uow = UnitOfWork(db)
        self.session_repository = ChatSessionRepository(db)
        self.message_repository = ChatMessageRepository(db)
        self.logger = get_app_logger(__name__)

    def create_session(self, user: User, payload: ChatSessionCreateRequest) -> ChatSession:
        """Create a new open chat session owned by the authenticated user."""
        session = ChatSession(
            user_id=user.id,
            summary=payload.summary,
            status=ChatSessionStatus.OPEN,
        )
        self.session_repository.add(session)
        self.uow.commit()
        self.uow.refresh(session)
        log_event(
            self.logger,
            "chat.session.created",
            user_id=mask_uuid(user.id),
            session_id=mask_uuid(session.id),
        )
        return session

    def get_open_session(self, user: User) -> ChatSession | None:
        """Return the current open chat session for the authenticated user, if any."""
        return self.session_repository.get_open_session_for_user(user.id)

    def list_sessions(self, user: User) -> list[ChatSession]:
        """List all chat sessions belonging to the authenticated user."""
        return self.session_repository.list_sessions_for_user(user.id)

    def get_session(self, user: User, session_id: UUID) -> ChatSession:
        """Return one owned chat session or raise when the session is not accessible."""
        session = self.session_repository.get_owned_session(user.id, session_id)
        if session is None:
            raise ChatSessionNotFoundError("Chat session not found.")
        return session

    def close_session(self, user: User, session_id: UUID) -> ChatSession:
        """Mark an owned open chat session as closed and stamp its end time."""
        session = self.get_session(user, session_id)
        if session.status != ChatSessionStatus.OPEN:
            return session
        session.status = ChatSessionStatus.CLOSED
        session.ended_at = utc_now()
        self.session_repository.add(session)
        self.uow.commit()
        self.uow.refresh(session)
        self._sync_reports_after_close(user, session)
        return session

    def archive_session(self, user: User, session_id: UUID) -> ChatSession:
        """Archive an owned chat session and preserve its recorded end time."""
        session = self.get_session(user, session_id)
        session.status = ChatSessionStatus.ARCHIVED
        session.ended_at = session.ended_at or utc_now()
        self.session_repository.add(session)
        self.uow.commit()
        self.uow.refresh(session)
        return session

    def _sync_reports_after_close(self, user: User, session: ChatSession) -> None:
        """Regenerate current period reports after a conversation is explicitly closed."""

        reference_date = (session.ended_at or session.last_message_at or session.started_at).date()
        try:
            report_service = ReportService(self.db)
            report_service.generate_report(user, ReportPeriod.WEEKLY, reference_date)
            report_service.generate_report(user, ReportPeriod.MONTHLY, reference_date)
        except RuntimeError as exc:
            log_event(
                self.logger,
                "chat.session.report_sync_failed",
                user_id=mask_uuid(user.id),
                session_id=mask_uuid(session.id),
                reason=str(exc),
            )

    def add_message(
        self,
        user: User,
        session_id: UUID,
        payload: ChatMessageCreateRequest,
    ) -> ChatMessage:
        """Persist a user-authored message into an open owned chat session."""
        try:
            ensure_user_sender(payload.sender)
        except ValueError as exc:
            raise InvalidChatSenderError(str(exc)) from exc

        session = self.get_session(user, session_id)
        if session.status != ChatSessionStatus.OPEN:
            raise ChatSessionClosedError("Cannot add messages to a closed chat session.")

        message = ChatMessage(
            session_id=session.id,
            sender=payload.sender,
            content=normalize_message_content(payload.content),
        )
        session.last_message_at = utc_now()

        self.message_repository.add(message)
        self.session_repository.add(session)
        self.uow.commit()
        self.uow.refresh(message)
        log_event(
            self.logger,
            "chat.message.added",
            user_id=mask_uuid(user.id),
            session_id=mask_uuid(session.id),
            message_id=mask_uuid(message.id),
            sender=message.sender.value,
        )
        return message

    def create_interaction(
        self,
        user: User,
        session_id: UUID,
        payload: ChatInteractionRequest,
    ) -> tuple[
        ChatMessage,
        ChatMessage,
        ChatSession,
        CriticalAppointmentSuggestionsResponse | None,
    ]:
        """Store a user message, generate an assistant reply, and return both messages."""
        session = self.get_session(user, session_id)
        if session.status != ChatSessionStatus.OPEN:
            raise ChatSessionClosedError("Cannot add messages to a closed chat session.")

        user_message = ChatMessage(
            session_id=session.id,
            sender=SenderType.USER,
            content=normalize_message_content(payload.content),
        )
        session.messages.append(user_message)
        session.last_message_at = utc_now()

        try:
            assistant_reply = AssistantService().generate_reply(user, session)
        except RuntimeError as exc:
            self.uow.rollback()
            log_event(
                self.logger,
                "chat.interaction.assistant_failed",
                user_id=mask_uuid(user.id),
                session_id=mask_uuid(session.id),
                detail=str(exc),
            )
            raise AssistantInteractionError(str(exc)) from exc

        assistant_message = ChatMessage(
            session_id=session.id,
            sender=SenderType.ASSISTANT,
            content=assistant_reply,
        )
        session.last_message_at = utc_now()

        self.message_repository.add(user_message)
        self.message_repository.add(assistant_message)
        self.session_repository.add(session)
        self.uow.commit()
        self.uow.refresh(assistant_message)
        self.uow.refresh(user_message)
        self.uow.refresh(session)
        analysis = run_best_effort_mood_analysis(self.db, user, session, user_message)
        appointment_suggestions = None
        if analysis is not None and analysis.risk == RiskLevel.CRITICAL:
            appointment_suggestions = SuggestionService(
                self.db
            ).get_critical_appointment_suggestions(
                user,
                require_recent_critical_alert=False,
            )
        self.uow.refresh(session)
        log_event(
            self.logger,
            "chat.interaction.created",
            user_id=mask_uuid(user.id),
            session_id=mask_uuid(session.id),
            user_message_id=mask_uuid(user_message.id),
            assistant_message_id=mask_uuid(assistant_message.id),
            has_appointment_suggestions=appointment_suggestions is not None,
        )

        return user_message, assistant_message, session, appointment_suggestions
