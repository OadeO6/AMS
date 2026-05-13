"""
Push channel.

Supports two sub-backends chosen per device by the ``platform`` field on
the UserDeviceToken row:

  platform="fcm"  → Firebase Cloud Messaging HTTP v1 API (Android / iOS)
  platform="web"  → Web Push / VAPID (browsers via pywebpush)

Stale tokens (UNREGISTERED from FCM, 404/410 from Web Push) are
automatically deactivated so future pushes skip them.
"""
from __future__ import annotations

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services.notification.channels.base import AbstractChannel, ChannelDeliveryError
from app.services.notification.context import DeliveryContext

log = structlog.get_logger()


# ---------------------------------------------------------------------------
# FCM v1 backend
# ---------------------------------------------------------------------------


async def _send_fcm(token: str, title: str, body: str, data: dict) -> bool:
    """Send via FCM HTTP v1 API.

    Returns
    -------
    bool
        True  — delivered successfully.
        False — token is stale (UNREGISTERED); caller should deactivate it.

    Raises
    ------
    ChannelDeliveryError
        On any non-recoverable FCM error other than a stale token.
    """
    import httpx

    payload = {
        "message": {
            "token": token,
            "notification": {"title": title, "body": body},
            # FCM data payload values must all be strings
            "data": {k: str(v) for k, v in data.items()},
        }
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"https://fcm.googleapis.com/v1/projects/{settings.FCM_PROJECT_ID}/messages:send",
            headers={"Authorization": f"Bearer {settings.FCM_SERVER_KEY}"},
            json=payload,
        )

    if resp.status_code == 200:
        return True

    body_text = resp.text
    if resp.status_code == 400 and "UNREGISTERED" in body_text:
        return False  # stale token
    if resp.status_code == 404:
        return False  # token not found

    raise ChannelDeliveryError(f"FCM error HTTP {resp.status_code}: {body_text[:300]}")


# ---------------------------------------------------------------------------
# Web Push / VAPID backend
# ---------------------------------------------------------------------------


async def _send_webpush(token: str, title: str, body: str, data: dict) -> bool:
    """Send via VAPID Web Push using pywebpush.

    Returns False if the subscription is stale (404 / 410).
    """
    import json as _json
    import asyncio

    try:
        from pywebpush import webpush, WebPushException  # type: ignore[import-untyped]
    except ImportError:
        log.warning(
            "push.webpush.not_installed",
            hint="Run: uv add pywebpush",
        )
        return True  # don't deactivate token; skip silently

    subscription_info = _json.loads(token)
    payload = _json.dumps({"title": title, "body": body, **data})

    try:
        # pywebpush is synchronous; run in a thread pool to avoid blocking
        await asyncio.to_thread(
            webpush,
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": f"mailto:{settings.VAPID_CLAIMS_EMAIL}"},
        )
        return True

    except WebPushException as exc:
        if exc.response is not None and exc.response.status_code in (404, 410):
            return False  # stale subscription
        raise ChannelDeliveryError(str(exc)) from exc
    except Exception as exc:
        raise ChannelDeliveryError(str(exc)) from exc


# ---------------------------------------------------------------------------
# Channel
# ---------------------------------------------------------------------------


class PushChannel(AbstractChannel):
    """Fan out push notifications to all of a user's registered devices.

    Requires a DB session to query UserDeviceToken and deactivate stale tokens.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def send(self, ctx: DeliveryContext) -> None:
        from app.repositories.notification import DeviceTokenRepository

        token_repo = DeviceTokenRepository(self._session)
        devices = await token_repo.get_active_tokens(ctx.user_id)

        if not devices:
            log.debug(
                "push.skipped.no_devices",
                user_id=str(ctx.user_id),
                event=str(ctx.event),
            )
            return

        if not settings.FCM_SERVER_KEY and not settings.VAPID_PRIVATE_KEY:
            log.warning(
                "push.skipped.no_backend",
                hint="Set FCM_SERVER_KEY or VAPID_PRIVATE_KEY in your environment.",
            )
            return

        stale_tokens: list[str] = []

        for device in devices:
            try:
                if device.platform == "fcm":
                    is_active = await _send_fcm(
                        device.token, ctx.title, ctx.body, ctx.data
                    )
                else:
                    is_active = await _send_webpush(
                        device.token, ctx.title, ctx.body, ctx.data
                    )

                if not is_active:
                    stale_tokens.append(device.token)
                else:
                    log.debug(
                        "push.sent",
                        platform=device.platform,
                        device_id=str(device.id),
                        event=str(ctx.event),
                    )

            except ChannelDeliveryError:
                log.exception(
                    "push.delivery_error",
                    platform=device.platform,
                    device_id=str(device.id),
                    user_id=str(ctx.user_id),
                )

        # Deactivate any stale tokens found during this fan-out
        for token in stale_tokens:
            await token_repo.deactivate(token)
            log.info(
                "push.token_deactivated",
                user_id=str(ctx.user_id),
                reason="stale",
            )

        delivered = len(devices) - len(stale_tokens)
        log.info(
            "push.fanout_complete",
            user_id=str(ctx.user_id),
            event=str(ctx.event),
            delivered=delivered,
            stale=len(stale_tokens),
        )
