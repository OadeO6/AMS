# AMS : Academic Management System

> A role-based academic platform designed to streamline course management, assessment, attendance, and AI-assisted learning for higher education institutions.

---

## Table of Contents

- [Overview](#overview)
- [User Roles](#user-roles)
- [Key Features](#key-features)
- [System Requirements](#system-requirements)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [Functional Requirements](#functional-requirements)
- [Non-Functional Requirements](#non-functional-requirements)
- [API Documentation](#api-documentation)

---

## Overview

AMS (Academic Management System) is a final-year project aimed at simplifying and improving the efficiency of academic activities within a department or faculty. It provides role-specific interfaces for students, lecturers, heads of department, and administrators : reducing information silos and supporting data-driven academic decisions.

The system integrates AI tutoring grounded in course materials, automatic task grading with mandatory human review, and detailed performance analytics across all user roles.

---

## User Roles

| Role | Responsibilities |
|---|---|
| **Student** | Register for courses, submit assignments, track attendance and grades, interact with AI tutor |
| **Lecturer** | Manage course sessions, upload materials, grade submissions, post announcements, configure AI tutor |
| **Head of Department (HOD)** | Oversee department courses, manage course offerings, assign lecturers |
| **Admin** | Manage faculties, departments, and academic sessions/semesters |

---

## Key Features

- **Lecturer Dashboard** : Centralized view of all assigned courses, organized by academic level.
- **Lecture Materials** : Upload and share course materials with configurable visibility (`Students`, `AI`, or `Both`).
- **Assignment Management** : Create, submit, and track assignments with deadline enforcement.
- **Announcements** : Post targeted announcements to specific course classes.
- **AI Tutoring** : A course-scoped AI chatbot grounded exclusively in uploaded course materials to prevent hallucinations. Custom instructions can be set per course by the lecturer.
- **Automatic Task Grading** : AI-assisted grading using an uploaded marking guide/rubric. Every AI-generated grade is subject to mandatory human review before it is finalized.
- **Attendance Marking** : Session-scoped attendance recording, with export to CSV/PDF.
- **Student Performance Analytics** : Visual dashboards for both students and lecturers covering academic progress and engagement.
- **Gradebook** : A private lecturer-maintained gradebook per course, with CSV/PDF export support.
- **Role-Based Access Control (RBAC)** : All routes are guarded based on user role. Semester-aware middleware blocks writes when no active semester exists.

---

## System Requirements

- Python 3.12+
- PostgreSQL 16
- Redis 7
- ChromaDB (vector database : runs embedded or as a standalone server)
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Docker & Docker Compose (recommended for local backing services)
- A Google Gemini API key (required for AI Tutor and Automatic Grading features)
- Node.js 20+ & pnpm (for the React frontend in the `frontend/` directory)


---

## Tech Stack

### Backend

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Framework | FastAPI 0.115+ (async-first) |
| ASGI Server | Uvicorn (dev) · Gunicorn + Uvicorn workers (prod) |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.x async + asyncpg |
| Migrations | Alembic |
| Cache / Sessions | Redis 7 |
| Authentication | JWT (access, 15 min) + opaque UUID in Redis (refresh, 7 days) |
| Package Manager | `uv` (`pyproject.toml` + `uv.lock`) |
| Background Tasks | ARQ |
| Observability | structlog + OpenTelemetry (OTLP) + Prometheus |

### AI Stack *(planned : not yet implemented)*

| Component | Technology | Purpose |
|---|---|---|
| LLM | Google Gemini 1.5 Flash (tutor) · Gemini 1.5 Pro (grading) | Response generation |
| Embedding Model | Gemini `text-embedding-004` | Converts material chunks into vector representations |
| Vector Database | ChromaDB | Stores and retrieves embedded course material chunks |
| Document Parser | PyMuPDF (`fitz`) · python-docx | Extracts text from uploaded PDF and Word files |
| Chunking & Orchestration | LangChain (`RecursiveCharacterTextSplitter`) | Splits documents and ties the RAG pipeline together |
| AI SDK | `google-generativeai` (Python) | Interface for Gemini LLM and embedding API calls |

> See [`docs/AI_DESIGN.md`](docs/AI_DESIGN.md) for the full pipeline design, prompt structures, and integration details.

### Frontend

The frontend is a React application configured with Vite and pnpm.

| Layer | Technology |
|---|---|
| Framework | React 19 + TypeScript |
| Build Tool | Vite 7 |
| Package Manager | `pnpm` |
| Styling | Tailwind CSS 4 |
| API Layer | Axios + tRPC React Client (react-query) |
| Routing | Wouter |
| Validation | React Hook Form + Zod |
| UI Components | Radix UI + Lucide React + Framer Motion |


---

## Project Structure

```
AMS/
├── backend/                 ← Main application folder
│   ├── src/app/
│   │   ├── api/v1/              ← route handlers only (no business logic)
│   │   │   ├── auth.py
│   │   │   ├── student.py
│   │   │   ├── lecturer.py
│   │   │   ├── hod.py
│   │   │   ├── admin.py
│   │   │   └── shared.py
│   │   ├── services/            ← business logic; orchestrates repositories
│   │   ├── repositories/        ← async DB/Redis queries only; zero business logic
│   │   ├── models/              ← SQLAlchemy ORM models
│   │   ├── schemas/             ← Pydantic v2 request/response schemas
│   │   ├── core/                ← DB engine, Redis pool, JWT utils, lifespan hooks
│   │   ├── middleware/          ← auth, active_semester, session_owner
│   │   ├── workers/             ← ARQ background task definitions
│   │   ├── config.py            ← single Settings class (lru_cache)
│   │   ├── dependencies.py      ← shared FastAPI Depends() helpers
│   │   ├── exceptions.py        ← AppException hierarchy + global error handlers
│   │   └── main.py              ← app factory + lifespan context manager
│   ├── tests/
│   │   ├── unit/                ← service logic with mocked repositories
│   │   └── integration/         ← real test-DB + Redis (no mocks)
│   ├── alembic/                 ← migration environment and version scripts
│   ├── Dockerfile               ← Multi-stage build definition
│   ├── pyproject.toml           ← Project dependencies managed by uv
│   └── uv.lock
├── docker-compose.yml       ← Local backing services & API containers
├── docs/                    ← architecture, endpoints, schema, setup, AI design
└── .github/workflows/       ← CI: lint → typecheck → test → docker build
```

> **Layer rule:** lower layers must never import from higher layers.
> `api/v1/` → `services/` → `repositories/` → DB/Redis

---

## Getting Started

> **Important:** Please see [`docs/SETUP.md`](docs/SETUP.md) for a detailed, step-by-step setup guide. 

### 1. Clone the repository

```bash
git clone <repository-url>
cd AMS
```

### 2. Start backing services (PostgreSQL + Redis)

```bash
docker compose up postgres redis -d
```

### 3. Enter backend directory and install dependencies

```bash
cd backend
cp .env.example .env
# Edit .env with your configuration
uv sync --group dev
```

### 4. Run database migrations

```bash
uv run alembic upgrade head
```

### 5. Start the development server

```bash
uv run uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.
Interactive API docs are at `http://localhost:8000/docs`.

### 6. Install frontend dependencies and start frontend dev server

Open a new terminal, navigate to the `frontend/` directory, install packages using `pnpm`, and run the development server:

```bash
cd frontend
pnpm install
pnpm dev
```

The frontend will be available locally at `http://localhost:5173` (or `http://localhost:3000` when running through Docker Compose).


---

## Environment Variables

The application is configured via a single `.env` file located in the `backend/` directory. Copy `.env.example` and update the values:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Async PostgreSQL connection string |
| `REDIS_URL` | Redis connection URL |
| `SECRET_KEY` | JWT signing secret |
| `ENVIRONMENT` | `local` \| `staging` \| `production` |
| `DEBUG` | `True` in local only : raises `ValueError` in production if set |
| `TEST_DATABASE_URL` | Separate DB URL used for integration tests |
| `GEMINI_API_KEY` | Google Gemini API key : required for AI Tutor and Automatic Grading features |

> Setting `DEBUG=True` in a production environment will cause the application to refuse to start.

---

## Running the Application

### Development

Start both the backend API and frontend dev server:

**Backend API:**
```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

**Frontend Dev Server:**
```bash
cd frontend
pnpm dev
```

### Production

**Backend API:**
```bash
cd backend
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:8000
```

**Frontend (Local Preview):**
```bash
cd frontend
pnpm build
pnpm preview
```

### Docker

You can run the entire stack (PostgreSQL, Redis, MinIO, Backend API, and Frontend) via Docker Compose.

You can launch the stack using the provided startup script, which will bring up all containers in the background and print a dashboard with the access URLs directly to your console:

```bash
./start.sh
```

Alternatively, run from the root directory:

```bash
docker compose up
```

To print a quick info dashboard containing all active service access URLs at any time, run:

```bash
docker compose up info
```


- **Frontend (Dev)**: Available at `http://localhost:3000` (mapped to port 3000 in dev mode via `docker-compose.override.yml`)
- **Frontend (Prod)**: Available at `http://localhost:8080` (mapped to port 80/nginx in production mode)
- **Backend API**: Available at `http://localhost:8000`
- **Swagger UI**: Available at `http://localhost:8000/docs`
- **MinIO Console**: Available at `http://localhost:9001`



### Health Checks

| Endpoint | Purpose |
|---|---|
| `GET /healthz` | Liveness : always returns `200 {"status": "ok"}` |
| `GET /readyz` | Readiness : returns `200` only if DB and Redis are reachable, else `503` |

---

## Running Tests

From the `backend/` directory:

```bash
# All tests (unit + integration) with coverage
uv run pytest

# Unit tests only : no DB or Redis required
uv run pytest tests/unit/

# Integration tests : requires TEST_DATABASE_URL and REDIS_URL in .env
uv run pytest tests/integration/
```

Coverage target: **≥ 80%** on `services/` and `repositories/`, enforced in CI.

---

## Functional Requirements

### Student

- Sign up using unique student details; sign in via email or matric number
- Register for and drop courses; view available and registered courses
- View course materials, download resources, and access session details
- Submit assignments and view grades, feedback, and submission history
- Track attendance history and personal performance analytics per course
- Chat with the AI tutor; receive and manage notifications and announcements

### Lecturer

- Sign up using lecturer details; sign in via email or staff ID
- Manage assigned courses: create sessions, schedule, reschedule, or cancel classes
- Upload materials with visibility controls (`Students`, `AI`, or `Both`)
- Create assignments, mark attendance, and manage the course gradebook
- Enable AI grading (requires a marking guide to be uploaded first); review and approve or reject AI-generated grades
- Send course announcements; view course and cross-course analytics
- Export attendance and gradebook records to CSV or PDF
- Configure AI tutor instructions and chat with the AI tutor directly

### Head of Department (HOD)

- View all students and lecturers in the department; access individual profiles
- Create, update, and delete course definitions; manage course offerings per semester
- Activate or deactivate offerings; assign and unassign lecturers from offerings
- Update a student's level offset for deferrals or repeats

### Admin

- Create and manage faculties and departments
- Manage academic sessions and semesters; activate the current semester
- Only one semester may be active globally at any time

---

## Non-Functional Requirements

- **Reliability** : High data integrity with no information silos or data loss.
- **Accuracy** : The AI tutor is grounded solely in uploaded course documents, preventing hallucinations.
- **Security** : Role-Based Access Control (RBAC) with OTP-based authentication and bcrypt password hashing.
- **Usability** : Role-specific interfaces designed to reduce cognitive load, accessible via standard web browsers.
- **Performance** : Async backend capable of handling concurrent users during peak periods such as enrollment and examinations.
- **Human-in-the-Loop** : All automated grading decisions are subordinate to mandatory human review before finalization.

---

## API Documentation

Once the server is running, full interactive API documentation is available at:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

All API responses follow a consistent structure. Errors are returned as:

```json
{
  "error": "ERROR_CODE",
  "detail": "Human-readable message"
}
```

---

*This project was developed as a final-year project. For questions or contributions, please refer to the project guidelines in the `docs/` directory.*
