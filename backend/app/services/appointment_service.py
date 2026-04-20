"""Application service for appointment booking and lifecycle changes."""

from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.unit_of_work import UnitOfWork
from app.models.appointment import Appointment
from app.models.enums import AppointmentActorRole, AppointmentStatus, NotificationType
from app.models.specialist import Specialist
from app.models.user import User
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.auth_repository import UserRepository
from app.repositories.specialist_repository import SpecialistRepository
from app.schemas.appointment import (
    AppointmentCancellationRequest,
    AppointmentCreateRequest,
    AppointmentRejectionRequest,
    AppointmentRescheduleRequest,
    SpecialistAppointmentCreateRequest,
)
from app.services.availability_service import AvailabilityService, SLOT_DURATION
from app.services.notification_service import NotificationService
from app.utils.logging import get_app_logger, log_event
from app.utils.validation import (
    ensure_appointment_cancellation_allowed,
    ensure_appointment_completion_allowed,
    ensure_appointment_reschedule_allowed,
    ensure_minimum_appointment_notice,
    ensure_specialist_decision_allowed,
    normalize_future_datetime,
    normalize_optional_comment,
)


class AppointmentNotFoundError(ValueError):
    """Raised when the requested appointment does not belong to the current user."""


class AppointmentStateError(ValueError):
    """Raised when an appointment is not in a mutable state."""


class AppointmentCancellationNotAllowedError(AppointmentStateError):
    """Raised when an appointment can no longer be cancelled."""


class AppointmentRescheduleNotAllowedError(AppointmentStateError):
    """Raised when an appointment can no longer be rescheduled."""


class AppointmentDecisionNotAllowedError(AppointmentStateError):
    """Raised when a specialist can no longer confirm or reject an appointment."""


class AppointmentCompletionNotAllowedError(AppointmentStateError):
    """Raised when an appointment cannot yet be completed."""


class InvalidAppointmentDateError(ValueError):
    """Raised when an appointment datetime is invalid."""


class SpecialistUnavailableError(ValueError):
    """Raised when an appointment references a missing or inactive specialist."""


class AppointmentSlotUnavailableError(ValueError):
    """Raised when the requested appointment slot is not currently bookable."""


class SpecialistProfileNotFoundError(ValueError):
    """Raised when a specialist user has no linked specialist profile."""


class AppointmentUserNotFoundError(ValueError):
    """Raised when a specialist-created appointment references a missing user."""


SLOT_UNAVAILABLE_MESSAGE = "The requested appointment slot is not available."
APPOINTMENT_NOT_FOUND_MESSAGE = "Appointment not found."
APPOINTMENT_OVERLAP_CONSTRAINT_NAME = "appointments_no_active_overlap"


class AppointmentService:
    """Manage appointment booking, retrieval, cancelation, and rescheduling."""

    def __init__(self, db: Session) -> None:
        """Bind appointment workflows to one SQLAlchemy session."""

        self.db = db
        self.uow = UnitOfWork(db)
        self.repository = AppointmentRepository(db)
        self.user_repository = UserRepository(db)
        self.specialist_repository = SpecialistRepository(db)
        self.availability_service = AvailabilityService(db)
        self.notification_service = NotificationService(db)
        self.logger = get_app_logger(__name__)

    def create_appointment(self, user: User, payload: AppointmentCreateRequest) -> Appointment:
        """Create a new appointment request for an active specialist."""

        appointment = self._create_appointment_record(
            user_id=user.id,
            specialist_id=payload.specialist_id,
            mode=payload.mode,
            preferred_datetime=payload.preferred_datetime,
            notes=payload.notes,
            created_by_user_id=user.id,
            initial_status=AppointmentStatus.REQUESTED,
        )
        self._notify_specialist_for_request(appointment)
        log_event(
            self.logger,
            "appointments.created",
            user_id=user.id,
            specialist_id=appointment.specialist_id,
            appointment_id=appointment.id,
            status=appointment.status.value,
            preferred_datetime=appointment.preferred_datetime.isoformat(),
            end_datetime=appointment.end_datetime.isoformat(),
        )
        return appointment

    def create_specialist_appointment(
        self,
        current_user: User,
        payload: SpecialistAppointmentCreateRequest,
    ) -> Appointment:
        """Create a confirmed appointment on behalf of a specialist for a user."""

        specialist = self._get_specialist_profile(current_user)
        target_user = self.user_repository.get_by_id(payload.user_id)
        if target_user is None or not target_user.is_active:
            raise AppointmentUserNotFoundError("Target user not found.")

        appointment = self._create_appointment_record(
            user_id=target_user.id,
            specialist_id=specialist.id,
            mode=payload.mode,
            preferred_datetime=payload.preferred_datetime,
            notes=payload.notes,
            created_by_user_id=current_user.id,
            initial_status=AppointmentStatus.CONFIRMED,
        )
        self._notify_user(
            appointment,
            NotificationType.APPOINTMENT_CONFIRMED,
            "Appointment booked for you",
            self._build_notification_message(
                "A specialist booked an appointment for you",
                appointment,
            ),
        )
        log_event(
            self.logger,
            "specialist.appointments.created",
            user_id=current_user.id,
            specialist_id=appointment.specialist_id,
            appointment_id=appointment.id,
            target_user_id=target_user.id,
            status=appointment.status.value,
            preferred_datetime=appointment.preferred_datetime.isoformat(),
            end_datetime=appointment.end_datetime.isoformat(),
        )
        return appointment

    def list_appointments(self, user: User) -> list[Appointment]:
        """Return appointments owned by the authenticated user."""

        return self.repository.list_for_user(user.id)

    def get_appointment(self, user: User, appointment_id: UUID) -> Appointment:
        """Return one owned appointment or raise if it does not exist."""

        appointment = self.repository.get_owned_appointment(user.id, appointment_id)
        if appointment is None:
            raise AppointmentNotFoundError(APPOINTMENT_NOT_FOUND_MESSAGE)
        return appointment

    def cancel_appointment(
        self,
        user: User,
        appointment_id: UUID,
        payload: AppointmentCancellationRequest | None = None,
    ) -> Appointment:
        """Cancel an owned appointment if it is still mutable."""

        appointment = self.get_appointment(user, appointment_id)
        try:
            ensure_appointment_cancellation_allowed(
                appointment.status,
                appointment.preferred_datetime,
                settings.appointment_cancellation_cutoff_hours,
            )
        except ValueError as exc:
            raise AppointmentCancellationNotAllowedError(str(exc)) from exc

        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancellation_reason = normalize_optional_comment(
            None if payload is None else payload.reason
        )
        appointment.cancelled_at = datetime.now(UTC)
        appointment.status_updated_by_user_id = user.id
        self.uow.commit()
        self.uow.refresh(appointment)
        self._notify_specialist(
            appointment,
            NotificationType.APPOINTMENT_CANCELLED,
            "Appointment cancelled",
            self._build_notification_message(
                "A user cancelled the appointment",
                appointment,
            ),
        )
        log_event(
            self.logger,
            "appointments.cancelled",
            user_id=user.id,
            specialist_id=appointment.specialist_id,
            appointment_id=appointment.id,
            status=appointment.status.value,
        )
        return appointment

    def list_specialist_appointments(self, current_user: User) -> list[Appointment]:
        """Return appointments assigned to the authenticated specialist."""

        specialist = self._get_specialist_profile(current_user)
        return self.repository.list_for_specialist(specialist.id)

    def get_specialist_appointment(self, current_user: User, appointment_id: UUID) -> Appointment:
        """Return one appointment assigned to the authenticated specialist."""

        specialist = self._get_specialist_profile(current_user)
        appointment = self.repository.get_for_specialist(specialist.id, appointment_id)
        if appointment is None:
            raise AppointmentNotFoundError(APPOINTMENT_NOT_FOUND_MESSAGE)
        return appointment

    def confirm_specialist_appointment(
        self,
        current_user: User,
        appointment_id: UUID,
    ) -> Appointment:
        """Confirm a requested appointment on behalf of the specialist."""

        appointment = self.get_specialist_appointment(current_user, appointment_id)
        try:
            ensure_specialist_decision_allowed(
                appointment.status,
                appointment.preferred_datetime,
            )
        except ValueError as exc:
            raise AppointmentDecisionNotAllowedError(str(exc)) from exc

        appointment.status = AppointmentStatus.CONFIRMED
        appointment.confirmed_at = datetime.now(UTC)
        appointment.status_updated_by_user_id = current_user.id
        self.uow.commit()
        self.uow.refresh(appointment)
        self._notify_user(
            appointment,
            NotificationType.APPOINTMENT_CONFIRMED,
            "Appointment confirmed",
            self._build_notification_message(
                "Your specialist confirmed the appointment",
                appointment,
            ),
        )
        self._log_specialist_transition(
            "specialist.appointments.confirmed",
            current_user,
            appointment,
        )
        return appointment

    def reject_specialist_appointment(
        self,
        current_user: User,
        appointment_id: UUID,
        payload: AppointmentRejectionRequest | None = None,
    ) -> Appointment:
        """Reject a requested appointment on behalf of the specialist."""

        appointment = self.get_specialist_appointment(current_user, appointment_id)
        try:
            ensure_specialist_decision_allowed(
                appointment.status,
                appointment.preferred_datetime,
            )
        except ValueError as exc:
            raise AppointmentDecisionNotAllowedError(str(exc)) from exc

        appointment.status = AppointmentStatus.REJECTED
        appointment.rejection_reason = normalize_optional_comment(
            None if payload is None else payload.reason
        )
        appointment.rejected_at = datetime.now(UTC)
        appointment.status_updated_by_user_id = current_user.id
        self.uow.commit()
        self.uow.refresh(appointment)
        self._notify_user(
            appointment,
            NotificationType.APPOINTMENT_REJECTED,
            "Appointment rejected",
            self._build_notification_message(
                "Your specialist rejected the appointment request",
                appointment,
            ),
        )
        self._log_specialist_transition(
            "specialist.appointments.rejected",
            current_user,
            appointment,
        )
        return appointment

    def reschedule_specialist_appointment(
        self,
        current_user: User,
        appointment_id: UUID,
        payload: AppointmentRescheduleRequest,
    ) -> Appointment:
        """Reschedule a specialist-owned appointment and move it back to requested state."""

        appointment = self.get_specialist_appointment(current_user, appointment_id)
        try:
            ensure_appointment_reschedule_allowed(
                appointment.status,
                appointment.preferred_datetime,
                settings.appointment_reschedule_cutoff_hours,
            )
        except ValueError as exc:
            raise AppointmentRescheduleNotAllowedError(str(exc)) from exc

        try:
            preferred_datetime = normalize_future_datetime(payload.preferred_datetime)
        except ValueError as exc:
            raise InvalidAppointmentDateError(str(exc)) from exc

        if not self.availability_service.is_bookable_slot(
            appointment.specialist_id,
            preferred_datetime,
        ):
            raise AppointmentSlotUnavailableError(SLOT_UNAVAILABLE_MESSAGE)
        self._ensure_slot_still_available(
            specialist_id=appointment.specialist_id,
            start_datetime=preferred_datetime,
            end_datetime=preferred_datetime + SLOT_DURATION,
            exclude_appointment_id=appointment.id,
        )

        appointment.preferred_datetime = preferred_datetime
        appointment.end_datetime = preferred_datetime + SLOT_DURATION
        appointment.status = AppointmentStatus.REQUESTED
        appointment.reschedule_note = normalize_optional_comment(payload.note)
        appointment.last_rescheduled_at = datetime.now(UTC)
        appointment.reminder_sent_at = None
        appointment.last_rescheduled_by_role = AppointmentActorRole.SPECIALIST
        appointment.status_updated_by_user_id = current_user.id
        self._commit_appointment_write()
        self.uow.refresh(appointment)
        self._notify_both_sides_rescheduled(
            appointment,
            actor_role=AppointmentActorRole.SPECIALIST,
        )
        self._log_specialist_transition(
            "specialist.appointments.rescheduled",
            current_user,
            appointment,
        )
        return appointment

    def complete_specialist_appointment(
        self,
        current_user: User,
        appointment_id: UUID,
    ) -> Appointment:
        """Mark a confirmed appointment as completed on behalf of the specialist."""

        appointment = self.get_specialist_appointment(current_user, appointment_id)
        try:
            ensure_appointment_completion_allowed(
                appointment.status,
                appointment.end_datetime,
            )
        except ValueError as exc:
            raise AppointmentCompletionNotAllowedError(str(exc)) from exc

        appointment.status = AppointmentStatus.COMPLETED
        appointment.completed_at = datetime.now(UTC)
        appointment.status_updated_by_user_id = current_user.id
        self.uow.commit()
        self.uow.refresh(appointment)
        self._log_specialist_transition(
            "specialist.appointments.completed",
            current_user,
            appointment,
        )
        return appointment

    def list_all_appointments(self) -> list[Appointment]:
        """Return all appointments for admin oversight views."""

        return self.repository.list_all()

    def list_filtered_appointments(
        self,
        *,
        status: AppointmentStatus | None = None,
        specialist_id: UUID | None = None,
        user_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Appointment], int]:
        """Return paginated admin appointments plus the total count for the filters."""

        appointments = self.repository.list_all_filtered(
            status=status,
            specialist_id=specialist_id,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            page=page,
            page_size=page_size,
        )
        total = self.repository.count_all_filtered(
            status=status,
            specialist_id=specialist_id,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        )
        return appointments, total

    def get_any_appointment(self, appointment_id: UUID) -> Appointment:
        """Return any appointment by id for admin oversight views."""

        appointment = self.repository.get_by_id(appointment_id)
        if appointment is None:
            raise AppointmentNotFoundError(APPOINTMENT_NOT_FOUND_MESSAGE)
        return appointment

    def reschedule_appointment(
        self,
        user: User,
        appointment_id: UUID,
        payload: AppointmentRescheduleRequest,
    ) -> Appointment:
        """Reschedule an owned appointment and move it back to requested state."""

        appointment = self.get_appointment(user, appointment_id)
        try:
            ensure_appointment_reschedule_allowed(
                appointment.status,
                appointment.preferred_datetime,
                settings.appointment_reschedule_cutoff_hours,
            )
        except ValueError as exc:
            raise AppointmentRescheduleNotAllowedError(str(exc)) from exc

        try:
            preferred_datetime = normalize_future_datetime(payload.preferred_datetime)
        except ValueError as exc:
            raise InvalidAppointmentDateError(str(exc)) from exc
        if not self.availability_service.is_bookable_slot(
            appointment.specialist_id,
            preferred_datetime,
        ):
            raise AppointmentSlotUnavailableError(SLOT_UNAVAILABLE_MESSAGE)
        self._ensure_slot_still_available(
            specialist_id=appointment.specialist_id,
            start_datetime=preferred_datetime,
            end_datetime=preferred_datetime + SLOT_DURATION,
            exclude_appointment_id=appointment.id,
        )

        appointment.preferred_datetime = preferred_datetime
        appointment.end_datetime = preferred_datetime + SLOT_DURATION
        appointment.status = AppointmentStatus.REQUESTED
        appointment.reschedule_note = normalize_optional_comment(payload.note)
        appointment.last_rescheduled_at = datetime.now(UTC)
        appointment.reminder_sent_at = None
        appointment.last_rescheduled_by_role = AppointmentActorRole.USER
        appointment.status_updated_by_user_id = user.id
        self._commit_appointment_write()
        self.uow.refresh(appointment)
        self._notify_both_sides_rescheduled(
            appointment,
            actor_role=AppointmentActorRole.USER,
        )
        log_event(
            self.logger,
            "appointments.rescheduled",
            user_id=user.id,
            specialist_id=appointment.specialist_id,
            appointment_id=appointment.id,
            status=appointment.status.value,
            preferred_datetime=appointment.preferred_datetime.isoformat(),
            end_datetime=appointment.end_datetime.isoformat(),
        )
        return appointment

    def _get_specialist_profile(self, current_user: User) -> Specialist:
        """Resolve the specialist profile linked to the authenticated specialist user."""

        specialist = self.specialist_repository.get_by_user_id(current_user.id)
        if specialist is None:
            raise SpecialistProfileNotFoundError("Specialist profile not found.")
        return specialist

    def _log_specialist_transition(
        self,
        event: str,
        current_user: User,
        appointment: Appointment,
    ) -> None:
        """Log a specialist-side appointment transition with consistent context."""

        self._log_transition(
            event,
            current_user.id,
            appointment.specialist_id,
            appointment,
        )

    def _log_transition(
        self,
        event: str,
        user_id,
        specialist_id,
        appointment: Appointment,
    ) -> None:
        """Log an appointment transition with the common event payload."""

        log_event(
            self.logger,
            event,
            user_id=user_id,
            specialist_id=specialist_id,
            appointment_id=appointment.id,
            status=appointment.status.value,
            preferred_datetime=appointment.preferred_datetime.isoformat(),
            end_datetime=appointment.end_datetime.isoformat(),
        )

    def _notify_specialist_for_request(self, appointment: Appointment) -> None:
        """Notify the specialist user when a new appointment is requested."""

        self._notify_specialist(
            appointment,
            NotificationType.APPOINTMENT_REQUESTED,
            "New appointment request",
            self._build_notification_message(
                "A user requested a new appointment",
                appointment,
            ),
        )

    def _notify_specialist(
        self,
        appointment: Appointment,
        notification_type: NotificationType,
        title: str,
        message: str,
    ) -> None:
        """Notify the specialist user linked to the appointment, if any."""

        specialist = self.specialist_repository.get_by_id(appointment.specialist_id)
        if specialist is None or specialist.user_id is None:
            return
        self.notification_service.create_notification(
            specialist.user_id,
            notification_type,
            title,
            message,
            appointment_id=appointment.id,
        )

    def _notify_user(
        self,
        appointment: Appointment,
        notification_type: NotificationType,
        title: str,
        message: str,
    ) -> None:
        """Notify a platform user about an appointment transition."""

        self.notification_service.create_notification(
            appointment.user_id,
            notification_type,
            title,
            message,
            appointment_id=appointment.id,
        )

    def _notify_both_sides_rescheduled(
        self,
        appointment: Appointment,
        actor_role: AppointmentActorRole,
    ) -> None:
        """Notify both user and specialist when either side reschedules an appointment."""

        if actor_role == AppointmentActorRole.USER:
            user_message = self._build_notification_message(
                "You changed the appointment time",
                appointment,
            )
            specialist_message = self._build_notification_message(
                "The user changed the appointment time",
                appointment,
            )
        else:
            user_message = self._build_notification_message(
                "The specialist changed the appointment time",
                appointment,
            )
            specialist_message = self._build_notification_message(
                "You changed the appointment time",
                appointment,
            )

        self._notify_user(
            appointment,
            NotificationType.APPOINTMENT_RESCHEDULED,
            "Appointment rescheduled",
            user_message,
        )
        self._notify_specialist(
            appointment,
            NotificationType.APPOINTMENT_RESCHEDULED,
            "Appointment rescheduled",
            specialist_message,
        )

    def _create_appointment_record(
        self,
        user_id: UUID,
        specialist_id: UUID,
        mode,
        preferred_datetime: datetime,
        notes: str | None,
        created_by_user_id: UUID,
        initial_status: AppointmentStatus,
    ) -> Appointment:
        """Validate slot availability and persist a new appointment row."""

        specialist = self.specialist_repository.get_active_specialist_by_id(specialist_id)
        if specialist is None:
            raise SpecialistUnavailableError("Specialist not found or unavailable.")

        try:
            normalized_datetime = normalize_future_datetime(preferred_datetime)
            ensure_minimum_appointment_notice(
                normalized_datetime,
                settings.appointment_booking_min_notice_hours,
            )
        except ValueError as exc:
            raise InvalidAppointmentDateError(str(exc)) from exc

        if not self.availability_service.is_bookable_slot(
            specialist_id,
            normalized_datetime,
        ):
            raise AppointmentSlotUnavailableError(SLOT_UNAVAILABLE_MESSAGE)
        self._ensure_slot_still_available(
            specialist_id=specialist_id,
            start_datetime=normalized_datetime,
            end_datetime=normalized_datetime + SLOT_DURATION,
        )

        appointment = Appointment(
            user_id=user_id,
            specialist_id=specialist_id,
            mode=mode,
            status=initial_status,
            preferred_datetime=normalized_datetime,
            end_datetime=normalized_datetime + SLOT_DURATION,
            notes=normalize_optional_comment(notes),
            status_updated_by_user_id=created_by_user_id,
            confirmed_at=datetime.now(UTC) if initial_status == AppointmentStatus.CONFIRMED
                                            else None,
        )
        self.repository.add(appointment)
        self._commit_appointment_write()
        self.uow.refresh(appointment)
        return appointment

    def _ensure_slot_still_available(
        self,
        specialist_id: UUID,
        start_datetime: datetime,
        end_datetime: datetime,
        exclude_appointment_id: UUID | None = None,
    ) -> None:
        """Recheck active overlaps immediately before persisting a slot change."""

        has_overlap = self.repository.has_overlapping_active_appointment(
            specialist_id=specialist_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            exclude_appointment_id=exclude_appointment_id,
        )
        if has_overlap:
            raise AppointmentSlotUnavailableError(SLOT_UNAVAILABLE_MESSAGE)

    def _commit_appointment_write(self) -> None:
        """Commit an appointment write and translate overlap conflicts into domain errors."""

        try:
            self.uow.commit()
        except IntegrityError as exc:
            self.uow.rollback()
            if self._is_overlap_constraint_error(exc):
                raise AppointmentSlotUnavailableError(SLOT_UNAVAILABLE_MESSAGE) from exc
            raise

    def _is_overlap_constraint_error(self, exc: IntegrityError) -> bool:
        """Return whether a database write failed on the active-overlap constraint."""

        diag = getattr(exc.orig, "diag", None)
        constraint_name = getattr(diag, "constraint_name", None)
        if constraint_name == APPOINTMENT_OVERLAP_CONSTRAINT_NAME:
            return True
        return APPOINTMENT_OVERLAP_CONSTRAINT_NAME in str(exc.orig)

    def _build_notification_message(self, prefix: str, appointment: Appointment) -> str:
        """Build a notification message that includes the appointment start time."""

        timestamp = appointment.preferred_datetime.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")
        return f"{prefix}. Scheduled for {timestamp}."
