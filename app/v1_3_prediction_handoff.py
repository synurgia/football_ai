from __future__ import annotations

from typing import Any, Dict

from app.v1_3_daily_reasoning_hook import V13DailyReasoningHook


class V13PredictionHandoff:
    """
    Connects V1.3 reasoning output to the existing prediction stage.

    The existing prediction service is not replaced. The reasoning
    report is attached as additional verified intelligence input.
    """

    def __init__(self) -> None:
        self.reasoning = V13DailyReasoningHook()

    def prepare(
        self,
        match: Dict[str, Any],
        evidence_state: Any,
        prediction_input: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        report = self.reasoning.process_match(
            match,
            evidence_state,
        )

        base = dict(prediction_input or {})

        base["v1_3_reasoning"] = report["reasoning"]

        base["evidence_intelligence"] = {
            "questions": report["reasoning"].get("questions", {}),
            "synthesis": report["reasoning"].get("synthesis", {}),
        }

        base["prediction_input_ready"] = report[
            "reasoning"
        ]["prediction_input_ready"]

        return base


def prepare_prediction_input(
    match: Dict[str, Any],
    evidence_state: Any,
    prediction_input: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    return V13PredictionHandoff().prepare(
        match,
        evidence_state,
        prediction_input,
    )


__all__ = [
    "V13PredictionHandoff",
    "prepare_prediction_input",
]
