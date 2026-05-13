# AMS (Academic Management System)

Production-grade FastAPI backend scaffold.

## Tech Stack
- **Framework**: FastAPI (async)
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.x
- **Cache / Sessions**: Redis 7
- **Worker**: ARQ
- **Observability**: structlog + OpenTelemetry
- **Tooling**: uv, ruff, mypy, pytest

See `docs/architecture.md` for full implementation details and developer guidelines.

## First Login / Admin Setup

To log in as an administrator for the first time, you must create a seed admin user using the provided script:

```bash
uv run python scripts/create_admin.py <your-admin-email> <your-secure-password>
```

Use these credentials to log in via `POST /api/v1/auth/login` and immediately change your password if this is a production environment.
