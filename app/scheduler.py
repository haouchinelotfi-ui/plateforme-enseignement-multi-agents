"""
Tâches planifiées (Cron) :
- Relance après 48h d'inactivité
- Rappel J+6 avant fin de trial
Exécuter via : python -m app.scheduler  (ou APScheduler en production)
"""
import asyncio
import uuid
from .database import init_db, close_db, get_db
from .email_service import send_inactivity_reminder, send_trial_expiry_warning


async def run_inactivity_reminders():
    """Envoie un email aux élèves inactifs depuis 48h."""
    db = get_db()
    rows = await db.fetch(
        """SELECT email FROM users
           WHERE subscription_status IN ('trialing','active')
             AND last_active_at < NOW() - INTERVAL '48 hours'
             AND last_active_at > NOW() - INTERVAL '72 hours'
             AND created_at < NOW() - INTERVAL '48 hours'"""
    )
    count = 0
    for row in rows:
        send_inactivity_reminder(row["email"])
        count += 1
    print(f"[CRON] Relances inactivité : {count} emails.")


async def run_trial_expiry_warnings():
    """Envoie un rappel aux élèves dont le trial expire dans ~1 jour (J+6)."""
    db = get_db()
    rows = await db.fetch(
        """SELECT email FROM users
           WHERE subscription_status = 'trialing'
             AND trial_ends_at < NOW() + INTERVAL '2 days'
             AND trial_ends_at > NOW()"""
    )
    count = 0
    for row in rows:
        send_trial_expiry_warning(row["email"], days_left=1)
        count += 1
    print(f"[CRON] Rappels fin de trial : {count} emails.")


async def run_all():
    await init_db()
    try:
        await run_inactivity_reminders()
        await run_trial_expiry_warnings()
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(run_all())
