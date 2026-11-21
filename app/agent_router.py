"""
Routeur dynamique d'agents — patron Cache-Aside (Redis TTL 1h).
Récupère la config d'agent (system_prompt, allowed_tools, model_config)
puis appelle l'API LLM avec uniquement les outils autorisés.
"""
import json
import time
import uuid
import httpx
from fastapi import HTTPException
from .database import get_db, get_redis
from .config import settings


async def get_agent_config(level_code: str, subject_slug: str) -> dict:
    """Cache-Aside : Redis d'abord, puis PostgreSQL, mise en cache 1h."""
    redis = get_redis()
    cache_key = f"agent:{level_code}:{subject_slug}"

    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    db = get_db()
    query = (
        "SELECT a.id, a.agent_name, a.system_prompt, a.allowed_tools, a.model_config "
        "FROM agents a "
        "JOIN levels l ON a.level_id = l.id "
        "JOIN subjects s ON a.subject_id = s.id "
        "WHERE l.code = $1 AND s.slug = $2 AND a.is_active = TRUE"
    )
    row = await db.fetchrow(query, level_code, subject_slug)
    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Agent pédagogique non disponible pour {level_code}/{subject_slug}.",
        )

    config = {
        "id": str(row["id"]),
        "agent_name": row["agent_name"],
        "system_prompt": row["system_prompt"],
        "allowed_tools": row["allowed_tools"],
        "model_config": row["model_config"],
    }
    await redis.setex(cache_key, 3600, json.dumps(config))  # TTL 1 heure
    return config


async def call_llm(system_prompt: str, user_message: str, model_config: dict) -> tuple[str, int, int]:
    """Appelle l'API LLM (compatible OpenAI). Retourne (reply, tokens_in, tokens_out)."""
    model = model_config.get("model", settings.LLM_MODEL)
    temperature = model_config.get("temperature", 0.3)

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{settings.LLM_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
            json={
                "model": model,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
            },
        )
        resp.raise_for_status()
        data = resp.json()

    reply = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    tokens_in = usage.get("prompt_tokens", 0)
    tokens_out = usage.get("completion_tokens", 0)
    return reply, tokens_in, tokens_out


async def log_usage(
    user_id: str,
    agent_id: str,
    session_id: str,
    tokens_input: int,
    tokens_output: int,
    latency_ms: int,
) -> int:
    """Enregistrement asynchrone dans usage_logs. Retourne l'ID du log."""
    db = get_db()
    row = await db.fetchrow(
        """INSERT INTO usage_logs
             (user_id, agent_id, session_id, tokens_input, tokens_output, latency_ms)
           VALUES ($1, $2, $3, $4, $5, $6)
           RETURNING id""",
        uuid.UUID(user_id),
        uuid.UUID(agent_id),
        uuid.UUID(session_id),
        tokens_input,
        tokens_output,
        latency_ms,
    )
    return row["id"]


async def execute_agent(
    user_id: str, level_code: str, subject_slug: str, message: str, session_id: str
) -> dict:
    """Pipeline complet : résolution config -> LLM -> log -> réponse."""
    start = time.perf_counter()

    config = await get_agent_config(level_code, subject_slug)
    reply, tokens_in, tokens_out = await call_llm(
        config["system_prompt"], message, config["model_config"]
    )

    latency_ms = int((time.perf_counter() - start) * 1000)
    log_id = await log_usage(
        user_id, config["id"], session_id, tokens_in, tokens_out, latency_ms
    )

    return {
        "agent_name": config["agent_name"],
        "reply": reply,
        "agent_id": config["id"],
        "latency_ms": latency_ms,
        "log_id": log_id,
    }
