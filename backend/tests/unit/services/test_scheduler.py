"""Unit tests for scheduler job execution and lifecycle guards."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from app.jobs import scheduler as scheduler_module


@pytest.mark.unit
def test_run_appointment_reminders_job_updates_success_state(monkeypatch: pytest.MonkeyPatch) -> None:
    """Record success metadata when the reminder job completes cleanly."""

    # Arrange
    reminder_service = Mock()
    reminder_service.send_due_reminders.return_value = 3
    fake_db = Mock()
    scheduler_module.RUNTIME_STATE.started = False
    scheduler_module.RUNTIME_STATE.last_run_at = None
    scheduler_module.RUNTIME_STATE.last_success_at = None
    scheduler_module.RUNTIME_STATE.last_error_at = None
    scheduler_module.RUNTIME_STATE.last_error_message = None
    monkeypatch.setattr(scheduler_module, "SessionLocal", lambda: fake_db)
    monkeypatch.setattr(scheduler_module, "AppointmentReminderService", lambda db: reminder_service)

    # Act
    scheduler_module.run_appointment_reminders_job()

    # Assert
    assert scheduler_module.RUNTIME_STATE.last_run_at is not None
    assert scheduler_module.RUNTIME_STATE.last_success_at is not None
    assert scheduler_module.RUNTIME_STATE.last_error_at is None
    assert scheduler_module.RUNTIME_STATE.last_error_message is None
    reminder_service.send_due_reminders.assert_called_once()
    fake_db.close.assert_called_once()


@pytest.mark.unit
def test_run_appointment_reminders_job_updates_error_state(monkeypatch: pytest.MonkeyPatch) -> None:
    """Record failure metadata when the reminder job raises an operational error."""

    # Arrange
    reminder_service = Mock()
    reminder_service.send_due_reminders.side_effect = RuntimeError("job failed")
    fake_db = Mock()
    scheduler_module.RUNTIME_STATE.last_run_at = None
    scheduler_module.RUNTIME_STATE.last_success_at = None
    scheduler_module.RUNTIME_STATE.last_error_at = None
    scheduler_module.RUNTIME_STATE.last_error_message = None
    monkeypatch.setattr(scheduler_module, "SessionLocal", lambda: fake_db)
    monkeypatch.setattr(scheduler_module, "AppointmentReminderService", lambda db: reminder_service)

    # Act
    scheduler_module.run_appointment_reminders_job()

    # Assert
    assert scheduler_module.RUNTIME_STATE.last_run_at is not None
    assert scheduler_module.RUNTIME_STATE.last_success_at is None
    assert scheduler_module.RUNTIME_STATE.last_error_at is not None
    assert scheduler_module.RUNTIME_STATE.last_error_message == "job failed"
    fake_db.close.assert_called_once()


@pytest.mark.unit
def test_start_scheduler_skips_when_already_running(monkeypatch: pytest.MonkeyPatch) -> None:
    """Avoid double-registration when the scheduler is already active in-process."""

    # Arrange
    fake_scheduler = Mock()
    fake_scheduler.running = True
    monkeypatch.setattr(scheduler_module, "scheduler", fake_scheduler)
    monkeypatch.setattr(scheduler_module.settings, "scheduler_enabled", True)
    monkeypatch.setattr(scheduler_module.settings, "debug", False)
    monkeypatch.setattr(scheduler_module.settings, "scheduler_run_in_debug", False)
    scheduler_module.RUNTIME_STATE.started = False

    # Act
    scheduler_module.start_scheduler()

    # Assert
    fake_scheduler.add_job.assert_not_called()
    fake_scheduler.start.assert_not_called()


@pytest.mark.unit
def test_get_scheduler_status_exposes_runtime_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return the expected scheduler health payload for the health endpoint."""

    # Arrange
    next_run = datetime.now(UTC)
    fake_job = Mock(id=scheduler_module.SCHEDULER_JOB_ID, next_run_time=next_run)
    fake_scheduler = Mock()
    fake_scheduler.running = True
    fake_scheduler.get_job.return_value = fake_job
    monkeypatch.setattr(scheduler_module, "scheduler", fake_scheduler)
    scheduler_module.RUNTIME_STATE.started = True
    scheduler_module.RUNTIME_STATE.last_run_at = next_run
    scheduler_module.RUNTIME_STATE.last_success_at = next_run
    scheduler_module.RUNTIME_STATE.last_error_at = None
    scheduler_module.RUNTIME_STATE.last_error_message = None

    # Act
    status = scheduler_module.get_scheduler_status()

    # Assert
    assert status["running"] is True
    assert status["started_in_process"] is True
    assert status["job_registered"] is True
    assert status["job_id"] == scheduler_module.SCHEDULER_JOB_ID
    assert status["next_run_time"] == next_run.isoformat()
    assert status["last_success_at"] == next_run.isoformat()
