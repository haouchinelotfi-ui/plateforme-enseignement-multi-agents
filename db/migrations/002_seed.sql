-- ============================================================================
-- Script de Seed Initial — Niveaux, Matières et Agents (extrait représentatif)
-- ============================================================================

-- Niveaux CEM
INSERT INTO levels (code, name, cycle) VALUES
  ('1AM', '1ère Année Moyenne', 'CEM'),
  ('2AM', '2ème Année Moyenne', 'CEM'),
  ('3AM', '3ème Année Moyenne', 'CEM'),
  ('4AM', '4ème Année Moyenne (BEM)', 'CEM')
ON CONFLICT (code) DO NOTHING;

-- Niveaux Lycée
INSERT INTO levels (code, name, cycle) VALUES
  ('1AS', '1ère Année Secondaire', 'LYCEE'),
  ('2AS', '2ème Année Secondaire', 'LYCEE'),
  ('3AS_MATH', '3ème AS — Série Maths', 'LYCEE'),
  ('3AS_SCI', '3ème AS — Sciences Expérimentales', 'LYCEE'),
  ('3AS_TECH', '3ème AS — Série Technique Maths', 'LYCEE'),
  ('3AS_LETTRES', '3ème AS — Lettres & Philosophie', 'LYCEE'),
  ('3AS_LANG', '3ème AS — Langues Étrangères', 'LYCEE')
ON CONFLICT (code) DO NOTHING;

-- Matières
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
-- Agents : extrait représentatif (le générateur ci-dessous crée les 100+)
-- Chaque agent reçoit un system_prompt pédagogique adapté au programme officiel.
-- ---------------------------------------------------------------------------

-- Helper : modèle de prompt par matière/cycle
-- En production, ces prompts seraient rédigés finement par matière.
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

-- Compteur de vérification
SELECT 'Niveaux: ' || count(*) FROM levels;
SELECT 'Matières: ' || count(*) FROM subjects;
SELECT 'Agents créés: ' || count(*) FROM agents;
