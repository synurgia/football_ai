from __future__ import annotations

from typing import Any, Dict, List

from app.v1_3_evidence_reasoning_engine import (
    Evidence,
    V13EvidenceReasoningEngine,
)


class V13ReasoningBridge:
    """
    Connects the existing V1.2/V1.3 evidence state to the
    V1.3 evidence reasoning engine.

    This is an adapter only:
    - existing evidence remains authoritative
    - existing questions remain authoritative
    - no new questions are created
    - no evidence is invented
    """

    def __init__(self) -> None:
        self.engine = V13EvidenceReasoningEngine()

    def _convert_item(
        self,
        question_id: str,
        item: Any,
    ) -> Evidence:

        if isinstance(item, dict):
            return Evidence(
                source_id=str(
                    item.get("source_id")
                    or item.get("source")
                    or "UNKNOWN_SOURCE"
                ),
                question_id=question_id,
                answer=item.get("answer"),
                status=str(
                    item.get("status")
                    or item.get("verification_status")
                    or "UNVERIFIED"
                ).upper(),
                method=str(
                    item.get("method")
                    or item.get("resolution_method")
                    or "SOURCE_EVIDENCE"
                ),
                confidence=str(
                    item.get("confidence")
                    or "MEDIUM"
                ).upper(),
                evidence=str(
                    item.get("evidence")
                    or item.get("evidence_text")
                    or item.get("reasoning")
                    or ""
                ),
                freshness=item.get("freshness"),
                source_url=(
                    item.get("source_url")
                    or item.get("url")
                ),
            )

        return Evidence(
            source_id="UNKNOWN_SOURCE",
            question_id=question_id,
            answer=None,
            status="UNVERIFIED",
            method="UNSUPPORTED_EVIDENCE_OBJECT",
            confidence="NONE",
            evidence=str(item),
        )

    def normalize_evidence(
        self,
        evidence_state: Any,
    ) -> Dict[str, List[Evidence]]:

        result: Dict[str, List[Evidence]] = {}

        if isinstance(evidence_state, dict):
            raw_questions = (
                evidence_state.get("questions")
                or evidence_state.get("evidence")
                or evidence_state
            )
        else:
            raw_questions = getattr(
                evidence_state,
                "questions",
                None,
            )

        if not isinstance(raw_questions, dict):
            return result

        for question_id, raw_items in raw_questions.items():

            if isinstance(raw_items, list):
                items = raw_items
            else:
                items = [raw_items]

            converted = [
                self._convert_item(question_id, item)
                for item in items
            ]

            result[str(question_id)] = converted

        return result

    def reason_match(
        self,
        evidence_state: Any,
    ) -> Dict[str, Any]:

        evidence_by_question = self.normalize_evidence(
            evidence_state
        )

        results = self.engine.reason_all(
            evidence_by_question
        )

        synthesis = self.engine.synthesize(results)

        return {
            "engine": "V1.3_REASONING_BRIDGE",
            "questions": {
                question_id: {
                    "answer": result.answer,
                    "status": result.status,
                    "method": result.method,
                    "confidence": result.confidence,
                    "supporting_evidence":
                        result.supporting_evidence,
                    "conflicting_evidence":
                        result.conflicting_evidence,
                    "unresolved_evidence":
                        result.unresolved_evidence,
                    "reasoning": result.reasoning,
                    "freshness": result.freshness,
                }
                for question_id, result in results.items()
            },
            "synthesis": synthesis,
        }


__all__ = ["V13ReasoningBridge"]
