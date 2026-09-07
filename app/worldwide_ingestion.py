from typing import Any, Dict, List, Optional

from app.data_providers.openfoot_provider import OpenFootProvider
from app.data_normalizers.openfoot_normalizer import OpenFootNormalizer
from app.data_services import OpenFootTeamSnapshot


class WorldwideOpenFootService:
    """
    Generic worldwide football ingestion service.

    Uses the OpenFoot competition catalogue dynamically.
    Does not hardcode individual countries or competitions.
    Does not modify Pieces 1-9.
    """

    def __init__(self, provider: Optional[OpenFootProvider] = None):
        self.provider = provider or OpenFootProvider()

    def list_competitions(self) -> List[Dict[str, Any]]:
        """Return the worldwide OpenFoot competition catalogue."""
        return self.provider.get_competitions()

    def get_competition(
        self,
        competition_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Find one competition by its OpenFoot ID."""
        competitions = self.list_competitions()

        for competition in competitions:
            if competition.get("id") == competition_id:
                return competition

        return None

    def load_competition(
        self,
        competition_id: str,
        season: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Load matches, standings and team snapshots for any
        valid OpenFoot competition.
        """

        competition = self.get_competition(competition_id)

        if competition is None:
            raise ValueError(
                f"OpenFoot competition not found: {competition_id}"
            )

        resolved_season = season or competition.get("currentSeason")

        if not resolved_season:
            raise ValueError(
                f"No season available for competition: {competition_id}"
            )

        raw_matches = self.provider.get_matches(
            competition=competition_id,
            season=resolved_season,
        )

        normalized_matches = OpenFootNormalizer.normalize_matches(
            raw_matches
        )

        standings = self.provider.get_standings(
            competition=competition_id
        )

        team_names = set()

        for match in normalized_matches:
            if match.get("home_team"):
                team_names.add(match["home_team"])

            if match.get("away_team"):
                team_names.add(match["away_team"])

        team_snapshots = {}

        for team_name in sorted(team_names):
            team_snapshots[team_name] = OpenFootTeamSnapshot.build(
                normalized_matches,
                standings,
                team_name,
            )

        return {
            "competition": {
                "id": competition.get("id"),
                "name": competition.get("name"),
                "country": competition.get("country"),
                "season": resolved_season,
            },
            "matches": normalized_matches,
            "standings": standings,
            "team_snapshots": team_snapshots,
            "provenance": {
                "matches": "openfoot",
                "standings": "openfoot",
                "competition_id": competition_id,
                "season": resolved_season,
            },
        }
