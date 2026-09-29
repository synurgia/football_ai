from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from app.data_providers.openfoot_provider import OpenFootProvider
from app.today_match_aggregator import TodayMatchAggregator
from app.data_normalizers.openfoot_normalizer import OpenFootNormalizer
from app.data_registry.v13_competition_identity_resolver import (
    V13CompetitionIdentityResolver,
)


class WorldwideDailyMatchScanner:
    def __init__(self, provider=None):
        self.provider = provider or OpenFootProvider()
        self.aggregator = TodayMatchAggregator(openfoot_provider=self.provider)
        self.v13_identity = V13CompetitionIdentityResolver()

    def _resolve_competition_identity(
        self, matches: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        resolved_matches = []

        for match in matches:
            item = dict(match)

            competition_id = item.get("competition_id")
            competition_name = (
                item.get("competition_name_canonical")
                or item.get("competition_name")
                or item.get("competition")
            )
            country = item.get("country")

            try:
                result = self.v13_identity.resolve(
                    competition_name=str(competition_name or ""),
                    country=country,
                    competition_id=competition_id,
                )

                if isinstance(result, dict):
                    if result.get("competition_id"):
                        item["competition_id"] = result.get("competition_id")

                    if result.get("competition_name"):
                        item["competition_name_canonical"] = result.get(
                            "competition_name"
                        )

                    item["competition_identity_status"] = result.get(
                        "status", "UNRESOLVED"
                    )
                    item["competition_identity_method"] = result.get(
                        "match_method", "NONE"
                    )
                else:
                    item["competition_identity_status"] = "UNRESOLVED"
                    item["competition_identity_method"] = "INVALID_RESOLVER_RESULT"

            except Exception as exc:
                item["competition_identity_status"] = "UNRESOLVED"
                item["competition_identity_method"] = "RESOLVER_ERROR"
                item["competition_identity_error"] = str(exc)

            resolved_matches.append(item)

        return resolved_matches

    def _scan_date(self, target_date: str) -> Dict[str, Any]:
        aggregated = self.aggregator.load_today(target_date)

        matches = [
            dict(match)
            for match in aggregated.get("matches", [])
            if str(match.get("kickoff_at", "")).startswith(target_date)
        ]

        # V1.3 identity resolution happens BEFORE V1.3 mapped-source collection.
        matches = self._resolve_competition_identity(matches)

        # Rebuild the unified source pool using the now-resolved competition IDs.
        try:
            unified_sources = self.aggregator._collect_unified_sources(matches)
        except Exception as exc:
            unified_sources = []
            for match in matches:
                if match.get("competition_id"):
                    unified_sources.append(
                        {
                            "competition_id": match.get("competition_id"),
                            "collection_mode": "UNIFIED_V1_3_ERROR",
                            "error": str(exc),
                        }
                    )

        return {
            "matches": matches,
            "unified_sources": unified_sources,
        }

    def scan(
        self,
        target_date: Optional[str] = None,
        include_tomorrow: bool = True,
    ) -> Dict[str, Any]:
        if target_date is None:
            today = date.today()
            today_str = today.isoformat()
        else:
            today_str = str(target_date)
            today = date.fromisoformat(today_str)

        tomorrow_str = (today + timedelta(days=1)).isoformat()

        today_result = self._scan_date(today_str)

        result = {
            "scan_date": today_str,
            "today": today_result["matches"],
            "tomorrow": [],
            "unified_sources": today_result["unified_sources"],
            "provenance": {
                "provider": "aggregated_sources",
                "scan_mode": "global_date",
                "v13_identity_bridge": True,
            },
        }

        if include_tomorrow:
            tomorrow_result = self._scan_date(tomorrow_str)
            result["tomorrow"] = tomorrow_result["matches"]
            result["unified_sources"].extend(
                tomorrow_result["unified_sources"]
            )

        return result
