from datetime import date, timedelta
from typing import Any, Dict, Optional

from app.v13_ai_intelligence_engine import http_get, ESPN_BASE


class V13MatchSourceAdapter:
    """
    V1.3 source-neutral match retrieval seam.

    This adapter normalizes source-specific fixture responses into the
    existing match object expected by the protected AI reasoning engine.

    It does not assign source priority and does not modify Pieces 1-9.
    """

    def _name_matches(self, candidate: str, target: str) -> bool:
        c = (candidate or "").lower().strip()
        t = (target or "").lower().strip()
        return bool(c and t and (t in c or c in t))

    def _dates_to_check(self, around_date: Optional[str]) -> list[str]:
        if around_date:
            return [around_date]

        today = date.today()
        return [
            (today + timedelta(days=delta)).strftime("%Y%m%d")
            for delta in range(-3, 15)
        ]

    def find_via_espn(
        self,
        *,
        espn_slug: str,
        team_a: str,
        team_b: str,
        around_date: Optional[str] = None,
    ) -> Dict[str, Any]:

        for match_date in self._dates_to_check(around_date):
            url = f"{ESPN_BASE}/{espn_slug}/scoreboard"

            data, status = http_get(
                url,
                params={"dates": match_date},
            )

            if data is None:
                continue

            for event in data.get("events", []):
                competition = event.get("competitions", [{}])[0]
                competitors = competition.get("competitors", [])

                names = [
                    c.get("team", {}).get("displayName", "")
                    for c in competitors
                ]

                if len(names) != 2:
                    continue

                matched = (
                    self._name_matches(names[0], team_a)
                    and self._name_matches(names[1], team_b)
                ) or (
                    self._name_matches(names[0], team_b)
                    and self._name_matches(names[1], team_a)
                )

                if not matched:
                    continue

                venue = competition.get("venue", {}).get("fullName")

                return {
                    "match_status": "FOUND",
                    "match_id": event.get("id"),
                    "home_team": next(
                        (
                            c.get("team", {}).get("displayName")
                            for c in competitors
                            if c.get("homeAway") == "home"
                        ),
                        None,
                    ),
                    "away_team": next(
                        (
                            c.get("team", {}).get("displayName")
                            for c in competitors
                            if c.get("homeAway") == "away"
                        ),
                        None,
                    ),
                    "kickoff_at": event.get("date"),
                    "match_date": match_date,
                    "venue": venue,
                    "season": data.get("season", {}).get("year"),
                    "status_detail": (
                        competition
                        .get("status", {})
                        .get("type", {})
                        .get("description")
                    ),
                    "source_id": "espn_football",
                    "source_name": "ESPN Soccer",
                    "source_url": url,
                    "raw_event": event,
                }

        return {
            "match_status": "NOT_FOUND",
            "source_id": "espn_football",
            "source_name": "ESPN Soccer",
        }

    def find_match(
        self,
        *,
        espn_slug: str,
        team_a: str,
        team_b: str,
        around_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Current V1.3 implementation.

        ESPN is used here only because its match-query mechanism is already
        verified in the protected AI library. The adapter is the replacement
        seam for additional V1.3 sources; ESPN is not declared authoritative.
        """
        return self.find_via_espn(
            espn_slug=espn_slug,
            team_a=team_a,
            team_b=team_b,
            around_date=around_date,
        )
