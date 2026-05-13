# src/app/api/router.py
"""
Central API router — mounts all versioned sub-routers.

To add a new feature router:
    1. Create src/app/api/v1/<feature>.py with an APIRouter.
    2. Import it here and add to api_router.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import admin, auth, health, hod, lecturer, notifications, shared, student

api_router = APIRouter(prefix="/api/v1")

# Health probes — no auth, no prefix beyond /api/v1
api_router.include_router(health.router)

# Auth — register/student, register/lecturer, login, refresh, logout, /me
api_router.include_router(auth.router)

# Role-scoped routes
api_router.include_router(student.router)
api_router.include_router(lecturer.router)
api_router.include_router(hod.router)
api_router.include_router(admin.router)

# Shared — materials download, notifications
api_router.include_router(shared.router)
api_router.include_router(notifications.router)
