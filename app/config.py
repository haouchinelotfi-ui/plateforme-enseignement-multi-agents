"""Configuration centralisée via variables d'environnement."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base de données & Cache
    DATABASE_URL: str
    REDIS_URL: str

    # LLM
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"

    # Sécurité / JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID_MONTHLY: str = ""
    STRIPE_PRICE_ID_YEARLY: str = ""

    # Resend
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "ecole@exemple.com"

    # Divers
    FRONTEND_URL: str = "http://localhost:5173"
    ENVIRONMENT: str = "development"

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 30
    RATE_LIMIT_WINDOW_SECONDS: int = 3600

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()  # type: ignore[call-arg]
