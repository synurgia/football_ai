from typing import Any, Dict, Optional

from app.v2_evidence_state import V2EvidenceItem, V2EvidenceState


class V12QuestionResolver:
    """
    V1.2 question-by-question evidence resolver.

    This component does not invent answers.
    It records verified evidence when supplied and otherwise
    preserves UNKNOWN / INSUFFICIENT_EVIDENCE states.
    """

    def resolve(
        self,
        state: V2EvidenceState,
        question_id: str,
        *,
        answer: Optional[str] = None,
        evidence: Optional[str] = None,
        supports: Optional[str] = None,
        confidence: Optional[float] = None,
        source: Optional[str] = None,
        source_reference: Optional[str] = None,
        observation_time: Optional[str] = None,
        impact: Optional[str] = None,
        status: str = "UNKNOWN",
        notes: Optional[str] = None,
    ) -> V2EvidenceState:
        item = self._get_item(state, question_id)

        if item is None:
            raise ValueError(f"Unknown question ID: {question_id}")

        item.answer = answer
        item.evidence = evidence
        item.supports = supports
        item.confidence = confidence
        item.source = source
        item.source_reference = source_reference
        item.observation_time = observation_time
        item.impact = impact
        item.status = status
        item.notes = notes

        return state

    def unresolved_questions(self, state: V2EvidenceState):
        return [
            item
            for item in state.items
            if str(item.status).upper() in {"UNKNOWN", "UNVERIFIED", "UNRESOLVED", "INSUFFICIENT", "INSUFFICIENT_EVIDENCE"}
        ]

    @staticmethod
    def _get_item(
        state: V2EvidenceState,
        question_id: str,
    ) -> Optional[V2EvidenceItem]:
        for item in state.items:
            if item.question_id == question_id:
                return item
        return None
