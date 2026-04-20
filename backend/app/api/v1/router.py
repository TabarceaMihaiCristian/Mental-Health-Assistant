"""Aggregate router for all version 1 API endpoints."""

from fastapi import APIRouter

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


api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    admin_appointments.router,
    prefix="/admin/appointments",
    tags=["admin-appointments"],
)
api_router.include_router(
    admin_specialists.router,
    prefix="/admin/specialists",
    tags=["admin-specialists"],
)
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(specialists.router, prefix="/specialists", tags=["specialists"])
api_router.include_router(
    specialist_appointments.router,
    prefix="/specialist/appointments",
    tags=["specialist-appointments"],
)
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
