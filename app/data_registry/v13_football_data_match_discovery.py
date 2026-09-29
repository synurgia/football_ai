from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.data_registry.v13_global_match_discovery import (
    V13MatchDiscoveryProvider,
)
from app.v13_ai_intelligence_engine import http_get


class V13FootballDataMatchDiscovery(V13MatchDiscoveryProvider):
    """
    football-data.org implementation of the V1.3 provider-neutral
    match-discovery interface.

    This is a source implementation only.
    It does not assign global source priority.
    It does not alter the V1.3 competition catalogue.
    """

    source_id = "football_data_org"
    source_name = "football-data.org"

    BASE_URL = "https://api.football-data.org/v4/matches"

    def discover(
        self,
        *,
        team_a: str,
        team_b: str,
        match_date: Optional[str],
        competition_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        api_key = os.getenv("FOOTBALL_DATA_API_KEY")

        if not api_key:
            return {
                "status": "SOURCE_UNAVAILABLE",
                "source_id": self.source_id,
                "source_name": self.source_name,
                "reason": "FOOTBALL_DATA_API_KEY not configured",
            }

        if not match_date:
            return {
                "status": "INSUFFICIENT_EVIDENCE",
                "source_id": self.source_id,
                "source_name": self.source_name,
                "reason": "match_date required",
            }

        try:
            response = http_get(
                self.BASE_URL,
                headers={"X-Auth-Token": api_key},
                params={
                    "dateFrom": match_date,
                    "dateTo": match_date,
                },
                timeout=15,
            )
        except Exception as exc:
            return {
                "status": "SOURCE_FAILED",
                "source_id": self.source_id,
                "source_name": self.source_name,
                "error": str(exc),
            }

        if response.status_code != 200:
            return {
                "status": "SOURCE_UNAVAILABLE",
                "source_id": self.source_id,
                "source_name": self.source_name,
                "http_status": response.status_code,
                "reason": "football-data.org request failed",
            }

        try:
            payload = response.json()
        except Exception as exc:
            return {
                "status": "SOURCE_FAILED",
                "source_id": self.source_id,
                "source_name": self.source_name,
                "error": f"Invalid JSON response: {exc}",
            }

        events = payload.get("matches", [])

        def norm(value: Any) -> str:
            return " ".join(
                str(value or "").lower().replace("-", " ").split()
            )

        wanted_a = norm(team_a)
        wanted_b = norm(team_b)

        candidates = []

        for event in events:
            home = event.get("homeTeam", {}).get("name")
            away = event.get("awayTeam", {}).get("name")

            home_n = norm(home)
            away_n = norm(away)

            if (
                (home_n == wanted_a and away_n == wanted_b)
                or
                (home_n == wanted_b and away_n == wanted_a)
            ):
                candidates.append(event)

        if not candidates:
            return {
                "status": "NOT_FOUND",
                "source_id": self.source_id,
                "source_name": self.source_name,
                "team_a": team_a,
                "team_b": team_b,
                "match_date": match_date,
                "competition_id": competition_id,
                "events_checked": len(events),
            }

        event = candidates[0]

        utc_now = datetime.now(timezone.utc).isoformat()

        return {
            "status": "FOUND",
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_url": self.BASE_URL,
            "retrieved_at": utc_now,
            "competition_id": competition_id,
            "match_id": str(event.get("id")),
            "home_team": event.get("homeTeam", {}).get("name"),
            "away_team": event.get("awayTeam", {}).get("name"),
            "kickoff_at": event.get("utcDate"),
            "status_detail": event.get("status"),
            "competition": event.get("competition", {}),
            "venue": event.get("venue"),
            "raw_event": event,
        }
