from app.v2_question_registry import get_all_questions

ENRICHMENT = {
    "Q1": ["competition_rules"],
    "Q2": ["competition_rules"],
    "Q3": ["financial_context", "news"],
    "Q4": ["squad_changes", "manager_changes", "tactical_changes"],
    "Q5": ["standings", "fixtures", "competition_rules"],
    "Q6": ["team_statistics", "xg", "model_output"],
    "Q7": ["geopolitical_context", "news"],
    "Q8": ["public_signal", "reputation_context"],
    "Q9": ["standings", "fixtures", "competition_rules"],
    "Q10": ["team_identity"],
    "Q11": ["standings", "competition_rules"],
    "Q12": ["rankings", "ratings", "team_strength"],
    "Q13": ["model_output"],
    "Q14": ["team_statistics", "performance_metrics"],
    "Q15": ["historical_results", "team_statistics", "xg"],
    "Q16": ["historical_results", "team_statistics", "model_inputs"],
    "Q17": ["Q11", "Q14", "Q15", "Q16"],
    "Q18": ["tactical_data", "formations", "team_statistics"],
    "Q19": ["standings", "rankings", "team_statistics"],
    "Q24": ["market_context"],
    "Q25": ["fixtures", "travel", "rest", "rotation"],
    "Q26": ["weather", "venue_condition", "pitch_condition"],
    "Q27": ["rankings", "ratings", "xg", "team_strength"],
    "Q28": ["standings", "competition_stage", "fixtures", "news"],
    "Q29": ["defensive_statistics", "tactical_data"],
    "Q30": ["historical_results", "opponent_strength", "xg", "team_statistics"],
    "Q31": ["defensive_statistics", "tactical_data"],
    "Q32": ["formations", "tactical_metrics", "lineups"],
    "Q33": ["transition_metrics", "pace", "finishing", "tactical_data"],
    "Q34": ["fixtures", "travel", "rest", "pitch_condition", "competition_stage", "rotation"],
    "Q35": ["finishing", "goalkeeping", "historical_matchups", "team_strength"],
    "Q36": ["historical_results", "opponent_strength"],
    "Q37": ["model_inputs", "statistical_models", "bayesian_adjustments"],
    "Q38": ["referee_appointment", "referee_statistics"],
    "Q39": ["venue", "pitch_dimensions", "surface", "grass", "watering"],
    "Q40": ["injuries", "suspensions", "squad_news"],
    "Q41": ["expected_lineup", "confirmed_lineup", "formations"],
}

questions = get_all_questions()

print("=== QUESTION ENRICHMENT AUDIT ===")
print("REGISTRY QUESTIONS:", len(questions))
print("ENRICHMENT ENTRIES:", len(ENRICHMENT))
print()

registry_ids = {
    str(q.get("id") or q.get("question_id") or "").upper()
    for q in questions
}

missing = sorted(registry_ids - set(ENRICHMENT))
extra = sorted(set(ENRICHMENT) - registry_ids)

print("MISSING ENRICHMENT:", missing)
print("EXTRA ENRICHMENT:", extra)

if missing or extra:
    raise SystemExit(1)

print()
for qid in sorted(ENRICHMENT, key=lambda x: int(x[1:])):
    print(f"{qid} -> {', '.join(ENRICHMENT[qid])}")

print()
print("ENRICHMENT STRUCTURE: VALID")
