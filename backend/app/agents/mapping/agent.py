from __future__ import annotations

import json
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import AgentResult, BaseAgent
from app.models.base import DocumentStatus
from app.models.compliance_gap import ComplianceGap, GapSeverity
from app.models.obligation import ObligationRecord
from app.models.policy import PolicyChunk, PolicyDocument
from app.services.anthropic_client import anthropic_client
from app.services.vector_store import vector_store

logger = structlog.get_logger(__name__)

REASONING_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "gaps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "gap_type": {
                        "type": "string",
                        "enum": [
                            "missing_policy",
                            "partial_coverage",
                            "outdated_policy",
                            "ambiguous_wording",
                            "no_assigned_owner",
                            "missing_monitoring",
                            "other",
                        ],
                    },
                    "gap_description": {"type": "string"},
                    "severity": {
                        "type": "string",
                        "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                    },
                    "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "recommendation": {"type": "string"},
                    "reasoning": {"type": "string"},
                },
                "required": [
                    "gap_type",
                    "gap_description",
                    "severity",
                    "confidence_score",
                    "recommendation",
                    "reasoning",
                ],
            },
        }
    },
    "required": ["gaps"],
}

SYSTEM_PROMPT = """You are a compliance mapping analyst. Your job is to compare regulatory obligations against existing internal policies and identify compliance gaps.

IMPORTANT RULES:
1. "Semantically adjacent ≠ compliant" — a policy that touches on a related topic but doesn't specifically address the obligation is a GAP, not compliance.
2. Be precise about what is missing. Vague gap descriptions are not acceptable.
3. Consider both explicit policies and implied obligations.
4. Rate confidence honestly — 0.9+ only when the gap is clear and unambiguous.
5. For each gap, provide a concrete, actionable recommendation."""


class MappingAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("mapping")

    async def execute(self, session: AsyncSession, context: dict[str, Any]) -> AgentResult:
        obligations = await self._get_unmapped_obligations(session)
        if not obligations:
            return AgentResult(success=True, data={"gaps_identified": 0})

        policies = await self._get_policies(session)
        total_gaps = 0
        errors: list[str] = []

        for obligation in obligations:
            try:
                gaps = await self._map_obligation(session, obligation, policies)
                total_gaps += len(gaps)
            except Exception as e:
                errors.append(f"Obligation {obligation.id}: {str(e)}")
                logger.error("mapping_error", obligation_id=obligation.id, error=str(e))

        return AgentResult(
            success=len(errors) == 0,
            data={"gaps_identified": total_gaps, "errors": errors},
        )

    async def _get_unmapped_obligations(self, session: AsyncSession) -> list[ObligationRecord]:
        result = await session.execute(
            select(ObligationRecord)
            .join(ObligationRecord.document)
            .where(
                RegulatoryDocument.status == DocumentStatus.ANALYZED  # type: ignore
            )
        )
        return list(result.scalars().all())

    async def _get_policies(self, session: AsyncSession) -> list[PolicyDocument]:
        result = await session.execute(
            select(PolicyDocument).where(PolicyDocument.is_active == True)
        )
        return list(result.scalars().all())

    async def _get_relevant_policy_text(
        self, obligation: ObligationRecord, policies: list[PolicyDocument]
    ) -> str:
        relevant_texts: list[str] = []

        for policy in policies:
            chunks = await vector_store.query_similar(
                query_vector=[0.0] * vector_store.dimension,
                top_k=3,
                namespace=f"policy_{policy.id}",
                filter_dict={"policy_id": policy.id},
            )
            if not chunks:
                for chunk in policy.chunks:
                    relevant_texts.append(
                        f"[Policy: {policy.title}]\n{chunk.content[:2000]}"
                    )
                continue

            for chunk in chunks:
                meta = chunk.get("metadata", {})
                content = meta.get("content", "")
                if content:
                    relevant_texts.append(
                        f"[Policy: {meta.get('policy_title', policy.title)}, Section: {meta.get('chunk_index', '?')}]\n{content[:2000]}"
                    )

        return "\n\n---\n\n".join(relevant_texts[:5]) or "No existing policies found."

    async def _map_obligation(
        self,
        session: AsyncSession,
        obligation: ObligationRecord,
        policies: list[PolicyDocument],
    ) -> list[ComplianceGap]:
        policy_context = await self._get_relevant_policy_text(obligation, policies)

        result = await anthropic_client.extract_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"""Regulatory Obligation:
{obligation.obligation_text}
Category: {obligation.obligation_category}
Severity: {obligation.severity.value}

Existing Internal Policies:
{policy_context}

Identify any compliance gaps between this obligation and the policies.""",
            json_schema=REASONING_SCHEMA,
        )

        if not result or "gaps" not in result:
            return []

        gaps: list[ComplianceGap] = []
        for gap_data in result["gaps"]:
            severity_str = gap_data.get("severity", "MEDIUM").upper()
            try:
                severity = GapSeverity(severity_str)
            except ValueError:
                severity = GapSeverity.MEDIUM

            gap = ComplianceGap(
                obligation_id=obligation.id,
                gap_type=gap_data.get("gap_type", "missing_policy"),
                gap_description=gap_data.get("gap_description", ""),
                severity=severity,
                confidence_score=min(max(gap_data.get("confidence_score", 0.0), 0.0), 1.0),
                recommendation=gap_data.get("recommendation"),
                reasoning=gap_data.get("reasoning"),
            )
            session.add(gap)
            gaps.append(gap)

        if gaps:
            doc = obligation.document
            self._enforce_transition(doc.status, DocumentStatus.MAPPED)
            doc.status = DocumentStatus.MAPPED
            session.add(doc)

        await session.commit()

        await self._log_audit(
            session,
            "obligation_mapped",
            "ObligationRecord",
            obligation.id,
            f"Mapped to {len(gaps)} gaps",
        )

        return gaps


from app.models.regulatory_document import RegulatoryDocument

mapping_agent = MappingAgent()
