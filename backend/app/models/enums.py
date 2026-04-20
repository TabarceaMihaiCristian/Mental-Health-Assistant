"""Enumerations and reusable SQLAlchemy enum types for the domain model."""

from __future__ import annotations

import enum

from sqlalchemy import Enum as SqlEnum


class UserRole(str, enum.Enum):
    """Application roles available to authenticated users."""

    USER = "user"
    ADMIN = "admin"
    SPECIALIST = "specialist"


class AuthProvider(str, enum.Enum):
    """Authentication providers supported by the platform."""

    LOCAL = "local"
    GOOGLE = "google"
    APPLE = "apple"
    FACEBOOK = "facebook"


class SenderType(str, enum.Enum):
    """Actors that can emit messages within a chat session."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class RiskLevel(str, enum.Enum):
    """Risk levels produced by the mood and safety analysis pipeline."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReportPeriod(str, enum.Enum):
    """Supported aggregation windows for generated reports."""

    WEEKLY = "weekly"
    MONTHLY = "monthly"


class AppointmentMode(str, enum.Enum):
    """Consultation delivery options for specialist appointments."""

    ONLINE = "online"
    ONSITE = "onsite"


class AppointmentStatus(str, enum.Enum):
    """Lifecycle states for an appointment booking."""

    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class AppointmentActorRole(str, enum.Enum):
    """Actor roles used in appointment audit metadata."""

    USER = "user"
    SPECIALIST = "specialist"
    ADMIN = "admin"


class NotificationType(str, enum.Enum):
    """Supported in-app notification categories."""

    APPOINTMENT_REQUESTED = "appointment_requested"
    APPOINTMENT_CONFIRMED = "appointment_confirmed"
    APPOINTMENT_REJECTED = "appointment_rejected"
    APPOINTMENT_RESCHEDULED = "appointment_rescheduled"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    APPOINTMENT_REMINDER = "appointment_reminder"


class SpecialistStatus(str, enum.Enum):
    """Availability states for specialist directory entries."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class MoodLabel(str, enum.Enum):
    """Mood labels used for session analysis and daily summaries."""

    CALM = "calm"
    HAPPY = "happy"
    TIRED = "tired"
    STRESSED = "stressed"
    ANXIOUS = "anxious"
    SAD = "sad"
    OVERWHELMED = "overwhelmed"
    FRUSTRATED = "frustrated"
    ISOLATED = "isolated"
    HOPEFUL = "hopeful"


class ChatSessionStatus(str, enum.Enum):
    """Lifecycle states for resumable chat sessions."""

    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"


AUTH_PROVIDER_ENUM = SqlEnum(AuthProvider, name="auth_provider")
USER_ROLE_ENUM = SqlEnum(UserRole, name="user_role")
SENDER_TYPE_ENUM = SqlEnum(SenderType, name="sender_type")
RISK_LEVEL_ENUM = SqlEnum(RiskLevel, name="risk_level")
REPORT_PERIOD_ENUM = SqlEnum(ReportPeriod, name="report_period")
APPOINTMENT_MODE_ENUM = SqlEnum(AppointmentMode, name="appointment_mode")
APPOINTMENT_STATUS_ENUM = SqlEnum(AppointmentStatus, name="appointment_status")
APPOINTMENT_ACTOR_ROLE_ENUM = SqlEnum(
    AppointmentActorRole,
    name="appointment_actor_role",
)
NOTIFICATION_TYPE_ENUM = SqlEnum(NotificationType, name="notification_type")
SPECIALIST_STATUS_ENUM = SqlEnum(SpecialistStatus, name="specialist_status")
MOOD_LABEL_ENUM = SqlEnum(MoodLabel, name="mood_label")
CHAT_SESSION_STATUS_ENUM = SqlEnum(ChatSessionStatus, name="chat_session_status")
