from typing import Dict, Set

from app.v1_2_question_capabilities import get_question_capabilities


EXTERNAL_FACT_CAPABILITIES: Set[str] = {
    "competition_context",
    "competition_rules",
    "financial_context",
    "geopolitical_context",
    "market_context",
    "match_status",
    "motivation",
    "pitch_conditions",
    "public_context",
    "results",
    "schedule",
    "standings",
    "team_changes",
    "team_identity",
    "weather_venue",
}

INTERNAL_ANALYTICAL_CAPABILITIES: Set[str] = {
    "bayesian_adjustment",
    "defensive_resistance",
    "favorite_risk",
    "model_analysis",
    "opponent_resistance",
    "statistical_models",
    "tactical_analysis",
    "tactical_metrics",
    "team_matrix",
    "team_strength",
    "transition_analysis",
}


def get_capability_classification() -> Dict[str, str]:
    canonical = set(get_question_capabilities().values())

    unknown = canonical - (
        EXTERNAL_FACT_CAPABILITIES
        | INTERNAL_ANALYTICAL_CAPABILITIES
    )

    if unknown:
        raise RuntimeError(
            f"Unclassified canonical capabilities: {sorted(unknown)}"
        )

    return {
        capability: (
            "EXTERNAL_FACT"
            if capability in EXTERNAL_FACT_CAPABILITIES
            else "INTERNAL_ANALYTICAL"
        )
        for capability in sorted(canonical)
    }


def validate_capability_classification() -> None:
    classification = get_capability_classification()

    if len(classification) != len(
        set(get_question_capabilities().values())
    ):
        raise RuntimeError(
            "Capability classification does not cover every "
            "canonical capability exactly once."
        )


if __name__ == "__main__":
    validate_capability_classification()

    classification = get_capability_classification()

    print("=== V1.2 CAPABILITY CLASSIFICATION ===")

    for capability, category in classification.items():
        print(f"{capability}: {category}")

    print()
    print("CANONICAL CAPABILITIES:", len(classification))
    print(
        "EXTERNAL FACT:",
        sum(
            1
            for category in classification.values()
            if category == "EXTERNAL_FACT"
        ),
    )
    print(
        "INTERNAL ANALYTICAL:",
        sum(
            1
            for category in classification.values()
            if category == "INTERNAL_ANALYTICAL"
        ),
    )
    print("RESULT: PASS")
