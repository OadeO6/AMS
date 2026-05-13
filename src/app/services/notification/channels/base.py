"""
Abstract base channel — the contract every channel implementation must satisfy.

Rules:
  - send() does one thing: deliver the notification via the external service.
  - send() must be idempotent where possible (safe to retry).
  - Transient errors (network timeouts, 5xx) should be retried by ARQ;
    raise ChannelDeliveryError only on a final, unrecoverable failure.
  - Channels must never commit or rollback transactions. That is the
    ARQ task's responsibility.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.services.notification.context import DeliveryContext


class ChannelDeliveryError(Exception):
    """Raised when a channel cannot deliver after all retries.

    The ARQ task catches this and marks the Notification row FAILED.
    """


class AbstractChannel(ABC):
    """Contract every channel must satisfy."""

    @abstractmethod
    async def send(self, ctx: DeliveryContext) -> None:
        """Deliver the notification described by ``ctx``.

        Parameters
        ----------
        ctx:
            Immutable delivery context (notification_id, title, body, etc.)

        Raises
        ------
        ChannelDeliveryError
            On a final unrecoverable failure. Transient errors that should
            be retried must NOT raise this — let them propagate as-is so
            ARQ's retry logic can handle them.
        """
        ...
