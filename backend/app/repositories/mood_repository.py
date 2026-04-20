"""Repositories for mood analyses and daily summaries."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.daily_mood_summary import DailyMoodSummary
from app.models.mood_analysis import MoodAnalysis


class MoodAnalysisRepository:
    """Database access helpers for mood analyses."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to one SQLAlchemy session."""

        self.db = db

    def add(self, analysis: MoodAnalysis) -> MoodAnalysis:
        """Persist a mood analysis row."""

        self.db.add(analysis)
        self.db.flush()
        return analysis

    def list_recent_for_user(self, user_id: UUID, limit: int = 50) -> list[MoodAnalysis]:
        """Return recent analyses for a user."""

        statement = (
            select(MoodAnalysis)
            .where(MoodAnalysis.user_id == user_id)
            .order_by(MoodAnalysis.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def list_for_user_on_date(self, user_id: UUID, summary_date: date) -> list[MoodAnalysis]:
        """Return all analyses for a user on a specific date."""

        statement = (
            select(MoodAnalysis)
            .where(
                MoodAnalysis.user_id == user_id,
                func.date(MoodAnalysis.created_at) == summary_date,
            )
            .order_by(MoodAnalysis.created_at.asc())
        )
        return list(self.db.scalars(statement).all())


class DailyMoodSummaryRepository:
    """Database access helpers for daily mood summaries."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to one SQLAlchemy session."""

        self.db = db

    def add(self, summary: DailyMoodSummary) -> DailyMoodSummary:
        """Persist a daily mood summary."""

        self.db.add(summary)
        self.db.flush()
        return summary

    def get_by_user_and_date(self, user_id: UUID, summary_date: date) -> DailyMoodSummary | None:
        """Return the stored daily summary for a user/date pair."""

        statement = select(DailyMoodSummary).where(
            DailyMoodSummary.user_id == user_id,
            DailyMoodSummary.summary_date == summary_date,
        )
        return self.db.scalar(statement)

    def list_for_user(
        self,
        user_id: UUID,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[DailyMoodSummary]:
        """Return daily summaries for a user and optional date window."""

        statement = select(DailyMoodSummary).where(DailyMoodSummary.user_id == user_id)
        if date_from is not None:
            statement = statement.where(DailyMoodSummary.summary_date >= date_from)
        if date_to is not None:
            statement = statement.where(DailyMoodSummary.summary_date <= date_to)
        statement = statement.order_by(DailyMoodSummary.summary_date.desc())
        return list(self.db.scalars(statement).all())
