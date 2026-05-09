"""
MAMA-LENS AI — Cache Client
Uses Redis in production, in-memory dict in development (no Redis server needed).
"""
import json
import time
from typing import Any, Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class InMemoryCache:
    """Simple in-memory cache for development — no Redis server required."""

    def __init__(self):
        self._store: dict = {}   # key -> (value, expires_at or None)

    def _is_expired(self, key: str) -> bool:
        if key not in self._store:
            return True
        _, expires_at = self._store[key]
        if expires_at and time.time() > expires_at:
            del self._store[key]
            return True
        return False

    async def ping(self) -> bool:
        return True

    async def close(self):
        pass

    async def get(self, key: str) -> Optional[str]:
        if self._is_expired(key):
            return None
        value, _ = self._store[key]
        return value

    async def set(self, key: str, value: str, expire: int = None) -> bool:
        expires_at = time.time() + expire if expire else None
        self._store[key] = (value, expires_at)
        return True

    async def delete(self, *keys: str) -> int:
        count = 0
        for key in keys:
            if key in self._store:
                del self._store[key]
                count += 1
        return count

    async def exists(self, key: str) -> bool:
        return not self._is_expired(key)

    async def get_json(self, key: str) -> Optional[Any]:
        value = await self.get(key)
        return json.loads(value) if value else None

    async def set_json(self, key: str, value: Any, expire: int = None) -> bool:
        return await self.set(key, json.dumps(value, default=str), expire)

    async def check_rate_limit(self, identifier: str, limit: int, window_seconds: int):
        key = f"rl:{identifier}"
        data = await self.get_json(key) or {"count": 0, "reset_at": time.time() + window_seconds}
        if time.time() > data["reset_at"]:
            data = {"count": 0, "reset_at": time.time() + window_seconds}
        data["count"] += 1
        await self.set_json(key, data, expire=window_seconds)
        allowed = data["count"] <= limit
        return allowed, max(0, limit - data["count"])

    async def store_otp(self, identifier: str, otp: str, expire: int = 300):
        await self.set(f"otp:{identifier}", otp, expire)

    async def verify_otp(self, identifier: str, otp: str) -> bool:
        stored = await self.get(f"otp:{identifier}")
        if stored and stored == otp:
            await self.delete(f"otp:{identifier}")
            return True
        return False

    async def store_session(self, session_id: str, data: dict, expire: int = 3600):
        await self.set_json(f"session:{session_id}", data, expire)

    async def get_session(self, session_id: str) -> Optional[dict]:
        return await self.get_json(f"session:{session_id}")

    async def invalidate_session(self, session_id: str):
        await self.delete(f"session:{session_id}")

    async def cache_risk_assessment(self, user_id: str, result: dict, expire: int = 3600):
        await self.set_json(f"risk:{user_id}", result, expire)

    async def get_cached_risk_assessment(self, user_id: str) -> Optional[dict]:
        return await self.get_json(f"risk:{user_id}")

    async def invalidate_user_cache(self, user_id: str):
        await self.delete(f"risk:{user_id}", f"user:{user_id}")


# Use Redis in production, in-memory in dev
def _make_client():
    if settings.APP_ENV == "production":
        try:
            import redis.asyncio as aioredis
            client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            logger.info("Using Redis cache")
            return client
        except ImportError:
            logger.warning("redis package not installed, falling back to in-memory cache")
    logger.info("Using in-memory cache (dev mode)")
    return InMemoryCache()


redis_client = _make_client()


async def get_redis():
    return redis_client
