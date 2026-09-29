from __future__ import annotations

from typing import Any, Dict, List

from app.v2_question_registry import get_all_questions


class V12CapabilityQuestionMapper:
    """
    Maps an explicitly identified V1.2 capability to the canonical
    37-question registry using enriched evidence requirements.

    This is routing only. It does not create answers or verification.
    """

    CAPABILITY_REQUIREMENT_ALIASES = {
        "competition_rules": {"competition_rules"},
        "financial_context": {"financial_context"},
        "team_changes": {
            "squad_changes",
            "manager_changes",
            "tactical_changes",
        },
        "motivation": {
            "standings",
            "fixtures",
            "competition_rules",
        },
        "results": {
            "historical_results",
            "team_statistics",
            "xg",
        },
        "geopolitical_context": {
            "geopolitical_context",
            "news",
        },
        "public_context": {
            "public_signal",
            "reputation_context",
        },
        "team_identity": {"team_identity"},
        "competition_context": {
            "standings",
            "competition_stage",
            "competition_rules",
        },
        "team_strength": {
            "rankings",
            "ratings",
            "team_strength",
            "xg",
        },
        "model_analysis": {
            "model_output",
            "model_inputs",
        },
        "team_matrix": {
            "team_statistics",
            "performance_metrics",
        },
        "statistical_models": {
            "historical_results",
            "team_statistics",
            "model_inputs",
            "statistical_models",
        },
        "tactical_analysis": {
            "tactical_data",
            "formations",
            "team_statistics",
        },
        "standings": {
            "standings",
            "rankings",
            "team_statistics",
        },
        "market_context": {"market_context"},
        "schedule": {
            "fixtures",
            "travel",
            "rest",
            "rotation",
            "competition_stage",
        },
        "weather_venue": {
            "weather",
            "venue_condition",
            "pitch_condition",
        },
        "defensive_resistance": {
            "defensive_statistics",
            "tactical_data",
        },
        "tactical_metrics": {
            "formations",
            "tactical_metrics",
            "lineups",
        },
        "transition_analysis": {
            "transition_metrics",
            "pace",
            "finishing",
            "tactical_data",
        },
        "favorite_risk": {
            "finishing",
            "goalkeeping",
            "historical_matchups",
            "team_strength",
        },
        "opponent_resistance": {
            "historical_results",
            "opponent_strength",
        },
        "bayesian_adjustment": {
            "model_inputs",
            "statistical_models",
            "bayesian_adjustments",
        },
        "match_status": {
            "referee_appointment",
            "referee_statistics",
            "expected_lineup",
            "confirmed_lineup",
            "formations",
        },
        "pitch_conditions": {
            "venue",
            "pitch_dimensions",
            "surface",
            "grass",
            "watering",
        },
    }

    def __init__(self) -> None:
        self.questions = get_all_questions()

    def questions_for_capability(
        self,
        capability: str,
    ) -> List[Dict[str, Any]]:
        capability = str(capability).strip()

        requirements = self.CAPABILITY_REQUIREMENT_ALIASES.get(
            capability,
            {capability},
        )

        return [
            question
            for question in self.questions
            if requirements.intersection(
                set(question.get("evidence_requirements", []) or [])
            )
        ]

    def question_ids_for_capability(
        self,
        capability: str,
    ) -> List[str]:
        return [
            str(question["id"])
            for question in self.questions_for_capability(capability)
        ]

    def map_evidence(
        self,
        capability_evidence: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        capability = str(
            capability_evidence.get("capability", "")
        ).strip()

        if not capability:
            raise ValueError(
                "Capability evidence requires an explicit capability."
            )

        questions = self.questions_for_capability(capability)

        return [
            {
                "question_id": str(question["id"]),
                "capability": capability,
                "source_url": capability_evidence.get("source_url"),
                "final_url": capability_evidence.get("final_url"),
                "content_type": capability_evidence.get("content_type"),
                "status": "SOURCE_CONTENT_AVAILABLE",
            }
            for question in questions
        ]


def _test() -> None:
    mapper = V12CapabilityQuestionMapper()

    expected = {
        "competition_rules": ["Q1", "Q2", "Q5", "Q9", "Q11"],
        "weather_venue": ["Q26"],
        "pitch_conditions": ["Q39"],
        "tactical_metrics": ["Q32", "Q41"],
        "bayesian_adjustment": ["Q37"],
    }

    print("=" * 70)
    print("V1.2 CAPABILITY → QUESTION MAPPER")
    print("=" * 70)

    for capability, expected_ids in expected.items():
        actual = mapper.question_ids_for_capability(capability)

        print(f"{capability}: {actual}")

        if actual != expected_ids:
            raise RuntimeError(
                f"Unexpected mapping for {capability}: "
                f"{actual} != {expected_ids}"
            )

    if len(get_all_questions()) != 37:
        raise RuntimeError("Canonical V1.2 question count changed.")

    print("QUESTIONS:", len(get_all_questions()))
    print("MAPPER: VALID")


if __name__ == "__main__":
    _test()
