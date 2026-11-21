"""Endpoints d'authentification : inscription, connexion, profil."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from ..database import get_db
from ..models import UserCreate, UserLogin, TokenOut, UserOut
from ..security import hash_password, verify_password, create_access_token, get_current_user_id
from ..email_service import send_welcome

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
async def register(payload: UserCreate):
    db = get_db()
    existing = await db.fetchval(
        "SELECT id FROM users WHERE email = $1", payload.email
    )
    if existing:
        raise HTTPException(status_code=409, detail="Email déjà inscrit.")

    user_id = uuid.uuid4()
    await db.execute(
        """INSERT INTO users (id, email, password_hash)
           VALUES ($1, $2, $3)""",
        user_id,
        payload.email,
        hash_password(payload.password),
    )

    # Email de bienvenue (asynchrone, non bloquant)
    try:
        send_welcome(payload.email)
    except Exception:
        pass  # l'envoi email ne doit pas bloquer l'inscription

    token = create_access_token(str(user_id))
    row = await db.fetchrow(
        "SELECT id, email, trial_ends_at, subscription_status FROM users WHERE id = $1",
        user_id,
    )
    return TokenOut(
        access_token=token,
        user=UserOut(
            id=row["id"],
            email=row["email"],
            detected_level_code=None,
            trial_ends_at=row["trial_ends_at"],
            subscription_status=row["subscription_status"],
        ),
    )


@router.post("/login", response_model=TokenOut)
async def login(payload: UserLogin):
    db = get_db()
    row = await db.fetchrow(
        "SELECT id, email, password_hash, trial_ends_at, subscription_status "
        "FROM users WHERE email = $1",
        payload.email,
    )
    if not row or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Identifiants invalides.")

    token = create_access_token(str(row["id"]))
    return TokenOut(
        access_token=token,
        user=UserOut(
            id=row["id"],
            email=row["email"],
            detected_level_code=None,
            trial_ends_at=row["trial_ends_at"],
            subscription_status=row["subscription_status"],
        ),
    )


@router.get("/me", response_model=UserOut)
async def me(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    row = await db.fetchrow(
        """SELECT u.id, u.email, u.trial_ends_at, u.subscription_status,
                  l.code AS detected_level_code
           FROM users u LEFT JOIN levels l ON u.detected_level_id = l.id
           WHERE u.id = $1""",
        uuid.UUID(user_id),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    return UserOut(
        id=row["id"],
        email=row["email"],
        detected_level_code=row["detected_level_code"],
        trial_ends_at=row["trial_ends_at"],
        subscription_status=row["subscription_status"],
    )
