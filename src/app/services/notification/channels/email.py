"""
Email channel.

Delivery priority:
  1. SendGrid REST API  — if SENDGRID_API_KEY is set.
  2. SMTP (aiosmtplib) — if SMTP_HOST is set.
  3. No-op + warning   — if neither backend is configured (dev/test).

The HTML template is kept inline to avoid managing template files.
It is intentionally plain — replace with a proper Jinja2 template
and ``jinja2`` dep if richer emails are needed.
"""
from __future__ import annotations

import structlog

from app.config import settings
from app.services.notification.channels.base import AbstractChannel, ChannelDeliveryError
from app.services.notification.context import DeliveryContext

log = structlog.get_logger()

# ---------------------------------------------------------------------------
# Minimal inline HTML template
# ---------------------------------------------------------------------------

_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body  {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
             background: #f4f4f5; margin: 0; padding: 32px 16px; color: #18181b; }}
    .card {{ background: #ffffff; max-width: 560px; margin: 0 auto;
             border-radius: 10px; overflow: hidden;
             box-shadow: 0 1px 3px rgba(0,0,0,.12); }}
    .hdr  {{ background: #1d4ed8; padding: 24px 32px; }}
    .hdr h1 {{ color: #fff; margin: 0; font-size: 18px; font-weight: 600; }}
    .body {{ padding: 28px 32px; line-height: 1.6; font-size: 15px; }}
    .foot {{ padding: 16px 32px; background: #f9fafb;
             font-size: 12px; color: #71717a; text-align: center; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="hdr"><h1>{title}</h1></div>
    <div class="body"><p>{body}</p></div>
    <div class="foot">
      AMS — Academic Management System &nbsp;|&nbsp; This is an automated message.
    </div>
  </div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Backend helpers
# ---------------------------------------------------------------------------


async def _send_sendgrid(to: str, subject: str, html: str) -> None:
    """Deliver via SendGrid REST API v3."""
    import httpx

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={"Authorization": f"Bearer {settings.SENDGRID_API_KEY}"},
            json={
                "personalizations": [{"to": [{"email": to}]}],
                "from": {
                    "email": settings.SMTP_FROM_EMAIL,
                    "name": "AMS Notifications",
                },
                "subject": subject,
                "content": [{"type": "text/html", "value": html}],
            },
        )

    if resp.status_code not in (200, 202):
        raise ChannelDeliveryError(
            f"SendGrid rejected the request: HTTP {resp.status_code} — {resp.text[:300]}"
        )


async def _send_smtp(to: str, subject: str, html: str) -> None:
    """Deliver via SMTP using aiosmtplib."""
    import aiosmtplib  # type: ignore[import-untyped]
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = to
    msg.attach(MIMEText(html, "html", "utf-8"))

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST or "localhost",
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER or None,
        password=settings.SMTP_PASSWORD or None,
        use_tls=settings.SMTP_USE_TLS,
        start_tls=settings.SMTP_START_TLS,
        timeout=15,
    )


# ---------------------------------------------------------------------------
# Channel
# ---------------------------------------------------------------------------


class EmailChannel(AbstractChannel):
    """Delivers emails via SendGrid (preferred) or SMTP (fallback).

    Does not take a DB session — no database access needed.
    """

    async def send(self, ctx: DeliveryContext) -> None:
        if not ctx.recipient_email:
            log.warning(
                "email.skipped.no_recipient",
                user_id=str(ctx.user_id),
                event=str(ctx.event),
            )
            return

        html = _HTML.format(
            title=ctx.title,
            body=ctx.body.replace("\n", "<br>"),
        )

        try:
            if settings.SENDGRID_API_KEY:
                await _send_sendgrid(ctx.recipient_email, ctx.title, html)
                backend = "sendgrid"

            elif settings.SMTP_HOST:
                await _send_smtp(ctx.recipient_email, ctx.title, html)
                backend = "smtp"

            else:
                log.warning(
                    "email.skipped.no_backend",
                    user_id=str(ctx.user_id),
                    hint="Set SENDGRID_API_KEY or SMTP_HOST in your environment.",
                )
                return

        except ChannelDeliveryError:
            raise
        except Exception as exc:
            raise ChannelDeliveryError(str(exc)) from exc

        log.info(
            "email.sent",
            backend=backend,
            to=ctx.recipient_email,
            event=str(ctx.event),
            notification_id=str(ctx.notification_id),
        )
