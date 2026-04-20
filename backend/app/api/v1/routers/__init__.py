"""Router modules for the version 1 API surface."""

from app.api.v1.routers import (
    admin_appointments,
    admin_specialists,
    appointments,
    auth,
    chat,
    health,
    notifications,
    reports,
    specialist_appointments,
    specialists,
    users,
)

__all__ = [
    "admin_specialists",
    "admin_appointments",
    "appointments",
    "auth",
    "chat",
    "health",
    "notifications",
    "reports",
    "specialist_appointments",
    "specialists",
    "users",
]
