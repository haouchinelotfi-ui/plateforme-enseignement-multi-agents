"""Modèles SQLAlchemy (async)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    String, Integer, Boolean, DateTime, ForeignKey, Text, Float, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class CycleEnum(PyEnum):
    CEM = "CEM"
    LYCEE = "LYCEE"


class SubscriptionStatusEnum(PyEnum):
    trialing = "trialing"
    active = "active"
    past_due = "past_due"
    canceled = "canceled"
    incomplete = "incomplete"
    trialing_expired = "trialing_expired"


class Level(Base):
    __tablename__ = "levels"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    cycle: Mapped[CycleEnum] = mapped_column(default=CycleEnum.CEM)

    agents: Mapped[list["Agent"]] = relationship(back_populates="level")
    users: Mapped[list["User"]] = relationship(back_populates="detected_level")


class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))

    agents: Mapped[list["Agent"]] = relationship(back_populates="subject")


class Agent(Base):
    __tablename__ = "agents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    agent_name: Mapped[str] = mapped_column(String(120))
    system_prompt: Mapped[str] = mapped_column(Text)
    allowed_tools: Mapped[list] = mapped_column(JSON, default=list)
    model_config_json: Mapped[dict] = mapped_column("model_config", JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    level: Mapped["Level"] = relationship(back_populates="agents")
    subject: Mapped["Subject"] = relationship(back_populates="agents")


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    detected_level_id: Mapped[int | None] = mapped_column(
        ForeignKey("levels.id"), nullable=True
    )
    trial_starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    trial_ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    subscription_status: Mapped[SubscriptionStatusEnum] = mapped_column(
        default=SubscriptionStatusEnum.trialing
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    detected_level: Mapped["Level | None"] = relationship(back_populates="users")
    sessions: Mapped[list["ChatSession"]] = relationship(back_populates="user")
    usage_logs: Mapped[list["UsageLog"]] = relationship(back_populates="user")


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    agent_id: Mapped[str | None] = mapped_column(ForeignKey("agents.id"), nullable=True)
    level_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    subject_slug: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user: Mapped["User"] = relationship(back_populates="sessions")
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    usage_logs: Mapped[list["UsageLog"]] = relationship(back_populates="session")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))  # user | assistant
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    session: Mapped["ChatSession"] = relationship(back_populates="messages")


class UsageLog(Base):
    __tablename__ = "usage_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[str | None] = mapped_column(ForeignKey("chat_sessions.id"), nullable=True)
    agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    tokens_input: Mapped[int] = mapped_column(Integer, default=0)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0)
    model_used: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="usage_logs")
    session: Mapped["ChatSession | None"] = relationship(back_populates="usage_logs")
