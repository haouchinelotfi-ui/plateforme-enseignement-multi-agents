"""Router chat: conversation avec un agent (LLM via httpx).

Supporte OpenAI-compatible API. Fallback: réponse de secours si pas de clé.
"""
import uuid
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Agent, ChatSession, ChatMessage, UsageLog
from app.schemas import ChatRequest, ChatResponse, ChatMessageOut
from app.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])


async def _call_llm(system_prompt: str, history: list[dict], user_msg: str) -> tuple[str, int, int]:
    """Appelle un LLM compatible OpenAI. Retourne (reply, tokens_in, tokens_out)."""
    if not settings.LLM_API_KEY or settings.LLM_API_KEY.startswith("sk-placeholder"):
        # Mode démo offline
        reply = (
            f"Je suis ton tuteur pédagogique. (Mode démo - configure LLM_API_KEY) "
            f"Tu m'as demandé: « {user_msg[:200]} ». "
            f"Voici une explication: pour bien comprendre cette notion, commence par "
            f"décomposer le problème en étapes simples, puis applique la règle de base. "
            f"N'hésite pas à me poser une question plus précise !"
        )
        return reply, len(user_msg) // 4, len(reply) // 4

    messages = [{"role": "system", "content": system_prompt}] + history + [
        {"role": "user", "content": user_msg}
    ]
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{settings.LLM_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
            json={
                "model": settings.LLM_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 600,
            },
        )
        resp.raise_for_status()
        data = resp.json()
    reply = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return reply, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)


async def _resolve_agent(db: AsyncSession, req: ChatRequest, user: User) -> Agent:
    """Trouve ou crée l'agent approprié."""
    if req.agent_id:
        agent = await db.get(Agent, req.agent_id)
        if agent and agent.is_active:
            return agent
    # Sinon: cherche par level + subject
    level_code = req.level_code or (user.detected_level.code if user.detected_level else "CEM-1")
    q = select(Agent).where(Agent.is_active == True)
    if req.subject_slug:
        q = q.join(Agent.subject, Agent.level).where(
            Agent.subject.has(slug=req.subject_slug),
            Agent.level.has(code=level_code),
        )
    agent = (await db.execute(q)).scalars().first()
    if not agent:
        # fallback: premier agent actif
        agent = (await db.execute(select(Agent).where(Agent.is_active == True))).scalars().first()
    if not agent:
        raise HTTPException(404, "Aucun agent disponible")
    return agent


@router.post("", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await _resolve_agent(db, req, user)

    # Session existante ou nouvelle
    session = None
    if req.session_id:
        session = await db.get(ChatSession, req.session_id)
    if not session:
        session = ChatSession(
            user_id=user.id,
            agent_id=agent.id,
            level_code=req.level_code,
            subject_slug=req.subject_slug,
        )
        db.add(session)
        await db.flush()

    # Historique (10 derniers messages)
    history_msgs = (
        await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
        )
    ).scalars().all()[::-1]
    history = [{"role": m.role, "content": m.content} for m in history_msgs]

    # Sauvegarde message user
    db.add(ChatMessage(session_id=session.id, role="user", content=req.message))

    # Appel LLM
    try:
        reply, tok_in, tok_out = await _call_llm(agent.system_prompt, history, req.message)
    except Exception as e:
        reply = f"Désolé, une erreur est survenue. Réessaie dans un instant. ({type(e).__name__})"
        tok_in, tok_out = 0, 0

    # Sauvegarde réponse assistant
    db.add(ChatMessage(session_id=session.id, role="assistant", content=reply))

    # Usage log
    usage = UsageLog(
        user_id=user.id,
        session_id=session.id,
        agent_id=agent.id,
        tokens_input=tok_in,
        tokens_output=tok_out,
        model_used=settings.LLM_MODEL,
    )
    db.add(usage)
    user.last_active_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(session)
    await db.refresh(usage)

    return ChatResponse(
        session_id=session.id,
        message=reply,
        agent_id=agent.id,
        agent_name=agent.agent_name,
        tokens_input=tok_in,
        tokens_output=tok_out,
        usage_log_id=usage.id,
    )


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageOut])
async def get_messages(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await db.get(ChatSession, session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(404, "Session introuvable")
    msgs = (
        await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        )
    ).scalars().all()
    return msgs


@router.get("/sessions", response_model=list[dict])
async def list_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sessions = (
        await db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user.id)
            .order_by(ChatSession.created_at.desc())
        )
    ).scalars().all()
    return [
        {
            "id": s.id,
            "agent_id": s.agent_id,
            "subject_slug": s.subject_slug,
            "level_code": s.level_code,
            "created_at": s.created_at.isoformat(),
        }
        for s in sessions
    ]
