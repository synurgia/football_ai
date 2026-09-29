from typing import Any, Dict, List, Optional

from app.data_registry.team_snapshot_store import TeamSnapshotStore
from app.data_validation.football_readiness import FootballDataReadiness


class WorldwideReadinessService:
    """
    Connects daily discovered matches to persistent real team snapshots
    and evaluates them through FootballDataReadiness 2.0.

    This layer does not run predictions and does not modify Pieces 1-9.
    """

    def __init__(
        self,
        store: Optional[TeamSnapshotStore] = None,
    ):
        self.store = store or TeamSnapshotStore()

    def evaluate_match(
        self,
        match: Dict[str, Any],
        day_role: str = "today",
    ) -> Dict[str, Any]:

        competition = match.get("competition", "")
        season = match.get("season", "")
        home_team = match.get("home_team", "")
        away_team = match.get("away_team", "")

        home_snapshot = None
        away_snapshot = None

        if competition and season and home_team:
            home_snapshot = self.store.get(
                match.get("openfoot_competition_id") or competition,
                season,
                home_team,
            )

        if competition and season and away_team:
            away_snapshot = self.store.get(
                match.get("openfoot_competition_id") or competition,
                season,
                away_team,
            )

        readiness = FootballDataReadiness.evaluate(
            match,
            home_snapshot=home_snapshot,
            away_snapshot=away_snapshot,
            day_role=day_role,
        )

        return {
            "match": match,
            "home_snapshot": home_snapshot,
            "away_snapshot": away_snapshot,
            "readiness": readiness,
        }

    def evaluate_daily(
        self,
        today_matches: List[Dict[str, Any]],
        tomorrow_matches: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:

        # Two independent tracks that both run for every match:
        #   ready       -> prediction track
        #   reasoning   -> intelligence track (always populated when eligible)
        #   held        -> match scanned but identity/context incomplete

        today_ready = []
        today_reasoning = []
        today_held = []
        tomorrow_preparation = []

        for match in today_matches:
            result = self.evaluate_match(match, day_role="today")
            readiness = result["readiness"]

            if readiness.get("process"):
                today_ready.append(result)

            if readiness.get("reasoning_eligible"):
                today_reasoning.append(result)
            else:
                today_held.append(result)

        for match in tomorrow_matches or []:
            tomorrow_preparation.append(
                self.evaluate_match(match, day_role="tomorrow")
            )

        return {
            "today_ready": today_ready,
            "today_reasoning": today_reasoning,
            "today_held": today_held,
            # kept for backwards compatibility with existing callers
            "today_insufficient": today_held,
            "tomorrow_preparation": tomorrow_preparation,
            "all_today": today_ready + today_reasoning + today_held,
            "summary": {
                "today_total": len(today_matches),
                "today_ready": len(today_ready),
                "today_reasoning": len(today_reasoning),
                "today_held": len(today_held),
                "today_insufficient": len(today_held),
                "tomorrow_preparation": len(tomorrow_preparation),
            },
        }
