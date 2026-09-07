from typing import Any, Dict, List


class FootballDataReadiness:
    """
    Stronger football-data readiness gate.

    This layer distinguishes:
        READY        -> eligible for today's analytical pipeline
        INSUFFICIENT -> held until critical data improves
        PREPARATION  -> tomorrow-only preparation

    Missing optional information is reported but does not automatically
    prevent processing. No unavailable data is invented.
    """

    CORE_FIELDS = (
        "competition",
        "season",
        "kickoff_at",
        "home_team",
        "away_team",
    )

    @classmethod
    def evaluate(
        cls,
        match: Dict[str, Any],
        home_snapshot: Dict[str, Any] | None = None,
        away_snapshot: Dict[str, Any] | None = None,
        *,
        day_role: str = "today",
    ) -> Dict[str, Any]:

        home_snapshot = home_snapshot or {}
        away_snapshot = away_snapshot or {}

        critical_missing: List[str] = []
        warnings: List[str] = []

        for field in cls.CORE_FIELDS:
            if not match.get(field):
                critical_missing.append(field)

        if day_role == "tomorrow":
            return {
                "status": "preparation",
                "process": False,
                "critical_missing": critical_missing,
                "warnings": warnings,
                "reasons": [
                    "Match is tomorrow and is preparation-only."
                ],
            }

        if day_role != "today":
            return {
                "status": "insufficient",
                "process": False,
                "critical_missing": ["invalid_day_role"],
                "warnings": warnings,
                "reasons": [
                    "Only today matches may enter the processing queue."
                ],
            }

        if not home_snapshot:
            critical_missing.append("home_team_snapshot")

        if not away_snapshot:
            critical_missing.append("away_team_snapshot")

        if home_snapshot:
            if home_snapshot.get("matches_played", 0) < 1:
                warnings.append("Limited home-team historical sample.")

            if home_snapshot.get("league_position") is None:
                warnings.append("Home-team standings position unavailable.")

        if away_snapshot:
            if away_snapshot.get("matches_played", 0) < 1:
                warnings.append("Limited away-team historical sample.")

            if away_snapshot.get("league_position") is None:
                warnings.append("Away-team standings position unavailable.")

        if critical_missing:
            return {
                "status": "insufficient",
                "process": False,
                "critical_missing": sorted(set(critical_missing)),
                "warnings": warnings,
                "reasons": [
                    "Critical football data is missing."
                ],
            }

        return {
            "status": "ready",
            "process": True,
            "critical_missing": [],
            "warnings": warnings,
            "reasons": [],
        }
