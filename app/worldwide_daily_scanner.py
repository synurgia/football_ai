from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from app.data_providers.openfoot_provider import OpenFootProvider
from app.data_normalizers.openfoot_normalizer import OpenFootNormalizer


class WorldwideDailyMatchScanner:
    """
    Global daily football fixture scanner.

    TODAY:
        Primary processing candidates.

    TOMORROW:
        Preparation candidates only.

    The scanner does not run predictions and does not modify
    Pieces 1-9.
    """

    def __init__(self, provider: Optional[OpenFootProvider] = None):
        self.provider = provider or OpenFootProvider()

    def _scan_date(self, target_date: str) -> List[Dict[str, Any]]:
        raw_matches = self.provider.get_all_matches(date=target_date)

        normalized = OpenFootNormalizer.normalize_matches(raw_matches)

        return [
            match
            for match in normalized
            if match.get("kickoff_at", "").startswith(target_date)
        ]

    def scan(
        self,
        target_date: Optional[str] = None,
        include_tomorrow: bool = True,
    ) -> Dict[str, Any]:
        if target_date is None:
            target = date.today()
        else:
            target = date.fromisoformat(target_date)

        today_str = target.isoformat()

        result: Dict[str, Any] = {
            "scan_date": today_str,
            "today": self._scan_date(today_str),
            "tomorrow": [],
            "provenance": {
                "provider": "openfoot",
                "scan_mode": "global_date",
            },
        }

        if include_tomorrow:
            tomorrow = target + timedelta(days=1)
            tomorrow_str = tomorrow.isoformat()
            result["tomorrow"] = self._scan_date(tomorrow_str)

        return result
