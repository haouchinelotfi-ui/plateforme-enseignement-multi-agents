"""Router feedback: notation des réponses (1-5 étoiles)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, UsageLog
from app.schemas import FeedbackRequest

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("")
async def create_feedback(
    payload: FeedbackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    log = await db.get(UsageLog, payload.usage_log_id)
    if not log or log.user_id != user.id:
        raise HTTPException(404, "Log d'usage introuvable")
    log.rating = payload.rating
    log.comment = payload.comment
    await db.commit()
    return {"status": "ok", "rating": log.rating}


@router.get("")
async def list_feedback(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    logs = (
        await db.execute(
            select(UsageLog)
            .where(UsageLog.user_id == user.id, UsageLog.rating.isnot(None))
            .order_by(UsageLog.created_at.desc())
        )
    ).scalars().all()
    return [
        {"usage_log_id": l.id, "rating": l.rating, "comment": l.comment, "created_at": l.created_at.isoformat()}
        for l in logs
    ]
