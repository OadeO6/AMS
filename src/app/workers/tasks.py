# src/app/workers/tasks.py
"""
ARQ background task definitions.

ARQ is a Redis-backed async task queue. Tasks are plain async functions.
To enqueue a task from application code:
    from arq import ArqRedis
    await arq_pool.enqueue_job("my_task_name", arg1, arg2)

Usage
-----
Run the worker process:
    uv run arq app.workers.tasks.WorkerSettings

Add new tasks as top-level async functions below, then register them
in WorkerSettings.functions.
"""

from __future__ import annotations

from arq.connections import RedisSettings

from app.config import settings

# ---------------------------------------------------------------------------
# Task definitions
# ---------------------------------------------------------------------------


async def example_task(ctx: dict[str, object], message: str) -> str:
    """Placeholder task — replace with real business logic.

    Parameters
    ----------
    ctx:
        ARQ worker context (contains ``redis`` and other shared resources).
    message:
        Arbitrary string payload from the enqueue call.
    """
    import structlog

    log = structlog.get_logger()
    log.info("Running example task", message=message)
    return f"processed: {message}"


# ---------------------------------------------------------------------------
# ARQ Worker Settings
# ---------------------------------------------------------------------------


class WorkerSettings:
    """ARQ worker configuration.

    ARQ reads this class when starting the worker process.
    Register all task functions in the ``functions`` list.
    """

    functions = [example_task]

    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)

    # Optional: scheduled / recurring tasks using cron syntax
    # cron_jobs = [
    #     cron(my_nightly_job, hour=2, minute=0),
    # ]

    # Max concurrent jobs
    max_jobs: int = 10

    # Job timeout in seconds
    job_timeout: int = 300
