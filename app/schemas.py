"""Schémas Pydantic v2 - alignés sur les types TypeScript du frontend."""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# --------------------------------------------------------------------------- #
#  Auth
# --------------------------------------------------------------------------- #
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    detected_level_id: Optional[int] = None
    detected_level: Optional["LevelOut"] = None
    trial_starts_at: datetime
    trial_ends_at: datetime
    subscription_status: str
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    last_active_at: datetime
    created_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --------------------------------------------------------------------------- #
#  Catalogue
# --------------------------------------------------------------------------- #
class LevelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    name: str
    cycle: str


class SubjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    name: str


class AgentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    id: str
    level_id: int
    subject_id: int
    agent_name: str
    system_prompt: str
    allowed_tools: list[str] = []
    model_config_json: dict = {}
    is_active: bool
    level: Optional[LevelOut] = None
    subject: Optional[SubjectOut] = None


# --------------------------------------------------------------------------- #
#  Quiz
# --------------------------------------------------------------------------- #
class QuizQuestion(BaseModel):
    id: str
    subject_slug: str
    question: str
    options: list[str]
    correct_index: int
    level_hint: str


class QuizSubmission(BaseModel):
    answers: dict[str, int]


class QuizResult(BaseModel):
    detected_level_code: str
    detected_level_name: str
    score_by_subject: dict[str, dict] = {}
    recommendation: str


# --------------------------------------------------------------------------- #
#  Chat
# --------------------------------------------------------------------------- #
class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    role: str
    content: str
    created_at: datetime
    rating: Optional[int] = None


class ChatRequest(BaseModel):
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    message: str
    level_code: Optional[str] = None
    subject_slug: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    message: str
    agent_id: str
    agent_name: str
    tokens_input: int
    tokens_output: int
    usage_log_id: str


# --------------------------------------------------------------------------- #
#  Feedback
# --------------------------------------------------------------------------- #
class FeedbackRequest(BaseModel):
    usage_log_id: str
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


# --------------------------------------------------------------------------- #
#  Billing
# --------------------------------------------------------------------------- #
class CheckoutRequest(BaseModel):
    price_id: str
    interval: Literal["month", "year"] = "month"


class PortalResponse(BaseModel):
    url: str


class CheckoutResponse(BaseModel):
    url: str
    session_id: str


class PricingPlan(BaseModel):
    id: str
    name: str
    price: float
    interval: str
    stripe_price_id: str
    features: list[str]
    highlighted: bool = False


# resolve forward ref
UserOut.model_rebuild()
AgentOut.model_rebuild()
