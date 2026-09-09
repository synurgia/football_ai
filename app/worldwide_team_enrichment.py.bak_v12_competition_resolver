from typing import Any, Dict, Optional, Set

from app.data_providers.openfoot_provider import OpenFootProvider
from app.data_registry.team_snapshot_store import TeamSnapshotStore


class WorldwideTeamEnrichment:
    """
    Enriches daily football fixtures with real OpenFoot standings data.

    Only competitions represented in the supplied daily fixtures are
    queried. This avoids unnecessarily requesting all 120+ competitions.

    This layer does not run predictions and does not modify Pieces 1-9.
    """

    def __init__(
        self,
        provider: Optional[OpenFootProvider] = None,
        store: Optional[TeamSnapshotStore] = None,
    ):
        self.provider = provider or OpenFootProvider()
        self.store = store or TeamSnapshotStore()

    @staticmethod
    def _competition_ids(matches) -> Set[str]:
        return {
            match.get("competition")
            for match in matches
            if match.get("competition")
        }

    def enrich_matches(self, matches) -> Dict[str, Any]:
        competition_ids = self._competition_ids(matches)

        competitions: Dict[str, Any] = {}
        teams_enriched = 0

        for competition_id in sorted(competition_ids):
            standings = self.provider.get_standings(
                competition=competition_id
            )

            competition_teams = 0

            for table in standings:
                for row in table.get("table", []):
                    team = row.get("team") or {}
                    team_name = team.get("name")

                    if not team_name:
                        continue

                    total = row.get("total") or {}

                    played = total.get("played", 0) or 0

                    # Ignore placeholder/non-playing rows.
                    if played <= 0:
                        continue

                    season = ""

                    for match in matches:
                        if match.get("competition") == competition_id:
                            season = match.get("season") or ""
                            if season:
                                break

                    if not season:
                        continue

                    snapshot = {
                        "matches_played": played,
                        "wins": total.get("won", 0) or 0,
                        "draws": total.get("drawn", 0) or 0,
                        "losses": total.get("lost", 0) or 0,
                        "goals_for": total.get("goalsFor", 0) or 0,
                        "goals_against": total.get("goalsAgainst", 0) or 0,
                        "goal_difference": (
                            total.get("goalDifference", 0) or 0
                        ),
                        "points": total.get("points", 0) or 0,
                        "points_per_game": (
                            (total.get("points", 0) or 0) / played
                        ),
                        "league_position": row.get("position"),
                        "recent_form": row.get("form") or [],
                        "source": "openfoot",
                    }

                    self.store.upsert(
                        competition_id,
                        season,
                        team_name,
                        snapshot,
                    )

                    teams_enriched += 1
                    competition_teams += 1

            competitions[competition_id] = {
                "standings_loaded": len(standings),
                "teams_enriched": competition_teams,
            }

        return {
            "competitions_processed": len(competition_ids),
            "teams_enriched": teams_enriched,
            "store_count": self.store.count(),
            "competitions": competitions,
            "provenance": {
                "provider": "openfoot",
                "source": "standings",
            },
        }
