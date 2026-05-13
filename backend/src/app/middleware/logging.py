# src/app/middleware/logging.py
"""
Logging middleware and structlog configuration.

Ensures every request gets a unique request_id and is logged
with its status code and duration. Structlog is configured to
output JSON in production and readable colored text locally.
"""

from __future__ import annotations

import logging
import sys
import time
import uuid
from typing import TYPE_CHECKING, Any

import structlog

from app.config import settings

if TYPE_CHECKING:
    from collections.abc import Callable

    from fastapi import FastAPI, Request, Response

# ---------------------------------------------------------------------------
# Structlog Configuration
# ---------------------------------------------------------------------------


def setup_logging() -> None:
    """Configure structlog based on environment.

    - Production: JSON lines, minimal formatting.
    - Local: Colored, human-readable terminal output.
    """
    shared_processors: list[structlog.types.Processor] = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.contextvars.merge_contextvars,
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
        structlog.processors.format_exc_info,
    ]

    if settings.is_local:
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer(colors=True)
    else:
        # Production uses JSON
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *shared_processors,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            # structlog.validators.MemoryLogger(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    # Intercept default uvicorn/fastapi loggers to pipe them through structlog
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.LOG_LEVEL)

    # Disable duplicated uvicorn loggers
    for _log in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        l = logging.getLogger(_log)
        l.handlers.clear()
        l.propagate = True


# ---------------------------------------------------------------------------
# FastAPI Middleware
# ---------------------------------------------------------------------------


async def logging_middleware(request: Request, call_next: Callable[..., Any]) -> Response:
    """FastAPI HTTP Middleware that logs requests/responses.

    Binds a unique `request_id` context variable.
    Logs method, path, status, and duration in ms.
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    logger = structlog.get_logger("api.access")

    start_time = time.perf_counter()
    duration_ms: float = 0.0
    status_code: int = 500

    try:
        response: Response = await call_next(request)
        status_code = response.status_code
        # inject id back into headers
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Don't log health probes at INFO level to avoid noise, use DEBUG instead
        is_health = request.url.path in ("/healthz", "/readyz", "/metrics")
        log_level_func = logger.debug if is_health else logger.info

        log_level_func(
            "Access",
            method=request.method,
            path=request.url.path,
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
            ip=request.client.host if request.client else None,
        )


def setup_logging_middleware(app: FastAPI) -> None:
    """Attach the structlog middleware and init logging."""
    setup_logging()
    app.middleware("http")(logging_middleware)
