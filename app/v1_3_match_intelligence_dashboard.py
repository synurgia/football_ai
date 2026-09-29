from __future__ import annotations

from typing import Any, Dict, List


class V13MatchIntelligenceDashboard:
    """
    Dashboard adapter for the V1.3 Match Intelligence Search.

    This does not replace the existing dashboard.
    It converts the V1.3 reasoning result into dashboard-ready data.
    """

    def build(
        self,
        match: Dict[str, Any],
        reasoning_report: Dict[str, Any],
    ) -> Dict[str, Any]:

        reasoning = reasoning_report.get(
            "reasoning",
            reasoning_report,
        )

        questions = reasoning.get("questions", {})
        synthesis = reasoning.get("synthesis", {})

        question_rows: List[Dict[str, Any]] = []

        for question_id, result in questions.items():
            question_rows.append(
                {
                    "question_id": question_id,
                    "answer": result.get("answer", "UNKNOWN"),
                    "status": result.get(
                        "status",
                        "INSUFFICIENT_EVIDENCE",
                    ),
                    "method": result.get(
                        "method",
                        "NO_VERIFIED_EVIDENCE",
                    ),
                    "confidence": result.get(
                        "confidence",
                        "NONE",
                    ),
                    "reasoning": result.get(
                        "reasoning",
                        "",
                    ),
                    "supporting_evidence": result.get(
                        "supporting_evidence",
                        [],
                    ),
                    "conflicting_evidence": result.get(
                        "conflicting_evidence",
                        [],
                    ),
                    "unresolved_evidence": result.get(
                        "unresolved_evidence",
                        [],
                    ),
                    "freshness": result.get(
                        "freshness",
                        [],
                    ),
                }
            )

        return {
            "match_intelligence": {
                "match_id": (
                    match.get("match_id")
                    or match.get("id")
                    or "UNKNOWN"
                ),
                "competition_id": match.get(
                    "competition_id",
                    "UNKNOWN",
                ),
                "home_team": match.get("home_team"),
                "away_team": match.get("away_team"),
            },
            "v1_3_reasoning": {
                "questions": question_rows,
                "synthesis": {
                    "resolved_questions": synthesis.get(
                        "resolved_questions",
                        0,
                    ),
                    "unresolved_questions": synthesis.get(
                        "unresolved_questions",
                        0,
                    ),
                    "conflicting_questions": synthesis.get(
                        "conflicting_questions",
                        0,
                    ),
                    "evidence_quality": synthesis.get(
                        "evidence_quality",
                        "LIMITED",
                    ),
                    "readiness": synthesis.get(
                        "readiness",
                        "INSUFFICIENT",
                    ),
                    "prediction_eligible": synthesis.get(
                        "prediction_eligible",
                        False,
                    ),
                },
            },
        }


def build_match_intelligence_dashboard(
    match: Dict[str, Any],
    reasoning_report: Dict[str, Any],
) -> Dict[str, Any]:

    return V13MatchIntelligenceDashboard().build(
        match,
        reasoning_report,
    )


__all__ = [
    "V13MatchIntelligenceDashboard",
    "build_match_intelligence_dashboard",
]
