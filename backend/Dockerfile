# Dockerfile
# Multi-stage production build using `uv`

# ---------------------------------------------------------------------------
# Stage 1: Builder
# ---------------------------------------------------------------------------
FROM python:3.12 AS builder

# Install uv globally via pip to avoid ghcr.io DNS resolution issues
RUN pip install uv
# Skip apt-get build-essential as most dependencies have wheels available. 
# This avoids extremely slow networking bottlenecks during build.

# Create a virtual environment that we will copy over to the runtime container
ENV VIRTUAL_ENV=/opt/venv
RUN uv venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /build

# Copy dependency files first to maximize Docker layer caching
COPY pyproject.toml uv.lock README.md ./

# Install dependencies without installing the project itself (--no-install-project)
RUN uv sync --active --locked --no-dev --no-install-project

# Copy project source and install the project itself
COPY src/ src/
RUN uv sync --active --locked --no-dev

# ---------------------------------------------------------------------------
# Stage 2: Runtime
# ---------------------------------------------------------------------------
FROM python:3.12 AS runtime

# Never run as root in production
RUN useradd --create-home --uid 1001 appuser
USER appuser
WORKDIR /home/appuser/app

# Copy the pre-built virtual environment from the builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source code and config files
COPY --chown=appuser:appuser src/ src/
COPY --chown=appuser:appuser alembic/ alembic/
COPY --chown=appuser:appuser alembic.ini .

# Set safe defaults that can be overridden in docker-compose or via env vars
ENV ENVIRONMENT=production
ENV WEB_CONCURRENCY=4
ENV PORT=8000
ENV PYTHONPATH=/home/appuser/app/src

# Gunicorn runs Uvicorn workers. This handles process management properly.
ENTRYPOINT ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
