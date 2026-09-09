from typing import Dict, List


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


def get_piece_questions(piece: int) -> List[Dict[str, str]]:
    return list(V2_QUESTION_REGISTRY.get(piece, []))


def get_all_questions() -> List[Dict[str, str]]:
    questions: List[Dict[str, str]] = []

    for piece, piece_questions in V2_QUESTION_REGISTRY.items():
        for question in piece_questions:
            questions.append(
                {
                    "piece": str(piece),
                    "id": question["id"],
                    "question": question["question"],
                }
            )

    return questions


def question_count() -> int:
    return len(get_all_questions())
