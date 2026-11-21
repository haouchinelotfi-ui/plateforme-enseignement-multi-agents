"""
Service d'emails transactionnels via Resend :
- Email de bienvenue (guide de démarrage)
- Relance après 48h d'inactivité
- Rappel J+6 avant expiration du trial
"""
import resend
from .config import settings

def _send(to: str, subject: str, html: str) -> dict | None:
    if not settings.RESEND_API_KEY:
        # Mode dev sans clé : on logge au lieu d'envoyer
        print(f"[EMAIL-DEV] to={to} subject={subject}")
        return None
    resend.api_key = settings.RESEND_API_KEY
    return resend.Emails.send(
        from_email=settings.FROM_EMAIL,
        to=[to],
        subject=subject,
        html=html,
    )


def send_welcome(email: str, level_name: str | None = None) -> dict | None:
    level_text = f" pour le niveau <strong>{level_name}</strong>" if level_name else ""
    return _send(
        email,
        "Bienvenue sur la plateforme ! 🎓",
        f"""
        <h2>Bienvenue !</h2>
        <p>Ton compte est créé{level_text}. Tu bénéficies de <strong>7 jours d'accès gratuit</strong>
        à plus de 100 agents pédagogiques spécialisés.</p>
        <h3>Pour bien démarrer :</h3>
        <ol>
          <li>Complète le quiz de diagnostic si ce n'est pas fait.</li>
          <li>Choisis ta matière et pose ta première question.</li>
          <li>Note les réponses pour aider à améliorer le service.</li>
        </ol>
        <p>Bonne réussite ! L'équipe pédagogique.</p>
        """,
    )


def send_inactivity_reminder(email: str) -> dict | None:
    return _send(
        email,
        "On te manque ! Reviens progresser 📚",
        f"""
        <h2>Cela fait 48h que tu n'as pas étudié.</h2>
        <p>Ton essai gratuit continue. Reprends où tu en étais et garde le rythme !
        Une seule question par jour suffit à progresser.</p>
        <p><a href="{settings.FRONTEND_URL}">Revenir maintenant →</a></p>
        """,
    )


def send_trial_expiry_warning(email: str, days_left: int = 1) -> dict | None:
    return _send(
        email,
        f"Ton essai gratuit expire dans {days_left} jour(s) ⏰",
        f"""
        <h2>Dernier jour(s) d'essai !</h2>
        <p>Ton accès gratuit se termine bientôt. Pour continuer à bénéficier
        de tous les agents pédagogiques sans interruption, abonne-toi dès maintenant.</p>
        <p><a href="{settings.FRONTEND_URL}/abonnement">S'abonner →</a></p>
        """,
    )
