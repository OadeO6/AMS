# src/app/api/v1/health.py
"""
Health check endpoints — no authentication required.

Liveness  GET /healthz  → 200 {"status": "ok"}
Readiness GET /readyz   → 200 if DB + Redis reachable, 503 otherwise.

Used by Kubernetes / Docker healthchecks and load balancers.
"""

from __future__ import annotations

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.database import AsyncSessionFactory

router = APIRouter(tags=["health"])


@router.get(
    "/healthz",
    summary="Liveness probe",
    status_code=status.HTTP_200_OK,
)
async def liveness() -> dict[str, str]:
    """Always returns 200. Signals the process is running."""
    return {"status": "ok"}


@router.get(
    "/readyz",
    summary="Readiness probe",
    status_code=status.HTTP_200_OK,
)
async def readiness() -> JSONResponse:
    """Return 200 only when the DB and Redis are reachable.

    The Redis check is performed via the module-level pool imported from
    ``core.redis`` (written in Layer 6). If redis is unreachable it is
    reported in the response but does NOT raise an exception during startup
    — the pod will simply never become Ready.
    """
    failures: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Database check
    # ------------------------------------------------------------------
    try:
        async with AsyncSessionFactory() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        failures["database"] = str(exc)

    # ------------------------------------------------------------------
    # Redis check (deferred import so Layer 5 compiles before redis.py exists)
    # ------------------------------------------------------------------
    try:
        from app.core.redis import redis_pool

        await redis_pool.ping()
    except Exception as exc:
        failures["redis"] = str(exc)

    if failures:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "degraded", "failures": failures},
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok"},
    )
