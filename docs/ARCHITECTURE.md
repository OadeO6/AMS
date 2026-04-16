# Architecture

> Defines the fundamental architecture, stack, and live project structure.
> Large architectural decisions (e.g. AI pipeline, file storage) should go in `/specs/arch/` and be referenced here.
## Developer Instructions

> **How to update:** Update stack decisions as they are finalized. Keep reasoning brief.
> Large architectural decisions (e.g. AI pipeline, file storage strategy) should go in individual
> files under `/specs/arch/` and be referenced here.
>
> **Keep in sync with:** `ENDPOINTS.md`, `DATABASE_SCHEMA.md`, `BUSINESS_RULES.md`, `DOC_HISTORY.md`
> **Update the Folder Structure section** whenever a new module, layer, or significant directory is added.
> Whenever the architecture changes (new layer, new service, stack decision), log the change in `DOC_HISTORY.md`.

---

## System Overview

An academic LMS (Learning Management System) supporting Students, Lecturers, HODs, and Admins.
Core features: course management, task/grading, attendance, AI tutoring, analytics.

---

## Architecture Style

**Monolithic REST API** (modular internals, single deployable)
- Feature-based module structure
- Clear service/controller separation
- Stateless — JWT auth, no server-side sessions

---

## Stack

| Layer | Choice | Reason |
|---|---|---|
| Language | Python 3.12+ | — |
| Framework | FastAPI 0.115+ (async-first) | Async-native, fast, excellent OpenAPI support |
| ASGI Server | Uvicorn (dev) · Gunicorn + Uvicorn workers (prod) | Standard FastAPI deployment |
| Database | PostgreSQL 16 | Relational, reliable, strong async support |
| ORM | SQLAlchemy 2.x async + asyncpg | Async-first, type-safe with Mapped[] API |
| Migrations | Alembic (autogenerate from ORM models) | Pairs with SQLAlchemy |
| Cache / Sessions | Redis 7 via redis-py async | Refresh token storage, future caching |
| Auth | JWT (access, 15 min) + opaque UUID in Redis (refresh, 7 days) | Stateless access + instant refresh invalidation |
| Package Manager | `uv` — `pyproject.toml` + `uv.lock` | Fast, modern Python package management |
| File Storage | TBD | — |
| AI Provider | TBD | For tutoring + grading |
| Vector DB | TBD | For RAG/material indexing |
| Hosting | TBD | — |

---

## Folder Structure

```
AMS/
├── src/app/
│   ├── api/v1/              ← route handlers only (no business logic)
│   │   ├── auth.py
│   │   ├── student.py
│   │   ├── lecturer.py
│   │   ├── hod.py
│   │   ├── admin.py
│   │   └── shared.py
│   ├── services/            ← business logic; orchestrates repositories
│   ├── repositories/        ← async DB/Redis queries only; zero business logic
│   ├── models/              ← SQLAlchemy ORM models
│   ├── schemas/             ← Pydantic v2 request/response schemas
│   ├── core/                ← DB engine, Redis pool, JWT utils, lifespan hooks
│   ├── middleware/          ← logging, CORS, rate-limit
│   │   ├── auth             (validates JWT, attaches user)
│   │   ├── active_semester  (blocks writes on inactive semester)
│   │   └── session_owner    (restricts session mutations to owner)
│   ├── workers/             ← ARQ background task definitions
│   ├── config.py            ← single Settings class via lru_cache
│   ├── dependencies.py      ← shared FastAPI Depends() helpers
│   ├── exceptions.py        ← AppException hierarchy + global error handlers
│   └── main.py              ← app factory + lifespan context manager
├── tests/
│   ├── unit/                ← service logic tested with mocked repositories
│   └── integration/         ← real test-DB + Redis (no mocks)
├── alembic/                 ← migration env and version scripts
├── docker/                  ← Dockerfile + docker-compose
├── docs/                    ← all spec files (ARCHITECTURE.md, ENDPOINTS.md, etc.)
└── .github/workflows/       ← CI: lint → typecheck → test → docker build
```

> **Rule:** lower layers must never import from higher layers.
> `api/v1/` → `services/` → `repositories/` → DB/Redis


---

## ASCII Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                    CLIENT APPS                      │
│         (Web / Mobile — Student, Lecturer,          │
│                    HOD, Admin)                      │
└────────────────────────┬────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────┐
│                   REST API SERVER                   │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Auth    │  │ Middleware│  │   Route Modules  │  │
│  │  (JWT)   │  │ (semester,│  │ courses/tasks/   │  │
│  └──────────┘  │  owner)  │  │ sessions/etc.    │  │
│                └──────────┘  └──────────────────┘  │
└────┬──────────────┬──────────────────┬──────────────┘
     │              │                  │
     ▼              ▼                  ▼
┌─────────┐  ┌───────────┐   ┌────────────────┐
│  Main   │  │   File    │   │   AI Services  │
│   DB    │  │  Storage  │   │                │
│         │  │           │   │ ┌────────────┐ │
│ (users, │  │(materials,│   │ │  LLM API   │ │
│ courses,│  │ markguide,│   │ │ (tutoring/ │ │
│ tasks,  │  │ uploads)  │   │ │  grading)  │ │
│ etc.)   │  └───────────┘   │ └────────────┘ │
└─────────┘                  │ ┌────────────┐ │
                             │ │ Vector DB  │ │
                             │ │ (material  │ │
                             │ │  indexing) │ │
                             │ └────────────┘ │
                             └────────────────┘
```

---

## Key Middleware

| Middleware | Purpose | Applied To |
|---|---|---|
| `authGuard` | Validates JWT, attaches user to request | All protected routes |
| `activeSemester` | Blocks writes if no active semester | All POST/PATCH/DELETE under `/courses/:courseId/*` |
| `sessionOwner` | Restricts to session creator | PATCH/DELETE session, POST attendance |
| `authorizedLecturer` | Blocks unauthorized lecturers | All lecturer routes |

---

## Key Design Decisions

- **Settings:** Single `Settings(BaseSettings)` class in `config.py`. `DEBUG=True` in production raises `ValueError` at startup.
- **Database:** All models use `Mapped[T]` / `mapped_column()` — legacy `Column()` API is banned. Every model inherits `Base` and `TimestampMixin`.
- **Sessions:** Injected via `Depends(get_db_session)` — never use a global session.
- **Error handling:** All domain errors are `AppException` subclasses → `{ "error": "<CODE>", "detail": "<message>" }`. No stack traces to clients in production.
- **Observability:** structlog (JSON in prod, coloured in local) + OpenTelemetry (OTLP HTTP) + Prometheus at `/metrics`.
- **Health probes:** `GET /healthz` (liveness) · `GET /readyz` (readiness — checks DB + Redis).
- **Local dev:** `uv sync --group dev` → `docker compose up postgres redis -d` → `uv run alembic upgrade head` → `uv run uvicorn app.main:app --reload`

