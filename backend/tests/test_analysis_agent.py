import uuid
from unittest.mock import patch

import pytest

from app.agents.analysis.agent import analysis_agent
from app.models.base import DocumentStatus
from app.models.regulatory_document import RegulatoryDocument
from app.models.regulatory_source import RegulatorySource


@pytest.mark.asyncio
async def test_execute_no_pending_docs(db_session):
    result = await analysis_agent.execute(db_session, {})
    assert result.success
    assert result.data["documents_analyzed"] == 0


@pytest.mark.asyncio
async def test_analyze_document(db_session, mock_anthropic):
    source = RegulatorySource(
        name="Test Source",
        url="https://example.com",
        source_type="html_index",
        jurisdiction="IN",
        regulator="SEBI",
        is_active=True,
    )
    db_session.add(source)
    await db_session.flush()

    doc = RegulatoryDocument(
        source_id=source.id,
        title="Test Circular",
        url="https://example.com/test",
        document_type="circular",
        raw_text="This is a regulatory circular about compliance requirements. Entities shall maintain proper records.",
        status=DocumentStatus.DETECTED,
    )
    db_session.add(doc)
    await db_session.commit()

    result = await analysis_agent.execute(db_session, {})
    assert result.success
    assert result.data["documents_analyzed"] == 1


@pytest.mark.asyncio
async def test_analyze_short_text(db_session):
    source = RegulatorySource(
        name="Test",
        url="https://example.com",
        source_type="html_index",
        jurisdiction="IN",
        regulator="SEBI",
        is_active=True,
    )
    db_session.add(source)
    await db_session.flush()

    doc = RegulatoryDocument(
        source_id=source.id,
        title="Short",
        url="https://example.com/short",
        raw_text="Short",
        status=DocumentStatus.DETECTED,
    )
    db_session.add(doc)
    await db_session.commit()

    result = await analysis_agent.execute(db_session, {})
    assert result.success
