"""
NotificationEmitter — the single public API for emitting notification events.

Usage
-----
Anywhere a service needs to notify a user, inject the ARQ pool and emit:

    from app.services.notification import NotificationEmitter, NotificationEvent

    class GradeService:
        def __init__(self, session: AsyncSession, arq: ArqRedis) -> None:
            self._emitter = NotificationEmitter(arq)

        async def publish_grade(self, student_id: UUID, course_name: str, grade: str) -> None:
            # ... business logic ...
            await self._emitter.emit(
                NotificationEvent.GRADE_PUBLISHED,
                user_id=student_id,
                course_name=course_name,
                grade=grade,
            )

What happens under the hood
---------------------------
1. The registry is consulted for the event to get its channels + render func.
2. (title, body) are rendered synchronously from the payload kwargs.
3. One ARQ job is enqueued per enabled channel.
4. Each job (in a separate worker process) creates a Notification DB row,
   calls the correct channel, and marks the row SENT or FAILED.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

import structlog

from app.services.notification.events import NotificationEvent
from app.services.notification.registry import EVENT_REGISTRY

if TYPE_CHECKING:
    from arq import ArqRedis

log = structlog.get_logger()


class NotificationEmitter:
    """Fire-and-forget notification dispatcher backed by ARQ."""

    def __init__(self, arq: ArqRedis) -> None:
        self._arq = arq

    async def emit(
        self,
        event: NotificationEvent,
        *,
        user_id: uuid.UUID,
        **payload: Any,
    ) -> None:
        """Enqueue one ARQ job per channel registered for ``event``.

        Parameters
        ----------
        event:
            The notification event to emit.
        user_id:
            UUID of the user who should receive the notification.
        **payload:
            Arbitrary keyword arguments forwarded to the event's render
            function and stored in the Notification.data JSON column.
            e.g. course_name="Mathematics", grade="A"

        Notes
        -----
        This method never raises — a failed enqueue is logged at ERROR level
        and swallowed so it cannot break the calling service's transaction.
        """
        config = EVENT_REGISTRY.get(event)
        if config is None:
            log.error(
                "notification.emit.unknown_event",
                notification_event=str(event),
                hint="Add the event to services/notification/registry.py",
            )
            return

        title, body = config.render(payload)

        log.info(
            "notification.emit",
            notification_event=str(event),
            user_id=str(user_id),
            channels=[c.value for c in config.channels],
        )

        for channel in config.channels:
            try:
                await self._arq.enqueue_job(
                    "deliver_notification",
                    user_id=str(user_id),
                    event=str(event),
                    channel=str(channel),
                    title=title,
                    body=body,
                    data=payload,
                )
            except Exception:
                log.exception(
                    "notification.emit.enqueue_failed",
                    notification_event=str(event),
                    channel=str(channel),
                    user_id=str(user_id),
                )


    async def emit_to_topic(
        self,
        event: NotificationEvent,
        *,
        topic_type: str,
        topic_id: str,
        **payload: Any,
    ) -> None:
        """Enqueue an ARQ job to expand a topic and fan out notifications.

        Parameters
        ----------
        event:
            The notification event to emit.
        topic_type:
            The entity type the topic relates to, e.g., 'course_offering'.
        topic_id:
            The UUID identifier for the specific topic.
        **payload:
            Arbitrary keyword arguments forwarded to the event's render function.
        """
        try:
            await self._arq.enqueue_job(
                "expand_topic_event",
                event=str(event),
                topic_type=topic_type,
                topic_id=str(topic_id),
                **payload,
            )
            log.info(
                "notification.emit_to_topic.enqueued",
                notification_event=str(event),
                topic_type=topic_type,
                topic_id=str(topic_id),
            )
        except Exception:
            log.exception(
                "notification.emit_to_topic.enqueue_failed",
                notification_event=str(event),
                topic_type=topic_type,
                topic_id=str(topic_id),
            )
