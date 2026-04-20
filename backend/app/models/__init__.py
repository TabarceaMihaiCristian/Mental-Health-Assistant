"""Convenience imports for the full ORM model registry."""

from app.models.auth_identity import AuthIdentity
from app.models.appointment import Appointment
from app.models.base import Base
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.daily_mood_summary import DailyMoodSummary
from app.models.mood_analysis import MoodAnalysis
from app.models.notification import Notification
from app.models.report import Report
from app.models.risk_event import RiskEvent
from app.models.specialist import Specialist
from app.models.specialist_availability_rule import SpecialistAvailabilityRule
from app.models.specialist_break import SpecialistBreak
from app.models.specialist_review import SpecialistReview
from app.models.specialist_time_off import SpecialistTimeOff
from app.models.user import User
from app.models.user_profile import UserProfile

__all__ = [
    "AuthIdentity",
    "Appointment",
    "Base",
    "ChatMessage",
    "ChatSession",
    "DailyMoodSummary",
    "MoodAnalysis",
    "Notification",
    "Report",
    "RiskEvent",
    "Specialist",
    "SpecialistAvailabilityRule",
    "SpecialistBreak",
    "SpecialistReview",
    "SpecialistTimeOff",
    "User",
    "UserProfile",
]
