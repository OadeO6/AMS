# src/app/middleware/tracing.py
"""
OpenTelemetry initialization and instrumentation.

Wires OTLP export and instruments FastAPI, SQLAlchemy, HTTPX, and Redis.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.config import settings

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = structlog.get_logger()


def setup_tracing(app: FastAPI) -> None:
    """Configure completely automated distributed tracing across the stack."""

    if settings.is_local:
        # In local development, we shouldn't fail or warn loudly if OTLP is missing,
        # but we wire it up just in case someone is running jaeger locally.
        logger.debug("Configuring OpenTelemetry in local mode")

    resource = Resource.create({"service.name": settings.OTEL_SERVICE_NAME})
    provider = TracerProvider(resource=resource)

    # Use OTLP HTTP (e.g., targeted to Jaeger, Tempo or an OTEL collector)
    # Exporter automatically picks up settings.OTEL_EXPORTER_OTLP_ENDPOINT.
    otlp_exporter = OTLPSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    trace.set_tracer_provider(provider)

    # ------------------------------------------------------------------
    # Instrument everything globally
    # ------------------------------------------------------------------

    # 1. FastAPI (ASGI)
    # Ignore health routes to avoid swamping trace storage
    FastAPIInstrumentor.instrument_app(
        app,
        excluded_urls="healthz,readyz,metrics",
    )

    # 2. Redis
    RedisInstrumentor().instrument()

    # 3. HTTPX
    HTTPXClientInstrumentor().instrument()

    # Note: SQLAlchemy is instrumented later in database engine creation,
    # but we can optionally instrument engine broadly here. The safer
    # route is instrumenting the driver globally:
    try:
        from app.core.database import engine

        SQLAlchemyInstrumentor().instrument(
            engine=engine.sync_engine,
        )
    except Exception as e:
        logger.warning(f"Failed to instrument sqlalchemy globally: {e}")
