from typing import Any, Dict


class DataSufficiencyChecker:
    """
    Checks whether normalized football match data contains the
    information required for trustworthy downstream analysis.

    Missing information is reported explicitly rather than fabricated.
    """

    REQUIRED_FIELDS = (
        "competition",
        "date",
        "home_team",
        "away_team",
    )

    OPTIONAL_FIELDS = (
        "starting_xi",
        "injuries",
        "suspensions",
        "referee",
        "environment",
        "team_statistics",
    )

    @classmethod
    def check_match(cls, match: Dict[str, Any]) -> Dict[str, Any]:
        missing_required = [
            field
            for field in cls.REQUIRED_FIELDS
            if not match.get(field)
        ]

        available_optional = [
            field
            for field in cls.OPTIONAL_FIELDS
            if match.get(field) is not None
        ]

        missing_optional = [
            field
            for field in cls.OPTIONAL_FIELDS
            if match.get(field) is None
        ]

        return {
            "sufficient_for_match_identification": not missing_required,
            "missing_required": missing_required,
            "available_optional": available_optional,
            "missing_optional": missing_optional,
            "source": match.get("source"),
            "competition": match.get("competition"),
            "home_team": match.get("home_team"),
            "away_team": match.get("away_team"),
        }
