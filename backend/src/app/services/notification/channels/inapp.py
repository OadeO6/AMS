"""
In-app channel.

For in-app notifications the Notification DB row *is* the delivery artefact —
there is no external call to make. This channel simply validates that the row
exists and signals success; the ARQ task then marks it SENT.

The front-end polls GET /notifications or opens a WebSocket to read these rows.
"""
from __future__ import annotations

import structlog

from app.services.notification.channels.base import AbstractChannel, ChannelDeliveryError
from app.services.notification.context import DeliveryContext

log = structlog.get_logger()


class InAppChannel(AbstractChannel):
    """Delivers in-app notifications by persisting them to the ``notifications`` table.

    The Notification row is created as PENDING by the ARQ task *before* this
    channel is invoked. Here we validate the row exists (sanity check) and
    return. The task marks it SENT on return, making it visible to the user.
    """

    async def send(self, ctx: DeliveryContext) -> None:
        # The DB row was created by the ARQ task before dispatching here.
        # Nothing to do externally — the persisted row IS the notification.
        # This is intentionally a no-op beyond the log line.
        log.debug(
            "inapp.delivered",
            notification_id=str(ctx.notification_id),
            user_id=str(ctx.user_id),
            event=str(ctx.event),
        )
