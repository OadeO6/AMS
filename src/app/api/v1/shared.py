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

from app.dependencies import CurrentUser, get_current_user

router = APIRouter(
    tags=["shared"],
    dependencies=[Depends(get_current_user)],
)

from app.dependencies import DBSession
from app.schemas.notification import NotificationListResponse, NotificationResponse
from app.services.shared import SharedService

_NOT_IMPLEMENTED = JSONResponse(
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    content={"detail": "Not implemented in this phase."},
)


@router.get(
    "/materials/{material_id}/download",
    status_code=status.HTTP_200_OK,
)
async def download_material(material_id: uuid.UUID, session: DBSession, current_user: CurrentUser) -> JSONResponse:
    svc = SharedService(session)
    url = await svc.get_material_download_url(current_user, material_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"url": url})


@router.get("/notifications", response_model=NotificationListResponse, status_code=status.HTTP_200_OK)
async def list_notifications(
    session: DBSession,
    current_user: CurrentUser,
    read: bool | None = None,
    page: int = 1,
    limit: int = 50,
) -> NotificationListResponse:
    svc = SharedService(session)
    total, items = await svc.list_notifications(current_user, read, page, limit)
    count = await svc.notification_repo.get_unread_count(current_user.id)
    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in items],
        unread_count=count,
    )


@router.patch(
    "/notifications/{notification_id}/read",
    status_code=status.HTTP_200_OK,
)
async def mark_notification_read(notification_id: uuid.UUID, session: DBSession, current_user: CurrentUser) -> JSONResponse:
    svc = SharedService(session)
    await svc.mark_notification_read(current_user, notification_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Notification marked as read"})
