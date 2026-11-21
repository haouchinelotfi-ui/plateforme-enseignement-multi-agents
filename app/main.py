"""Point d'entrée FastAPI — assemble tous les routers et le cycle de vie."""
import stripe
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .config import settings
from .database import init_db, close_db, init_redis, close_redis
from .routers import auth, quiz, agents, feedback, webhooks, admin, billing


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await init_redis()
    stripe.api_key = settings.STRIPE_SECRET_KEY
    yield
    # Shutdown
    await close_db()
    await close_redis()


app = FastAPI(
    title="Plateforme d'Enseignement Multi-Agents",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS (frontend)
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(quiz.router)
app.include_router(agents.router)
app.include_router(feedback.router)
app.include_router(billing.router)
app.include_router(webhooks.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.ENVIRONMENT}
