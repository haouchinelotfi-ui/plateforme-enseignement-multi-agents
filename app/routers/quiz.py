"""Router quiz: questions diagnostic + soumission + détection niveau.

Questions codées en dur (banque statique) couvrant CEM et LYCEE.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Level
from app.schemas import QuizQuestion, QuizSubmission, QuizResult

router = APIRouter(prefix="/quiz", tags=["quiz"])

# --------------------------------------------------------------------------- #
#  Banque de questions (2 par matière-clé, niveau agnostique)
#  level_hint: niveau estimé si bonne réponse
# --------------------------------------------------------------------------- #
QUESTIONS: list[dict] = [
    {
        "subject_slug": "mathematiques",
        "question": "Résous: 3x + 7 = 22. Quelle est la valeur de x ?",
        "options": ["x = 5", "x = 7", "x = 15", "x = 29"],
        "correct_index": 0,
        "level_hint": "CEM-2",
    },
    {
        "subject_slug": "mathematiques",
        "question": "Quelle est la dérivée de f(x) = x² + 3x ?",
        "options": ["2x", "x + 3", "2x + 3", "x²"],
        "correct_index": 2,
        "level_hint": "LYC-1",
    },
    {
        "subject_slug": "physique",
        "question": "Quelle est l'unité de la force dans le SI ?",
        "options": ["Joule", "Newton", "Watt", "Pascal"],
        "correct_index": 1,
        "level_hint": "CEM-3",
    },
    {
        "subject_slug": "physique",
        "question": "Énonce la seconde loi de Newton.",
        "options": [
            "F = ma",
            "E = mc²",
            "v = d/t",
            "P = mv",
        ],
        "correct_index": 0,
        "level_hint": "LYC-2",
    },
    {
        "subject_slug": "francais",
        "question": "Identifie la nature du mot « rapidement » dans: « Il court rapidement ».",
        "options": ["Adjectif", "Verbe", "Adverbe", "Nom"],
        "correct_index": 2,
        "level_hint": "CEM-1",
    },
    {
        "subject_slug": "francais",
        "question": "Qu'est-ce qu'une métaphore ?",
        "options": [
            "Une comparaison sans mot-outil",
            "Une répétition",
            "Une question rhétorique",
            "Un contraire",
        ],
        "correct_index": 0,
        "level_hint": "LYC-1",
    },
    {
        "subject_slug": "anglais",
        "question": "Choose the correct form: 'She ___ to school every day.'",
        "options": ["go", "goes", "going", "gone"],
        "correct_index": 1,
        "level_hint": "CEM-1",
    },
    {
        "subject_slug": "anglais",
        "question": "What is the passive voice of: 'They built the house'?",
        "options": [
            "The house was built",
            "The house is building",
            "They were built",
            "The house built",
        ],
        "correct_index": 0,
        "level_hint": "LYC-1",
    },
    {
        "subject_slug": "svt",
        "question": "Quel organe pompe le sang dans le corps humain ?",
        "options": ["Le foie", "Le cœur", "Les poumons", "Le cerveau"],
        "correct_index": 1,
        "level_hint": "CEM-2",
    },
    {
        "subject_slug": "svt",
        "question": "Qu'est-ce que la photosynthèse ?",
        "options": [
            "Respiration des plantes",
            "Production de matière organique grâce à la lumière",
            "Absorption d'eau",
            "Croissance des racines",
        ],
        "correct_index": 1,
        "level_hint": "LYC-1",
    },
    {
        "subject_slug": "histoire-geo",
        "question": "Quelle est la capitale de l'Algérie ?",
        "options": ["Oran", "Alger", "Constantine", "Annaba"],
        "correct_index": 1,
        "level_hint": "CEM-1",
    },
    {
        "subject_slug": "histoire-geo",
        "question": "En quelle année l'Algérie a-t-elle obtenu son indépendance ?",
        "options": ["1954", "1962", "1965", "1972"],
        "correct_index": 1,
        "level_hint": "CEM-3",
    },
    {
        "subject_slug": "philosophie",
        "question": "Qui a dit « Je pense, donc je suis » ?",
        "options": ["Platon", "Descartes", "Kant", "Socrate"],
        "correct_index": 1,
        "level_hint": "LYC-2",
    },
    {
        "subject_slug": "informatique",
        "question": "Que signifie l'acronyme CPU ?",
        "options": [
            "Central Processing Unit",
            "Computer Personal Unit",
            "Central Print Unit",
            "Control Program Unit",
        ],
        "correct_index": 0,
        "level_hint": "CEM-4",
    },
    {
        "subject_slug": "arabe",
        "question": "ما هو جمع كلمة « كتاب » ؟",
        "options": ["كتب", "كتابات", "مكتب", "كاتب"],
        "correct_index": 0,
        "level_hint": "CEM-1",
    },
    {
        "subject_slug": "islamiques",
        "question": "Combien de piliers compte l'Islam ?",
        "options": ["3", "5", "7", "10"],
        "correct_index": 1,
        "level_hint": "CEM-1",
    },
]

# Map level_hint → level_id approximatif (détection simple)
LEVEL_ORDER = ["CEM-1", "CEM-2", "CEM-3", "CEM-4", "LYC-1", "LYC-2", "LYC-3S"]


def _detect_level(score_by_level: dict[str, int]) -> tuple[str, str]:
    """Retourne (code, name) basé sur le niveau le plus haut atteint."""
    best = "CEM-1"
    for code in LEVEL_ORDER:
        if score_by_level.get(code, 0) > 0:
            best = code
    names = {
        "CEM-1": "CEM 1ère année",
        "CEM-2": "CEM 2ème année",
        "CEM-3": "CEM 3ème année",
        "CEM-4": "CEM 4ème année",
        "LYC-1": "Lycée 1ère année",
        "LYC-2": "Lycée 2ème année",
        "LYC-3S": "Lycée 3ème année Sciences",
    }
    return best, names.get(best, best)


@router.get("", response_model=list[QuizQuestion])
async def get_quiz():
    return [
        QuizQuestion(id=str(uuid.uuid4()), **q) for q in QUESTIONS
    ]


@router.post("/submit", response_model=QuizResult)
async def submit_quiz(
    payload: QuizSubmission,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Construit une lookup question_id → question
    lookup = {str(i): q for i, q in enumerate(QUESTIONS)}
    # Le frontend envoie answers comme {question_id: chosen_index}
    # On rebuild via index si id non trouvé
    score_by_subject: dict[str, dict] = {}
    score_by_level: dict[str, int] = {}

    for qid, chosen in payload.answers.items():
        # On essaie de retrouver la question par position (le frontend génère des ids)
        # Fallback: si qid est numérique
        q = None
        if qid in lookup:
            q = lookup[qid]
        elif qid.isdigit() and int(qid) < len(QUESTIONS):
            q = QUESTIONS[int(qid)]
        if not q:
            continue
        subj = q["subject_slug"]
        score_by_subject.setdefault(subj, {"correct": 0, "total": 0})
        score_by_subject[subj]["total"] += 1
        if chosen == q["correct_index"]:
            score_by_subject[subj]["correct"] += 1
            score_by_level[q["level_hint"]] = score_by_level.get(q["level_hint"], 0) + 1

    code, name = _detect_level(score_by_level)

    # Met à jour le niveau détecté de l'utilisateur
    level = await db.scalar(select(Level).where(Level.code == code))
    if level:
        user.detected_level_id = level.id
        await db.commit()

    recommendation = (
        f"Ton niveau estimé est {name}. "
        f"Nous te recommandons de commencer par réviser les bases de ce niveau "
        f"puis progresser vers les notions plus avancées."
    )

    return QuizResult(
        detected_level_code=code,
        detected_level_name=name,
        score_by_subject=score_by_subject,
        recommendation=recommendation,
    )
