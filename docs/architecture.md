# AMS — Architecture Overview
> Quick-reference for new developers. Read this first.

---

## Tech Stack at a Glance

| Concern | Choice |
|---------|--------|
| Framework | FastAPI 0.115+ (async-first) |
| ASGI server | Uvicorn (dev) · Gunicorn + Uvicorn workers (prod) |
| DB | PostgreSQL 16 via SQLAlchemy 2.x async + asyncpg |
| Migrations | Alembic (autogenerate from ORM models) |
| Cache / Sessions | Redis 7 via redis-py async |
| Auth | JWT (access) + opaque UUID stored in Redis (refresh) |
| Package manager | `uv` — dependencies declared in `pyproject.toml`, lockfile is `uv.lock` |
| Python | 3.12+ |

---

## Project Layout

```
AMS/
├── src/app/         ← all application source code
│   ├── api/v1/      ← thin route handlers only (no business logic here)
│   ├── services/    ← business logic; orchestrates repositories
│   ├── repositories/← async DB/Redis access only; zero business logic
│   ├── models/      ← SQLAlchemy ORM models
│   ├── schemas/     ← Pydantic v2 request / response schemas
│   ├── core/        ← DB engine, Redis pool, JWT utils, lifespan hooks
│   ├── middleware/  ← logging, tracing, CORS / rate-limit
│   ├── workers/     ← ARQ background task definitions
│   ├── config.py    ← single Settings class, loaded once via lru_cache
│   ├── dependencies.py ← shared FastAPI Depends() helpers
│   ├── exceptions.py   ← AppException hierarchy + global error handlers
│   └── main.py      ← app factory + lifespan context manager
├── tests/
│   ├── unit/        ← service logic tested with mocked repositories
│   └── integration/ ← real test-DB + Redis (no mocks)
├── alembic/         ← migration env and version scripts
├── docker/          ← Dockerfile (multi-stage) + docker-compose
└── .github/workflows/ci.yml  ← lint → typecheck → test → docker build
```

---

## Layered Architecture (strict call direction)

```
HTTP Request
    │
    ▼
Router (api/v1/)      ← validates input, calls service, returns schema
    │
    ▼
Service (services/)   ← business logic, raises AppException on failures
    │
    ▼
Repository (repositories/)  ← async SQLAlchemy / Redis queries only
    │
    ▼
Database / Redis
```

> **Rule:** lower layers must never import from higher layers.

---

## Key Design Decisions

### Settings (`src/app/config.py`)
- Single `Settings(BaseSettings)` class. Import the module-level `settings` singleton everywhere.
- `ENVIRONMENT` is a `StrEnum`: `local | staging | production`.
- `DEBUG=True` in production raises a `ValueError` at startup — prevents accidental misconfiguration.

### Database (`src/app/core/database.py`)
- SQLAlchemy 2.x **async** engine + `AsyncSession`.
- All models use `Mapped[T]` / `mapped_column()` — the legacy `Column()` API is banned.
- Every model inherits `Base` **and** `TimestampMixin` (adds `created_at`, `updated_at`).
- Sessions are injected via `Depends(get_db_session)` — never use a global session.

### Auth Flow
1. `POST /api/v1/auth/login` → returns **access token** (JWT, 15 min) + **refresh token** (UUID, stored in Redis for 7 days).
2. `POST /api/v1/auth/refresh` → validates refresh token in Redis, issues new access token.
3. `POST /api/v1/auth/logout` → deletes refresh token from Redis (instant invalidation).
4. Protected routes use `Depends(get_current_user)` declared at **router level**, not per-route.
5. Passwords are bcrypt-hashed (cost factor 12) and **never returned in any response**.

### Error Handling
All domain errors are `AppException` subclasses. A global handler converts them to:
```json
{ "error": "<ERROR_CODE>", "detail": "<human message>" }
```
In production, unhandled exceptions are caught, logged via structlog, and a generic `500` is returned — no stack traces to clients.

### Observability
- **structlog**: JSON in production/staging, coloured console in local.
- Every request is tagged with a `request_id` UUID and logs `method`, `path`, `status_code`, `duration_ms`.
- **OpenTelemetry** (OTLP HTTP): instruments FastAPI, SQLAlchemy, httpx, Redis.
- **Prometheus** metrics exposed at `/metrics`.

### Health Probes
| Endpoint | Auth | Purpose |
|----------|------|---------|
| `GET /healthz` | None | Liveness — always `200 {"status":"ok"}` |
| `GET /readyz` | None | Readiness — `200` only if DB + Redis reachable; else `503` |

---

## Local Development

```bash
# 1. Copy env file and fill in values
cp .env.example .env

# 2. Install dependencies (uv reads pyproject.toml)
uv sync --group dev

# 3. Start backing services
docker compose -f docker/docker-compose.yml up postgres redis -d

# 4. Run migrations
uv run alembic upgrade head

# 5. Start dev server (auto-reload)
uv run uvicorn app.main:app --reload --port 8000
```

---

## Running Tests

```bash
# All tests (unit + integration) with coverage
uv run pytest

# Unit tests only (fast, no DB/Redis needed)
uv run pytest tests/unit/

# Integration tests (need TEST_DATABASE_URL + REDIS_URL in .env)
uv run pytest tests/integration/
```

Coverage target: **≥ 80%** on `services/` and `repositories/` — enforced in CI.

---

## Adding a New Feature

1. **Model** → `src/app/models/<domain>.py` + inherit `Base, TimestampMixin`.
2. **Schema** → `src/app/schemas/<domain>.py` with Pydantic v2.
3. **Repository** → `src/app/repositories/<domain>.py` extending `BaseRepository`.
4. **Service** → `src/app/services/<domain>.py` — business logic only.
5. **Router** → `src/app/api/v1/<domain>.py` — register in `src/app/api/router.py`.
6. **Migration** → `uv run alembic revision --autogenerate -m "add <domain>"`.
7. **Tests** → unit test the service; integration-test the endpoints.
