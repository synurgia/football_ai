from typing import Any, Dict, List


class OpenFootballNormalizer:
    """
    Converts OpenFootball JSON records into a stable internal structure.

    This layer does not perform prediction and does not modify Pieces 1-9.
    """

    @staticmethod
    def normalize_match(
        match: Dict[str, Any],
        competition: str,
    ) -> Dict[str, Any]:
        score = match.get("score")

        if score is not None and "ft" in score:
            status = "completed"
        else:
            status = "scheduled"

        return {
            "competition": competition,
            "round": match.get("round"),
            "date": match.get("date"),
            "time": match.get("time"),
            "home_team": match.get("team1"),
            "away_team": match.get("team2"),
            "status": status,
            "score": score,
            "source": "openfootball",
        }

    @classmethod
    def normalize_dataset(
        cls,
        data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        competition = data.get("name")

        if not competition:
            raise ValueError("OpenFootball dataset has no competition name.")

        matches = data.get("matches")

        if not isinstance(matches, list):
            raise ValueError("OpenFootball dataset has no valid matches list.")

        return [
            cls.normalize_match(match, competition)
            for match in matches
            if isinstance(match, dict)
        ]
