"""Webhooks Stripe — synchronise le statut d'abonnement."""
import stripe
from fastapi import APIRouter, Request, HTTPException
from ..database import get_db
from ..config import settings

router = APIRouter(prefix="/api/webhooks/stripe", tags=["webhooks"])


@router.post("")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Payload invalide")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Signature invalide")

    db = get_db()
    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        customer_id = data.get("customer")
        sub_id = data.get("subscription")
        client_ref = data.get("client_reference_id")  # user_id passé à la création
        if client_ref:
            await db.execute(
                """UPDATE users
                      SET subscription_status = 'active',
                          stripe_customer_id = $1,
                          stripe_subscription_id = $2
                    WHERE id = $3""",
                customer_id,
                sub_id,
                client_ref,
            )

    elif event_type == "invoice.payment_failed":
        sub_id = data.get("subscription")
        await db.execute(
            """UPDATE users SET subscription_status = 'past_due'
               WHERE stripe_subscription_id = $1""",
            sub_id,
        )

    elif event_type == "customer.subscription.deleted":
        sub_id = data.get("id")
        await db.execute(
            """UPDATE users SET subscription_status = 'canceled'
               WHERE stripe_subscription_id = $1""",
            sub_id,
        )

    return {"status": "received", "type": event_type}
