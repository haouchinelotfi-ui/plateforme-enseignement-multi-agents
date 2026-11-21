# Oupsii — Frontend Next.js

Plateforme d'enseignement multi-agents — interface élève (App Router, TypeScript, Tailwind).

## Stack

- **Next.js 15** (App Router, Server Components)
- **React 19**
- **TypeScript** strict
- **Tailwind CSS** (dark mode, animations custom)
- **Stripe** (Checkout + Customer Portal)
- **JWT** auth (localStorage + fetch interceptor)

## Structure

```
src/
├── app/
│   ├── layout.tsx          # Root layout (AuthProvider, ThemeProvider, fonts)
│   ├── page.tsx            # Landing page (hero, features, pricing, CTA)
│   ├── globals.css         # Tailwind + utilitaires animés
│   ├── register/           # Inscription → redirect quiz
│   ├── login/              # Connexion → redirect dashboard
│   ├── quiz/               # Diagnostic de niveau multi-étapes
│   ├── dashboard/          # Tableau de bord + chat agent
│   ├── pricing/            # Tarifs + Stripe Checkout
│   └── account/            # Profil + gestion abonnement (portal)
├── components/
│   ├── navbar.tsx          # Nav sticky avec dark mode toggle
│   ├── footer.tsx
│   ├── reveal.tsx          # Animation on scroll (IntersectionObserver)
│   ├── decorations.tsx     # Blobs, grid background, orbs
│   └── feedback-modal.tsx  # Notation 1-5 étoiles
└── lib/
    ├── types.ts            # Types alignés sur le schéma PostgreSQL
    ├── api.ts              # Client fetch vers backend FastAPI
    ├── auth-context.tsx    # Context auth (JWT, trial, subscription)
    ├── theme-provider.tsx  # Dark/light mode
    └── pricing.ts          # Plans & formatage prix
```

## Démarrage

```bash
npm install
cp .env.example .env.local
# Renseigner NEXT_PUBLIC_API_URL (backend FastAPI)
npm run dev
```

→ http://localhost:3000

## Variables d'environnement

| Variable | Description | Exemple |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | URL du backend FastAPI | `https://edtech-orchestrator.onrender.com` |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Clé publique Stripe | `pk_test_...` |
| `NEXT_PUBLIC_APP_URL` | URL du frontend | `https://oupsii.vercel.app` |

## Endpoints API consommés

| Route backend | Méthode | Usage frontend |
|---|---|---|
| `/api/auth/register` | POST | Inscription |
| `/api/auth/login` | POST | Connexion |
| `/api/auth/me` | GET | Profil courant |
| `/api/quiz/questions` | GET | Questions du diagnostic |
| `/api/quiz/submit` | POST | Soumission & détection niveau |
| `/api/agents` | GET | Liste des agents |
| `/api/agents/chat` | POST | Chat avec tuteur IA |
| `/api/agents/history/:id` | GET | Historique session |
| `/api/billing/checkout` | POST | Stripe Checkout Session |
| `/api/billing/portal` | POST | Stripe Customer Portal |
| `/api/feedback` | POST | Notation réponse (1-5) |

## Déploiement Vercel

1. Importer le dépôt sur [vercel.com](https://vercel.com/new)
2. Framework auto-détecté : **Next.js**
3. Variables d'environnement (voir tableau ci-dessus)
4. Deploy → URL `https://oupsii.vercel.app`

Le fichier `vercel.json` configure automatiquement les env vars et la région (CDG).

## Build

```bash
npm run build
```

## Fonctionnalités

- ✅ Landing page animée (hero, features, pricing, CTA trial 7j)
- ✅ Auth (register/login) avec redirect intelligent
- ✅ Quiz diagnostic multi-étapes avec barre de progression
- ✅ Dashboard + chat agent conversationnel (11 matières)
- ✅ Stripe Checkout + Customer Portal
- ✅ Feedback 1-5 étoiles sur chaque réponse
- ✅ Page compte/profil avec statut abonnement
- ✅ Dark mode (persistant)
- ✅ Responsive mobile + desktop
- ✅ SSR-ready (metadata SEO, OpenGraph)

## Workflow utilisateur

```
Landing → Register → Quiz diagnostic → Dashboard (chat agent)
                                    ↓
                              Trial 7j actif
                                    ↓
                              Pricing → Stripe Checkout
                                    ↓
                              Abonnement actif → Account (portal)
```

## Licence

Propriétaire — © Oupsii
