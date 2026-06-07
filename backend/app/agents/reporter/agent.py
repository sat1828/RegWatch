from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import AgentResult, BaseAgent
from app.models.base import DocumentStatus
from app.models.compliance_gap import ComplianceGap
from app.models.obligation import ObligationRecord, SeverityLevel
from app.models.policy import PolicyDraft
from app.models.regulatory_document import RegulatoryDocument
from app.models.risk_score import RiskScore
from app.services.anthropic_client import anthropic_client
from app.services.notification import notification_service

logger = structlog.get_logger(__name__)

DRAFT_SYSTEM_PROMPT = """You are a compliance policy writer. You create precise, actionable policy amendments 
or new policy documents based on regulatory obligations and identified compliance gaps.
Write in clear, formal language suitable for a corporate policy document.
Include: purpose, scope, policy statements, responsibilities, and review cadence."""


class ReporterAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("reporter")

    async def execute(self, session: AsyncSession, context: dict[str, Any]) -> AgentResult:
        docs = await self._get_reportable_docs(session)
        if not docs:
            return AgentResult(success=True, data={"drafts_created": 0, "notifications_sent": 0})

        drafts_created = 0
        notifications_sent = 0
        errors: list[str] = []

        for doc in docs:
            try:
                draft = await self._create_draft(session, doc)
                if draft:
                    drafts_created += 1
            except Exception as e:
                errors.append(f"Doc {doc.id} draft: {str(e)}")

        digest = await self._compile_digest_stats(session)
        notified = await self._send_digest(session, digest)
        if notified:
            notifications_sent += 1

        return AgentResult(
            success=len(errors) == 0,
            data={
                "drafts_created": drafts_created,
                "notifications_sent": notifications_sent,
                "errors": errors,
                "digest": digest,
            },
        )

    async def _get_reportable_docs(self, session: AsyncSession) -> list[RegulatoryDocument]:
        result = await session.execute(
            select(RegulatoryDocument).where(
                RegulatoryDocument.status == DocumentStatus.SCORED
            )
        )
        return list(result.scalars().all())

    async def _create_draft(
        self, session: AsyncSession, doc: RegulatoryDocument
    ) -> PolicyDraft | None:
        gaps = await self._get_doc_gaps(session, doc)
        gaps_text = self._format_gaps_for_prompt(gaps) if gaps else "No specific gaps identified."

        prompt = f"""Create a policy amendment or new policy document addressing the following regulatory requirements:

Document: {doc.title}
Source: {doc.source.name if doc.source else 'Unknown'}

Regulatory Obligations:
{chr(10).join(f'- [{o.severity.value}] {o.obligation_text[:200]}' for o in (doc.obligations or []))}

Compliance Gaps:
{gaps_text}

Write a complete policy document section that addresses these requirements."""

        draft_text = await anthropic_client.generate_text(
            system_prompt=DRAFT_SYSTEM_PROMPT,
            user_prompt=prompt,
            max_tokens=4096,
        )

        if not draft_text:
            logger.warning("draft_generation_failed", doc_id=doc.id)
            return None

        draft = PolicyDraft(
            document_id=doc.id,
            title=f"Amendment: {doc.title}",
            content=draft_text,
            status=DocumentStatus.PENDING_REVIEW,
            change_summary=f"Auto-generated amendment for {doc.title}",
        )
        session.add(draft)

        self._enforce_transition(doc.status, DocumentStatus.NOTIFIED)
        doc.status = DocumentStatus.NOTIFIED
        session.add(doc)

        await self._log_audit(
            session,
            "draft_created",
            "PolicyDraft",
            draft.id,
            f"Draft for {doc.title}",
        )
        await session.commit()

        return draft

    async def _get_doc_gaps(
        self, session: AsyncSession, doc: RegulatoryDocument
    ) -> list[ComplianceGap]:
        if not doc.obligations:
            return []
        obligation_ids = [o.id for o in doc.obligations]
        result = await session.execute(
            select(ComplianceGap).where(
                ComplianceGap.obligation_id.in_(obligation_ids)
            )
        )
        return list(result.scalars().all())

    @staticmethod
    def _format_gaps_for_prompt(gaps: list[ComplianceGap]) -> str:
        lines: list[str] = []
        for g in gaps:
            lines.append(f"- [{g.severity.value}] {g.gap_description}")
            if g.recommendation:
                lines.append(f"  Recommendation: {g.recommendation}")
        return "\n".join(lines) if lines else "No gaps identified."

    async def _compile_digest_stats(self, session: AsyncSession) -> dict[str, Any]:
        total_docs = await session.scalar(select(func.count(RegulatoryDocument.id)))
        total_obligations = await session.scalar(select(func.count(ObligationRecord.id)))

        critical_count = await session.scalar(
            select(func.count(ObligationRecord.id)).where(
                ObligationRecord.severity == SeverityLevel.CRITICAL
            )
        )

        high_scores = await session.scalar(
            select(func.count(RiskScore.id)).where(RiskScore.overall_score >= 0.7)
        )

        pending_review = await session.scalar(
            select(func.count(PolicyDraft.id)).where(
                PolicyDraft.status == DocumentStatus.PENDING_REVIEW
            )
        )

        return {
            "total_documents": total_docs or 0,
            "total_obligations": total_obligations or 0,
            "critical_obligations": critical_count or 0,
            "high_risk_items": high_scores or 0,
            "pending_reviews": pending_review or 0,
            "report_time": datetime.now(timezone.utc).isoformat(),
        }

    async def _send_digest(
        self, session: AsyncSession, digest: dict[str, Any]
    ) -> bool:
        subject = f"RegWatch Digest - {digest['report_time'][:10]}"

        message = (
            f"*RegWatch Daily Digest*\n"
            f"• Documents tracked: {digest['total_documents']}\n"
            f"• Obligations found: {digest['total_obligations']}\n"
            f"• Critical obligations: {digest['critical_obligations']}\n"
            f"• High-risk items: {digest['high_risk_items']}\n"
            f"• Pending reviews: {digest['pending_reviews']}"
        )

        slack_sent = await notification_service.send_slack_message(message)

        return slack_sent


reporter_agent = ReporterAgent()
