from unittest.mock import AsyncMock, patch

import pytest

from app.orchestrator.pipeline import orchestrator


@pytest.mark.asyncio
async def test_pipeline_registration():
    with patch("app.orchestrator.pipeline.async_session_factory"):
        pipeline_id = await orchestrator.run_full_pipeline({"trigger": "test"})
        status = orchestrator.get_pipeline_status(pipeline_id)
        assert status is not None
        assert "status" in status


@pytest.mark.asyncio
async def test_pipeline_capped():
    with patch("app.orchestrator.pipeline.async_session_factory"):
        for i in range(101):
            await orchestrator.run_full_pipeline({"trigger": "test", "idx": i})
        assert len(orchestrator.get_active_pipelines()) <= 100


@pytest.mark.asyncio
async def test_watcher_only():
    with patch("app.orchestrator.pipeline.async_session_factory"):
        pipeline_id = await orchestrator.run_watcher_only({"trigger": "test"})
        status = orchestrator.get_pipeline_status(pipeline_id)
        assert status is not None


@pytest.mark.asyncio
async def test_pipeline_not_found():
    status = orchestrator.get_pipeline_status("nonexistent-id")
    assert status is None
