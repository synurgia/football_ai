from typing import Any, Dict, List, Optional

from app.services.prediction_service import run_prediction
from app.worldwide_readiness_service import WorldwideReadinessService


class WorldwidePredictionRunner:
    """
    Sends only READY today's matches into the existing prediction service.

    Pieces 1-9 are untouched.

    Tomorrow matches are never submitted for prediction.
    """

    def __init__(
        self,
        readiness_service: Optional[WorldwideReadinessService] = None,
    ):
        self.readiness_service = (
            readiness_service or WorldwideReadinessService()
        )

    @staticmethod
    def _team_payload(
        team_name: str,
        snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "team_name": team_name,
            "league_position": snapshot.get("league_position"),
            "recent_form": {
                "sequence": snapshot.get("recent_form", [])
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
                "points_per_game": snapshot.get(
                    "points_per_game",
                    0.0,
                ),
            },
            "starting_xi": {
                "formation": "Unknown",
                "players": [],
            },
            "injuries": [],
            "suspensions": [],
            "additional_data": {
                "source": snapshot.get("source", "openfoot"),
                "data_status": "team_level_only",
                "team_snapshot": snapshot,
            },
        }

    def build_prediction_payload(
        self,
        item: Dict[str, Any],
    ) -> Dict[str, Any]:

        match = item["match"]
        home_snapshot = item["home_snapshot"]
        away_snapshot = item["away_snapshot"]

        if not home_snapshot or not away_snapshot:
            raise ValueError(
                "Cannot build prediction payload without "
                "both team snapshots."
            )

        return {
            "competition": match.get(
                "competition",
                "Unknown Competition",
            ),
            "home_team": self._team_payload(
                match["home_team"],
                home_snapshot,
            ),
            "away_team": self._team_payload(
                match["away_team"],
                away_snapshot,
            ),
            "market_odds": {},
            "data_sources": {
                "provider": "openfoot",
                "competition_id": match.get("competition"),
                "season": match.get("season"),
                "source_match_id": match.get("source_match_id"),
                "source_refs": match.get("source_refs"),
                "kickoff_at": match.get("kickoff_at"),
                "data_status": "daily_ready_team_level",
            },
            "environment": {},
            "referee": {},
        }

    def run_ready_matches(
        self,
        readiness_result: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        predictions = []

        for item in readiness_result.get(
            "today_ready",
            [],
        ):
            payload = self.build_prediction_payload(item)

            prediction = run_prediction(payload)

            predictions.append(
                {
                    "match": item["match"],
                    "prediction": prediction,
                }
            )

        return predictions
