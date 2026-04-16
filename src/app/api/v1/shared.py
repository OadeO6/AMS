# src/app/api/v1/shared.py
"""
Shared endpoints — accessible to multiple roles.

All routes in this module currently return 501 Not Implemented.
They will be fleshed out in Phase 6 (Materials) and Phase 10 (Notifications).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.dependencies import get_current_user

router = APIRouter(
    tags=["shared"],
    dependencies=[Depends(get_current_user)],
)

_NOT_IMPLEMENTED = JSONResponse(
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    content={"detail": "Not implemented in this phase."},
)


@router.get(
    "/materials/{material_id}/download",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def download_material(material_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.get("/notifications", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def list_notifications() -> JSONResponse:
    return _NOT_IMPLEMENTED


@router.patch(
    "/notifications/{notification_id}/read",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def mark_notification_read(notification_id: uuid.UUID) -> JSONResponse:
    return _NOT_IMPLEMENTED
