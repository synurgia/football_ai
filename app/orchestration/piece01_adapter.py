from typing import Any, Dict

from app.analytics.piece01_engine import (
    CompetitionRules,
    MatchAnalyticalEngine,
    TeamProfile,
)
from app.models.match_data import PreMatchData


def run_piece01(match: PreMatchData) -> Dict[str, Any]:
    """
    Adapt the central PreMatchData contract to Piece 1's
    existing MatchAnalyticalEngine.

    Piece 1 itself is not modified.
    """

    rules = CompetitionRules(
        goes_to_penalties_on_draw=False,
        penalty_points_awarded=False,
        tournament_name=match.competition,
    )

    home = match.home_team
    away = match.away_team

    home_profile = TeamProfile(
        name=home.team_name,
        has_major_funding=bool(
            home.additional_data.get(
                "has_major_funding",
                False,
            )
        ),
        funding_notes=str(
            home.additional_data.get(
                "funding_notes",
                "",
            )
        ),
        is_must_win=bool(
            home.additional_data.get(
                "is_must_win",
                False,
            )
        ),
        must_win_context=str(
            home.additional_data.get(
                "must_win_context",
                "",
            )
        ),
        scoring_probability=float(
            home.additional_data.get(
                "scoring_probability",
                0.50,
            )
        ),
    )

    away_profile = TeamProfile(
        name=away.team_name,
        has_major_funding=bool(
            away.additional_data.get(
                "has_major_funding",
                False,
            )
        ),
        funding_notes=str(
            away.additional_data.get(
                "funding_notes",
                "",
            )
        ),
        is_must_win=bool(
            away.additional_data.get(
                "is_must_win",
                False,
            )
        ),
        must_win_context=str(
            away.additional_data.get(
                "must_win_context",
                "",
            )
        ),
        scoring_probability=float(
            away.additional_data.get(
                "scoring_probability",
                0.50,
            )
        ),
    )

    engine = MatchAnalyticalEngine(
        rules=rules,
        team_a=home_profile,
        team_b=away_profile,
    )

    return engine.run_full_analysis()
