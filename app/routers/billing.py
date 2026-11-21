"""Endpoints de facturation Stripe — Checkout + portail client."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
import stripe
from ..database import get_db
from ..config import settings
from ..security import get_current_user_id

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.post("/checkout")
async def create_checkout(
    plan: str = "monthly",
    user_id: str = Depends(get_current_user_id),
):
    """Crée une session Stripe Checkout (monthly ou yearly)."""
    price_id = (
        settings.STRIPE_PRICE_ID_YEARLY if plan == "yearly"
        else settings.STRIPE_PRICE_ID_MONTHLY
    )
    if not price_id:
        raise HTTPException(status_code=500, detail="Prix Stripe non configuré.")

    db = get_db()
    row = await db.fetchrow(
        "SELECT email, stripe_customer_id FROM users WHERE id = $1",
        uuid.UUID(user_id),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            client_reference_id=user_id,  # pour le webhook
            customer_email=row["stripe_customer_id"] or None,
            success_url=f"{settings.FRONTEND_URL}/abonnement?status=success",
            cancel_url=f"{settings.FRONTEND_URL}/abonnement?status=cancel",
            metadata={"user_id": user_id},
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=502, detail=f"Erreur Stripe: {e}")

    return {"checkout_url": session.url}


@router.post("/portal")
async def customer_portal(user_id: str = Depends(get_current_user_id)):
    """Redirige vers le portail client Stripe (gérer/annuler l'abonnement)."""
    db = get_db()
    customer_id = await db.fetchval(
        "SELECT stripe_customer_id FROM users WHERE id = $1", uuid.UUID(user_id)
    )
    if not customer_id:
        raise HTTPException(status_code=400, detail="Aucun abonnement Stripe lié.")

    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=f"{settings.FRONTEND_URL}/profil",
    )
    return {"portal_url": session.url}
