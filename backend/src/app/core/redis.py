# src/app/core/redis.py
"""
Redis async connection pool and slowapi rate limiter.

Exports `redis_pool` for cache / refresh token operations,
and `limiter` to be attached to FastAPI.
"""

from __future__ import annotations

from redis.asyncio import ConnectionPool, Redis
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

# ---------------------------------------------------------------------------
# Redis Pool
# ---------------------------------------------------------------------------
_pool = ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True,  # Automatically decode bytes to str
    max_connections=100,  # Max connections in pool
)
redis_pool = Redis(connection_pool=_pool)

# ---------------------------------------------------------------------------
# Rate Limiter (slowapi)
# ---------------------------------------------------------------------------
# We configure slowapi to use standard memory locally if needed, but in
# production it should technically be hooked up to Redis to distribute limit.
# For simplicity in this scaffold, Limiter uses the default memory backend.
# In a real distributed deployment, Limiter(storage_uri=settings.REDIS_URL) is used.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri=settings.REDIS_URL if settings.is_production else "memory://",
)
