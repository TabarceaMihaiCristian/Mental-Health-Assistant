"""Generate daily, weekly, and monthly mood reports from stored analyses."""

from __future__ import annotations

from collections import Counter
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.db.unit_of_work import UnitOfWork
from app.models.daily_mood_summary import DailyMoodSummary
from app.models.enums import ReportPeriod, RiskLevel
from app.models.report import Report
from app.models.user import User
from app.repositories.mood_repository import DailyMoodSummaryRepository
from app.repositories.report_repository import ReportRepository


RISK_PRIORITY = {
    RiskLevel.LOW: 0,
    RiskLevel.MEDIUM: 1,
    RiskLevel.HIGH: 2,
    RiskLevel.CRITICAL: 3,
}


class ReportService:
    """Build and persist weekly and monthly reports for a user."""

    def __init__(self, db: Session) -> None:
        """Bind reporting workflows to one SQLAlchemy session."""

        self.db = db
        self.uow = UnitOfWork(db)
        self.daily_summary_repository = DailyMoodSummaryRepository(db)
        self.report_repository = ReportRepository(db)

    def list_daily_summaries(
        self,
        user: User,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[DailyMoodSummary]:
        """Return daily summaries for the given user and optional date window."""

        return self.daily_summary_repository.list_for_user(user.id, date_from, date_to)

    def generate_report(
        self,
        user: User,
        period: ReportPeriod,
        reference_date: date,
    ) -> Report:
        """Generate and persist a weekly or monthly report for a user."""

        period_start, period_end = self._resolve_period_window(period, reference_date)
        summaries = self.list_daily_summaries(user, period_start, period_end)

        report_data = self._build_report_data(period, period_start, period_end, summaries)

        report = self.report_repository.replace_for_window(
            user.id,
            period,
            period_start,
            period_end,
            report_data=report_data,
        )
        self.uow.commit()
        self.uow.refresh(report)
        return report

    def get_report(
        self,
        user: User,
        period: ReportPeriod,
        reference_date: date,
    ) -> Report | None:
        """Return an already-generated report for a user and concrete time window."""

        period_start, period_end = self._resolve_period_window(period, reference_date)
        return self.report_repository.get_for_window(user.id, period, period_start, period_end)

    def _resolve_period_window(self, period: ReportPeriod,
                                reference_date: date) -> tuple[date, date]:
        """Translate a report period plus reference date into a concrete date window."""

        if period == ReportPeriod.WEEKLY:
            period_start = reference_date - timedelta(days=reference_date.weekday())
            return period_start, period_start + timedelta(days=6)

        period_start = reference_date.replace(day=1)
        if period_start.month == 12:
            next_month = period_start.replace(year=period_start.year + 1, month=1, day=1)
        else:
            next_month = period_start.replace(month=period_start.month + 1, day=1)
        return period_start, next_month - timedelta(days=1)

    def _build_report_data(
        self,
        period: ReportPeriod,
        period_start: date,
        period_end: date,
        summaries: list[DailyMoodSummary],
    ) -> dict:
        """Build deterministic report data from daily summaries."""

        mood_counts = Counter(summary.dominant_mood.value for summary in summaries)
        risk_counts = Counter(summary.risk.value for summary in summaries)
        average_intensity = (
            float(sum(float(summary.average_intensity) for summary in summaries) / len(summaries))
            if summaries
            else 0.0
        )
        highest_risk = (
            max(summaries, key=lambda item: RISK_PRIORITY[item.risk]).risk.value
            if summaries
            else RiskLevel.LOW.value
        )
        highlights = [summary.summary_text for summary in summaries if summary.summary_text][:3]

        return {
            "period": period.value,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "days_with_data": len(summaries),
            "average_intensity": round(average_intensity, 2),
            "highest_risk": highest_risk,
            "dominant_mood_distribution": dict(mood_counts),
            "risk_distribution": dict(risk_counts),
            "highlights": highlights,
            "generated_summary": self._build_generated_summary(
                period,
                len(summaries),
                mood_counts,
                highest_risk,
                average_intensity,
            ),
        }

    def _build_generated_summary(
        self,
        period: ReportPeriod,
        days_with_data: int,
        mood_counts: Counter[str],
        highest_risk: str,
        average_intensity: float,
    ) -> str:
        """Build a concise human-readable report summary."""

        if days_with_data == 0:
            return (
                f"No mood data is available yet for this {period.value} window. "
                "The report will become more useful after more conversations are analyzed."
            )

        top_mood = mood_counts.most_common(1)[0][0]
        summary = (
            f"This {period.value} report is based on {days_with_data} day"
            f"{'' if days_with_data == 1 else 's'} of data. "
            f"The most common dominant mood was {top_mood},"+
                f"with an average intensity of {average_intensity:.2f}."
        )
        if highest_risk != RiskLevel.LOW.value:
            summary += f" The highest observed risk during this period was {highest_risk}."
        return summary
