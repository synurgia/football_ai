from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


VALID_STATUSES = {
    "VERIFIED",
    "UNVERIFIED",
    "INSUFFICIENT_EVIDENCE",
    "FAILED",
}


@dataclass
class Evidence:
    source_id: str
    question_id: str
    answer: Any
    status: str = "VERIFIED"
    method: str = "SOURCE_EVIDENCE"
    confidence: str = "MEDIUM"
    evidence: str = ""
    freshness: Any = None
    source_url: str | None = None

    def __post_init__(self) -> None:
        if self.status not in VALID_STATUSES:
            self.status = "UNVERIFIED"


@dataclass
class QuestionReasoning:
    question_id: str
    answer: Any = "UNKNOWN"
    status: str = "INSUFFICIENT_EVIDENCE"
    method: str = "NO_VERIFIED_EVIDENCE"
    confidence: str = "NONE"

    supporting_evidence: List[Dict[str, Any]] = field(
        default_factory=list
    )
    conflicting_evidence: List[Dict[str, Any]] = field(
        default_factory=list
    )
    unresolved_evidence: List[Dict[str, Any]] = field(
        default_factory=list
    )

    reasoning: str = ""
    freshness: List[Any] = field(default_factory=list)


class V13EvidenceReasoningEngine:
    """
    Evidence-to-answer reasoning layer.

    Rules:
    1. Uses only supplied evidence.
    2. Never invents an answer.
    3. Never gives a source artificial priority.
    4. Agreement increases confidence.
    5. Direct conflict produces CONFLICT unless one side is
       independently unavailable/invalid.
    6. Missing evidence remains INSUFFICIENT_EVIDENCE.
    """

    def reason(
        self,
        question_id: str,
        evidence_items: List[Evidence],
    ) -> QuestionReasoning:

        verified = [
            e for e in evidence_items
            if e.status == "VERIFIED"
            and e.answer is not None
            and e.answer != "UNKNOWN"
        ]

        unresolved = [
            e for e in evidence_items
            if e not in verified
        ]

        if not verified:
            return QuestionReasoning(
                question_id=question_id,
                unresolved_evidence=[
                    self._serialize(e) for e in unresolved
                ],
                reasoning=(
                    "No verified evidence currently establishes "
                    "an answer to this question."
                ),
            )

        groups: Dict[str, List[Evidence]] = {}

        for item in verified:
            key = self._normalise_answer(item.answer)
            groups.setdefault(key, []).append(item)

        if len(groups) == 1:
            winning = next(iter(groups.values()))
            answer = winning[0].answer

            confidence = (
                "HIGH" if len(winning) >= 2 else winning[0].confidence
            )

            return QuestionReasoning(
                question_id=question_id,
                answer=answer,
                status="VERIFIED",
                method="MULTI_SOURCE_AGREEMENT"
                if len(winning) >= 2
                else winning[0].method,
                confidence=confidence,
                supporting_evidence=[
                    self._serialize(e) for e in winning
                ],
                unresolved_evidence=[
                    self._serialize(e) for e in unresolved
                ],
                reasoning=self._agreement_reasoning(
                    answer, len(winning)
                ),
                freshness=[
                    e.freshness
                    for e in winning
                    if e.freshness is not None
                ],
            )

        # Multiple verified answers disagree.
        all_verified = [
            self._serialize(e) for e in verified
        ]

        return QuestionReasoning(
            question_id=question_id,
            answer="UNKNOWN",
            status="INSUFFICIENT_EVIDENCE",
            method="VERIFIED_SOURCE_CONFLICT",
            confidence="NONE",
            supporting_evidence=all_verified,
            conflicting_evidence=all_verified,
            unresolved_evidence=[
                self._serialize(e) for e in unresolved
            ],
            reasoning=(
                "Verified sources provide conflicting answers. "
                "The engine does not arbitrarily choose a source; "
                "the conflict remains unresolved."
            ),
            freshness=[
                e.freshness
                for e in verified
                if e.freshness is not None
            ],
        )

    def reason_all(
        self,
        evidence_by_question: Dict[str, List[Evidence]],
    ) -> Dict[str, QuestionReasoning]:

        return {
            question_id: self.reason(question_id, items)
            for question_id, items in evidence_by_question.items()
        }

    def synthesize(
        self,
        results: Dict[str, QuestionReasoning],
    ) -> Dict[str, Any]:

        verified = [
            r for r in results.values()
            if r.status == "VERIFIED"
        ]

        unresolved = [
            r for r in results.values()
            if r.status != "VERIFIED"
        ]

        conflicts = [
            r for r in results.values()
            if r.method == "VERIFIED_SOURCE_CONFLICT"
        ]

        return {
            "resolved_questions": len(verified),
            "unresolved_questions": len(unresolved),
            "conflicting_questions": len(conflicts),
            "evidence_quality": (
                "STRONG"
                if len(verified) > len(unresolved)
                else "LIMITED"
            ),
            "readiness": (
                "READY"
                if verified and not conflicts
                else "INSUFFICIENT"
            ),
            "prediction_eligible": bool(
                verified and not conflicts
            ),
        }

    @staticmethod
    def _normalise_answer(answer: Any) -> str:
        return str(answer).strip().casefold()

    @staticmethod
    def _serialize(evidence: Evidence) -> Dict[str, Any]:
        return {
            "source_id": evidence.source_id,
            "question_id": evidence.question_id,
            "answer": evidence.answer,
            "status": evidence.status,
            "method": evidence.method,
            "confidence": evidence.confidence,
            "evidence": evidence.evidence,
            "freshness": evidence.freshness,
            "source_url": evidence.source_url,
        }

    @staticmethod
    def _agreement_reasoning(
        answer: Any,
        source_count: int,
    ) -> str:
        if source_count >= 2:
            return (
                f"Verified evidence from {source_count} sources "
                f"agrees on the answer: {answer}."
            )

        return (
            f"One verified evidence source currently supports "
            f"the answer: {answer}."
        )


def build_v13_reasoning_report(
    evidence_by_question: Dict[str, List[Evidence]],
) -> Dict[str, Any]:

    engine = V13EvidenceReasoningEngine()

    questions = engine.reason_all(evidence_by_question)
    synthesis = engine.synthesize(questions)

    return {
        "engine": "V1.3_EVIDENCE_REASONING",
        "questions": {
            question_id: {
                "answer": result.answer,
                "status": result.status,
                "method": result.method,
                "confidence": result.confidence,
                "supporting_evidence": result.supporting_evidence,
                "conflicting_evidence": result.conflicting_evidence,
                "unresolved_evidence": result.unresolved_evidence,
                "reasoning": result.reasoning,
                "freshness": result.freshness,
            }
            for question_id, result in questions.items()
        },
        "synthesis": synthesis,
    }


__all__ = [
    "Evidence",
    "QuestionReasoning",
    "V13EvidenceReasoningEngine",
    "build_v13_reasoning_report",
]
