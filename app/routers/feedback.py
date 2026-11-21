"""Endpoint de feedback granulaire (note 1-5 + commentaire par réponse d'agent)."""
from fastapi import APIRouter, Depends, HTTPException
from ..database import get_db
from ..models import FeedbackCreate
from ..security import get_current_user_id

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("")
async def create_feedback(
    payload: FeedbackCreate, user_id: str = Depends(get_current_user_id)
):
    db = get_db()
    # Vérifier que le log appartient bien à l'utilisateur
    owner = await db.fetchval(
        "SELECT user_id FROM usage_logs WHERE id = $1", payload.usage_log_id
    )
    if not owner or str(owner) != user_id:
        raise HTTPException(status_code=403, detail="Log introuvable ou non autorisé.")

    await db.execute(
        """UPDATE usage_logs
              SET rating = $1, feedback_comment = $2
            WHERE id = $3""",
        payload.rating,
        payload.comment,
        payload.usage_log_id,
    )
    return {"status": "ok", "message": "Feedback enregistré."}
