from unittest.mock import AsyncMock, patch

import pytest

from app.agents.watcher.agent import watcher_agent
from app.models.base import DocumentStatus
from app.models.regulatory_source import RegulatorySource


@pytest.mark.asyncio
async def test_execute_no_active_sources(db_session):
    with patch.object(watcher_agent, "_get_active_sources", return_value=[]):
        result = await watcher_agent.execute(db_session, {})
        assert result.success
        assert result.data["documents_detected"] == 0


@pytest.mark.asyncio
async def test_execute_with_source(db_session, mock_anthropic):
    source = RegulatorySource(
        name="Test Source",
        url="https://example.com",
        source_type="html_index",
        jurisdiction="IN",
        regulator="SEBI",
        is_active=True,
    )
    db_session.add(source)
    await db_session.commit()

    with patch("app.agents.watcher.agent.scraper_factory.fetch_document_content", new_callable=AsyncMock) as mock_scrape:
        mock_scrape.return_value.success = True
        mock_scrape.return_value.html = "<html><body>test content</body></html>"
        mock_scrape.return_value.text = "test content"
        mock_scrape.return_value.links = [
            {"title": "Circular 2025/01", "url": "https://example.com/circular1"},
        ]
        mock_scrape.return_value.pdf_bytes = None

        with patch("app.agents.watcher.agent.scraper_factory.fetch_document_content") as mock_doc_fetch:
            mock_doc_fetch.return_value.success = True
            mock_doc_fetch.return_value.text = "Full circular text"
            mock_doc_fetch.return_value.pdf_bytes = None

            result = await watcher_agent.execute(db_session, {})
            assert result.success


@pytest.mark.asyncio
async def test_detect_change(db_session):
    source = RegulatorySource(
        name="Test Source",
        url="https://example.com/pdf-test.pdf",
        source_type="pdf",
        jurisdiction="IN",
        regulator="RBI",
        is_active=True,
        last_content_hash="oldhash",
        last_raw_text="old content",
    )
    db_session.add(source)
    await db_session.commit()

    with patch("app.agents.watcher.agent.scraper_factory.fetch_document_content", new_callable=AsyncMock) as mock_scrape:
        mock_scrape.return_value.success = True
        mock_scrape.return_value.pdf_bytes = b"new pdf content"
        mock_scrape.return_value.html = ""
        mock_scrape.return_value.text = ""
        mock_scrape.return_value.links = []

        with patch("app.agents.watcher.agent.pdf_parser.extract_text", return_value="new pdf text content"):
            result = await watcher_agent.execute(db_session, {})
            assert result.success
            assert result.data["documents_detected"] >= 1
