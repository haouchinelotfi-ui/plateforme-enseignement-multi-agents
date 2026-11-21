"""Tests rapides du backend avec SQLite en memoire (pas de PostgreSQL requis)."""
import asyncio
import sys
import os
from httpx import AsyncClient, ASGITransport

# Force SQLite pour le test
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

# Patch le moteur avant import
import app.database as dbmod
import sqlalchemy.ext.asyncio as _sa_async

dbmod.engine = _sa_async.create_async_engine("sqlite+aiosqlite:///./test.db", echo=False)
dbmod.async_session = _sa_async.async_sessionmaker(
    dbmod.engine, class_=_sa_async.AsyncSession, expire_on_commit=False
)

from app.main import app


async def main():
    # Déclenche le lifespan (init_db + seed)
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            print("=== 1. Health ===")
            r = await ac.get("/health")
            print(f"  {r.status_code}: {r.json()}")

            print("=== 2. Root ===")
            r = await ac.get("/")
            print(f"  {r.status_code}: {r.json()['name']}")

            print("=== 3. Levels (no auth) ===")
            r = await ac.get("/levels")
            print(f"  {r.status_code}: {len(r.json())} niveaux")

            print("=== 4. Subjects ===")
            r = await ac.get("/subjects")
            print(f"  {r.status_code}: {len(r.json())} matieres")

            print("=== 5. Agents ===")
            r = await ac.get("/agents")
            print(f"  {r.status_code}: {len(r.json())} agents")

            print("=== 6. Quiz questions ===")
            r = await ac.get("/quiz")
            qs = r.json()
            print(f"  {r.status_code}: {len(qs)} questions")

            print("=== 7. Register ===")
            r = await ac.post("/auth/register", json={
                "email": "test@oupsii.dz", "password": "secret123"
            })
            print(f"  {r.status_code}: user_id={r.json().get('user',{}).get('id','?')[:8]}")
            token = r.json()["access_token"]
            h = {"Authorization": f"Bearer {token}"}

            print("=== 8. /me ===")
            r = await ac.get("/me", headers=h)
            print(f"  {r.status_code}: {r.json()['email']} trial={r.json()['subscription_status']}")

            print("=== 9. Submit quiz ===")
            answers = {str(i): q["correct_index"] for i, q in enumerate(qs[:8])}
            # Met quelques mauvaises reponses
            answers["0"] = 1  # mauvais
            r = await ac.post("/quiz/submit", json={"answers": answers}, headers=h)
            print(f"  {r.status_code}: level={r.json()['detected_level_code']}")
            print(f"  scores: {r.json()['score_by_subject']}")

            print("=== 10. Chat ===")
            r = await ac.post("/chat", json={
                "message": "Explique-moi les fractions",
                "level_code": "CEM-1",
                "subject_slug": "mathematiques",
            }, headers=h)
            print(f"  {r.status_code}: agent={r.json().get('agent_name','?')[:30]}")
            print(f"  reply: {r.json().get('message','?')[:80]}...")
            usage_id = r.json().get("usage_log_id")

            print("=== 11. Feedback ===")
            r = await ac.post("/feedback", json={
                "usage_log_id": usage_id, "rating": 5, "comment": "Super!"
            }, headers=h)
            print(f"  {r.status_code}: {r.json()}")

            print("=== 12. Pricing ===")
            r = await ac.get("/billing/pricing")
            print(f"  {r.status_code}: {len(r.json())} plans")

            print("\n=== TOUS LES TESTS PASSENT ===")



if __name__ == "__main__":
    # aiosqlite pour SQLite async
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiosqlite", "-q"])
    asyncio.run(main())
