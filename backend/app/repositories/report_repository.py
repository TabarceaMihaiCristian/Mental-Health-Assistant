"""Repositories for generated reports."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.enums import ReportPeriod
from app.models.report import Report


class ReportRepository:
    """Database access helpers for generated reports."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to one SQLAlchemy session."""

        self.db = db

    def replace_for_window(
        self,
        user_id: UUID,
        period: ReportPeriod,
        period_start: date,
        period_end: date,
        report_data: dict,
    ) -> Report:
        """Replace any existing report for a period window and persist a new one."""

        self.db.execute(
            delete(Report).where(
                Report.user_id == user_id,
                Report.period == period,
                Report.period_start == period_start,
                Report.period_end == period_end,
            )
        )
        report = Report(
            user_id=user_id,
            period=period,
            period_start=period_start,
            period_end=period_end,
            report_data=report_data,
        )
        self.db.add(report)
        self.db.flush()
        return report

    def get_for_window(
        self,
        user_id: UUID,
        period: ReportPeriod,
        period_start: date,
        period_end: date,
    ) -> Report | None:
        """Return the stored report for a specific user/period window."""

        statement = (
            self.db.query(Report)
            .filter(
                Report.user_id == user_id,
                Report.period == period,
                Report.period_start == period_start,
                Report.period_end == period_end,
            )
            .limit(1)
        )
        return statement.one_or_none()
