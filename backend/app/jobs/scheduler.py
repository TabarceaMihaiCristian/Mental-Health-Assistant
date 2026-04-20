"""Background APScheduler setup for periodic application jobs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import os
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.appointment_reminder_service import AppointmentReminderService
from app.utils.logging import get_app_logger, log_event

logger = get_app_logger(__name__)
scheduler = AsyncIOScheduler(timezone="UTC")
SCHEDULER_JOB_ID = "appointment_reminders"


@dataclass(slots=True)
class SchedulerRuntimeState:
    """Mutable runtime state for the in-process scheduler lifecycle."""

    started: bool = False
    last_run_at: datetime | None = None
    last_success_at: datetime | None = None
    last_error_at: datetime | None = None
    last_error_message: str | None = None


RUNTIME_STATE = SchedulerRuntimeState()


def run_appointment_reminders_job() -> None:
    """Execute the appointment reminder workflow in an isolated database session."""

    RUNTIME_STATE.last_run_at = datetime.now(UTC)
    db = SessionLocal()
    try:
        lead_time = timedelta(hours=settings.appointment_reminder_lead_hours)
        sent_count = AppointmentReminderService(db).send_due_reminders(lead_time=lead_time)
        RUNTIME_STATE.last_success_at = datetime.now(UTC)
        RUNTIME_STATE.last_error_at = None
        RUNTIME_STATE.last_error_message = None
        log_event(
            logger,
            "scheduler.appointment_reminders.completed",
            count=sent_count,
            lead_hours=settings.appointment_reminder_lead_hours,
        )
    except (SQLAlchemyError, RuntimeError, ValueError, TypeError, OSError) as exc:
        RUNTIME_STATE.last_error_at = datetime.now(UTC)
        RUNTIME_STATE.last_error_message = str(exc)
        log_event(
            logger,
            "scheduler.appointment_reminders.failed",
            error=str(exc),
            lead_hours=settings.appointment_reminder_lead_hours,
        )
    finally:
        db.close()


def start_scheduler() -> None:
    """Start the background scheduler and register periodic jobs once."""

    if not settings.scheduler_enabled:
        log_event(logger, "scheduler.disabled")
        return

    if settings.debug and not settings.scheduler_run_in_debug:
        log_event(logger, "scheduler.start_skipped", reason="debug_disabled")
        return

    if RUNTIME_STATE.started or scheduler.running:
        log_event(logger, "scheduler.start_skipped", reason="already_running")
        return

    existing_job = scheduler.get_job(SCHEDULER_JOB_ID)
    if existing_job is None:
        scheduler.add_job(
            run_appointment_reminders_job,
            trigger="interval",
            minutes=settings.appointment_reminder_interval_minutes,
            id=SCHEDULER_JOB_ID,
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
    scheduler.start()
    RUNTIME_STATE.started = True
    log_event(
        logger,
        "scheduler.started",
        pid=os.getpid(),
        debug=settings.debug,
        scheduler_run_in_debug=settings.scheduler_run_in_debug,
        reminder_interval_minutes=settings.appointment_reminder_interval_minutes,
        reminder_lead_hours=settings.appointment_reminder_lead_hours,
    )


def stop_scheduler() -> None:
    """Stop the background scheduler if it is currently running."""

    if not scheduler.running:
        return
    scheduler.shutdown(wait=False)
    RUNTIME_STATE.started = False
    log_event(logger, "scheduler.stopped", pid=os.getpid())


def get_scheduler_status() -> dict[str, Any]:
    """Return a structured snapshot of the current scheduler runtime state."""

    job = scheduler.get_job(SCHEDULER_JOB_ID)
    return {
        "enabled": settings.scheduler_enabled,
        "running": scheduler.running,
        "started_in_process": RUNTIME_STATE.started,
        "debug": settings.debug,
        "run_in_debug": settings.scheduler_run_in_debug,
        "pid": os.getpid(),
        "job_registered": job is not None,
        "job_id": None if job is None else job.id,
        "next_run_time": (
            None
            if job is None or job.next_run_time is None
            else job.next_run_time.isoformat()
        ),
        "last_run_at": (
            None
            if RUNTIME_STATE.last_run_at is None
            else RUNTIME_STATE.last_run_at.isoformat()
        ),
        "last_success_at": (
            None
            if RUNTIME_STATE.last_success_at is None
            else RUNTIME_STATE.last_success_at.isoformat()
        ),
        "last_error_at": (
            None
            if RUNTIME_STATE.last_error_at is None
            else RUNTIME_STATE.last_error_at.isoformat()
        ),
        "last_error_message": RUNTIME_STATE.last_error_message,
        "appointment_reminder_interval_minutes": settings.appointment_reminder_interval_minutes,
        "appointment_reminder_lead_hours": settings.appointment_reminder_lead_hours,
    }
