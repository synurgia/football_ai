from typing import Any, Dict, List


class V12QuestionReasoningEngine:
    """
    V1.2 evidence-first question reasoning layer.

    This component reasons ONLY from evidence already present in the
    V2EvidenceState. It never invents facts and never replaces the
    existing prediction pipeline.
    """

    VERIFIED = "VERIFIED"
    INSUFFICIENT = "INSUFFICIENT_EVIDENCE"
    UNVERIFIED = "UNVERIFIED"
    FAILED = "FAILED"

    def evaluate_question(self, item: Any) -> Dict[str, Any]:
        evidence = str(getattr(item, "evidence", "") or "").strip()
        requirements = list(
            getattr(item, "minimum_evidence", []) or []
        )

        if not evidence or evidence == "No verified evidence collected yet.":
            return {
                "question_id": item.question_id,
                "answer": "UNKNOWN",
                "confidence": None,
                "status": self.UNVERIFIED,
                "reasoning": "No usable evidence is currently attached to the question.",
                "missing_evidence": requirements,
            }

        status = getattr(item, "status", self.UNVERIFIED)

        if status == self.VERIFIED:
            return {
                "question_id": item.question_id,
                "answer": item.answer,
                "confidence": item.confidence,
                "status": self.VERIFIED,
                "reasoning": (
                    "The question already has verified evidence in the "
                    "canonical V1.2 evidence state."
                ),
                "missing_evidence": [],
            }

        return {
            "question_id": item.question_id,
            "answer": item.answer,
            "confidence": item.confidence,
            "status": status,
            "reasoning": (
                "Evidence exists, but the current evidence state does not "
                "establish a verified answer."
            ),
            "missing_evidence": requirements,
        }

    def evaluate_state(self, state: Any) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = []

        for item in state.items:
            results.append(self.evaluate_question(item))

        return {
            "match_id": getattr(state, "match_id", None),
            "question_count": len(results),
            "questions": results,
        }
