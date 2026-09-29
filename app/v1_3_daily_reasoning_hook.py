from __future__ import annotations

from typing import Any, Dict

from app.v1_3_reasoning_bridge import V13ReasoningBridge


class V13DailyReasoningHook:
    """
    Final evidence-reasoning stage for the V1.3 daily lifecycle.

    Existing collection, questions, readiness and prediction systems
    remain intact. This hook adds the missing reasoning pass.
    """

    def __init__(self) -> None:
        self.bridge = V13ReasoningBridge()

    def process(
        self,
        evidence_state: Any,
    ) -> Dict[str, Any]:
        report = self.bridge.reason_match(evidence_state)

        report["stage"] = "V1.3_REASONING"
        report["prediction_input_ready"] = (
            report["synthesis"]["prediction_eligible"]
        )

        return report

    def process_match(
        self,
        match: Dict[str, Any],
        evidence_state: Any,
    ) -> Dict[str, Any]:

        report = self.process(evidence_state)

        return {
            "match_id": (
                match.get("match_id")
                or match.get("id")
                or "UNKNOWN"
            ),
            "competition_id": (
                match.get("competition_id")
                or "UNKNOWN"
            ),
            "home_team": match.get("home_team"),
            "away_team": match.get("away_team"),
            "reasoning": report,
        }


def reason_daily_match(
    match: Dict[str, Any],
    evidence_state: Any,
) -> Dict[str, Any]:

    return V13DailyReasoningHook().process_match(
        match,
        evidence_state,
    )


__all__ = [
    "V13DailyReasoningHook",
    "reason_daily_match",
]
