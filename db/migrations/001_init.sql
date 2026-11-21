-- ============================================================================
-- Plateforme d'Enseignement Centralisée Multi-Agents
-- Schéma PostgreSQL complet — Partie 1 (Catalogue + Utilisateurs + Logs)
-- ============================================================================

-- Extension UUID
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Référentiel des Niveaux Scolaires (CEM & Lycée)
CREATE TABLE IF NOT EXISTS levels (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,       -- ex: '1AM', '4AM', '1AS_SC', '3AS_MATH'
    name VARCHAR(100) NOT NULL,             -- ex: '4ème Année Moyenne (BEM)'
    cycle VARCHAR(20) NOT NULL              -- 'CEM' ou 'LYCEE'
);

-- 2. Référentiel des Matières
CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL,       -- ex: 'mathematiques', 'physique', 'arabe'
    name VARCHAR(100) NOT NULL
);

-- 3. Registre Centralisé des 100+ Agents Spécialisés
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level_id INT REFERENCES levels(id) ON DELETE CASCADE,
    subject_id INT REFERENCES subjects(id) ON DELETE CASCADE,
    agent_name VARCHAR(120) NOT NULL,
    system_prompt TEXT NOT NULL,
    allowed_tools JSONB DEFAULT '[]'::jsonb,
    model_config JSONB DEFAULT '{"model": "gpt-4o-mini", "temperature": 0.3}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(level_id, subject_id)
);

-- 4. Utilisateurs, Période d'Essai (7 jours) & Abonnements
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    detected_level_id INT REFERENCES levels(id),
    trial_starts_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    trial_ends_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days'),
    subscription_status VARCHAR(30) DEFAULT 'trialing',
    stripe_customer_id VARCHAR(100) UNIQUE,
    stripe_subscription_id VARCHAR(100),
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Analytique, Télémétrie d'Usage & Feedback Élèves
CREATE TABLE IF NOT EXISTS usage_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    session_id UUID NOT NULL,
    tokens_input INT DEFAULT 0,
    tokens_output INT DEFAULT 0,
    latency_ms INT,
    rating SMALLINT CHECK (rating BETWEEN 1 AND 5),
    feedback_comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index optimisés
CREATE INDEX IF NOT EXISTS idx_agents_lookup ON agents(level_id, subject_id) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_usage_user_date ON usage_logs(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_usage_agent ON usage_logs(agent_id, created_at);
CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_status);
