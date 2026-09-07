from typing import Any, Dict

from app.worldwide_ingestion import WorldwideOpenFootService


class OpenFootPredictionAdapter:
    """
    Translates WorldwideOpenFootService data into the payload
    already accepted by app.services.prediction_service.run_prediction().

    This adapter does not modify Pieces 1-9 and does not invent
    unavailable player, injury, referee, weather, or tactical data.
    """

    def __init__(self, service=None):
        self.service = service or WorldwideOpenFootService()

    @staticmethod
    def _team_payload(
        team_name: str,
        snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "team_name": team_name,
            "league_position": snapshot.get("league_position"),
            "recent_form": {
                "sequence": snapshot.get("recent_form", []),
            },
            "team_statistics": {
                "matches_played": snapshot.get("matches_played", 0),
                "wins": snapshot.get("wins", 0),
                "draws": snapshot.get("draws", 0),
                "losses": snapshot.get("losses", 0),
                "goals_for": snapshot.get("goals_for", 0),
                "goals_against": snapshot.get("goals_against", 0),
                "goal_difference": snapshot.get("goal_difference", 0),
                "points": snapshot.get("points", 0),
                "points_per_game": snapshot.get("points_per_game", 0.0),
            },
            "starting_xi": {
                "formation": "Unknown",
                "players": [],
            },
            "injuries": [],
            "suspensions": [],
            "additional_data": {
                "source": "openfoot",
                "data_status": "team_level_only",
                "team_snapshot": snapshot,
            },
        }

    def build_prediction_payload(
        self,
        competition_id: str,
        match_index: int = 0,
        season: str = None,
    ) -> Dict[str, Any]:
        """
        Build an existing run_prediction() payload from one
        worldwide OpenFoot competition.
        """

        dataset = self.service.load_competition(
            competition_id=competition_id,
            season=season,
        )

        matches = dataset["matches"]

        if not matches:
            raise ValueError(
                f"No matches returned for competition: {competition_id}"
            )

        if match_index < 0 or match_index >= len(matches):
            raise IndexError(
                f"match_index {match_index} is outside the returned "
                f"match range 0-{len(matches) - 1}"
            )

        match = matches[match_index]

        home_name = match.get("home_team")
        away_name = match.get("away_team")

        if not home_name or not away_name:
            raise ValueError(
                "OpenFoot match is missing home or away team."
            )

        home_snapshot = dataset["team_snapshots"].get(home_name)
        away_snapshot = dataset["team_snapshots"].get(away_name)

        if home_snapshot is None or away_snapshot is None:
            raise ValueError(
                "Team snapshots are missing for the selected match."
            )

        competition = dataset["competition"]

        return {
            "competition": competition["name"],
            "home_team": self._team_payload(
                home_name,
                home_snapshot,
            ),
            "away_team": self._team_payload(
                away_name,
                away_snapshot,
            ),
            "market_odds": {},
            "data_sources": {
                "provider": "openfoot",
                "competition_id": competition["id"],
                "season": competition["season"],
                "source_match_id": match.get("source_match_id"),
                "source_refs": match.get("source_refs"),
                "kickoff_at": match.get("kickoff_at"),
                "data_status": "team_level_match_input",
            },
            "environment": {},
            "referee": {},
        }
