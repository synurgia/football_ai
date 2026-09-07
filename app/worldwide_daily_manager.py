from datetime import date
from typing import Any, Dict, Optional

from app.worldwide_daily_scanner import WorldwideDailyMatchScanner
from app.data_validation.daily_readiness import DailyDataReadiness
from app.data_registry.rolling_match_store import RollingMatchStore


class WorldwideDailyDataManager:
    """
    Controls the daily worldwide football data workflow.

    TODAY:
        Discover matches and identify candidates that may be processed.

    TOMORROW:
        Discover matches for preparation only.

    This manager does not run predictions and does not modify Pieces 1-9.
    """

    def __init__(self, scanner: Optional[WorldwideDailyMatchScanner] = None, store=None):
        self.scanner = scanner or WorldwideDailyMatchScanner()
        self.store = store or RollingMatchStore()

    def run(
        self,
        target_date: Optional[str] = None,
    ) -> Dict[str, Any]:

        if target_date is None:
            target = date.today()
            target_date = target.isoformat()
        else:
            target = date.fromisoformat(target_date)
            target_date = target.isoformat()

        scan = self.scanner.scan(
            target_date=target_date,
            include_tomorrow=True,
        )

        readiness = DailyDataReadiness.evaluate_daily_scan(scan)

        today_ids = self.store.upsert_many(
            scan.get("today", []),
            "today",
        )

        tomorrow_ids = self.store.upsert_many(
            scan.get("tomorrow", []),
            "tomorrow",
        )

        return {
            "date": target_date,
            "today": {
                "discovered": len(scan.get("today", [])),
                "ready": len(readiness["today_ready"]),
                "held": len(readiness["today_held"]),
            },
            "tomorrow": {
                "discovered": len(scan.get("tomorrow", [])),
                "preparation": len(
                    readiness["tomorrow_preparation"]
                ),
            },
            "today_ready_matches": readiness["today_ready"],
            "today_held_matches": readiness["today_held"],
            "tomorrow_preparation": readiness[
                "tomorrow_preparation"
            ],
            "stored": {
                "today": len(today_ids),
                "tomorrow": len(tomorrow_ids),
                "total_records": self.store.count(),
            },
            "provenance": scan.get("provenance", {}),
        }
