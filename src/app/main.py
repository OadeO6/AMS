# src/app/main.py
"""
Application Factory.

Assembles routers, middlewares, exception handlers, and observability.
To run:
    uvicorn app.main:app --reload
"""

from __future__ import annotations

import prometheus_fastapi_instrumentator
from fastapi import FastAPI

from app.api.router import api_router
from app.config import settings
from app.core.events import lifespan
from app.exceptions import setup_exception_handlers
from app.middleware.logging import setup_logging_middleware
from app.middleware.security import setup_security_middlewares
from app.middleware.tracing import setup_tracing


def create_app() -> FastAPI:
    """Factory function to create and configure the FastAPI application."""

    # 1. Basic initialization
    app = FastAPI(
        title="AMS API",
        version="0.1.0",
        description="Academic Management System.",
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
    )

    # 2. Observability: Tracing
    # Must be done early to trace middleware and routers
    setup_tracing(app)

    # 3. Observability: Logging
    setup_logging_middleware(app)

    # 4. Observability: Metrics
    # Exposes Prometheus instrumentation endpoint at /metrics
    prometheus_fastapi_instrumentator.Instrumentator(
        excluded_handlers=["/metrics", "/healthz", "/readyz"]
    ).instrument(app).expose(app, include_in_schema=False)

    # 5. Security & Rate Limiting
    setup_security_middlewares(app)

    # 6. Exception Handlers
    setup_exception_handlers(app)

    # 7. Routers
    app.include_router(api_router)

    return app


app = create_app()
