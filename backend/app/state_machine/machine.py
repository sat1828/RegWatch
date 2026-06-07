from __future__ import annotations

from collections.abc import Callable

from app.models.base import DocumentStatus


class StateTransitionError(Exception):
    def __init__(self, from_status: DocumentStatus, to_status: DocumentStatus) -> None:
        self.from_status = from_status
        self.to_status = to_status
        super().__init__(f"Invalid transition: {from_status.value} -> {to_status.value}")


TransitionGuard = Callable[[], bool] | None


class StateMachine:
    TRANSITIONS: dict[DocumentStatus, set[DocumentStatus]] = {
        DocumentStatus.DETECTED: {DocumentStatus.ANALYZED},
        DocumentStatus.ANALYZED: {DocumentStatus.MAPPED, DocumentStatus.PENDING_REVIEW},
        DocumentStatus.MAPPED: {DocumentStatus.SCORED, DocumentStatus.PENDING_REVIEW},
        DocumentStatus.SCORED: {DocumentStatus.NOTIFIED, DocumentStatus.PENDING_REVIEW},
        DocumentStatus.NOTIFIED: {DocumentStatus.PENDING_REVIEW},
        DocumentStatus.PENDING_REVIEW: {
            DocumentStatus.APPROVED,
            DocumentStatus.REJECTED,
            DocumentStatus.ANALYZED,
            DocumentStatus.MAPPED,
            DocumentStatus.SCORED,
        },
        DocumentStatus.APPROVED: {DocumentStatus.CLOSED, DocumentStatus.PENDING_REVIEW},
        DocumentStatus.REJECTED: {DocumentStatus.CLOSED, DocumentStatus.PENDING_REVIEW},
        DocumentStatus.CLOSED: set(),
    }

    def __init__(
        self,
        guard: TransitionGuard = None,
        on_transition: Callable[[DocumentStatus, DocumentStatus], None] | None = None,
    ) -> None:
        self._guard = guard
        self._on_transition = on_transition

    def can_transition(self, from_status: DocumentStatus, to_status: DocumentStatus) -> bool:
        allowed = self.TRANSITIONS.get(from_status, set())
        return to_status in allowed

    def transition(
        self,
        from_status: DocumentStatus,
        to_status: DocumentStatus,
    ) -> DocumentStatus:
        if from_status == to_status:
            return to_status

        if not self.can_transition(from_status, to_status):
            raise StateTransitionError(from_status, to_status)

        if self._guard is not None and not self._guard():
            raise StateTransitionError(from_status, to_status)

        if self._on_transition is not None:
            self._on_transition(from_status, to_status)

        return to_status

    def get_allowed_transitions(self, status: DocumentStatus) -> list[DocumentStatus]:
        return list(self.TRANSITIONS.get(status, set()))


pipeline_state_machine = StateMachine()
