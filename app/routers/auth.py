"""Router auth: register + login."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, SubscriptionStatusEnum
from app.schemas import RegisterRequest, LoginRequest, AuthResponse, UserOut
from app.security import hash_password, verify_password, create_access_token
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

TRIAL_DAYS = 7


@router.post("/register", response_model=AuthResponse)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email déjà utilisé")
    now = datetime.now(timezone.utc)
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        trial_starts_at=now,
        trial_ends_at=now + timedelta(days=TRIAL_DAYS),
        subscription_status=SubscriptionStatusEnum.trialing,
        last_active_at=now,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email ou mot de passe incorrect")
    user.last_active_at = datetime.now(timezone.utc)
    await db.commit()
    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user=UserOut.model_validate(user))
