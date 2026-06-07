from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.state_machine.machine import pipeline_state_machine


@dataclass
class AgentResult:
    success: bool = False
    data: Any = None
    error: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)


class BaseAgent:
    def __init__(self, name: str) -> None:
        self.name = name

    async def execute(self, session: AsyncSession, context: dict[str, Any]) -> AgentResult:
        raise NotImplementedError

    def _enforce_transition(self, current: Any, target: Any) -> None:
        pipeline_state_machine.transition(current, target)

    async def _log_audit(
        self,
        session: AsyncSession,
        action: str,
        entity_type: str,
        entity_id: str | None = None,
        details: str | None = None,
    ) -> None:
        try:
            from app.models.audit_log import AuditLog

            log = AuditLog(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                actor="system",
                details=details,
            )
            session.add(log)
        except Exception:
            pass
