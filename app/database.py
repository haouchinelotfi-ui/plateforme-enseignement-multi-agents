"""Pool de connexion PostgreSQL (asyncpg) et client Redis."""
import asyncpg
import redis.asyncio as redis
from .config import settings

_pool: asyncpg.Pool | None = None
_redis: redis.Redis | None = None


async def init_db() -> asyncpg.Pool:
    """Initialise le pool PostgreSQL (à appeler au démarrage)."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=2,
            max_size=10,
        )
    return _pool


async def close_db() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_db() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Pool DB non initialisé — appeler init_db() au startup.")
    return _pool


async def init_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None


def get_redis() -> redis.Redis:
    if _redis is None:
        raise RuntimeError("Redis non initialisé — appeler init_redis() au startup.")
    return _redis
