"""
Notification endpoints — in-app inbox + device token management.

All routes require an authenticated user (CurrentUser dependency).
These endpoints serve the in-app channel only; email/push/SMS are
outbound-only and have no corresponding REST surface.

Routes
------
GET  /notifications              — List in-app notifications (paginated)
PATCH /notifications/read        — Mark specific notifications as read
PATCH /notifications/read-all    — Mark all in-app notifications as read
POST /notifications/device-tokens        — Register a push token
DELETE /notifications/device-tokens/{token} — Deregister a push token
"""
from __future__ import annotations

from fastapi import APIRouter, Query, status

from app.dependencies import CurrentUser, DBSession
from app.repositories.notification import DeviceTokenRepository, NotificationRepository
from app.schemas.notification import (
    DeviceTokenRegister,
    DeviceTokenResponse,
    MarkReadRequest,
    MarkReadResponse,
    NotificationListResponse,
    NotificationResponse,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


# ---------------------------------------------------------------------------
# In-app inbox
# ---------------------------------------------------------------------------


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    session: DBSession,
    current_user: CurrentUser,
    unread_only: bool = Query(False, description="If true, return only unread notifications."),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> NotificationListResponse:
    """Return the authenticated user's in-app notifications, newest first."""
    repo = NotificationRepository(session)
    notifications, total = await repo.list_for_user(
        current_user.id,
        unread_only=unread_only,
        offset=offset,
        limit=limit,
    )
    unread_count = await repo.count_unread(current_user.id)
    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notifications],
        unread_count=unread_count,
        total=total,
        offset=offset,
        limit=limit,
    )


@router.patch(
    "/read",
    response_model=MarkReadResponse,
    summary="Mark specific notifications as read",
)
async def mark_notifications_read(
    payload: MarkReadRequest,
    session: DBSession,
    current_user: CurrentUser,
) -> MarkReadResponse:
    """Mark a list of notification IDs as read.

    Scoped to the current user — cannot mark other users' notifications.
    Idempotent: already-read IDs are ignored silently.
    """
    repo = NotificationRepository(session)
    marked = await repo.mark_read(payload.notification_ids, current_user.id)
    return MarkReadResponse(marked=marked)


@router.patch(
    "/read-all",
    response_model=MarkReadResponse,
    summary="Mark all in-app notifications as read",
)
async def mark_all_notifications_read(
    session: DBSession,
    current_user: CurrentUser,
) -> MarkReadResponse:
    """Mark every unread in-app notification for the current user as read."""
    repo = NotificationRepository(session)
    marked = await repo.mark_all_read(current_user.id)
    return MarkReadResponse(marked=marked)


# ---------------------------------------------------------------------------
# Push device token management
# ---------------------------------------------------------------------------


@router.post(
    "/device-tokens",
    response_model=DeviceTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a push notification token",
)
async def register_device_token(
    payload: DeviceTokenRegister,
    session: DBSession,
    current_user: CurrentUser,
) -> DeviceTokenResponse:
    """Register (or reactivate) a FCM / Web Push subscription token.

    If the token already exists it is re-associated with the current user
    and marked active — handles re-installs and token refreshes gracefully.
    """
    repo = DeviceTokenRepository(session)
    token = await repo.upsert(current_user.id, payload.token, payload.platform)
    return DeviceTokenResponse.model_validate(token)


@router.delete(
    "/device-tokens/{token}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deregister a push notification token",
)
async def deregister_device_token(
    token: str,
    session: DBSession,
    current_user: CurrentUser,  # noqa: ARG001  (used implicitly for auth)
) -> None:
    """Deactivate a push token (e.g. on logout or browser permission revoke)."""
    repo = DeviceTokenRepository(session)
    await repo.deactivate(token)
