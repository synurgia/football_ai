from typing import Any, Dict, List


class DailyDataReadiness:
    """
    Controls whether a discovered match is ready for analytical processing.

    TODAY:
        May be processed if minimum data requirements are satisfied.

    TOMORROW:
        Preparation only; never marked prediction-ready by this gate.

    Missing information is never invented.
    """

    REQUIRED_MATCH_FIELDS = (
        "competition",
        "home_team",
        "away_team",
        "kickoff_at",
    )

    @classmethod
    def evaluate_match(
        cls,
        match: Dict[str, Any],
        *,
        day_role: str,
    ) -> Dict[str, Any]:

        missing = [
            field
            for field in cls.REQUIRED_MATCH_FIELDS
            if not match.get(field)
        ]

        if missing:
            return {
                "status": "not_ready",
                "day_role": day_role,
                "process": False,
                "reasons": [
                    f"Missing required field: {field}"
                    for field in missing
                ],
            }

        if day_role == "tomorrow":
            return {
                "status": "preparation",
                "day_role": "tomorrow",
                "process": False,
                "reasons": [
                    "Tomorrow match is preparation-only until it becomes today."
                ],
            }

        if day_role != "today":
            return {
                "status": "not_ready",
                "day_role": day_role,
                "process": False,
                "reasons": [
                    "Only today matches may enter the processing queue."
                ],
            }

        return {
            "status": "ready",
            "day_role": "today",
            "process": True,
            "reasons": [],
        }

    @classmethod
    def evaluate_daily_scan(
        cls,
        scan_result: Dict[str, Any],
    ) -> Dict[str, List[Dict[str, Any]]]:

        today_ready = []
        today_held = []
        tomorrow_preparation = []

        for match in scan_result.get("today", []):
            result = cls.evaluate_match(match, day_role="today")
            item = {
                "match": match,
                "readiness": result,
            }

            if result["process"]:
                today_ready.append(item)
            else:
                today_held.append(item)

        for match in scan_result.get("tomorrow", []):
            result = cls.evaluate_match(match, day_role="tomorrow")
            tomorrow_preparation.append({
                "match": match,
                "readiness": result,
            })

        return {
            "today_ready": today_ready,
            "today_held": today_held,
            "tomorrow_preparation": tomorrow_preparation,
        }
