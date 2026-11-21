"""Seed des données: 3 niveaux, 11 matières, agents, questions quiz.

Exécuté au startup si la DB est vide.
"""
from datetime import timedelta, timezone, datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Level, Subject, Agent, User, CycleEnum, SubscriptionStatusEnum,
)

# --------------------------------------------------------------------------- #
#  Catalogue
# --------------------------------------------------------------------------- #
LEVELS = [
    {"id": 1, "code": "CEM-1", "name": "CEM 1ère année", "cycle": "CEM"},
    {"id": 2, "code": "CEM-2", "name": "CEM 2ème année", "cycle": "CEM"},
    {"id": 3, "code": "CEM-3", "name": "CEM 3ème année", "cycle": "CEM"},
    {"id": 4, "code": "CEM-4", "name": "CEM 4ème année", "cycle": "CEM"},
    {"id": 5, "code": "LYC-1", "name": "Lycée 1ère année (Tronc commun)", "cycle": "LYCEE"},
    {"id": 6, "code": "LYC-2", "name": "Lycée 2ème année", "cycle": "LYCEE"},
    {"id": 7, "code": "LYC-3S", "name": "Lycée 3ème année (Sciences)", "cycle": "LYCEE"},
    {"id": 8, "code": "LYC-3L", "name": "Lycée 3ème année (Lettres)", "cycle": "LYCEE"},
]

SUBJECTS = [
    ("mathematiques", "Mathématiques"),
    ("physique", "Physique"),
    ("svt", "Sciences de la Vie et de la Terre"),
    ("francais", "Français"),
    ("arabe", "Arabe"),
    ("anglais", "Anglais"),
    ("histoire-geo", "Histoire-Géographie"),
    ("philosophie", "Philosophie"),
    ("informatique", "Informatique"),
    ("islamiques", "Sciences islamiques"),
    ("tamazight", "Tamazight"),
]

SYSTEM_PROMPT_TEMPLATE = """Tu es {agent_name}, un tuteur pédagogique expert en {subject} pour des élèves de niveau {level} ({cycle}).

RÈGLES:
- Tu enseignes selon le programme officiel algérien.
- Tu es bienveillant, patient et encourageant.
- Tu expliques avec des exemples concrets adaptés au niveau.
- Si l'élève se trompe, guide-le sans donner la réponse directement.
- Réponds en français (ou en arabe si l'élève écrit en arabe).
- Sois concis (max 200 mots par réponse) sauf si l'élève demande une explication détaillée.
- Utilise des listes et des étapes pour structurer tes explications."""

# Mapping matières × niveaux (on crée un agent par couple actif)
ACTIVE_LEVELS = {
    "CEM": ["mathematiques", "physique", "svt", "francais", "arabe", "anglais", "histoire-geo", "informatique", "islamiques"],
    "LYCEE": ["mathematiques", "physique", "svt", "francais", "arabe", "anglais", "histoire-geo", "philosophie", "informatique", "islamiques", "tamazight"],
}


async def seed_if_empty(db: AsyncSession):
    """Insère le catalogue si les tables sont vides."""
    # Levels
    cnt = await db.scalar(select(func.count(Level.id)))
    if cnt == 0:
        for lv in LEVELS:
            db.add(Level(**lv))
        await db.flush()

    # Subjects
    cnt = await db.scalar(select(func.count(Subject.id)))
    if cnt == 0:
        for slug, name in SUBJECTS:
            db.add(Subject(slug=slug, name=name))
        await db.flush()

    # Agents
    cnt = await db.scalar(select(func.count(Agent.id)))
    if cnt == 0:
        levels = (await db.execute(select(Level))).scalars().all()
        subjects = {s.slug: s for s in (await db.execute(select(Subject))).scalars().all()}
        for lv in levels:
            cycle_key = "LYCEE" if lv.cycle == CycleEnum.LYCEE else "CEM"
            for slug in ACTIVE_LEVELS.get(cycle_key, []):
                subj = subjects.get(slug)
                if not subj:
                    continue
                agent_name = f"Tuteur {subj.name} - {lv.code}"
                db.add(Agent(
                    level_id=lv.id,
                    subject_id=subj.id,
                    agent_name=agent_name,
                    system_prompt=SYSTEM_PROMPT_TEMPLATE.format(
                        agent_name=agent_name, subject=subj.name,
                        level=lv.name, cycle=cycle_key,
                    ),
                    allowed_tools=["explain", "quiz", "example"],
                    model_config_json={"model": "gpt-4o-mini", "temperature": 0.7},
                    is_active=True,
                ))
        await db.commit()
