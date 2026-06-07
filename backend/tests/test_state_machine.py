import pytest

from app.models.base import DocumentStatus
from app.state_machine.machine import StateMachine, StateTransitionError


class TestStateMachine:
    def setup_method(self):
        self.machine = StateMachine()

    def test_valid_transition(self):
        result = self.machine.transition(DocumentStatus.DETECTED, DocumentStatus.ANALYZED)
        assert result == DocumentStatus.ANALYZED

    def test_invalid_transition(self):
        with pytest.raises(StateTransitionError):
            self.machine.transition(DocumentStatus.DETECTED, DocumentStatus.MAPPED)

    def test_same_status(self):
        result = self.machine.transition(DocumentStatus.DETECTED, DocumentStatus.DETECTED)
        assert result == DocumentStatus.DETECTED

    def test_full_lifecycle(self):
        transitions = [
            (DocumentStatus.DETECTED, DocumentStatus.ANALYZED),
            (DocumentStatus.ANALYZED, DocumentStatus.MAPPED),
            (DocumentStatus.MAPPED, DocumentStatus.SCORED),
            (DocumentStatus.SCORED, DocumentStatus.NOTIFIED),
            (DocumentStatus.NOTIFIED, DocumentStatus.PENDING_REVIEW),
            (DocumentStatus.PENDING_REVIEW, DocumentStatus.APPROVED),
            (DocumentStatus.APPROVED, DocumentStatus.CLOSED),
        ]
        current = None
        for from_s, to_s in transitions:
            current = self.machine.transition(from_s, to_s)
            assert current == to_s

    def test_reject_flow(self):
        self.machine.transition(DocumentStatus.DETECTED, DocumentStatus.ANALYZED)
        self.machine.transition(DocumentStatus.ANALYZED, DocumentStatus.MAPPED)
        self.machine.transition(DocumentStatus.MAPPED, DocumentStatus.SCORED)
        self.machine.transition(DocumentStatus.SCORED, DocumentStatus.NOTIFIED)
        self.machine.transition(DocumentStatus.NOTIFIED, DocumentStatus.PENDING_REVIEW)
        result = self.machine.transition(DocumentStatus.PENDING_REVIEW, DocumentStatus.REJECTED)
        assert result == DocumentStatus.REJECTED

    def test_can_transition(self):
        assert self.machine.can_transition(DocumentStatus.DETECTED, DocumentStatus.ANALYZED)
        assert not self.machine.can_transition(DocumentStatus.DETECTED, DocumentStatus.CLOSED)

    def test_get_allowed_transitions(self):
        allowed = self.machine.get_allowed_transitions(DocumentStatus.PENDING_REVIEW)
        assert DocumentStatus.APPROVED in allowed
        assert DocumentStatus.REJECTED in allowed

    def test_guard_blocked(self):
        guard_machine = StateMachine(guard=lambda: False)
        with pytest.raises(StateTransitionError):
            guard_machine.transition(DocumentStatus.DETECTED, DocumentStatus.ANALYZED)
