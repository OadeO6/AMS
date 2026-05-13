"""
ARQ connection pool — singleton for the web process.

The ARQ pool is separate from the Redis pool used for caching/rate-limiting
(core/redis.py). ARQ manages its own connection lifecycle and job serialisation.

Usage
-----
In FastAPI route handlers, use the ``ArqPool`` annotated dependency:

    from app.core.arq_pool import ArqPool

    @router.post("/grades/{grade_id}/publish")
    async def publish_grade(grade_id: UUID, arq: ArqPool, session: DBSession):
        ...
        emitter = NotificationEmitter(arq)
        await emitter.emit(NotificationEvent.GRADE_PUBLISHED, user_id=..., ...)

Lifecycle
---------
Call ``init_arq_pool()`` in the application lifespan startup and
``close_arq_pool()`` in shutdown (see core/events.py).
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends

_arq_pool = None  # ArqRedis | None — intentionally untyped to avoid import at module level


async def init_arq_pool() -> None:
    """Create the module-level ARQ pool. Call once at application startup."""
    global _arq_pool  # noqa: PLW0603
    from arq import create_pool
    from arq.connections import RedisSettings

    from app.config import settings

    _arq_pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))


async def close_arq_pool() -> None:
    """Drain and close the ARQ pool. Call once at application shutdown."""
    global _arq_pool  # noqa: PLW0603
    if _arq_pool is not None:
        await _arq_pool.aclose()
        _arq_pool = None


async def get_arq_pool():  # type: ignore[return]
    """FastAPI dependency — yield the shared ARQ pool.

    Raises RuntimeError if ``init_arq_pool()`` was never called
    (i.e. the lifespan hook is missing).
    """
    if _arq_pool is None:
        raise RuntimeError(
            "ARQ pool has not been initialised. "
            "Ensure init_arq_pool() is called in your lifespan startup."
        )
    return _arq_pool


# Annotated dependency alias — import this in route handlers
ArqPool = Annotated[object, Depends(get_arq_pool)]  # type: ignore[valid-type]
# (object is a stand-in for ArqRedis to avoid a heavy import at module level;
#  the pool is fully typed at the call site via the Emitter's __init__ hint)
