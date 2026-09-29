from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from app.v13_ai_intelligence_engine import http_get
from app.data_registry.v13_global_match_discovery import V13MatchDiscoveryProvider


ESPN_GLOBAL_SCOREBOARD = (
    "https://site.api.espn.com/apis/site/v2/sports/soccer/all/scoreboard"
)


class V13ESPNMatchDiscovery(V13MatchDiscoveryProvider):
    """ESPN global soccer discovery provider.

    ESPN is one external evidence source only.
    It is not authoritative and does not define the V1.3 competition universe.
    """

    source_id = "espn_football"
    source_name = "ESPN Soccer"

    @staticmethod
    def _normalise(value: str) -> str:
        import re

        value = (value or "").lower()
        value = re.sub(r"[^a-z0-9]+", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    @classmethod
    def _matches(cls, candidate: str, target: str) -> bool:
        c = cls._normalise(candidate)
        t = cls._normalise(target)
        return bool(c and t and (t in c or c in t))

    def discover(
        self,
        *,
        team_a: str,
        team_b: str,
        match_date: Optional[str],
        competition_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        if not match_date:
            return {
                "status": "INSUFFICIENT_EVIDENCE",
                "source_id": self.source_id,
                "source_name": self.source_name,
                "reason": "A match date is required for global ESPN discovery.",
            }

        try:
            dt = datetime.fromisoformat(match_date.replace("Z", "+00:00"))
            date_value = dt.strftime("%Y%m%d")
        except ValueError:
            date_value = match_date.replace("-", "")[:8]

        url = ESPN_GLOBAL_SCOREBOARD

        data, status = http_get(
            url,
            params={"dates": date_value},
        )

        if not data or status != 200:
            return {
                "status": "SOURCE_UNAVAILABLE",
                "source_id": self.source_id,
                "source_name": self.source_name,
                "source_url": url,
                "status_code": status,
            }

        for event in data.get("events", []):
            competition = (event.get("competitions") or [{}])[0]
            competitors = competition.get("competitors", [])

            if len(competitors) != 2:
                continue

            names = [
                c.get("team", {}).get("displayName", "")
                for c in competitors
            ]

            if not (
                (
                    self._matches(names[0], team_a)
                    and self._matches(names[1], team_b)
                )
                or
                (
                    self._matches(names[0], team_b)
                    and self._matches(names[1], team_a)
                )
            ):
                continue

            home = next(
                (
                    c.get("team", {}).get("displayName")
                    for c in competitors
                    if c.get("homeAway") == "home"
                ),
                None,
            )

            away = next(
                (
                    c.get("team", {}).get("displayName")
                    for c in competitors
                    if c.get("homeAway") == "away"
                ),
                None,
            )

            venue = competition.get("venue", {}).get("fullName")

            return {
                "status": "FOUND",
                "source_id": self.source_id,
                "source_name": self.source_name,
                "source_url": url,
                "match_id": event.get("id"),
                "home_team": home,
                "away_team": away,
                "kickoff_at": event.get("date"),
                "venue": venue,
                "competition_id": competition_id,
                "raw_event": event,
            }

        return {
            "status": "NOT_FOUND",
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_url": url,
            "competition_id": competition_id,
        }
