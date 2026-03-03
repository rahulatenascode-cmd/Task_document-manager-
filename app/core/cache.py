import json
from typing import Any, Optional


try:
    import redis
    from redis.exceptions import RedisError
except ImportError:
    redis = None  # type: ignore
    class RedisError(Exception):
        pass

from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


_redis_client: Optional[Any] = None


def get_redis() -> "redis.Redis":
    """Return a singleton Redis client, configured from settings.
    Raises ImportError if the redis library is not installed.
    """
    if redis is None:
        raise ImportError("redis library is not installed; caching is disabled")

    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


def set_cache(key: str, value: Any, ex: Optional[int] = None) -> None:
    try:
        r = get_redis()
        r.set(key, json.dumps(value, default=str), ex=ex)
    except (RedisError, ImportError) as e:

        logger.warning(f"Redis set failed for {key}: {e}")


def get_cache(key: str) -> Any:
    try:
        r = get_redis()
        data = r.get(key)
        if data is None:
            return None
        return json.loads(data)
    except (RedisError, ImportError) as e:
        logger.warning(f"Redis get failed for {key}: {e}")
        return None


def delete_cache(key: str) -> None:
    try:
        r = get_redis()
        r.delete(key)
    except (RedisError, ImportError) as e:
        logger.warning(f"Redis delete failed for {key}: {e}")


def invalidate_prefix(prefix: str) -> None:
    """Delete all keys that start with the provided prefix."""
    try:
        r = get_redis()
        for k in r.scan_iter(f"{prefix}*"):
            r.delete(k)
    except (RedisError, ImportError) as e:
        logger.warning(f"Redis prefix invalidation failed for {prefix}: {e}")
