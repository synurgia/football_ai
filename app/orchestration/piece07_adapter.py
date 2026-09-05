from typing import Any, Dict
import pandas as pd

from app.statistical.piece07_engine import (
    StatisticalMatchFilter,
    MarketAlignmentEngine,
    BayesianBusParkAdjuster,
    MatchProbabilities,
    MarketQuote,
    OddsFormat,
)
from app.models.match_data import PreMatchData


def _matches_to_dataframe(team) -> pd.DataFrame:
    matches = team.team_statistics.get("matches", [])

    if isinstance(matches, pd.DataFrame):
        return matches.copy()

    if isinstance(matches, list):
        return pd.DataFrame(matches)

    return pd.DataFrame()


def _history_dataframe(team, key: str) -> pd.DataFrame:
    value = team.additional_data.get(key, [])

    if isinstance(value, pd.DataFrame):
        return value.copy()

    if isinstance(value, list):
        return pd.DataFrame(value)

    return pd.DataFrame()


def _build_market_quotes(match: PreMatchData):
    quotes = []

    raw_quotes = match.data_sources.get("market_quotes", [])

    if not isinstance(raw_quotes, list):
        return quotes

    for item in raw_quotes:
        if not isinstance(item, dict):
            continue

        selection_id = item.get("selection_id")
        bid_price = item.get("bid_price")
        ask_price = item.get("ask_price")
        liquidity = item.get("available_liquidity_usd")

        if selection_id is None:
            continue

        try:
            bid_price = float(bid_price)
            ask_price = float(ask_price)
            liquidity = float(liquidity)
        except (TypeError, ValueError):
            continue

        fmt = str(item.get("odds_format", "cents")).lower()

        if fmt in {"decimal", "odds"}:
            odds_format = OddsFormat.DECIMAL
        else:
            odds_format = OddsFormat.PROBABILITY_CENTS

        quotes.append(
            MarketQuote(
                selection_id=str(selection_id),
                bid_price=bid_price,
                ask_price=ask_price,
                available_liquidity_usd=liquidity,
                odds_format=odds_format,
            )
        )

    return quotes


def run_piece07(match: PreMatchData) -> Dict[str, Any]:
    home = match.home_team
    away = match.away_team

    home_matches = _matches_to_dataframe(home)
    away_matches = _matches_to_dataframe(away)

    # Determine favorite/underdog from the pre-match contract.
    home_is_underdog = bool(
        home.additional_data.get("is_underdog", False)
    )

    if home_is_underdog:
        favorite = away
        underdog = home
    else:
        favorite = home
        underdog = away

    favorite_matches = _matches_to_dataframe(favorite)
    underdog_matches = _matches_to_dataframe(underdog)

    # ---------------------------------------------------------------
    # 1. Statistical Match Filter
    # ---------------------------------------------------------------
    statistical_filter = StatisticalMatchFilter()

    favorite_xg_result = statistical_filter.filter_fraudulent_favorite(
        favorite_matches
    )

    goalkeeper_df = _history_dataframe(
        underdog,
        "goalkeeper_recent_matches",
    )

    h2h_df = _history_dataframe(
        underdog,
        "h2h_matches",
    )

    underdog_id = str(
        underdog.additional_data.get(
            "team_id",
            underdog.team_name,
        )
    )

    baseline_ppg = float(
        underdog.additional_data.get(
            "baseline_ppg_vs_top_tier",
            0.0,
        )
    )

    gk_result = statistical_filter.filter_goalkeeper_hot_period(
        goalkeeper_df
    )

    h2h_result = statistical_filter.filter_h2h_bogeyman_status(
        h2h_df,
        underdog_id,
        baseline_ppg,
    )

    matchup_profile = statistical_filter.Evaluate_matchup(
        favorite_df=favorite_matches,
        underdog_gk_df=goalkeeper_df,
        h2h_df=h2h_df,
        underdog_id=underdog_id,
        underdog_baseline_ppg=baseline_ppg,
    )

    # ---------------------------------------------------------------
    # 2. Bayesian Bus-Park Adjustment
    # ---------------------------------------------------------------
    poisson_input = match.data_sources.get("poisson_probabilities", {})

    favorite_prob = float(
        poisson_input.get("favorite", 0.0)
    )
    draw_prob = float(
        poisson_input.get("draw", 0.0)
    )
    underdog_prob = float(
        poisson_input.get("underdog", 0.0)
    )

    poisson_probs = MatchProbabilities(
        p_favorite_win=favorite_prob,
        p_draw=draw_prob,
        p_underdog_win=underdog_prob,
    )

    top_tier_history = _history_dataframe(
        underdog,
        "top_tier_history",
    )

    bayesian_adjuster = BayesianBusParkAdjuster()

    bayesian_result = bayesian_adjuster.adjust_probabilities(
        poisson_probs=poisson_probs,
        underdog_top_tier_history=top_tier_history,
    )

    # ---------------------------------------------------------------
    # 3. Market Alignment
    # ---------------------------------------------------------------
    market_ai_probs = {
        "HOME": float(
            poisson_input.get(
                "home",
                0.0,
            )
        ),
        "DRAW": float(
            poisson_input.get(
                "draw",
                0.0,
            )
        ),
        "AWAY": float(
            poisson_input.get(
                "away",
                0.0,
            )
        ),
    }

    market_quotes = _build_market_quotes(match)

    market_alignment = MarketAlignmentEngine()

    if market_quotes:
        market_result = market_alignment.Scan_and_align_match(
            ai_1x2_probs=market_ai_probs,
            market_quotes=market_quotes,
        )
        market_result = market_result.to_dict(orient="records")
    else:
        market_result = []

    return {
        "statistical_filter": {
            "favorite_xg": favorite_xg_result,
            "goalkeeper": gk_result,
            "h2h": h2h_result,
            "matchup_profile": matchup_profile.__dict__,
        },
        "bayesian_adjustment": {
            "base_probabilities": bayesian_result.poisson_base_probs.__dict__,
            "adjusted_probabilities": bayesian_result.adjusted_probs.__dict__,
            "top_tier_matches_evaluated": bayesian_result.top_tier_matches_evaluated,
            "successful_bus_parks": bayesian_result.successful_bus_parks,
            "prior_condition_met": bayesian_result.prior_condition_met,
            "applied_boost_factor": bayesian_result.applied_boost_factor,
        },
        "market_alignment": market_result,
    }
