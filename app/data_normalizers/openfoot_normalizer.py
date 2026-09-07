from typing import Any, Dict, List


class OpenFootNormalizer:
    """
    Converts OpenFoot records into the stable internal match structure.

    This layer does not perform prediction and does not modify Pieces 1-9.
    """

    @staticmethod
    def normalize_match(match: Dict[str, Any]) -> Dict[str, Any]:
        home = match.get("homeTeam") or {}
        away = match.get("awayTeam") or {}
        score = match.get("score") or {}

        status = match.get("status")

        if status == "finished":
            normalized_status = "completed"
        else:
            normalized_status = "scheduled"

        return {
            "competition": match.get("competitionId"),
            "season": match.get("season"),
            "round": match.get("round"),
            "kickoff_at": match.get("kickoffAt"),
            "home_team": home.get("name"),
            "away_team": away.get("name"),
            "home_team_id": home.get("id"),
            "away_team_id": away.get("id"),
            "status": normalized_status,
            "score": {
                "home": score.get("home"),
                "away": score.get("away"),
            } if score else None,
            "source": "openfoot",
            "source_match_id": match.get("id"),
            "source_refs": match.get("sourceRefs"),
        }

    @classmethod
    def normalize_matches(
        cls,
        matches: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        return [
            cls.normalize_match(match)
            for match in matches
            if isinstance(match, dict)
        ]
