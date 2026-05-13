"""Pydantic schemas for user registration and user-facing account data."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import UserRole


class UserBase(BaseModel):
    """Shared user fields used across request and response schemas."""

    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr


class UserCreate(UserBase):
    """Payload used to register a new user account."""

    password: str = Field(min_length=8, max_length=128)


class UserProfileResponse(BaseModel):
    """Serialized profile data returned alongside a user account."""

    model_config = ConfigDict(from_attributes=True)

    age_range: str | None = None
    occupation: str | None = None
    goals: str | None = None
    preferred_activities: list[str] = Field(default_factory=list)
    timezone: str


class UserProfileUpsertRequest(BaseModel):
    """Payload used to create or update the current user's profile."""

    full_name: str = Field(min_length=1, max_length=255)
    age_range: str | None = Field(default=None, max_length=50)
    occupation: str | None = Field(default=None, max_length=255)
    goals: str | None = Field(default=None, max_length=5000)
    preferred_activities: list[str] = Field(default_factory=list, max_length=25)
    timezone: str = Field(min_length=1, max_length=100)


class UserPasswordChangeRequest(BaseModel):
    """Payload used to change the current user's local password."""

    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserResponse(UserBase):
    """Public user representation safe to return from the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    profile: UserProfileResponse | None = None
