from typing import Any, Dict

from app.tactical.piece04_engine import (
    TacticalResearchEngine,
    RankingEngine,
    SeniorMenMatchFilter,
    CompetitiveFirstXIFilter,
)
from app.models.match_data import PreMatchData


def run_piece04(match: PreMatchData) -> Dict[str, Any]:
    home = match.home_team
    away = match.away_team

    # ---------------------------------------------------------------
    # 1. Tactical research
    # ---------------------------------------------------------------
    tactical_engine = TacticalResearchEngine()

    home_metrics = {
        key: float(value)
        for key, value in home.team_statistics.items()
        if isinstance(value, (int, float))
    }

    away_metrics = {
        key: float(value)
        for key, value in away.team_statistics.items()
        if isinstance(value, (int, float))
    }

    tactical_report = tactical_engine.generate_tactical_research_report(
        home_team=home.team_name,
        home_metrics=home_metrics,
        away_team=away.team_name,
        away_metrics=away_metrics,
    )

    # ---------------------------------------------------------------
    # 2. Ranking analysis
    # ---------------------------------------------------------------
    ranking_engine = RankingEngine()

    standings_data = match.data_sources.get("standings", [])

    ranking_result = ranking_engine.process_rankings(
        competition_name=match.competition,
        standings_data=standings_data,
        home_team=home.team_name,
        away_team=away.team_name,
    )

    # ---------------------------------------------------------------
    # 3. Senior men's official-match eligibility
    # ---------------------------------------------------------------
    senior_filter = SeniorMenMatchFilter()

    eligibility_result = senior_filter.validate_match_eligibility(
        home_team=home.team_name,
        away_team=away.team_name,
        league_name=match.competition,
    )

    # ---------------------------------------------------------------
    # 4. Competitive fixture + starting XI status
    # ---------------------------------------------------------------
    xi_filter = CompetitiveFirstXIFilter()

    lineup_metadata = {}

    if home.starting_xi is not None:
        lineup_metadata["home_starting_xi"] = [
            {
                "player_id": player.player_id,
                "name": player.name,
                "position": player.position,
            }
            for player in home.starting_xi.players
        ]

    if away.starting_xi is not None:
        lineup_metadata["away_starting_xi"] = [
            {
                "player_id": player.player_id,
                "name": player.name,
                "position": player.position,
            }
            for player in away.starting_xi.players
        ]

    competitive_xi_result = (
        xi_filter.evaluate_competitive_and_first_xi_status(
            home_team=home.team_name,
            away_team=away.team_name,
            league_or_tournament=match.competition,
            is_official_competitive_fixture=match.data_sources.get(
                "is_official_competitive_fixture"
            ),
            starting_lineup_metadata=lineup_metadata,
        )
    )

    return {
        "tactical_research": tactical_report,
        "rankings": ranking_result,
        "match_eligibility": eligibility_result,
        "competitive_first_xi": competitive_xi_result,
    }
