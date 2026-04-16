# src/app/repositories/token.py
"""
Redis-backed refresh token repository.

Refresh tokens are opaque UUIDs stored as Redis keys with a TTL.
Key format: ``refresh_token:{token_uuid}``
Value: user UUID as string

On logout or any security event, the key is deleted to immediately
invalidate the token — no need to wait for expiry.
"""

from __future__ import annotations

import uuid

from app.config import settings
from app.core.redis import redis_pool

_KEY_PREFIX = "refresh_token"


def _key(token: str) -> str:
    return f"{_KEY_PREFIX}:{token}"


class RefreshTokenRepository:
    """Async CRUD operations for refresh tokens stored in Redis."""

    async def store(self, user_id: uuid.UUID) -> str:
        """Create a new refresh token and persist it with a TTL.

        Returns
        -------
        str
            The opaque refresh token string (a UUID4) to return to the client.
        """
        token = str(uuid.uuid4())
        ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86_400
        await redis_pool.setex(
            name=_key(token),
            time=ttl_seconds,
            value=str(user_id),
        )
        return token

    async def get_user_id(self, token: str) -> str | None:
        """Return the user ID string linked to the refresh token, or ``None``."""
        result: str | None = await redis_pool.get(_key(token))
        return result

    async def revoke(self, token: str) -> None:
        """Delete the refresh token from Redis (immediate invalidation)."""
        await redis_pool.delete(_key(token))
