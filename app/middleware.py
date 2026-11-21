"""
Middleware de vérification d'accès :
- Période d'essai 7 jours active OU abonnement Stripe 'active'
- Sinon -> HTTP 402 Payment Required
- Rate limiting Redis (30 req/heure par utilisateur)
"""
import time
from fastapi import HTTPException, Request, status
from .database import get_db, get_redis
from .config import settings


async def check_access(user_id: str) -> None:
    """Vérifie le statut d'abonnement. Lève 402 si accès expiré."""
    db = get_db()
    row = await db.fetchrow(
        "SELECT trial_ends_at, subscription_status FROM users WHERE id = $1",
        user_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

    now = time.time()
    trial_ok = row["trial_ends_at"].timestamp() > now
    sub_active = row["subscription_status"] == "active"

    if not (trial_ok or sub_active):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Période d'essai expirée. Abonnez-vous pour continuer.",
        )


async def check_rate_limit(user_id: str) -> None:
    """Rate limiting via Redis : N requêtes par fenêtre glissante."""
    redis = get_redis()
    key = f"ratelimit:{user_id}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, settings.RATE_LIMIT_WINDOW_SECONDS)
    if count > settings.RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Limite atteinte : {settings.RATE_LIMIT_REQUESTS} requêtes/heure.",
        )
