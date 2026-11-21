# Oupsii - Backend FastAPI

API REST pour la plateforme d'enseignement multi-agents Oupsii.

## Stack

- **FastAPI** (async)
- **PostgreSQL** (via asyncpg / SQLAlchemy)
- **JWT** auth (python-jose + passlib[bcrypt])
- **Stripe** (abonnements + checkout + portal)
- **Pydantic v2** validation

## Installation locale

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Variables d'environnement (.env)

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/oupsii
JWT_SECRET=change-me
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_MONTHLY=price_...
STRIPE_PRICE_YEARLY=price_...
APP_URL=http://localhost:3000
OPENAI_API_KEY=sk-...   # ou tout provider compatible
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1
```

## Démarrage

```bash
uvicorn app.main:app --reload --port 8000
```

## Endpoints

| Méthode | Route | Description |
|---|---|---|
| POST | /auth/register | Inscription (démarre trial 7j) |
| POST | /auth/login | Connexion (JWT) |
| GET | /me | Profil utilisateur courant |
| GET | /levels | Liste des niveaux (CEM/LYCEE) |
| GET | /subjects | Liste des 11 matières |
| GET | /agents | Liste des agents (par niveau/matière) |
| GET | /quiz | Questions du diagnostic de niveau |
| POST | /quiz/submit | Soumission + détection niveau |
| POST | /chat | Conversation avec un agent |
| GET | /chat/sessions | Historique des sessions |
| GET / POST | /feedback | Notation des réponses |
| POST | /billing/checkout | Stripe Checkout Session |
| POST | /billing/portal | Stripe Customer Portal |
| POST | /billing/webhook | Webhook Stripe |
| GET | /pricing | Plans tarifaires |

## Déploiement (Render)

1. Créer une DB PostgreSQL sur Render
2. Web Service: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Configurer les env vars
4. Build: `pip install -r requirements.txt`
