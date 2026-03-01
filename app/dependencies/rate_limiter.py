from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import time


from app.core.cache import get_redis, RedisError

_use_redis = False
_redis_client = None
try:
    _redis_client = get_redis()
    _redis_client.ping()
    _use_redis = True
except Exception:
    _use_redis = False

_attempts: dict[str, tuple[int, float]] = {}
RATE_LIMIT = 5
PER_SECONDS = 60


def _get_ip(request: Request) -> str:
    return request.client.host


def check_rate_limit(ip: str) -> None:
    """Verify that the given IP has not exceeded the rate limit.
    Raises HTTPException if the limit is breached.
    """
    if _use_redis and _redis_client is not None:
        key = f"rate_limit:{ip}"
        try:
            count = _redis_client.get(key)
            if count is not None and int(count) >= RATE_LIMIT:
                raise HTTPException(
                    status_code=HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "rate_limit_exceeded",
                        "message": f"Too many login attempts, please try again after {PER_SECONDS} seconds."
                    }
                )
        except RedisError:
            pass

    now = time.time()
    rec = _attempts.get(ip)
    if rec:
        count, first_time = rec
        if now - first_time > PER_SECONDS:
            return
        if count >= RATE_LIMIT:
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": f"Too many login attempts, please try again after {PER_SECONDS} seconds."
                }
            )


def increment_attempt(ip: str) -> None:
    if _use_redis and _redis_client is not None:
        key = f"rate_limit:{ip}"
        try:
            pipe = _redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, PER_SECONDS)
            pipe.execute()
            return
        except RedisError:
            pass

    now = time.time()
    rec = _attempts.get(ip)
    if rec:
        count, first_time = rec
        if now - first_time > PER_SECONDS:
            count = 0
            first_time = now
    else:
        count = 0
        first_time = now

    count += 1
    _attempts[ip] = (count, first_time)


def reset_attempts(ip: str) -> None:
    if _use_redis and _redis_client is not None:
        try:
            _redis_client.delete(f"rate_limit:{ip}")
            return
        except RedisError:
            pass
    _attempts.pop(ip, None)


def rate_limit_dependency(request: Request):
    ip = _get_ip(request)
    check_rate_limit(ip)
    return True
