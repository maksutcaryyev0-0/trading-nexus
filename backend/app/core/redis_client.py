import redis.asyncio as redis
from loguru import logger
from app.core.config import settings

_redis = None


async def init_redis():
    global _redis
    _redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
    await _redis.ping()
    logger.info("Redis connected")


def get_redis():
    return _redis


async def cache_set(key: str, value: str, ttl: int = 300):
    if _redis:
        await _redis.setex(key, ttl, value)


async def cache_get(key: str) -> str | None:
    if _redis:
        return await _redis.get(key)
    return None


async def cache_delete(key: str):
    if _redis:
        await _redis.delete(key)
