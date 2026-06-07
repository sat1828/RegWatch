from __future__ import annotations

import time
from collections import OrderedDict
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.analysis.agent import analysis_agent
from app.agents.mapping.agent import mapping_agent
from app.agents.reporter.agent import reporter_agent
from app.agents.risk_scorer.agent import risk_scorer_agent
from app.agents.watcher.agent import watcher_agent
from app.db.database import async_session_factory

logger = structlog.get_logger(__name__)

MAX_ACTIVE_PIPELINES = 100


class PipelineOrchestrator:
    def __init__(self) -> None:
        self._active_pipelines: OrderedDict[str, dict[str, Any]] = OrderedDict()

    async def run_full_pipeline(self, context: dict[str, Any] | None = None) -> str:
        pipeline_id = str(uuid4())
        ctx = context or {}
        ctx["pipeline_id"] = pipeline_id
        ctx["started_at"] = datetime.now(timezone.utc).isoformat()

        self._register_pipeline(pipeline_id, ctx)

        try:
            ctx["mode"] = "full_pipeline"
            await self._run_watcher(ctx)
            await self._run_analysis(ctx)
            await self._run_mapping(ctx)
            await self._run_scoring(ctx)
            await self._run_reporter(ctx)
            self._update_pipeline(pipeline_id, "status", "completed")
        except Exception as e:
            self._update_pipeline(pipeline_id, "status", "failed")
            self._update_pipeline(pipeline_id, "error", str(e))
            logger.error("pipeline_failed", pipeline_id=pipeline_id, error=str(e))
        finally:
            self._update_pipeline(pipeline_id, "completed_at", datetime.now(timezone.utc).isoformat())

        return pipeline_id

    async def run_watcher_only(self, context: dict[str, Any] | None = None) -> str:
        pipeline_id = str(uuid4())
        ctx = context or {}
        ctx["pipeline_id"] = pipeline_id
        ctx["started_at"] = datetime.now(timezone.utc).isoformat()
        ctx["mode"] = "watcher"

        self._register_pipeline(pipeline_id, ctx)

        try:
            await self._run_watcher(ctx)
            self._update_pipeline(pipeline_id, "status", "completed")
        except Exception as e:
            self._update_pipeline(pipeline_id, "status", "failed")
            self._update_pipeline(pipeline_id, "error", str(e))
            logger.error("watcher_pipeline_failed", pipeline_id=pipeline_id, error=str(e))
        finally:
            self._update_pipeline(pipeline_id, "completed_at", datetime.now(timezone.utc).isoformat())

        return pipeline_id

    async def _run_watcher(self, context: dict[str, Any]) -> None:
        logger.info("pipeline_step", step="watcher", pipeline_id=context.get("pipeline_id"))
        async with async_session_factory() as session:
            result = await watcher_agent.execute(session, context)
            context["watcher_result"] = result
            if not result.success:
                logger.warning("watcher_step_issues", errors=result.data.get("errors"))

    async def _run_analysis(self, context: dict[str, Any]) -> None:
        logger.info("pipeline_step", step="analysis", pipeline_id=context.get("pipeline_id"))
        async with async_session_factory() as session:
            result = await analysis_agent.execute(session, context)
            context["analysis_result"] = result

    async def _run_mapping(self, context: dict[str, Any]) -> None:
        logger.info("pipeline_step", step="mapping", pipeline_id=context.get("pipeline_id"))
        async with async_session_factory() as session:
            result = await mapping_agent.execute(session, context)
            context["mapping_result"] = result

    async def _run_scoring(self, context: dict[str, Any]) -> None:
        logger.info("pipeline_step", step="scoring", pipeline_id=context.get("pipeline_id"))
        async with async_session_factory() as session:
            result = await risk_scorer_agent.execute(session, context)
            context["scoring_result"] = result

    async def _run_reporter(self, context: dict[str, Any]) -> None:
        logger.info("pipeline_step", step="reporter", pipeline_id=context.get("pipeline_id"))
        async with async_session_factory() as session:
            result = await reporter_agent.execute(session, context)
            context["reporter_result"] = result

    def _register_pipeline(self, pipeline_id: str, context: dict[str, Any]) -> None:
        self._active_pipelines[pipeline_id] = {
            "status": "running",
            "context": context,
            "started_at": context.get("started_at"),
            "completed_at": None,
            "error": None,
        }
        while len(self._active_pipelines) > MAX_ACTIVE_PIPELINES:
            self._active_pipelines.popitem(last=False)

    def _update_pipeline(self, pipeline_id: str, key: str, value: Any) -> None:
        if pipeline_id in self._active_pipelines:
            self._active_pipelines[pipeline_id][key] = value

    def get_pipeline_status(self, pipeline_id: str) -> dict[str, Any] | None:
        return self._active_pipelines.get(pipeline_id)

    def get_active_pipelines(self) -> dict[str, dict[str, Any]]:
        return dict(self._active_pipelines)


orchestrator = PipelineOrchestrator()
