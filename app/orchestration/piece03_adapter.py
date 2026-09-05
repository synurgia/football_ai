from typing import Any, Dict

from app.statistical.piece03_engine import (
    FiveDimensionalAnalyticsEngine,
    PoissonModelEngine,
    ValueBettingEngine,
    AgentAIHybridEngine,
    Step16MultiSystemVerifier,
    MustWinEvaluator,
)
from app.models.match_data import PreMatchData


def run_piece03(match: PreMatchData) -> Dict[str, Any]:
    home = match.home_team
    away = match.away_team

    home_stats = home.team_statistics
    away_stats = away.team_statistics

    home_xg = float(home_stats.get("xg_avg", 1.6))
    away_xg = float(away_stats.get("xg_avg", 1.1))

    # ---------------------------------------------------------------
    # 1. Five-dimensional historical/form analysis
    # ---------------------------------------------------------------
    five_d = FiveDimensionalAnalyticsEngine()

    home_history = home_stats.get("matches", [])
    away_history = away_stats.get("matches", [])

    home_history_result = five_d.analyze_10_game_history(
        home.team_name,
        home_history,
    )

    away_history_result = five_d.analyze_10_game_history(
        away.team_name,
        away_history,
    )

    five_d_matrix = five_d.generate_5d_prediction_matrix(
        home_form=home_history_result,
        away_form=away_history_result,
        home_xg_avg=home_xg,
        away_xg_avg=away_xg,
    )

    dim_5_index = float(
        five_d_matrix.get(
            "composite_index",
            five_d_matrix.get("dim_5_index", 0.5),
        )
    )

    # ---------------------------------------------------------------
    # 2. Poisson probability model
    # ---------------------------------------------------------------
    poisson = PoissonModelEngine()

    poisson_probs = poisson.calculate_1x2_probabilities(
        home_xg=home_xg,
        away_xg=away_xg,
    )

    # ---------------------------------------------------------------
    # 3. AI hybrid consensus
    # ---------------------------------------------------------------
    hybrid = AgentAIHybridEngine()

    consensus = hybrid.synthesize_consensus(
        poisson_probs=poisson_probs,
        dim_5_index=dim_5_index,
    )

    # ---------------------------------------------------------------
    # 4. Market edge
    # ---------------------------------------------------------------
    value_engine = ValueBettingEngine()

    market_odds = {
        key: float(value)
        for key, value in match.market_odds.items()
        if isinstance(value, (int, float))
    }

    value_results = {}

    for selection, odds in market_odds.items():
        if selection in poisson_probs:
            value_results[selection] = value_engine.evaluate_market_edge(
                model_prob=float(poisson_probs[selection]),
                bookmaker_odds=odds,
            )

    # ---------------------------------------------------------------
    # 5. Multi-system verification
    # ---------------------------------------------------------------
    verifier = Step16MultiSystemVerifier()

    verification = verifier.execute_multi_system_verification(
        home_team=home.team_name,
        away_team=away.team_name,
        home_xg=home_xg,
        away_xg=away_xg,
        dim_5_composite_index=dim_5_index,
        bookmaker_odds=market_odds,
    )

    # ---------------------------------------------------------------
    # 6. Must-win selection
    # ---------------------------------------------------------------
    must_win = MustWinEvaluator()

    must_win_result = must_win.isolate_must_win_selection(
        home_team=home.team_name,
        away_team=away.team_name,
        probabilities=poisson_probs,
    )

    return {
        "five_dimensional": {
            "home_history": home_history_result,
            "away_history": away_history_result,
            "prediction_matrix": five_d_matrix,
            "composite_index": dim_5_index,
        },
        "poisson": poisson_probs,
        "hybrid_consensus": consensus,
        "value_analysis": value_results,
        "verification": verification,
        "must_win": must_win_result,
    }
