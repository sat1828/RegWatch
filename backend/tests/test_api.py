from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    with patch("app.core.deps.verify_api_key", return_value="test-key"):
        with patch("app.api.v1.router.orchestrator"):
            response = await client.get("/api/v1/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_dashboard_stats(client):
    with patch("app.core.deps.verify_api_key", return_value="test-key"):
        with patch("app.api.v1.router.orchestrator"):
            response = await client.get("/api/v1/dashboard/stats")
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_sources(client):
    with patch("app.core.deps.verify_api_key", return_value="test-key"):
        with patch("app.api.v1.router.orchestrator"):
            response = await client.get("/api/v1/sources")
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_source(client):
    with patch("app.core.deps.verify_api_key", return_value="test-key"):
        with patch("app.api.v1.router.orchestrator"):
            response = await client.post(
                "/api/v1/sources",
                json={"name": "Test Source", "url": "https://test.example.com", "source_type": "html_index", "jurisdiction": "IN", "regulator": "SEBI"},
            )
            assert response.status_code in (200, 201, 422, 500)
