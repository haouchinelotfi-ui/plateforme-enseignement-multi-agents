"""Pool de connexion PostgreSQL (asyncpg) et client Redis."""
import logging
import asyncpg
import redis.asyncio as redis
from .config import settings

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None
_redis: redis.Redis | None = None


async def init_db() -> asyncpg.Pool | None:
    """Initialise le pool PostgreSQL. Retourne None si la DB est indisponible (démarrage résilient)."""
    global _pool
    if _pool is None:
        try:
            _pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL,
                min_size=1,
                max_size=10,
                timeout=5,
            )
            logger.info("Pool PostgreSQL initialisé avec succès.")
        except Exception as e:
            logger.warning("DB indisponible au démarrage: %s — l'app démarre en mode dégradé.", e)
            _pool = None
    return _pool


async def close_db() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_db() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Service DB indisponible. Configurez DATABASE_URL avec une base PostgreSQL valide.")
    return _pool


async def init_redis() -> redis.Redis | None:
    """Initialise Redis. Retourne None si indisponible (démarrage résilient)."""
    global _redis
    if _redis is None:
        try:
            _redis = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
            )
            await _redis.ping()
            logger.info("Redis initialisé avec succès.")
        except Exception as e:
            logger.warning("Redis indisponible au démarrage: %s — l'app démarre en mode dégradé.", e)
            _redis = None
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None


def get_redis() -> redis.Redis:
    if _redis is None:
        raise RuntimeError("Redis indisponible. Configurez REDIS_URL avec une instance Redis valide.")
    return _redis
