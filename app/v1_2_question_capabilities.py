from typing import Dict

# Canonical V1.2 question -> evidence capability mapping.
# This mapping routes source evidence only.
# It does NOT answer questions and does NOT modify Pieces 1-9.

QUESTION_CAPABILITIES: Dict[str, str] = {
    "Q1": "competition_rules",
    "Q2": "competition_rules",
    "Q3": "financial_context",
    "Q4": "team_changes",
    "Q5": "motivation",
    "Q6": "results",
    "Q7": "geopolitical_context",
    "Q8": "public_context",
    "Q9": "motivation",
    "Q10": "team_identity",
    "Q11": "competition_context",
    "Q12": "team_strength",
    "Q13": "model_analysis",
    "Q14": "team_matrix",
    "Q15": "results",
    "Q16": "statistical_models",
    "Q17": "model_analysis",
    "Q18": "tactical_analysis",
    "Q19": "standings",
    "Q24": "market_context",
    "Q25": "schedule",
    "Q26": "weather_venue",
    "Q27": "team_strength",
    "Q28": "motivation",
    "Q29": "defensive_resistance",
    "Q30": "results",
    "Q31": "defensive_resistance",
    "Q32": "tactical_metrics",
    "Q33": "transition_analysis",
    "Q34": "schedule",
    "Q35": "favorite_risk",
    "Q36": "opponent_resistance",
    "Q37": "bayesian_adjustment",
    "Q38": "match_status",
    "Q39": "pitch_conditions",
    "Q40": "team_identity",
    "Q41": "match_status",
}


def get_question_capabilities() -> Dict[str, str]:
    """Return a copy of the canonical V1.2 capability mapping."""
    return dict(QUESTION_CAPABILITIES)


def question_count() -> int:
    return len(QUESTION_CAPABILITIES)


def question_ids():
    return list(QUESTION_CAPABILITIES.keys())


if __name__ == "__main__":
    print("=== V1.2 QUESTION CAPABILITY MAP ===")
    print("QUESTION COUNT:", question_count())
    print("UNIQUE QUESTIONS:", len(set(question_ids())))
    print("RESULT:", "PASS" if question_count() == 37 else "FAIL")
