"""
ARQ background task definitions.

ARQ is a Redis-backed async task queue already present in this project.
Tasks are plain async functions; the worker process runs them concurrently.

Worker process
--------------
    uv run arq app.workers.tasks.WorkerSettings

Enqueuing from application code
--------------------------------
    from app.core.arq_pool import get_arq_pool      # or use ArqPool dependency
    arq = await get_arq_pool()
    await arq.enqueue_job("deliver_notification", user_id=..., ...)

    # Or, more ergonomically via the emitter:
    from app.services.notification import NotificationEmitter, NotificationEvent
    emitter = NotificationEmitter(arq)
    await emitter.emit(NotificationEvent.GRADE_PUBLISHED, user_id=..., course_name=...)
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

import structlog
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

log = structlog.get_logger()


# ---------------------------------------------------------------------------
# Worker lifecycle hooks
# ---------------------------------------------------------------------------


async def startup(ctx: dict[str, Any]) -> None:
    """Create shared resources injected into every job's context dict."""
    engine: AsyncEngine = create_async_engine(
        settings.DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )
    ctx["engine"] = engine
    ctx["session_factory"] = async_sessionmaker(engine, expire_on_commit=False)
    log.info("arq.worker.startup", dsn=settings.DATABASE_URL.split("@")[-1])


async def shutdown(ctx: dict[str, Any]) -> None:
    """Dispose the DB engine cleanly on worker exit."""
    engine: AsyncEngine | None = ctx.get("engine")
    if engine is not None:
        await engine.dispose()
    log.info("arq.worker.shutdown")


# ---------------------------------------------------------------------------
# Notification topic expansion task
# ---------------------------------------------------------------------------


async def expand_topic_event(
    ctx: dict[str, Any],
    *,
    event: str,
    topic_type: str,
    topic_id: str,
    **payload: Any,
) -> None:
    """ARQ task: expand a topic into individual users and dispatch notifications.
    
    Queries the database (safely outside the web request cycle) to find all users
    who should receive a broadcast message based on the topic.
    """
    from app.services.notification.events import NotificationEvent
    from app.services.notification.registry import EVENT_REGISTRY

    config = EVENT_REGISTRY.get(NotificationEvent(event))
    if config is None:
        log.error("expand_topic_event.unknown_event", event=event)
        return

    title, body = config.render(payload)
    session_factory: async_sessionmaker[AsyncSession] = ctx["session_factory"]
    arq_redis = ctx["redis"]

    user_ids: list[str] = []

    # 1. Expand the topic
    if topic_type == "course_offering":
        import uuid
        from sqlalchemy import select
        from app.models.course import CourseRegistration

        offering_uuid = uuid.UUID(topic_id)
        async with session_factory() as session:
            stmt = select(CourseRegistration.student_id).where(
                CourseRegistration.offering_id == offering_uuid,
                CourseRegistration.status == "approved"
            )
            result = await session.execute(stmt)
            user_ids = [str(row[0]) for row in result.all()]
    else:
        log.error("expand_topic_event.unknown_topic_type", topic_type=topic_type)
        return

    log.info(
        "expand_topic_event.expanded",
        notification_event=event,
        topic_type=topic_type,
        topic_id=topic_id,
        user_count=len(user_ids)
    )

    # 2. Fan out jobs per-user and per-channel
    for uid in user_ids:
        for channel in config.channels:
            try:
                await arq_redis.enqueue_job(
                    "deliver_notification",
                    user_id=uid,
                    event=event,
                    channel=str(channel),
                    title=title,
                    body=body,
                    data=payload,
                )
            except Exception:
                log.exception(
                    "expand_topic_event.enqueue_failed",
                    notification_event=event,
                    channel=str(channel),
                    user_id=uid,
                )


# ---------------------------------------------------------------------------
# Notification delivery task
# ---------------------------------------------------------------------------


async def deliver_notification(
    ctx: dict[str, Any],
    *,
    user_id: str,
    event: str,
    channel: str,
    title: str,
    body: str,
    data: dict[str, Any],
) -> None:
    """ARQ task: persist a Notification row and dispatch it to its channel.

    Flow
    ----
    1. Open a DB transaction.
    2. Create a ``Notification`` row with status=PENDING.
    3. Resolve the User row to get contact details (email, phone).
    4. Build a ``DeliveryContext`` and call the channel's ``send()``.
    5. Mark the row SENT on success, FAILED on exception.

    ARQ will retry this task up to ``WorkerSettings.max_tries`` times on
    unhandled exceptions (transient network errors, DB timeouts, etc.).
    ``ChannelDeliveryError`` is also retriable — the channel raises it only
    after it has exhausted its own retry attempts.

    Parameters
    ----------
    user_id:
        String representation of the target user UUID.
    event:
        Dot-notated event name (``NotificationEvent`` value).
    channel:
        Channel identifier (``NotificationChannel`` value).
    title:
        Pre-rendered notification title.
    body:
        Pre-rendered notification body.
    data:
        Original emit() kwargs stored as JSONB for deep-linking.
    """
    from app.models.notification import Notification, NotificationChannel, NotificationStatus
    from app.models.user import User
    from app.services.notification.context import DeliveryContext
    from app.services.notification.events import NotificationEvent

    session_factory: async_sessionmaker[AsyncSession] = ctx["session_factory"]
    uid = uuid.UUID(user_id)

    async with session_factory() as session:
        async with session.begin():

            # ------------------------------------------------------------------
            # 1. Create the Notification record (status = PENDING)
            # ------------------------------------------------------------------
            notif = Notification(
                user_id=uid,
                event=event,
                channel=channel,
                title=title,
                body=body,
                data=data,
                status=NotificationStatus.PENDING,
            )
            session.add(notif)
            await session.flush()
            await session.refresh(notif)

            notification_id: uuid.UUID = notif.id

            # ------------------------------------------------------------------
            # 2. Resolve the User row for contact details
            # ------------------------------------------------------------------
            user: User | None = await session.get(User, uid)
            if user is None:
                log.error(
                    "deliver_notification.user_not_found",
                    user_id=user_id,
                    notification_id=str(notification_id),
                )
                notif.status = NotificationStatus.FAILED
                notif.failed_at = datetime.now(timezone.utc)
                notif.failure_reason = f"User {user_id} not found"
                return

            # ------------------------------------------------------------------
            # 3. Build DeliveryContext
            # ------------------------------------------------------------------
            delivery_ctx = DeliveryContext(
                notification_id=notification_id,
                user_id=uid,
                event=NotificationEvent(event),
                channel=NotificationChannel(channel),
                title=title,
                body=body,
                data=data,
                recipient_email=getattr(user, "email", None),
                # Assumes an optional phone_number field on User.
                # If your User model doesn't have it yet, this safely returns None.
                recipient_phone=getattr(user, "phone_number", None),
            )

            # ------------------------------------------------------------------
            # 4. Dispatch to the correct channel
            # ------------------------------------------------------------------
            ch = _resolve_channel(NotificationChannel(channel), session)

            try:
                await ch.send(delivery_ctx)

                notif.status = NotificationStatus.SENT
                notif.sent_at = datetime.now(timezone.utc)
                log.info(
                    "deliver_notification.sent",
                    notification_event=event,
                    channel=channel,
                    user_id=user_id,
                    notification_id=str(notification_id),
                )

            except Exception as exc:
                notif.status = NotificationStatus.FAILED
                notif.failed_at = datetime.now(timezone.utc)
                notif.failure_reason = str(exc)[:500]
                log.exception(
                    "deliver_notification.failed",
                    notification_event=event,
                    channel=channel,
                    user_id=user_id,
                    notification_id=str(notification_id),
                    error=str(exc),
                )
                raise  # re-raise so ARQ can retry


def _resolve_channel(
    channel: "NotificationChannel",
    session: AsyncSession,
) -> "AbstractChannel":
    """Factory: map a NotificationChannel enum value to its implementation."""
    from app.models.notification import NotificationChannel
    from app.services.notification.channels.base import AbstractChannel
    from app.services.notification.channels.email import EmailChannel
    from app.services.notification.channels.inapp import InAppChannel
    from app.services.notification.channels.push import PushChannel
    from app.services.notification.channels.sms import SmsChannel

    match channel:
        case NotificationChannel.INAPP:
            return InAppChannel()
        case NotificationChannel.EMAIL:
            return EmailChannel()
        case NotificationChannel.PUSH:
            return PushChannel(session)
        case NotificationChannel.SMS:
            return SmsChannel()
        case _:
            raise ValueError(f"Unknown channel: {channel!r}")


# ---------------------------------------------------------------------------
# Existing placeholder task (keep for backwards compat)
# ---------------------------------------------------------------------------


async def example_task(ctx: dict[str, object], message: str) -> str:
    """Placeholder task — replace with real business logic."""
    log.info("example_task.running", message=message)
    return f"processed: {message}"


# ---------------------------------------------------------------------------
# ARQ Worker Settings
# ---------------------------------------------------------------------------


class WorkerSettings:
    """ARQ worker configuration.

    Run:
        uv run arq app.workers.tasks.WorkerSettings
    """

    functions = [
        example_task,
        deliver_notification,
        expand_topic_event,
    ]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    on_startup = startup
    on_shutdown = shutdown

    max_jobs: int = 20
    job_timeout: int = 300       # 5 minutes per job
    retry_jobs: bool = True
    max_tries: int = 3           # 3 total attempts before marking failed
    keep_result: int = 3600      # keep job results in Redis for 1 hour
