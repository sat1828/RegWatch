from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import AgentResult, BaseAgent
from app.models.base import DocumentStatus
from app.models.enforcement import EnforcementAction
from app.models.obligation import ObligationRecord, SeverityLevel
from app.models.regulatory_document import RegulatoryDocument
from app.models.risk_score import RiskScore

logger = structlog.get_logger(__name__)


class RiskScorerAgent(BaseAgent):
    PENALTY_WEIGHT = 0.40
    DEADLINE_WEIGHT = 0.40
    ENFORCEMENT_WEIGHT = 0.20
    MAX_PENALTY_NORMALIZATION = 10_000_000

    def __init__(self) -> None:
        super().__init__("risk_scorer")

    async def execute(self, session: AsyncSession, context: dict[str, Any]) -> AgentResult:
        docs = await self._get_scorable_docs(session)
        if not docs:
            return AgentResult(success=True, data={"documents_scored": 0})

        total_scored = 0
        errors: list[str] = []

        for doc in docs:
            try:
                await self._score_document(session, doc)
                total_scored += 1
            except Exception as e:
                errors.append(f"Doc {doc.id}: {str(e)}")
                logger.error("scoring_error", doc_id=doc.id, error=str(e))

        if total_scored > 0:
            await self._rerank_priorities(session)

        return AgentResult(
            success=len(errors) == 0,
            data={"documents_scored": total_scored, "errors": errors},
        )

    async def _get_scorable_docs(self, session: AsyncSession) -> list[RegulatoryDocument]:
        result = await session.execute(
            select(RegulatoryDocument).where(
                RegulatoryDocument.status == DocumentStatus.MAPPED
            )
        )
        return list(result.scalars().all())

    async def _get_enforcement_stats(
        self, session: AsyncSession
    ) -> dict[str, Any]:
        result = await session.execute(
            select(EnforcementAction).where(EnforcementAction.is_active == True)
        )
        actions: list[EnforcementAction] = list(result.scalars().all())

        if not actions:
            return {"total_actions": 0, "avg_penalty": 0, "max_penalty": 0, "by_type": {}}

        penalties = [a.penalty_amount or 0 for a in actions if a.penalty_amount]
        by_type: dict[str, float] = {}
        for a in actions:
            by_type[a.action_type] = by_type.get(a.action_type, 0) + 1

        return {
            "total_actions": len(actions),
            "avg_penalty": sum(penalties) / len(penalties) if penalties else 0,
            "max_penalty": max(penalties) if penalties else 0,
            "by_type": by_type,
        }

    async def _score_document(
        self, session: AsyncSession, doc: RegulatoryDocument
    ) -> None:
        obligations = doc.obligations
        if not obligations:
            penalty_score = 0.1
            deadline_score = 0.3
            enforcement_score = 0.2
        else:
            penalty_score = self._calculate_penalty_score(obligations)
            deadline_score = self._calculate_deadline_score(obligations)
            enforcement_score = await self._calculate_enforcement_score(session, doc)

        overall = (
            penalty_score * self.PENALTY_WEIGHT
            + deadline_score * self.DEADLINE_WEIGHT
            + enforcement_score * self.ENFORCEMENT_WEIGHT
        )

        risk_category = self._categorize_risk(overall)

        reasoning = (
            f"Penalty score: {penalty_score:.2f} (weight {self.PENALTY_WEIGHT}), "
            f"Deadline score: {deadline_score:.2f} (weight {self.DEADLINE_WEIGHT}), "
            f"Enforcement score: {enforcement_score:.2f} (weight {self.ENFORCEMENT_WEIGHT})"
        )

        score = RiskScore(
            document_id=doc.id,
            overall_score=round(overall, 4),
            penalty_score=round(penalty_score, 4),
            deadline_score=round(deadline_score, 4),
            enforcement_score=round(enforcement_score, 4),
            priority_rank=999,
            risk_category=risk_category,
            reasoning=reasoning,
        )
        session.add(score)

        self._enforce_transition(doc.status, DocumentStatus.SCORED)
        doc.status = DocumentStatus.SCORED
        session.add(doc)

        await self._log_audit(
            session,
            "document_scored",
            "RegulatoryDocument",
            doc.id,
            f"Overall: {overall:.4f}, Category: {risk_category}",
        )
        await session.commit()

    def _calculate_penalty_score(self, obligations: list[ObligationRecord]) -> float:
        severity_map = {
            SeverityLevel.CRITICAL: 1.0,
            SeverityLevel.HIGH: 0.7,
            SeverityLevel.MEDIUM: 0.4,
            SeverityLevel.LOW: 0.2,
            SeverityLevel.INFO: 0.05,
        }

        if not obligations:
            return 0.0

        scores = [severity_map.get(o.severity, 0.3) for o in obligations]
        return sum(scores) / len(scores)

    def _calculate_deadline_score(self, obligations: list[ObligationRecord]) -> float:
        if not obligations:
            return 0.3

        now = datetime.now(timezone.utc)
        scores: list[float] = []

        for obligation in obligations:
            if obligation.deadline:
                days_remaining = (obligation.deadline - now).days
                if days_remaining < 0:
                    scores.append(1.0)
                elif days_remaining <= 30:
                    scores.append(0.9)
                elif days_remaining <= 90:
                    scores.append(0.6)
                elif days_remaining <= 180:
                    scores.append(0.3)
                else:
                    scores.append(0.1)
            else:
                scores.append(0.3)

        return sum(scores) / len(scores)

    async def _calculate_enforcement_score(
        self, session: AsyncSession, doc: RegulatoryDocument
    ) -> float:
        stats = await self._get_enforcement_stats(session)
        if stats["total_actions"] == 0:
            return 0.2

        max_penalty = stats["max_penalty"]
        if max_penalty > 0 and doc.source:
            regulator_actions = [
                a
                for a in (
                    await session.execute(
                        select(EnforcementAction).where(
                            EnforcementAction.regulator == doc.source.regulator,
                            EnforcementAction.is_active == True,
                        )
                    )
                ).scalars().all()
            ]
            if regulator_actions:
                recent = [
                    a for a in regulator_actions if a.action_date
                    and (datetime.now(timezone.utc) - a.action_date).days < 365
                ]
                if recent:
                    return 0.8
                return 0.5

        return 0.3

    def _categorize_risk(self, score: float) -> str:
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        elif score >= 0.2:
            return "LOW"
        return "NEGLIGIBLE"

    async def _rerank_priorities(self, session: AsyncSession) -> None:
        result = await session.execute(
            select(RiskScore).order_by(RiskScore.overall_score.desc())
        )
        scores: list[RiskScore] = list(result.scalars().all())
        for rank, score in enumerate(scores, start=1):
            score.priority_rank = rank
            session.add(score)
        await session.commit()


risk_scorer_agent = RiskScorerAgent()
