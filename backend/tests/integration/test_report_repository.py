"""Repository tests for generated report replacement semantics."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.models.enums import ReportPeriod
from app.models.user import User
from app.repositories.report_repository import ReportRepository


@pytest.mark.integration
def test_report_repository_replaces_existing_window(
    db_session: Session,
    user_factory: Callable[..., User],
) -> None:
    """Replace an existing report for the same user/period window instead of duplicating it."""

    # Arrange
    user = user_factory()
    repository = ReportRepository(db_session)
    first_report = repository.replace_for_window(
        user.id,
        ReportPeriod.WEEKLY,
        date(2026, 4, 20),
        date(2026, 4, 26),
        {"version": 1},
    )

    # Act
    second_report = repository.replace_for_window(
        user.id,
        ReportPeriod.WEEKLY,
        date(2026, 4, 20),
        date(2026, 4, 26),
        {"version": 2},
    )
    db_session.flush()
    found_report = repository.get_for_window(
        user.id,
        ReportPeriod.WEEKLY,
        date(2026, 4, 20),
        date(2026, 4, 26),
    )

    # Assert
    assert second_report.id != first_report.id
    assert found_report is not None
    assert found_report.id == second_report.id
    assert found_report.report_data == {"version": 2}
