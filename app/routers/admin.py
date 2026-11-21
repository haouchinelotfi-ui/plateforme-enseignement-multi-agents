"""
Endpoints d'administration & analytique :
- Taux d'activation (quiz + 3 messages à J1)
- DAU / WAU (Daily/WAU Active Users)
- Rétention par cohorte
- Alertes qualité (agents < 3.5/5)
"""
from fastapi import APIRouter, Depends
from ..database import get_db
from ..security import get_current_user_id

router = APIRouter(prefix="/api/admin", tags=["admin"])


async def _is_admin(user_id: str) -> bool:
    # En production : table roles ou flag is_admin. Simplifié ici.
    db = get_db()
    return await db.fetchval(
        "SELECT email LIKE '%@admin.%' FROM users WHERE id = $1", user_id
    )


async def admin_guard(user_id: str):
    if not await _is_admin(user_id):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Accès administrateur requis.")


@router.get("/activation")
async def activation_rate(user_id: str = Depends(get_current_user_id)):
    """Taux d'activation : a fait le quiz ET ≥3 messages dans les 24h après inscription."""
    await admin_guard(user_id)
    db = get_db()
    row = await db.fetchrow(
        """SELECT
             COUNT(DISTINCT u.id) AS total_users,
             COUNT(DISTINCT CASE
               WHEN u.detected_level_id IS NOT NULL
                 AND (SELECT COUNT(*) FROM usage_logs ul
                      WHERE ul.user_id = u.id
                        AND ul.created_at < u.created_at + INTERVAL '24 hours') >= 3
               THEN u.id
             END) AS activated
           FROM users u
           WHERE u.created_at > NOW() - INTERVAL '30 days'"""
    )
    total = row["total_users"] or 0
    activated = row["activated"] or 0
    rate = (activated / total * 100) if total else 0
    return {"total_users": total, "activated": activated, "activation_rate_pct": round(rate, 1)}


@router.get("/dau-wau")
async def dau_wau(user_id: str = Depends(get_current_user_id)):
    """Daily / Weekly Active Users."""
    await admin_guard(user_id)
    db = get_db()
    dau = await db.fetchval(
        "SELECT COUNT(DISTINCT user_id) FROM usage_logs WHERE created_at > NOW() - INTERVAL '24 hours'"
    )
    wau = await db.fetchval(
        "SELECT COUNT(DISTINCT user_id) FROM usage_logs WHERE created_at > NOW() - INTERVAL '7 days'"
    )
    return {"dau": dau or 0, "wau": wau or 0}


@router.get("/retention")
async def retention_cohorts(user_id: str = Depends(get_current_user_id)):
    """Rétention par cohorte d'inscription (semaine)."""
    await admin_guard(user_id)
    db = get_db()
    rows = await db.fetch(
        """WITH cohorts AS (
             SELECT
               date_trunc('week', created_at) AS cohort_week,
               id AS user_id
             FROM users
             WHERE created_at > NOW() - INTERVAL '8 weeks'
           ),
           active AS (
             SELECT DISTINCT user_id, date_trunc('week', created_at) AS active_week
             FROM usage_logs
           )
           SELECT
             c.cohort_week,
             COUNT(DISTINCT c.user_id) AS cohort_size,
             COUNT(DISTINCT CASE WHEN a.active_week = c.cohort_week + INTERVAL '1 week'
                  THEN c.user_id END) AS w1,
             COUNT(DISTINCT CASE WHEN a.active_week = c.cohort_week + INTERVAL '2 weeks'
                  THEN c.user_id END) AS w2,
             COUNT(DISTINCT CASE WHEN a.active_week = c.cohort_week + INTERVAL '4 weeks'
                  THEN c.user_id END) AS w4
           FROM cohorts c
           LEFT JOIN active a ON a.user_id = c.user_id
           GROUP BY c.cohort_week
           ORDER BY c.cohort_week DESC"""
    )
    return [
        {
            "cohort_week": r["cohort_week"].isoformat(),
            "cohort_size": r["cohort_size"],
            "w1": r["w1"],
            "w2": r["w2"],
            "w4": r["w4"],
        }
        for r in rows
    ]


@router.get("/quality-alerts")
async def quality_alerts(user_id: str = Depends(get_current_user_id)):
    """Alertes qualité : agents dont la note moyenne < 3.5/5 (≥ 10 votes)."""
    await admin_guard(user_id)
    db = get_db()
    rows = await db.fetch(
        """SELECT
             a.id, a.agent_name, l.code AS level_code, s.slug AS subject_slug,
             AVG(ul.rating)::numeric(3,2) AS avg_rating,
             COUNT(ul.rating) AS vote_count
           FROM agents a
           JOIN usage_logs ul ON ul.agent_id = a.id
           JOIN levels l ON a.level_id = l.id
           JOIN subjects s ON a.subject_id = s.id
           WHERE ul.rating IS NOT NULL
           GROUP BY a.id, a.agent_name, l.code, s.slug
           HAVING COUNT(ul.rating) >= 10 AND AVG(ul.rating) < 3.5
           ORDER BY avg_rating ASC"""
    )
    return [
        {
            "agent_id": str(r["id"]),
            "agent_name": r["agent_name"],
            "level_code": r["level_code"],
            "subject_slug": r["subject_slug"],
            "avg_rating": float(r["avg_rating"]),
            "vote_count": r["vote_count"],
        }
        for r in rows
    ]
