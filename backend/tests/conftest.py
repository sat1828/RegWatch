from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base


@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with factory() as session:
        yield session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    with patch("app.core.deps.verify_api_key", return_value="test-key"):
        from app.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest.fixture
def mock_anthropic():
    with patch("app.agents.analysis.agent.anthropic_client.extract_structured", new_callable=AsyncMock) as mock:
        mock.return_value = {
            "obligations": [
                {
                    "obligation_text": "Maintain transaction records",
                    "obligation_category": "record_keeping",
                    "severity": "HIGH",
                    "deadline": None,
                    "regulation_reference": "SEBI Reg 15",
                    "is_mandatory": True,
                }
            ],
            "summary": "Test analysis",
            "document_category": "circular",
        }
        yield mock
