"""ORM model for login identities linked to an application user."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import AUTH_PROVIDER_ENUM, AuthProvider

if TYPE_CHECKING:
    from app.models.user import User


class AuthIdentity(Base, TimestampMixin):
    """Store an authentication method associated with a user account."""

    __tablename__ = "auth_identities"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_auth_identity_provider_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[AuthProvider] = mapped_column(AUTH_PROVIDER_ENUM, nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    password_hash: Mapped[str | None] = mapped_column(Text)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user: Mapped[User] = relationship("User", back_populates="auth_identities")
