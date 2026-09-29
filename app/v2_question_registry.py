from typing import Dict, List, Any

V2_QUESTION_REGISTRY: Dict[int, List[Dict[str, str]]] = {
    1: [
        {"id": "Q1", "question": "Does the competition go to penalties after a draw?"},
        {"id": "Q2", "question": "Does a special competition penalty-point or draw rule apply?"},
        {"id": "Q3", "question": "Is there significant financial backing or funding affecting either team?"},
        {"id": "Q4", "question": "Are there major squad, managerial, or tactical changes, and what is their impact?"},
        {"id": "Q5", "question": "Is either team under a genuine must-win or high-urgency situation?"},
        {"id": "Q6", "question": "Which team has the stronger goal-scoring probability based on verified football evidence?"},
    ],
    2: [
        {"id": "Q7", "question": "Is there a verified geopolitical, conflict, or war-related impact on the match?"},
        {"id": "Q8", "question": "Is public reputation, fame, hype, or expectation creating a potential analytical distortion?"},
        {"id": "Q9", "question": "Is either team under a genuine must-win or high-urgency situation?"},
        {"id": "Q10", "question": "Are both teams verified men's first teams?"},
        {"id": "Q11", "question": "Is there a genuine win-to-secure-or-protect-top-position situation?"},
        {"id": "Q12", "question": "Is this a top-tier versus underdog matchup based on verified team-strength evidence?"},
        {"id": "Q13", "question": "What are the model-based probabilities and most likely football outcome?"},
    ],
    3: [
        {"id": "Q14", "question": "What does the multidimensional team matrix show for momentum, attacking threat, defensive stability, volatility, and composite strength?"},
        {"id": "Q15", "question": "What does the recent-match record show, including form, points per game, goals, goal difference, clean sheets, failed-to-score rate, recency, and trend?"},
        {"id": "Q16", "question": "What do the available statistical models show, including Poisson, hybrid/agent-style analysis, and cross-validation?"},
        {"id": "Q17", "question": "What is the highest-probability football outcome, dominance gap, and genuine must-win classification?"},
    ],
    4: [
        {"id": "Q18", "question": "What are the tactical strengths, weaknesses, and exploitable matchup factors for each team?"},
        {"id": "Q19", "question": "What do league/table/ranking position, points, record, goal difference, zones, and position gap indicate?"},
    ],
    5: [
        {"id": "Q24", "question": "What relevant external outcome-price or market information exists, if any, and does it provide legitimate football-context evidence?"},
        {"id": "Q25", "question": "Does the schedule create fatigue, congestion, rotation risk, lookahead risk, or pressure from an upcoming major fixture?"},
        {"id": "Q26", "question": "What is the verified weather and venue condition, and could it cause tactical disruption, delay, or postponement?"},
        {"id": "Q27", "question": "What is the verified team-strength gap using available table, rating, xG, and squad-value indicators?"},
        {"id": "Q28", "question": "What is each team's verified motivation, and is there a meaningful motivation asymmetry?"},
        {"id": "Q29", "question": "What defensive and tactical resistance does each team provide?"},
        {"id": "Q30", "question": "What does the verified recent form, opponent strength, xG trend, actual points, and sustainability analysis show?"},
    ],
    6: [
        {"id": "Q31", "question": "What does the defensive resistance analysis show, including low-block, compactness, set-piece, and transition resistance?"},
        {"id": "Q32", "question": "What does the tactical metrics analysis show for formation, defensive line, spacing, compactness, directness, and attacking structure?"},
        {"id": "Q33", "question": "What transition matchup advantages or disadvantages exist, including pace, finishing, and counter-attacking potential?"},
        {"id": "Q34", "question": "What schedule, travel, rest, pitch, competition-stage, and rotation factors alter the tactical matchup?"},
    ],
    7: [
        {"id": "Q35", "question": "Is there evidence of fraudulent-favorite risk, inefficient finishing, an unusually strong goalkeeper, or a recurring matchup problem?"},
        {"id": "Q36", "question": "Does recent evidence against stronger opponents indicate unusual resistance or upset potential?"},
        {"id": "Q37", "question": "How should Bayesian and statistical matchup adjustments change the football outcome analysis?"},
    ],
    8: [
        {"id": "Q38", "question": "What referee tendencies could materially affect the match, including fouls, cards, tackles, penalties, and box decisions?"},
        {"id": "Q39", "question": "What pitch dimensions, grass, watering, and surface conditions could affect play?"},
        {"id": "Q40", "question": "Are there key-player absences or single-point-of-failure risks?"},
        {"id": "Q41", "question": "What does the expected or confirmed starting XI show about formations, unit matchups, and tactical exploits?"},
    ],
}

QUESTION_ENRICHMENT: Dict[str, Dict[str, Any]] = {
    "Q1": {"evidence_requirements":["competition_rules"],"source_domains":["official_competition","competition_rules"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["competition_format_or_rules"],"staleness_policy":"SEASONAL"},
    "Q2": {"evidence_requirements":["competition_rules"],"source_domains":["official_competition","competition_rules"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["competition_format_or_rules"],"staleness_policy":"SEASONAL"},
    "Q3": {"evidence_requirements":["financial_context","news"],"source_domains":["official_club","official_competition","news"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["credible_financial_or_funding_evidence"],"staleness_policy":"RECENT"},
    "Q4": {"evidence_requirements":["squad_changes","manager_changes","tactical_changes"],"source_domains":["official_club","official_competition","news"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["verified_change_and_relevant_impact"],"staleness_policy":"RECENT"},
    "Q5": {"evidence_requirements":["standings","fixtures","competition_rules"],"source_domains":["official_competition","official_club"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["current_standings","relevant_fixture_context"],"staleness_policy":"TIME_SENSITIVE"},
    "Q6": {"evidence_requirements":["team_statistics","xg","model_output"],"source_domains":["statistics","model"],"answer_mode":"MODEL_DERIVED","minimum_evidence":["validated_team_attacking_inputs"],"staleness_policy":"RECENT"},
    "Q7": {"evidence_requirements":["geopolitical_context","news"],"source_domains":["news","official_sources"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["credible_verified_context"],"staleness_policy":"TIME_SENSITIVE"},
    "Q8": {"evidence_requirements":["public_signal","reputation_context"],"source_domains":["news","public_sources"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["documented_public_signal"],"staleness_policy":"RECENT"},
    "Q9": {"evidence_requirements":["standings","fixtures","competition_rules"],"source_domains":["official_competition","official_club"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["current_standings","fixture_context"],"staleness_policy":"TIME_SENSITIVE"},
    "Q10": {"evidence_requirements":["team_identity"],"source_domains":["official_club","official_competition"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["verified_team_identity"],"staleness_policy":"SEASONAL"},
    "Q11": {"evidence_requirements":["standings","competition_rules"],"source_domains":["official_competition"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["current_standings","competition_rules"],"staleness_policy":"TIME_SENSITIVE"},
    "Q12": {"evidence_requirements":["rankings","ratings","team_strength"],"source_domains":["statistics","official_competition","ratings"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["verified_strength_indicators"],"staleness_policy":"RECENT"},
    "Q13": {"evidence_requirements":["model_output"],"source_domains":["model"],"answer_mode":"MODEL_DERIVED","minimum_evidence":["validated_model_inputs"],"staleness_policy":"MATCH_SPECIFIC"},
    "Q14": {"evidence_requirements":["team_statistics","performance_metrics"],"source_domains":["statistics"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["recent_team_performance_data"],"staleness_policy":"RECENT"},
    "Q15": {"evidence_requirements":["historical_results","team_statistics","xg"],"source_domains":["results","statistics"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["recent_verified_results"],"staleness_policy":"RECENT"},
    "Q16": {"evidence_requirements":["historical_results","team_statistics","model_inputs"],"source_domains":["results","statistics","model"],"answer_mode":"MODEL_DERIVED","minimum_evidence":["validated_statistical_inputs"],"staleness_policy":"RECENT"},
    "Q17": {"evidence_requirements":["Q11","Q14","Q15","Q16"],"source_domains":["evidence_state","model"],"answer_mode":"DERIVED_FROM_QUESTIONS","minimum_evidence":["required_question_dependencies"],"staleness_policy":"MATCH_SPECIFIC"},
    "Q18": {"evidence_requirements":["tactical_data","formations","team_statistics"],"source_domains":["statistics","lineups","tactical_sources"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["verified_tactical_indicators"],"staleness_policy":"RECENT"},
    "Q19": {"evidence_requirements":["standings","rankings","team_statistics"],"source_domains":["official_competition","statistics"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["current_competition_position"],"staleness_policy":"TIME_SENSITIVE"},
    "Q24": {"evidence_requirements":["market_context"],"source_domains":["market_sources"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["legitimate_market_context_if_available"],"staleness_policy":"TIME_SENSITIVE"},
    "Q25": {"evidence_requirements":["fixtures","travel","rest","rotation"],"source_domains":["official_competition","official_club","fixtures"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["fixture_and_rest_context"],"staleness_policy":"TIME_SENSITIVE"},
    "Q26": {"evidence_requirements":["weather","venue_condition","pitch_condition"],"source_domains":["weather","venue","official_competition","official_club"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["match_venue","match_datetime","weather_or_venue_evidence"],"staleness_policy":"TIME_SENSITIVE"},
    "Q27": {"evidence_requirements":["rankings","ratings","xg","team_strength"],"source_domains":["statistics","ratings","official_competition"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["verified_strength_indicators"],"staleness_policy":"RECENT"},
    "Q28": {"evidence_requirements":["standings","competition_stage","fixtures","news"],"source_domains":["official_competition","official_club","news"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["competition_context_and_fixture_context"],"staleness_policy":"TIME_SENSITIVE"},
    "Q29": {"evidence_requirements":["defensive_statistics","tactical_data"],"source_domains":["statistics","tactical_sources"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["verified_defensive_indicators"],"staleness_policy":"RECENT"},
    "Q30": {"evidence_requirements":["historical_results","opponent_strength","xg","team_statistics"],"source_domains":["results","statistics","ratings"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["recent_results_and_opponent_context"],"staleness_policy":"RECENT"},
    "Q31": {"evidence_requirements":["defensive_statistics","tactical_data"],"source_domains":["statistics","tactical_sources"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["verified_defensive_and_tactical_data"],"staleness_policy":"RECENT"},
    "Q32": {"evidence_requirements":["formations","tactical_metrics","lineups"],"source_domains":["lineups","tactical_sources","statistics"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["formation_or_tactical_evidence"],"staleness_policy":"MATCH_SPECIFIC"},
    "Q33": {"evidence_requirements":["transition_metrics","pace","finishing","tactical_data"],"source_domains":["statistics","tactical_sources"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["verified_transition_indicators"],"staleness_policy":"RECENT"},
    "Q34": {"evidence_requirements":["fixtures","travel","rest","pitch_condition","competition_stage","rotation"],"source_domains":["official_competition","official_club","venue","fixtures"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["fixture_schedule_and_match_context"],"staleness_policy":"TIME_SENSITIVE"},
    "Q35": {"evidence_requirements":["finishing","goalkeeping","historical_matchups","team_strength"],"source_domains":["statistics","results","ratings"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["verified_performance_indicators"],"staleness_policy":"RECENT"},
    "Q36": {"evidence_requirements":["historical_results","opponent_strength"],"source_domains":["results","ratings","statistics"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["recent_results_against_stronger_opponents"],"staleness_policy":"RECENT"},
    "Q37": {"evidence_requirements":["model_inputs","statistical_models","bayesian_adjustments"],"source_domains":["model"],"answer_mode":"MODEL_DERIVED","minimum_evidence":["validated_model_inputs"],"staleness_policy":"MATCH_SPECIFIC"},
    "Q38": {"evidence_requirements":["referee_appointment","referee_statistics"],"source_domains":["official_competition","referee_sources","statistics"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["verified_referee_appointment"],"staleness_policy":"MATCH_SPECIFIC"},
    "Q39": {"evidence_requirements":["venue","pitch_dimensions","surface","grass","watering"],"source_domains":["venue","official_competition","official_club"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["verified_venue_information"],"staleness_policy":"SEASONAL"},
    "Q40": {"evidence_requirements":["injuries","suspensions","squad_news"],"source_domains":["official_club","official_competition","news"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["verified_absence_information"],"staleness_policy":"MATCH_SPECIFIC"},
    "Q41": {"evidence_requirements":["expected_lineup","confirmed_lineup","formations"],"source_domains":["official_club","official_competition","lineup_sources"],"answer_mode":"EVIDENCE_DERIVED","minimum_evidence":["expected_or_confirmed_lineup"],"staleness_policy":"MATCH_SPECIFIC"},
}


def _enrich(question: Dict[str, str], piece: int) -> Dict[str, Any]:
    return {
        "piece": str(piece),
        "id": question["id"],
        "question": question["question"],
        **QUESTION_ENRICHMENT[question["id"]],
        "default_status": "UNVERIFIED",
    }


def get_piece_questions(piece: int) -> List[Dict[str, Any]]:
    return [
        _enrich(question, piece)
        for question in V2_QUESTION_REGISTRY.get(piece, [])
    ]


def get_all_questions() -> List[Dict[str, Any]]:
    questions: List[Dict[str, Any]] = []
    for piece, piece_questions in V2_QUESTION_REGISTRY.items():
        for question in piece_questions:
            questions.append(_enrich(question, piece))
    return questions


def question_count() -> int:
    return len(get_all_questions())
