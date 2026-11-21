"""Router billing: Stripe Checkout + Portal + Webhook + Pricing."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, SubscriptionStatusEnum
from app.schemas import CheckoutRequest, CheckoutResponse, PortalResponse, PricingPlan
from app.config import settings

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/billing", tags=["billing"])

PRICING_PLANS = [
    PricingPlan(
        id="monthly",
        name="Mensuel",
        price=1500,
        interval="month",
        stripe_price_id=settings.STRIPE_PRICE_MONTHLY,
        features=[
            "Accès illimité aux 11 matières",
            "Tutorat IA personnalisé 24/7",
            "Quiz et suivi de progression",
            "Annulable à tout moment",
        ],
        highlighted=True,
    ),
    PricingPlan(
        id="yearly",
        name="Annuel",
        price=12000,
        interval="year",
        stripe_price_id=settings.STRIPE_PRICE_YEARLY,
        features=[
            "Tout le plan mensuel inclus",
            "2 mois offerts (économie 16%)",
            "Support prioritaire",
            "Rapports de progression détaillés",
        ],
    ),
]


async def _ensure_stripe_customer(user: User, db: AsyncSession) -> str:
    if user.stripe_customer_id:
        return user.stripe_customer_id
    customer = stripe.Customer.create(email=user.email, metadata={"user_id": user.id})
    user.stripe_customer_id = customer.id
    await db.commit()
    return customer.id


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    req: CheckoutRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not settings.STRIPE_SECRET_KEY or settings.STRIPE_SECRET_KEY.startswith("sk_test_placeholder"):
        raise HTTPException(503, "Stripe non configuré. Configurez STRIPE_SECRET_KEY.")
    customer_id = await _ensure_stripe_customer(user, db)
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": req.price_id, "quantity": 1}],
        success_url=f"{settings.APP_URL}/account?upgrade=success",
        cancel_url=f"{settings.APP_URL}/pricing?upgrade=cancelled",
        metadata={"user_id": user.id},
    )
    return CheckoutResponse(url=session.url, session_id=session.id)


@router.post("/portal", response_model=PortalResponse)
async def create_portal(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.stripe_customer_id:
        raise HTTPException(400, "Aucun abonnement Stripe trouvé")
    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=f"{settings.APP_URL}/account",
    )
    return PortalResponse(url=session.url)


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Webhook Stripe - met à jour le statut d'abonnement."""
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    if settings.STRIPE_WEBHOOK_SECRET and not settings.STRIPE_WEBHOOK_SECRET.startswith("whsec_placeholder"):
        try:
            event = stripe.Webhook.construct_event(
                payload, sig, settings.STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            raise HTTPException(400, "Signature invalide")
    else:
        # Mode dev: parse sans vérif
        import json
        event = json.loads(payload)

    obj = event.get("data", {}).get("object", {})
    event_type = event.get("type")

    customer_id = obj.get("customer")
    if not customer_id:
        return {"status": "ignored"}

    user = await db.scalar(select(User).where(User.stripe_customer_id == customer_id))
    if not user:
        return {"status": "no_user"}

    if event_type == "checkout.session.completed":
        user.subscription_status = SubscriptionStatusEnum.active
        if obj.get("subscription"):
            user.stripe_subscription_id = obj["subscription"]
    elif event_type == "customer.subscription.updated":
        status_map = {
            "active": SubscriptionStatusEnum.active,
            "past_due": SubscriptionStatusEnum.past_due,
            "canceled": SubscriptionStatusEnum.canceled,
            "incomplete": SubscriptionStatusEnum.incomplete,
            "trialing": SubscriptionStatusEnum.trialing,
        }
        user.subscription_status = status_map.get(
            obj.get("status"), user.subscription_status
        )
    elif event_type == "customer.subscription.deleted":
        user.subscription_status = SubscriptionStatusEnum.canceled
        user.stripe_subscription_id = None

    await db.commit()
    return {"status": "ok"}


# Pricing public (pas d'auth requise)
@router.get("/pricing", response_model=list[PricingPlan])
async def get_pricing():
    return PRICING_PLANS
