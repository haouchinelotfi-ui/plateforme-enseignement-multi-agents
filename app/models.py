"""Modèles Pydantic pour validation stricte des payloads."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# --- Auth ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    detected_level_code: str | None = None
    trial_ends_at: datetime
    subscription_status: str
    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --- Quiz diagnostic ---
class QuizAnswer(BaseModel):
    question_id: str
    level_code: str
    answer: str


class DiagnosticSubmit(BaseModel):
    answers: list[QuizAnswer] = Field(min_length=3, max_length=6)


class DiagnosticResult(BaseModel):
    detected_level_code: str
    level_name: str


# --- Agent ---
class AgentRequest(BaseModel):
    level_code: str = Field(min_length=2, max_length=20)
    subject_slug: str = Field(min_length=2, max_length=50)
    message: str = Field(min_length=1, max_length=4000)


class AgentResponse(BaseModel):
    agent_name: str
    reply: str
    agent_id: UUID
    latency_ms: int


# --- Feedback ---
class FeedbackCreate(BaseModel):
    usage_log_id: int
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)
