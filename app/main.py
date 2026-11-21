"""Point d'entrée FastAPI - Oupsii Backend."""
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, async_session
from app.seed import seed_if_empty
from app.routers import auth, catalogue, quiz, chat, feedback, billing
from app.models import User, SubscriptionStatusEnum
from sqlalchemy import select


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables + seed
    await init_db()
    async with async_session() as db:
        await seed_if_empty(db)
        # Met à jour les trials expirés
        now = datetime.now(timezone.utc)
        expired = (
            await db.execute(
                select(User).where(
                    User.subscription_status == SubscriptionStatusEnum.trialing,
                    User.trial_ends_at < now,
                )
            )
        ).scalars().all()
        for u in expired:
            u.subscription_status = SubscriptionStatusEnum.trialing_expired
        if expired:
            await db.commit()
    yield


app = FastAPI(
    title="Oupsii API",
    version="1.0.0",
    description="Plateforme d'enseignement multi-agents - Backend",
    lifespan=lifespan,
)

# CORS - autorise le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.APP_URL,
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(catalogue.router)
app.include_router(quiz.router)
app.include_router(chat.router)
app.include_router(feedback.router)
app.include_router(billing.router)


@app.get("/")
async def root():
    return {
        "name": "Oupsii API",
        "version": "1.0.0",
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
