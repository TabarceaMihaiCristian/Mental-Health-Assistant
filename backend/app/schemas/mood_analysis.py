"""Schemas for structured mood analysis, summaries, and reports."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import MoodLabel, ReportPeriod, RiskLevel


class MoodAnalysisResult(BaseModel):
    """Validated structured output returned by the mood analysis workflow."""

    primary_mood: MoodLabel
    secondary_mood: MoodLabel | None = None
    intensity: int = Field(ge=1, le=5)
    confidence: float = Field(ge=0, le=1)
    risk: RiskLevel
    possible_triggers: list[str] = Field(default_factory=list)


class MoodAnalysisResponse(BaseModel):
    """Serialized mood analysis row."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    message_id: UUID
    user_id: UUID
    primary_mood: MoodLabel
    secondary_mood: MoodLabel | None
    intensity: int
    confidence: float
    risk: RiskLevel
    trigger_notes: str | None
    created_at: datetime


class DailyMoodSummaryResponse(BaseModel):
    """Serialized per-day aggregated mood summary."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    summary_date: date
    dominant_mood: MoodLabel
    average_intensity: float
    risk: RiskLevel
    summary_text: str | None
    created_at: datetime


class ReportResponse(BaseModel):
    """Serialized generated weekly or monthly report."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    period: ReportPeriod
    period_start: date
    period_end: date
    report_data: dict
    created_at: datetime
