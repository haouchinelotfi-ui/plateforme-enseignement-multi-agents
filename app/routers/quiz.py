"""
Quiz de diagnostic — 3-4 questions permettant d'identifier le niveau exact
de l'élève (ex: 4AM, 1AS, Bac) puis de l'associer à son profil.
"""
import uuid
from fastapi import APIRouter, Depends
from ..database import get_db
from ..models import DiagnosticSubmit, DiagnosticResult
from ..security import get_current_user_id

router = APIRouter(prefix="/api/quiz", tags=["quiz"])

# Banque de questions de diagnostic (par cycle)
QUIZ_BANK = [
    {
        "id": "q_cycle",
        "question": "Quel cycle scolaire suis-tu actuellement ?",
        "options": ["CEM (Moyen)", "Lycée (Secondaire)"],
        "maps_to": {"CEM (Moyen)": "CEM", "Lycée (Secondaire)": "LYCEE"},
    },
    {
        "id": "q_cem_year",
        "question": "Quelle année du cycle moyen ?",
        "options": ["1AM", "2AM", "3AM", "4AM (BEM)"],
        "maps_to": {v: v for v in ["1AM", "2AM", "3AM", "4AM"]},
        "depends_cycle": "CEM",
    },
    {
        "id": "q_lycee_year",
        "question": "Quelle année du lycée ?",
        "options": ["1AS", "2AS", "3AS (Terminale)"],
        "maps_to": {"1AS": "1AS", "2AS": "2AS", "3AS (Terminale)": "3AS"},
        "depends_cycle": "LYCEE",
    },
    {
        "id": "q_lycee_series",
        "question": "Quelle série en terminale ?",
        "options": ["Maths", "Sciences Exp.", "Technique Maths", "Lettres", "Langues"],
        "maps_to": {
            "Maths": "3AS_MATH",
            "Sciences Exp.": "3AS_SCI",
            "Technique Maths": "3AS_TECH",
            "Lettres": "3AS_LETTRES",
            "Langues": "3AS_LANG",
        },
        "depends_cycle": "LYCEE",
    },
]


@router.get("/diagnostic")
async def get_diagnostic_quiz():
    """Retourne les questions de diagnostic adaptatives."""
    return {"questions": QUIZ_BANK}


@router.post("/diagnostic", response_model=DiagnosticResult)
async def submit_diagnostic(
    payload: DiagnosticSubmit, user_id: str = Depends(get_current_user_id)
):
    """Détermine le niveau exact à partir des réponses et l'associe au profil."""
    detected_code = None
    cycle = None

    # Première réponse : détermine le cycle
    for ans in payload.answers:
        if ans.question_id == "q_cycle":
            cycle = QUIZ_BANK[0]["maps_to"].get(ans.answer)
            break

    # Recherche du code de niveau le plus précis
    for q in QUIZ_BANK[1:]:
        if q.get("depends_cycle") and q["depends_cycle"] != cycle:
            continue
        for ans in payload.answers:
            if ans.question_id == q["id"]:
                mapped = q["maps_to"].get(ans.answer)
                if mapped:
                    detected_code = mapped

    if not detected_code:
        detected_code = "1AM"  # défaut prudent

    db = get_db()
    level_id = await db.fetchval(
        "SELECT id FROM levels WHERE code = $1", detected_code
    )
    await db.execute(
        "UPDATE users SET detected_level_id = $1, last_active_at = NOW() WHERE id = $2",
        level_id,
        uuid.UUID(user_id),
    )

    level_name = await db.fetchval(
        "SELECT name FROM levels WHERE code = $1", detected_code
    )
    return DiagnosticResult(
        detected_level_code=detected_code, level_name=level_name or detected_code
    )
