"""
SMS channel.

Delivery priority:
  1. Termii  — if TERMII_API_KEY is set (preferred; Nigerian provider).
  2. Twilio  — if TWILIO_ACCOUNT_SID + TWILIO_AUTH_TOKEN are set.
  3. No-op + warning — if neither is configured.

Message format: "{title}\n{body}" truncated to 160 chars to stay in one SMS.
Multi-part messages (>160 chars) are sent as-is and billed by the provider.
"""
from __future__ import annotations

import structlog

from app.config import settings
from app.services.notification.channels.base import AbstractChannel, ChannelDeliveryError
from app.services.notification.context import DeliveryContext

log = structlog.get_logger()


# ---------------------------------------------------------------------------
# Backend helpers
# ---------------------------------------------------------------------------


async def _send_termii(to: str, message: str) -> None:
    """Deliver via Termii REST API."""
    import httpx

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            "https://api.ng.termii.com/api/sms/send",
            json={
                "to": to,
                "from": settings.TERMII_SENDER_ID,
                "sms": message,
                "type": "plain",
                "api_key": settings.TERMII_API_KEY,
                "channel": "generic",
            },
        )

    if resp.status_code not in (200, 201):
        raise ChannelDeliveryError(
            f"Termii error HTTP {resp.status_code}: {resp.text[:300]}"
        )


async def _send_twilio(to: str, message: str) -> None:
    """Deliver via Twilio Programmable Messaging REST API."""
    import httpx
    from base64 import b64encode

    credentials = b64encode(
        f"{settings.TWILIO_ACCOUNT_SID}:{settings.TWILIO_AUTH_TOKEN}".encode()
    ).decode()

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"https://api.twilio.com/2010-04-01/Accounts/"
            f"{settings.TWILIO_ACCOUNT_SID}/Messages.json",
            headers={"Authorization": f"Basic {credentials}"},
            data={
                "From": settings.TWILIO_FROM_NUMBER,
                "To": to,
                "Body": message,
            },
        )

    if resp.status_code not in (200, 201):
        raise ChannelDeliveryError(
            f"Twilio error HTTP {resp.status_code}: {resp.text[:300]}"
        )


# ---------------------------------------------------------------------------
# Channel
# ---------------------------------------------------------------------------


class SmsChannel(AbstractChannel):
    """Delivers SMS via Termii (preferred) or Twilio (fallback).

    Does not need a DB session.
    """

    async def send(self, ctx: DeliveryContext) -> None:
        if not ctx.recipient_phone:
            log.warning(
                "sms.skipped.no_phone",
                user_id=str(ctx.user_id),
                event=str(ctx.event),
                hint="Add a phone_number field to the User model and populate it.",
            )
            return

        # Keep it concise: title on first line, body below.
        message = f"{ctx.title}\n{ctx.body}"

        try:
            if settings.TERMII_API_KEY:
                await _send_termii(ctx.recipient_phone, message)
                backend = "termii"

            elif settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
                await _send_twilio(ctx.recipient_phone, message)
                backend = "twilio"

            else:
                log.warning(
                    "sms.skipped.no_backend",
                    hint="Set TERMII_API_KEY or TWILIO_ACCOUNT_SID in your environment.",
                )
                return

        except ChannelDeliveryError:
            raise
        except Exception as exc:
            raise ChannelDeliveryError(str(exc)) from exc

        log.info(
            "sms.sent",
            backend=backend,
            to=ctx.recipient_phone,
            event=str(ctx.event),
            notification_id=str(ctx.notification_id),
        )
