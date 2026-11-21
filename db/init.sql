-- ============================================================================
-- Plateforme d'Enseignement Centralisée Multi-Agents
-- Script d'initialisation UNIFIÉ — à exécuter sur Neon / Supabase / Render PG
--
-- Usage (psql) :
--   psql "$DATABASE_URL" -f db/init.sql
--
-- Usage (Supabase) : copier-coller dans SQL Editor
-- Usage (Neon)     : copier-coller dans le SQL web editor
--
-- Ce fichier regroupe 001_init.sql (schéma) + 002_seed.sql (données).
-- Il est idempotent : peut être ré-exécuté sans erreur (IF NOT EXISTS / ON CONFLICT).
-- ============================================================================

BEGIN;

-- Extension UUID (pgcrypto) — requise pour gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- PARTIE 1 — SCHÉMA
-- ============================================================================

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

-- ============================================================================
-- PARTIE 2 — SEED (données initiales)
-- ============================================================================

-- Niveaux CEM (4 niveaux)
INSERT INTO levels (code, name, cycle) VALUES
  ('1AM', '1ère Année Moyenne', 'CEM'),
  ('2AM', '2ème Année Moyenne', 'CEM'),
  ('3AM', '3ème Année Moyenne', 'CEM'),
  ('4AM', '4ème Année Moyenne (BEM)', 'CEM')
ON CONFLICT (code) DO NOTHING;

-- Niveaux Lycée (7 niveaux / séries)
INSERT INTO levels (code, name, cycle) VALUES
  ('1AS', '1ère Année Secondaire', 'LYCEE'),
  ('2AS', '2ème Année Secondaire', 'LYCEE'),
  ('3AS_MATH', '3ème AS — Série Maths', 'LYCEE'),
  ('3AS_SCI', '3ème AS — Sciences Expérimentales', 'LYCEE'),
  ('3AS_TECH', '3ème AS — Série Technique Maths', 'LYCEE'),
  ('3AS_LETTRES', '3ème AS — Lettres & Philosophie', 'LYCEE'),
  ('3AS_LANG', '3ème AS — Langues Étrangères', 'LYCEE')
ON CONFLICT (code) DO NOTHING;

-- Matières (11 matières)
INSERT INTO subjects (slug, name) VALUES
  ('mathematiques', 'Mathématiques'),
  ('physique', 'Physique'),
  ('chimie', 'Chimie'),
  ('svt', 'Sciences de la Vie et de la Terre'),
  ('arabe', 'Langue Arabe'),
  ('francais', 'Langue Française'),
  ('anglais', 'Langue Anglaise'),
  ('histoire_geo', 'Histoire-Géographie'),
  ('philo', 'Philosophie'),
  ('islamiques', 'Sciences Islamiques'),
  ('informatique', 'Informatique')
ON CONFLICT (slug) DO NOTHING;

-- ---------------------------------------------------------------------------
-- Génération automatique des agents (11 niveaux × 11 matières = 121 agents)
-- Chaque agent reçoit un system_prompt pédagogique adapté au programme officiel
-- algérien, une liste d'outils autorisés (sandboxing) et une config de modèle.
-- En production, ces prompts peuvent être affinés individuellement via UPDATE.
-- ---------------------------------------------------------------------------
INSERT INTO agents (level_id, subject_id, agent_name, system_prompt, allowed_tools, model_config)
SELECT
  l.id, s.id,
  'Tuteur ' || s.name || ' — ' || l.code,
  'Tu es un enseignant expert en ' || s.name || ' pour le niveau ' || l.name ||
  '. Ton rôle est d''accompagner l''élève selon le programme officiel algérien, ' ||
  'd''expliquer les notions avec clarté, de proposer des exercices progressifs ' ||
  'et de vérifier la compréhension par des questions ciblées. ' ||
  'Adapte toujours ton vocabulaire au niveau de l''élève. ' ||
  'Sois bienveillant, patient et encourageant. Réponds en français, ' ||
  'sauf pour les matières de langue où tu réponds dans la langue étudiée.',
  CASE
    WHEN s.slug IN ('mathematiques','physique','chimie') THEN
      '["calculatrice_formelle","traceur_graphe","quiz_gen","formule_resolver"]'::jsonb
    WHEN s.slug IN ('svt','histoire_geo','philo','islamiques') THEN
      '["quiz_gen","schema_explainer","resume_gen"]'::jsonb
    WHEN s.slug IN ('arabe','francais','anglais') THEN
      '["quiz_gen","conjugueur","correcteur_orthographique"]'::jsonb
    ELSE
      '["quiz_gen","code_runner","schema_explainer"]'::jsonb
  END,
  '{"model": "gpt-4o-mini", "temperature": 0.3}'::jsonb
FROM levels l
CROSS JOIN subjects s
WHERE NOT EXISTS (
  SELECT 1 FROM agents a WHERE a.level_id = l.id AND a.subject_id = s.id
);

-- ============================================================================
-- VÉRIFICATION — compteurs de contrôle
-- ============================================================================

SELECT 'Niveaux: ' || count(*) AS nb_levels FROM levels;
SELECT 'Matières: ' || count(*) AS nb_subjects FROM subjects;
SELECT 'Agents créés: ' || count(*) AS nb_agents FROM agents WHERE is_active = TRUE;

-- Répartition par cycle (vue rapide)
SELECT l.cycle, count(*) AS nb_agents
FROM agents a
JOIN levels l ON a.level_id = l.id
WHERE a.is_active = TRUE
GROUP BY l.cycle
ORDER BY l.cycle;

COMMIT;

-- ============================================================================
-- FIN — La base est prête à recevoir les connexions du backend FastAPI.
-- ============================================================================