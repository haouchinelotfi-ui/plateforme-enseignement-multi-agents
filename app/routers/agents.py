"""Endpoint d'exécution d'agent — avec vérification d'accès + rate limiting."""
import uuid
from fastapi import APIRouter, Depends
from ..models import AgentRequest, AgentResponse
from ..security import get_current_user_id
from ..middleware import check_access, check_rate_limit
from ..agent_router import execute_agent

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("/ask", response_model=AgentResponse)
async def ask_agent(
    payload: AgentRequest, user_id: str = Depends(get_current_user_id)
):
    # 1. Vérification abonnement / trial
    await check_access(user_id)
    # 2. Rate limiting
    await check_rate_limit(user_id)
    # 3. Exécution
    session_id = str(uuid.uuid4())
    result = await execute_agent(
        user_id=user_id,
        level_code=payload.level_code,
        subject_slug=payload.subject_slug,
        message=payload.message,
        session_id=session_id,
    )
    return AgentResponse(
        agent_name=result["agent_name"],
        reply=result["reply"],
        agent_id=result["agent_id"],
        latency_ms=result["latency_ms"],
    )
