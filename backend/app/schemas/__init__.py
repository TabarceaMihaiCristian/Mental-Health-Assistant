"""Pydantic schema package for request and response models."""

from app.schemas.admin_specialist import (
    AdminSpecialistCreateRequest,
    AdminSpecialistResponse,
    AdminSpecialistStatusUpdateRequest,
    AdminSpecialistUpdateRequest,
)
from app.schemas.availability import (
    SpecialistCalendarResponse,
    SpecialistAvailabilityResponse,
    SpecialistAvailabilitySlotResponse,
)
from app.schemas.auth import AuthResponse, LocalLoginRequest, LocalRegisterRequest, TokenResponse
from app.schemas.assistant import ChatInteractionRequest, ChatInteractionResponse
from app.schemas.appointment import (
    AppointmentCreateRequest,
    AppointmentRescheduleRequest,
    AppointmentResponse,
    SpecialistAppointmentCreateRequest,
)
from app.schemas.chat import (
    ChatMessageCreateRequest,
    ChatMessageResponse,
    ChatSessionCreateRequest,
    ChatSessionDetailResponse,
    ChatSessionResponse,
)
from app.schemas.notification import NotificationResponse
from app.schemas.specialist import (
    SpecialistResponse,
    SpecialistReviewResponse,
    SpecialistReviewUpsertRequest,
)
from app.schemas.suggestion import (
    AppointmentSuggestionItemResponse,
    CriticalAppointmentSuggestionsResponse,
)
from app.schemas.specialist_schedule import (
    AvailabilityRuleResponse,
    AvailabilityRuleUpsertRequest,
    BreakCreateRequest,
    BreakResponse,
    BreakUpdateRequest,
    TimeOffCreateRequest,
    TimeOffResponse,
    TimeOffUpdateRequest,
)
from app.schemas.user import UserBase, UserCreate, UserProfileResponse, UserResponse

__all__ = [
    "AdminSpecialistCreateRequest",
    "AdminSpecialistResponse",
    "AdminSpecialistStatusUpdateRequest",
    "AdminSpecialistUpdateRequest",
    "AuthResponse",
    "AvailabilityRuleResponse",
    "AvailabilityRuleUpsertRequest",
    "SpecialistCalendarResponse",
    "SpecialistAvailabilityResponse",
    "SpecialistAvailabilitySlotResponse",
    "AppointmentCreateRequest",
    "AppointmentRescheduleRequest",
    "AppointmentResponse",
    "SpecialistAppointmentCreateRequest",
    "BreakCreateRequest",
    "BreakResponse",
    "BreakUpdateRequest",
    "ChatInteractionRequest",
    "ChatInteractionResponse",
    "ChatMessageCreateRequest",
    "ChatMessageResponse",
    "ChatSessionCreateRequest",
    "ChatSessionDetailResponse",
    "ChatSessionResponse",
    "LocalLoginRequest",
    "LocalRegisterRequest",
    "NotificationResponse",
    "AppointmentSuggestionItemResponse",
    "CriticalAppointmentSuggestionsResponse",
    "SpecialistResponse",
    "SpecialistReviewResponse",
    "SpecialistReviewUpsertRequest",
    "TimeOffCreateRequest",
    "TimeOffResponse",
    "TimeOffUpdateRequest",
    "TokenResponse",
    "UserBase",
    "UserCreate",
    "UserProfileResponse",
    "UserResponse",
]
