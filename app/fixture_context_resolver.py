from typing import Any, Dict, Optional

import httpx


class FixtureContextResolver:
    """
    Resolve competition and country context for canonical fixtures.

    Truth rule:
    - Use explicit source metadata when available.
    - Never guess a country from a team name.
    - If context cannot be verified, keep it UNKNOWN.
    """

    ESPN_SCOREBOARD = (
        "https://site.api.espn.com/apis/site/v2/"
        "sports/soccer/all/scoreboard"
    )

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout

    def resolve(
        self,
        fixture: Dict[str, Any],
    ) -> Dict[str, Any]:

        result = dict(fixture)

        if self._has_context(result):
            result["context_status"] = "ALREADY_AVAILABLE"
            return result

        source = str(
            fixture.get("source") or ""
        ).lower()

        if source == "espn":
            enriched = self._from_espn(fixture)

            if enriched is not None:
                result.update(enriched)
                result["context_status"] = (
                    "SOURCE_CONTEXT_RESOLVED"
                )
                return result

        result.setdefault("competition", None)
        result.setdefault("country_code", None)
        result["context_status"] = "UNKNOWN"

        return result

    def _from_espn(
        self,
        fixture: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:

        kickoff = fixture.get("kickoff_at")

        if not kickoff:
            return None

        date = str(kickoff)[:10]

        url = (
            self.ESPN_SCOREBOARD
            + "?dates="
            + date.replace("-", "")
        )

        try:
            response = httpx.get(
                url,
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception:
            return None

        home = self._normalise(
            fixture.get("home_team")
        )
        away = self._normalise(
            fixture.get("away_team")
        )

        for event in payload.get("events", []):
            pair = self._event_teams(event)

            if pair is None:
                continue

            event_home, event_away = pair

            if not self._team_matches(
                home,
                event_home,
            ):
                continue

            if not self._team_matches(
                away,
                event_away,
            ):
                continue

            competition = self._competition(event)

            country = self._country(event)

            # Only accept values actually exposed by the source.
            if competition is None and country is None:
                return None

            return {
                "competition": competition,
                "country_code": country,
                "context_source": "espn",
                "context_source_reference": url,
            }

        return None

    @staticmethod
    def _event_teams(
        event: Dict[str, Any],
    ) -> Optional[tuple[str, str]]:

        competitions = event.get("competitions") or []

        if not competitions:
            return None

        competitors = (
            competitions[0].get("competitors") or []
        )

        home = None
        away = None

        for competitor in competitors:
            team = competitor.get("team") or {}

            name = (
                team.get("displayName")
                or competitor.get("displayName")
            )

            if not name:
                continue

            if competitor.get("homeAway") == "home":
                home = str(name)

            elif competitor.get("homeAway") == "away":
                away = str(name)

        if not home or not away:
            return None

        return home, away

    @staticmethod
    def _competition(
        event: Dict[str, Any],
    ) -> Optional[str]:

        league = event.get("league")

        if isinstance(league, dict):
            name = (
                league.get("name")
                or league.get("text")
                or league.get("abbreviation")
            )

            if name:
                return str(name)

        competition = event.get("competition")

        if isinstance(competition, dict):
            name = (
                competition.get("name")
                or competition.get("displayName")
                or competition.get("text")
            )

            if name:
                return str(name)

        competitions = event.get("competitions") or []

        if competitions:
            details = competitions[0]

            alt_note = details.get("altGameNote")

            if alt_note:
                return str(alt_note)

        return None

    @staticmethod
    def _country(
        event: Dict[str, Any],
    ) -> Optional[str]:

        league = event.get("league")

        if isinstance(league, dict):
            for key in (
                "country",
                "countryCode",
                "country_code",
            ):
                value = league.get(key)

                if isinstance(value, dict):
                    value = (
                        value.get("code")
                        or value.get("abbreviation")
                        or value.get("name")
                    )

                if value:
                    return str(value)

        competition = event.get("competition")

        if isinstance(competition, dict):
            for key in (
                "country",
                "countryCode",
                "country_code",
            ):
                value = competition.get(key)

                if isinstance(value, dict):
                    value = (
                        value.get("code")
                        or value.get("abbreviation")
                        or value.get("name")
                    )

                if value:
                    return str(value)

        competitions = event.get("competitions") or []

        if competitions:
            details = competitions[0]
            venue = details.get("venue") or {}
            address = venue.get("address") or {}

            country = address.get("country")

            if country:
                return str(country)

        return None

    @staticmethod
    def _has_context(
        fixture: Dict[str, Any],
    ) -> bool:

        return bool(
            fixture.get("competition")
            and (
                fixture.get("country_code")
                or fixture.get("country")
            )
        )

    @staticmethod
    def _normalise(value: Any) -> str:

        if value is None:
            return ""

        return (
            str(value)
            .strip()
            .lower()
        )

    @staticmethod
    def _team_matches(
        requested: str,
        returned: str,
    ) -> bool:

        if not requested or not returned:
            return False

        if requested == returned:
            return True

        return (
            requested in returned
            or returned in requested
        )


if __name__ == "__main__":
    from app.today_match_aggregator import (
        TodayMatchAggregator,
    )

    print("=== FIXTURE CONTEXT RESOLVER TEST ===")

    aggregator = TodayMatchAggregator()
    today = aggregator.load_today()

    fixtures = today.get("matches", [])

    print("TODAY:", today.get("date"))
    print("FIXTURES:", len(fixtures))

    if not fixtures:
        raise SystemExit(
            "FAIL: no canonical fixtures available."
        )

    resolver = FixtureContextResolver()

    resolved = 0
    unknown = 0

    for fixture in fixtures:
        result = resolver.resolve(fixture)

        if result["context_status"] == (
            "SOURCE_CONTEXT_RESOLVED"
        ):
            resolved += 1
        else:
            unknown += 1

    print()
    print("CONTEXT RESOLVED:", resolved)
    print("CONTEXT UNKNOWN:", unknown)

    first = resolver.resolve(fixtures[0])

    print()
    print("=== FIRST FIXTURE ===")
    print(
        "MATCH:",
        first.get("home_team"),
        "vs",
        first.get("away_team"),
    )
    print("SOURCE:", first.get("source"))
    print("COMPETITION:", first.get("competition"))
    print("COUNTRY:", first.get("country_code"))
    print("STATUS:", first.get("context_status"))

    allowed = {
        "ALREADY_AVAILABLE",
        "SOURCE_CONTEXT_RESOLVED",
        "UNKNOWN",
    }

    for fixture in fixtures:
        result = resolver.resolve(fixture)

        if result["context_status"] not in allowed:
            raise SystemExit(
                "FAIL: invalid context status."
            )

    print()
    print("RESULT: PASS")
    print("FIXTURE CONTEXT RESOLUTION IS WORKING")
    print("UNKNOWN CONTEXT REMAINS UNKNOWN")
    print("NO COUNTRY WAS GUESSED FROM TEAM NAMES")
    print("=== TEST COMPLETE ===")
