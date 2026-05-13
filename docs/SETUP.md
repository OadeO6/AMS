# SETUP : Local Development Guide

> Step-by-step guide for setting up the AMS backend for local development.
> Read `ARCHITECTURE.md` first to understand the project structure before diving in.

---

## Prerequisites

Make sure the following are installed on your machine before proceeding:

| Tool | Version | Notes |
|---|---|---|
| Python | 3.12+ | Required. Use `pyenv` to manage versions if needed. |
| `uv` | Latest | Python package manager. Install via `curl -Ls https://astral.sh/uv/install.sh \| sh` |
| Docker | Latest | Used to run PostgreSQL and Redis locally |
| Docker Compose | Latest | Bundled with Docker Desktop |
| Git | Any | For cloning the repository |

---

## 1. Clone the Repository

```bash
git clone <repository-url>
cd AMS
```

---

## 2. Start Backing Services

Use Docker Compose to start PostgreSQL and Redis from the root directory:

```bash
docker compose up postgres redis -d
```

To verify both services are running:

```bash
docker compose ps
```

---

## 3. Navigate to Backend and Configure Environment Variables

The application code is located in the `backend/` directory.

```bash
cd backend
cp .env.example .env
```

Open `backend/.env` and update the following:

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://ams_user:ams_pass@localhost:5432/ams_db` |
| `TEST_DATABASE_URL` | Separate DB used for integration tests | `postgresql+asyncpg://ams_user:ams_pass@localhost:5432/ams_test` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT signing secret : use a long random string | `openssl rand -hex 32` |
| `ENVIRONMENT` | Runtime environment | `local` |
| `DEBUG` | Enable debug mode (local only) | `True` |
| `GEMINI_API_KEY` | Google Gemini API key (AI features) | Obtain from [Google AI Studio](https://aistudio.google.com/) |

> **Never set `DEBUG=True` in staging or production.** The application will refuse to start if this is detected.

---

## 4. Install Dependencies

Ensure you are still inside the `backend/` directory, then run:

```bash
uv sync --group dev
```

This reads `backend/pyproject.toml` and installs all dependencies including development tools (linters, test runner, type checker) into a local virtual environment managed by `uv`.

---

## 5. Run Database Migrations

Apply all Alembic migrations to set up the database schema:

```bash
uv run alembic upgrade head
```

To check the current migration state:

```bash
uv run alembic current
```

---

## 6. Seed the Database (Optional)

If a seed script is available, run it to populate the database with initial test data (e.g. an admin account, a department, a sample academic session):

```bash
uv run python scripts/seed.py
```

> Check whether this script exists in your project. If not, create test data manually via the API after starting the server.

---

## 7. Start the Development Server

```bash
uv run uvicorn app.main:app --reload --port 8000
```

The server will auto-reload on file changes.

| URL | Purpose |
|---|---|
| `http://localhost:8000` | API root |
| `http://localhost:8000/docs` | Swagger UI (interactive API docs) |
| `http://localhost:8000/redoc` | ReDoc API docs |
| `http://localhost:8000/healthz` | Liveness check |
| `http://localhost:8000/readyz` | Readiness check (DB + Redis) |

---

## Running Tests

Ensure you are in the `backend/` directory.

### All tests

```bash
uv run pytest
```

### Unit tests only (no DB or Redis required)

```bash
uv run pytest tests/unit/
```

### Integration tests (requires `TEST_DATABASE_URL` and `REDIS_URL` in `.env`)

```bash
uv run pytest tests/integration/
```

### With coverage report

```bash
uv run pytest --cov=app --cov-report=term-missing
```

Coverage target: **≥ 80%** on `services/` and `repositories/`. This is enforced in CI.

---

## Working with Alembic (Database Migrations)

Ensure you are in the `backend/` directory.

### Generate a new migration after changing a model

```bash
uv run alembic revision --autogenerate -m "describe your change here"
```

Review the generated file in `alembic/versions/` before applying it : autogenerate is not always perfect.

### Apply pending migrations

```bash
uv run alembic upgrade head
```

### Roll back the last migration

```bash
uv run alembic downgrade -1
```

### View migration history

```bash
uv run alembic history --verbose
```

---

## Adding a New Feature

Follow the layered architecture strictly : lower layers must never import from higher layers.

1. **Model** → `src/app/models/<domain>.py` : inherit `Base` and `TimestampMixin`
2. **Schema** → `src/app/schemas/<domain>.py` : use Pydantic v2
3. **Repository** → `src/app/repositories/<domain>.py` : async DB/Redis queries only, no business logic
4. **Service** → `src/app/services/<domain>.py` : business logic only, raises `AppException` on failures
5. **Router** → `src/app/api/v1/<domain>.py` : register it in `src/app/api/router.py`
6. **Migration** → `uv run alembic revision --autogenerate -m "add <domain>"`
7. **Tests** → unit test the service with mocked repositories; integration test the endpoints

---

## Code Quality

The following tools are used and run in CI:

```bash
# Linting and formatting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy src/
```

Fix all linting and type errors before opening a pull request.

---

## Stopping Services

From the root directory of the project:

```bash
# Stop postgres and redis containers
docker compose down

# Stop and remove volumes (resets DB data)
docker compose down -v
```
