from __future__ import annotations

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings

logger = structlog.get_logger(__name__)

scheduler = AsyncIOScheduler()


async def run_watcher_job() -> None:
    from app.orchestrator.pipeline import orchestrator

    logger.info("scheduler_watcher_job_started")
    try:
        pipeline_id = await orchestrator.run_watcher_only({"trigger": "scheduler_nightly"})
        logger.info("scheduler_watcher_job_completed", pipeline_id=pipeline_id)
    except Exception as e:
        logger.error("scheduler_watcher_job_failed", error=str(e))


async def run_full_pipeline_job() -> None:
    from app.orchestrator.pipeline import orchestrator

    logger.info("scheduler_full_pipeline_job_started")
    try:
        pipeline_id = await orchestrator.run_full_pipeline({"trigger": "scheduler_weekly"})
        logger.info("scheduler_full_pipeline_job_completed", pipeline_id=pipeline_id)
    except Exception as e:
        logger.error("scheduler_full_pipeline_job_failed", error=str(e))


def setup_scheduler() -> None:
    if settings.environment == "production":
        scheduler.add_job(
            run_watcher_job,
            trigger=IntervalTrigger(hours=settings.scheduler_watcher_interval_hours),
            id="nightly_watcher",
            name="Nightly Watcher",
            replace_existing=True,
        )
        logger.info(
            "scheduler_watcher_configured",
            interval_hours=settings.scheduler_watcher_interval_hours,
        )

        scheduler.add_job(
            run_full_pipeline_job,
            trigger=IntervalTrigger(hours=settings.scheduler_full_pipeline_interval_hours),
            id="weekly_full_pipeline",
            name="Weekly Full Pipeline",
            replace_existing=True,
        )
        logger.info(
            "scheduler_full_pipeline_configured",
            interval_hours=settings.scheduler_full_pipeline_interval_hours,
        )
    else:
        logger.info("scheduler_disabled_non_production")
