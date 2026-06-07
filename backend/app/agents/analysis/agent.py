from __future__ import annotations

import json
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import AgentResult, BaseAgent
from app.models.base import DocumentStatus
from app.models.obligation import ObligationRecord, SeverityLevel
from app.models.regulatory_document import RegulatoryDocument
from app.services.anthropic_client import anthropic_client

logger = structlog.get_logger(__name__)

OBLIGATION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "obligations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "obligation_text": {"type": "string"},
                    "obligation_category": {
                        "type": "string",
                        "enum": [
                            "record_keeping",
                            "reporting",
                            "disclosure",
                            "governance",
                            "risk_management",
                            "capital_adequacy",
                            "consumer_protection",
                            "market_conduct",
                            "anti_money_laundering",
                            "data_protection",
                            "general",
                        ],
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"],
                    },
                    "deadline": {"type": ["string", "null"]},
                    "regulation_reference": {"type": ["string", "null"]},
                    "is_mandatory": {"type": "boolean"},
                },
                "required": ["obligation_text", "obligation_category", "severity", "is_mandatory"],
            },
        },
        "summary": {"type": "string"},
        "document_category": {"type": "string"},
    },
    "required": ["obligations", "summary"],
}

SYSTEM_PROMPT = """You are a regulatory compliance analyst specializing in Indian financial regulations.
Analyze the given regulatory document text and extract all explicit and implicit obligations.
For each obligation, classify its category, severity, deadline (if any), and regulation reference.
Be thorough — capture every compliance requirement, even implied ones.
Consider regulations from SEBI, RBI, IRDAI, MCA, and other Indian regulators."""


class AnalysisAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("analysis")

    async def execute(self, session: AsyncSession, context: dict[str, Any]) -> AgentResult:
        docs = await self._get_pending_docs(session)
        if not docs:
            return AgentResult(success=True, data={"documents_analyzed": 0})

        total_analyzed = 0
        errors: list[str] = []

        for doc in docs:
            try:
                await self._analyze_document(session, doc)
                total_analyzed += 1
            except Exception as e:
                errors.append(f"Doc {doc.id}: {str(e)}")
                logger.error("analysis_error", doc_id=doc.id, error=str(e))

        return AgentResult(
            success=len(errors) == 0,
            data={"documents_analyzed": total_analyzed, "errors": errors},
        )

    async def _get_pending_docs(self, session: AsyncSession) -> list[RegulatoryDocument]:
        result = await session.execute(
            select(RegulatoryDocument).where(
                RegulatoryDocument.status == DocumentStatus.DETECTED
            )
        )
        return list(result.scalars().all())

    async def _analyze_document(
        self, session: AsyncSession, doc: RegulatoryDocument
    ) -> None:
        text_to_analyze = doc.delta_text or doc.raw_text or ""
        if len(text_to_analyze.strip()) < 20:
            logger.warning("doc_text_too_short", doc_id=doc.id)
            doc.status = DocumentStatus.ANALYZED
            session.add(doc)
            await session.commit()
            return

        result = await anthropic_client.extract_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"Analyze this regulatory document and extract all obligations:\n\n{text_to_analyze[:50000]}",
            json_schema=OBLIGATION_SCHEMA,
        )

        if not result or "obligations" not in result:
            logger.warning("no_obligations_extracted", doc_id=doc.id)
            doc.status = DocumentStatus.ANALYZED
            session.add(doc)
            await session.commit()
            return

        obligations_data = result["obligations"]
        for obl_data in obligations_data:
            deadline = None
            if obl_data.get("deadline"):
                try:
                    from datetime import datetime

                    deadline = datetime.fromisoformat(obl_data["deadline"].replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    deadline = None

            severity_str = obl_data.get("severity", "MEDIUM").upper()
            try:
                severity = SeverityLevel(severity_str)
            except ValueError:
                severity = SeverityLevel.MEDIUM

            obligation = ObligationRecord(
                document_id=doc.id,
                obligation_text=obl_data.get("obligation_text", ""),
                obligation_category=obl_data.get("obligation_category", "general"),
                severity=severity,
                deadline=deadline,
                regulation_reference=obl_data.get("regulation_reference"),
                is_mandatory=obl_data.get("is_mandatory", True),
                metadata_json=json.dumps({"summary": result.get("summary", "")}),
            )
            session.add(obligation)

        self._enforce_transition(doc.status, DocumentStatus.ANALYZED)
        doc.status = DocumentStatus.ANALYZED
        session.add(doc)

        await self._log_audit(
            session,
            "document_analyzed",
            "RegulatoryDocument",
            doc.id,
            f"Extracted {len(obligations_data)} obligations",
        )
        await session.commit()


analysis_agent = AnalysisAgent()
