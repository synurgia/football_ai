from typing import Any, Dict

from app.analytics.piece02_engine import (
    GeopoliticalContext,
    MarketHypeContext,
    TeamProfile,
    ExtendedAnalyticalEngine,
)
from app.models.match_data import PreMatchData


def run_piece02(match: PreMatchData) -> Dict[str, Any]:
    home = match.home_team
    away = match.away_team

    def build_profile(team):
        geo = GeopoliticalContext(
            is_conflict_zone=bool(
                team.additional_data.get("is_conflict_zone", False)
            ),
            is_displaced_home_venue=bool(
                team.additional_data.get("is_displaced_home_venue", False)
            ),
            disruption_notes=str(
                team.additional_data.get("disruption_notes", "")
            ),
        )

        hype = MarketHypeContext(
            global_fame_level=str(
                team.additional_data.get("global_fame_level", "medium")
            ),
            public_reputation_bias=bool(
                team.additional_data.get("public_reputation_bias", False)
            ),
            market_odds_inflated=bool(
                team.additional_data.get("market_odds_inflated", False)
            ),
        )

        return TeamProfile(
            name=team.team_name,
            geopolitical_status=geo,
            hype_status=hype,
            scoring_probability=float(
                team.additional_data.get("scoring_probability", 0.50)
            ),
            is_must_win=bool(
                team.additional_data.get("is_must_win", False)
            ),
        )

    home_profile = build_profile(home)
    away_profile = build_profile(away)

    engine = ExtendedAnalyticalEngine(
        team_a=home_profile,
        team_b=away_profile,
    )

    return engine.run_full_evaluation()
