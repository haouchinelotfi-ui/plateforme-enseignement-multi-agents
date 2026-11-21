# Plateforme d'Enseignement Centralisée Multi-Agents

Backend orchestrateur unique gérant **100+ agents pédagogiques spécialisés** par niveau scolaire (CEM & Lycée) et par matière, avec monétisation Trial 7 jours + Stripe, cache Redis, analytique et boucle de feedback.

## Stack

| Couche | Technologie |
|---|---|
| Backend | Python · FastAPI · Uvicorn |
| Base de données | PostgreSQL (Neon / Supabase / Render) |
| Cache & Rate-limit | Redis (Upstash / Render) |
| Paiement | Stripe (Checkout + Webhooks) |
| Emails | Resend |
| LLM | API compatible OpenAI (gpt-4o-mini) |
| Hébergement | GitHub + Render (free tier) |

## Architecture

```
Interface Élève → Backend Orchestrateur → { Redis (cache config), PostgreSQL (catalogue), API LLM, Stripe, Resend }
```

Le backend charge **dynamiquement** la configuration de chaque agent (system_prompt, allowed_tools, model_config) depuis PostgreSQL, avec cache Redis (patron Cache-Aside, TTL 1h). Aucun microservice par agent — un seul orchestrator.

## Structure du projet

```
plateforme-enseignement-multi-agents/
├── app/
│   ├── main.py              # Point d'entrée FastAPI + lifespan
│   ├── config.py            # Settings (pydantic-settings)
│   ├── database.py          # Pool asyncpg + client Redis
│   ├── models.py            # Schémas Pydantic (validation stricte)
│   ├── security.py          # bcrypt + JWT
│   ├── middleware.py        # Vérif accès (trial/Stripe) + rate limiting
│   ├── agent_router.py      # Routeur dynamique + Cache-Aside + appel LLM
│   ├── email_service.py     # Resend (bienvenue, relance, fin trial)
│   ├── scheduler.py         # Cron emails (inactivité, fin trial)
│   └── routers/
│       ├── auth.py          # register / login / me
│       ├── quiz.py          # diagnostic de niveau
│       ├── agents.py        # POST /api/agents/ask
│       ├── feedback.py      # POST /api/feedback
│       ├── billing.py       # Stripe Checkout + portal
│       ├── webhooks.py      # Webhooks Stripe
│       └── admin.py         # Analytique + alertes qualité
├── db/migrations/
│   ├── 001_init.sql         # Schéma complet
│   └── 002_seed.sql         # Niveaux, matières, 100+ agents
├── requirements.txt
├── render.yaml              # Infrastructure as Code
├── .env.example
└── .gitignore
```

## Démarrage local

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # renseigner les valeurs
uvicorn app.main:app --reload --port 8000
```

Appliquer les migrations SQL sur votre base PostgreSQL :
```bash
psql $DATABASE_URL -f db/migrations/001_init.sql
psql $DATABASE_URL -f db/migrations/002_seed.sql
```

## Endpoints API

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/auth/register` | Inscription (+ trial 7j) |
| POST | `/api/auth/login` | Connexion → JWT |
| GET | `/api/auth/me` | Profil courant |
| GET | `/api/quiz/diagnostic` | Questions de diagnostic |
| POST | `/api/quiz/diagnostic` | Soumettre → niveau détecté |
| POST | `/api/agents/ask` | Poser une question à l'agent |
| POST | `/api/feedback` | Noter une réponse (1-5) |
| POST | `/api/billing/checkout` | Stripe Checkout |
| POST | `/api/billing/portal` | Portail client Stripe |
| POST | `/api/webhooks/stripe` | Webhook Stripe |
| GET | `/api/admin/activation` | Taux d'activation |
| GET | `/api/admin/dau-wau` | DAU / WAU |
| GET | `/api/admin/retention` | Rétention par cohorte |
| GET | `/api/admin/quality-alerts` | Agents < 3.5/5 |
| GET | `/health` | Health check |

## Déploiement GitHub + Render

1. **Push GitHub** : créer un dépôt et pousser ce dossier.
2. **Base PostgreSQL** : créer une base sur [Neon](https://neon.tech) ou [Supabase](https://supabase.com) (free tier permanent), appliquer les migrations SQL, copier `DATABASE_URL`.
3. **Redis** : créer une instance sur [Upstash](https://upstash.com) (free tier), copier `REDIS_URL`.
4. **Render** : `New + → Blueprint`, connecter le dépôt GitHub, Render lit `render.yaml`. Renseigner les variables d'environnement marquées `sync: false`.
5. **Stripe webhook** : pointer l'URL vers `https://<service>.onrender.com/api/webhooks/stripe`, copier le secret dans `STRIPE_WEBHOOK_SECRET`.
6. **Cron** : le service `edtech-cron-emails` (render.yaml) envoie automatiquement les emails de relance et fin de trial toutes les 6h.

## Sécurité

- Mots de passe hachés (bcrypt)
- Authentification JWT (HS256)
- Validation stricte des payloads (Pydantic v2)
- Rate limiting Redis (30 req/heure/utilisateur)
- Vérification d'accès avant chaque appel d'agent (trial 7j ou abonnement actif → sinon HTTP 402)
- Outils sandboxés par agent (`allowed_tools` JSONB)
- SQL paramétrée (asyncpg, zéro injection)
