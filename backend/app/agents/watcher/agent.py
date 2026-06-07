from __future__ import annotations

import hashlib
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import AgentResult, BaseAgent
from app.models.base import DocumentStatus
from app.models.regulatory_document import RegulatoryDocument
from app.models.regulatory_source import RegulatorySource
from app.services.diff_engine import diff_engine
from app.services.pdf_parser import pdf_parser
from app.services.scraper import ScrapeResult, scraper_factory

logger = structlog.get_logger(__name__)


class WatcherAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("watcher")

    async def execute(self, session: AsyncSession, context: dict[str, Any]) -> AgentResult:
        sources = await self._get_active_sources(session)
        if not sources:
            return AgentResult(success=True, data={"documents_detected": 0, "message": "No active sources"})

        total_detected = 0
        errors: list[str] = []

        for source in sources:
            try:
                count = await self._check_source(session, source)
                total_detected += count
            except Exception as e:
                error_msg = f"Source {source.name}: {str(e)}"
                errors.append(error_msg)
                logger.error("watcher_source_error", source=source.name, error=str(e))

        return AgentResult(
            success=len(errors) == 0,
            data={
                "documents_detected": total_detected,
                "sources_checked": len(sources),
                "errors": errors,
            },
        )

    async def _get_active_sources(self, session: AsyncSession) -> list[RegulatorySource]:
        result = await session.execute(
            select(RegulatorySource).where(RegulatorySource.is_active == True)
        )
        return list(result.scalars().all())

    async def _check_source(
        self, session: AsyncSession, source: RegulatorySource
    ) -> int:
        result = await scraper_factory.fetch_document_content(source.url)
        if not result.success:
            logger.warning("source_scrape_failed", source=source.name, url=source.url)
            return 0

        if result.pdf_bytes:
            documents = await self._process_pdf_source(session, source, result)
        else:
            documents = await self._process_html_source(session, source, result)

        source.last_scraped_at = __import__("datetime").datetime.now(__import__("pytz").UTC)
        session.add(source)
        await session.commit()

        return len(documents)

    async def _process_pdf_source(
        self, session: AsyncSession, source: RegulatorySource, result: ScrapeResult
    ) -> list[RegulatoryDocument]:
        text = await pdf_parser.extract_text(result.pdf_bytes)
        if not text:
            logger.warning("pdf_extraction_empty", source=source.name)
            return []

        content_hash = hashlib.sha256(text.encode()).hexdigest()

        if source.last_content_hash == content_hash:
            logger.info("no_change_pdf", source=source.name)
            return []

        previous_text = source.last_raw_text or ""

        delta = diff_engine.compute_delta(previous_text, text)

        doc = RegulatoryDocument(
            source_id=source.id,
            title=f"PDF from {source.name}",
            url=source.url,
            document_type="pdf",
            raw_text=text,
            previous_raw_text=previous_text,
            delta_text=delta,
            content_hash=content_hash,
            status=DocumentStatus.DETECTED,
        )
        session.add(doc)

        source.last_raw_text = text
        source.last_content_hash = content_hash

        await self._log_audit(session, "document_detected", "RegulatoryDocument", doc.id)
        return [doc]

    async def _process_html_source(
        self, session: AsyncSession, source: RegulatorySource, result: ScrapeResult
    ) -> list[RegulatoryDocument]:
        documents: list[RegulatoryDocument] = []
        links = result.links

        if not links:
            content_hash = hashlib.sha256(result.text.encode()).hexdigest()
            if source.last_content_hash == content_hash:
                return []

            previous_text = source.last_raw_text or ""
            delta = diff_engine.compute_delta(previous_text, result.text)

            doc = RegulatoryDocument(
                source_id=source.id,
                title=source.name,
                url=source.url,
                document_type="html_index",
                raw_text=result.text,
                previous_raw_text=previous_text,
                delta_text=delta,
                content_hash=content_hash,
                status=DocumentStatus.DETECTED,
            )
            session.add(doc)
            source.last_raw_text = result.text
            source.last_content_hash = content_hash
            documents.append(doc)
            return documents

        seen_hashes: set[str] = set()
        if source.documents:
            seen_hashes = {d.content_hash or "" for d in source.documents if d.content_hash}

        for link in links[:50]:
            link_url = link.get("url", "")
            link_title = link.get("title", "").strip()

            if not link_url or not link_title:
                continue

            doc_result = await scraper_factory.fetch_document_content(link_url)
            doc_text = ""

            if doc_result.pdf_bytes:
                doc_text = await pdf_parser.extract_text(doc_result.pdf_bytes) or link_title
            elif doc_result.text:
                doc_text = doc_result.text
            else:
                doc_text = link_title

            content_hash = hashlib.sha256(doc_text.encode()).hexdigest()
            if content_hash in seen_hashes:
                continue

            seen_hashes.add(content_hash)

            doc = RegulatoryDocument(
                source_id=source.id,
                title=link_title,
                url=link_url,
                document_type="circular",
                raw_text=doc_text,
                previous_raw_text=None,
                delta_text=None,
                content_hash=content_hash,
                status=DocumentStatus.DETECTED,
            )
            session.add(doc)
            documents.append(doc)

        source.last_raw_text = result.text
        source.last_content_hash = hashlib.sha256(result.text.encode()).hexdigest()

        for doc in documents:
            await self._log_audit(session, "document_detected", "RegulatoryDocument", doc.id)

        return documents


watcher_agent = WatcherAgent()
