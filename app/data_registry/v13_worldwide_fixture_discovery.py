from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.data_registry.v1_3_competition_catalogue import (
    V13_COMPETITION_CATALOGUE,
)
from app.data_registry.v1_3_source_registry import (
    V13_COMPETITION_SOURCE_MAP,
    V13_SOURCES,
)


class V13WorldwideFixtureDiscovery:
    """
    V1.3 worldwide fixture discovery.

    Rules:
    - V1.3's 191-competition catalogue is authoritative.
    - V1.3 source mappings are authoritative.
    - ESPN/OpenFoot are NOT global discovery drivers.
    - Only structured/recognizable fixture data is accepted.
    - Unreadable sources remain unavailable; fixtures are never invented.
    """

    EXCLUDED_DISCOVERY_SOURCES = {
        "espn_football",
        "openfoot",
        "openfootball",
    }

    def __init__(self, max_workers: int = 16, timeout: float = 8.0):
        self.max_workers = max_workers
        self.timeout = timeout

    # ---------------------------------------------------------
    # SOURCE ROUTING
    # ---------------------------------------------------------

    def _competition_sources(self, competition_id: str) -> List[Dict[str, Any]]:
        rows = [
            row
            for row in V13_COMPETITION_SOURCE_MAP
            if row.competition_id == competition_id
        ]

        result = []

        for row in rows:
            source_id = row.source_id

            if source_id in self.EXCLUDED_DISCOVERY_SOURCES:
                continue

            source = V13_SOURCES.get(source_id)
            if not source:
                continue

            if "fixture" not in {
                str(x).lower() for x in source.data_classes
            } and "schedule" not in {
                str(x).lower() for x in source.data_classes
            }:
                continue

            result.append(
                {
                    "source_id": source.source_id,
                    "name": source.name,
                    "url": source.base_url,
                    "competition_id": competition_id,
                    "coverage_scope": source.coverage_scope,
                }
            )

        return result

    # ---------------------------------------------------------
    # HTTP
    # ---------------------------------------------------------

    def _retrieve_source(
        self,
        competition_id: str,
        source: Dict[str, Any],
        target_date: str,
    ) -> Dict[str, Any]:

        url = source["url"]

        headers = {
            "User-Agent": (
                "FootballAI-V1.3/1.0 "
                "(worldwide-fixture-discovery)"
            ),
            "Accept": (
                "application/json,text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
        }

        try:
            response = httpx.get(
                url,
                params={"date": target_date},
                headers=headers,
                timeout=self.timeout,
                follow_redirects=True,
            )

            content_type = response.headers.get(
                "content-type", ""
            ).lower()

            return {
                "competition_id": competition_id,
                "source_id": source["source_id"],
                "source_name": source["name"],
                "url": str(response.url),
                "requested_url": url,
                "status_code": response.status_code,
                "content_type": content_type,
                "retrieved_at": datetime.utcnow().isoformat() + "Z",
                "body": response.text[:2_000_000],
                "state": (
                    "AVAILABLE"
                    if response.status_code < 400
                    and response.text.strip()
                    else "UNAVAILABLE"
                ),
            }

        except Exception as exc:
            return {
                "competition_id": competition_id,
                "source_id": source["source_id"],
                "source_name": source["name"],
                "url": url,
                "requested_url": url,
                "status_code": None,
                "content_type": "",
                "retrieved_at": datetime.utcnow().isoformat() + "Z",
                "body": "",
                "state": "UNAVAILABLE",
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # NORMALIZATION HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def _clean(value: Any) -> str:
        if value is None:
            return ""

        value = str(value)
        value = re.sub(r"\s+", " ", value)
        return value.strip()

    @staticmethod
    def _looks_like_team(value: str) -> bool:
        value = value.strip()

        if not value:
            return False

        if len(value) < 2 or len(value) > 80:
            return False

        blocked = {
            "home",
            "away",
            "team",
            "teams",
            "winner",
            "loser",
            "unknown",
            "tbd",
            "tbc",
        }

        return value.lower() not in blocked

    @staticmethod
    def _parse_datetime(value: Any) -> Optional[str]:
        if value is None:
            return None

        text = str(value).strip()

        if not text:
            return None

        # ISO timestamps
        try:
            parsed = datetime.fromisoformat(
                text.replace("Z", "+00:00")
            )
            return parsed.isoformat()
        except Exception:
            pass

        # Unix milliseconds
        if text.isdigit():
            try:
                number = int(text)

                if number > 10_000_000_000:
                    number /= 1000

                return datetime.utcfromtimestamp(number).isoformat() + "Z"
            except Exception:
                return None

        return text

    # ---------------------------------------------------------
    # JSON-LD
    # ---------------------------------------------------------

    def _extract_jsonld(self, html: str) -> List[Dict[str, Any]]:
        documents = []

        pattern = re.compile(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>'
            r"(.*?)"
            r"</script>",
            re.I | re.S,
        )

        for match in pattern.finditer(html):
            raw = match.group(1).strip()

            try:
                data = json.loads(raw)
            except Exception:
                continue

            if isinstance(data, dict):
                documents.append(data)

            elif isinstance(data, list):
                documents.extend(
                    item for item in data if isinstance(item, dict)
                )

        return documents

    def _fixtures_from_jsonld(
        self,
        documents: List[Dict[str, Any]],
        competition_id: str,
        source: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        fixtures = []

        for item in documents:

            item_type = item.get("@type", "")

            if isinstance(item_type, list):
                types = {str(x).lower() for x in item_type}
            else:
                types = {str(item_type).lower()}

            if not (
                "sportsEvent" in item_type
                or "sportsevent" in types
                or "sports event" in types
            ):
                continue

            home = item.get("homeTeam")
            away = item.get("awayTeam")

            if isinstance(home, dict):
                home = (
                    home.get("name")
                    or home.get("alternateName")
                )

            if isinstance(away, dict):
                away = (
                    away.get("name")
                    or away.get("alternateName")
                )

            home = self._clean(home)
            away = self._clean(away)

            if not (
                self._looks_like_team(home)
                and self._looks_like_team(away)
            ):
                continue

            start = (
                item.get("startDate")
                or item.get("startTime")
            )

            fixtures.append(
                self._fixture(
                    competition_id,
                    source,
                    home,
                    away,
                    start,
                    method="JSON_LD_SPORTS_EVENT",
                )
            )

        return fixtures

    # ---------------------------------------------------------
    # COMMON EMBEDDED JSON
    # ---------------------------------------------------------

    def _walk_json(
        self,
        value: Any,
        callback,
        found: List[Dict[str, Any]],
    ) -> None:

        if isinstance(value, dict):
            if callback(value):
                found.append(value)

            for child in value.values():
                self._walk_json(child, callback, found)

        elif isinstance(value, list):
            for child in value:
                self._walk_json(child, callback, found)

    def _fixture_candidate(self, obj: Dict[str, Any]) -> bool:
        keys = {str(k).lower() for k in obj.keys()}

        home_keys = {
            "hometeam",
            "home_team",
            "home",
            "hometeamname",
        }

        away_keys = {
            "awayteam",
            "away_team",
            "away",
            "awayteamname",
        }

        time_keys = {
            "startdate",
            "starttime",
            "kickoff",
            "kickofftime",
            "date",
            "datetime",
            "scheduled",
        }

        return (
            bool(keys & home_keys)
            and bool(keys & away_keys)
            and bool(keys & time_keys)
        )

    def _fixtures_from_embedded_json(
        self,
        html: str,
        competition_id: str,
        source: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        found: List[Dict[str, Any]] = []

        patterns = [
            r'<script[^>]*type=["\']application/json["\'][^>]*>'
            r"(.*?)</script>",
            r'<script[^>]*>(.*?)</script>',
        ]

        for pattern in patterns:

            for match in re.finditer(
                pattern,
                html,
                re.I | re.S,
            ):
                raw = match.group(1).strip()

                if len(raw) < 2:
                    continue

                try:
                    data = json.loads(raw)
                except Exception:
                    continue

                self._walk_json(
                    data,
                    self._fixture_candidate,
                    found,
                )

        fixtures = []

        for obj in found:

            def get_any(names):
                for name in names:
                    if name in obj:
                        return obj[name]

                    for key in obj:
                        if str(key).lower() == name.lower():
                            return obj[key]

                return None

            home = get_any(
                [
                    "homeTeam",
                    "home_team",
                    "home",
                    "homeTeamName",
                ]
            )

            away = get_any(
                [
                    "awayTeam",
                    "away_team",
                    "away",
                    "awayTeamName",
                ]
            )

            if isinstance(home, dict):
                home = home.get("name") or home.get("displayName")

            if isinstance(away, dict):
                away = away.get("name") or away.get("displayName")

            home = self._clean(home)
            away = self._clean(away)

            if not (
                self._looks_like_team(home)
                and self._looks_like_team(away)
            ):
                continue

            kickoff = get_any(
                [
                    "startDate",
                    "startTime",
                    "kickoff",
                    "kickoffTime",
                    "date",
                    "datetime",
                    "scheduled",
                ]
            )

            fixtures.append(
                self._fixture(
                    competition_id,
                    source,
                    home,
                    away,
                    kickoff,
                    method="EMBEDDED_JSON",
                )
            )

        return fixtures

    # ---------------------------------------------------------
    # GENERIC HTML FALLBACK
    # ---------------------------------------------------------

    def _fixtures_from_html(
        self,
        html: str,
        competition_id: str,
        source: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        """
        Conservative HTML fallback.

        We only accept explicit 'Home Team vs Away Team'-style
        structures. We never manufacture a fixture from arbitrary
        page text.
        """

        fixtures = []

        pattern = re.compile(
            r"""
            (?P<home>[A-Za-zÀ-ÖØ-öø-ÿ0-9.'’&()\- ]{2,70})
            \s+
            (?:vs\.?|v\.?|versus)
            \s+
            (?P<away>[A-Za-zÀ-ÖØ-öø-ÿ0-9.'’&()\- ]{2,70})
            """,
            re.I | re.X,
        )

        for match in pattern.finditer(html):

            home = self._clean(match.group("home"))
            away = self._clean(match.group("away"))

            if not (
                self._looks_like_team(home)
                and self._looks_like_team(away)
            ):
                continue

            # Avoid extracting prose fragments.
            if len(home.split()) > 8 or len(away.split()) > 8:
                continue

            fixtures.append(
                self._fixture(
                    competition_id,
                    source,
                    home,
                    away,
                    None,
                    method="EXPLICIT_HTML_PAIR",
                )
            )

        return fixtures

    # ---------------------------------------------------------
    # FIXTURE OBJECT
    # ---------------------------------------------------------

    def _fixture(
        self,
        competition_id: str,
        source: Dict[str, Any],
        home: str,
        away: str,
        kickoff: Any,
        method: str,
    ) -> Dict[str, Any]:

        return {
            "competition_id": competition_id,
            "home_team": home,
            "away_team": away,
            "kickoff_at": self._parse_datetime(kickoff),
            "status": "STATUS_SCHEDULED",
            "fixture_identity_status": "UNVERIFIED",
            "discovery_source_id": source["source_id"],
            "discovery_source_name": source["source_name"],
            "discovery_url": source["url"],
            "discovery_method": method,
            "retrieved_at": datetime.utcnow().isoformat() + "Z",
            "evidence_status": "UNVERIFIED",
        }

    # ---------------------------------------------------------
    # SOURCE EXTRACTION
    # ---------------------------------------------------------

    def _extract_fixtures(
        self,
        result: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        if result.get("state") != "AVAILABLE":
            return []

        body = result.get("body") or ""

        source = {
            "source_id": result["source_id"],
            "source_name": result["source_name"],
            "url": result["url"],
        }

        competition_id = result["competition_id"]

        fixtures: List[Dict[str, Any]] = []

        # 1. JSON response
        content_type = result.get("content_type", "")

        if "json" in content_type:
            try:
                data = json.loads(body)

                candidates: List[Dict[str, Any]] = []
                self._walk_json(
                    data,
                    self._fixture_candidate,
                    candidates,
                )

                for obj in candidates:
                    def get_any(names):
                        for name in names:
                            for key in obj:
                                if str(key).lower() == name.lower():
                                    return obj[key]
                        return None

                    home = get_any(
                        ["homeTeam", "home_team", "home"]
                    )
                    away = get_any(
                        ["awayTeam", "away_team", "away"]
                    )

                    if isinstance(home, dict):
                        home = (
                            home.get("name")
                            or home.get("displayName")
                        )

                    if isinstance(away, dict):
                        away = (
                            away.get("name")
                            or away.get("displayName")
                        )

                    home = self._clean(home)
                    away = self._clean(away)

                    if not (
                        self._looks_like_team(home)
                        and self._looks_like_team(away)
                    ):
                        continue

                    kickoff = get_any(
                        [
                            "startDate",
                            "startTime",
                            "kickoff",
                            "kickoffTime",
                            "date",
                            "datetime",
                            "scheduled",
                        ]
                    )

                    fixtures.append(
                        self._fixture(
                            competition_id,
                            source,
                            home,
                            away,
                            kickoff,
                            "JSON_FIXTURE_OBJECT",
                        )
                    )

            except Exception:
                pass

        # 2. JSON-LD
        fixtures.extend(
            self._fixtures_from_jsonld(
                self._extract_jsonld(body),
                competition_id,
                source,
            )
        )

        # 3. Embedded application JSON
        fixtures.extend(
            self._fixtures_from_embedded_json(
                body,
                competition_id,
                source,
            )
        )

        # 4. Conservative HTML
        if not fixtures:
            fixtures.extend(
                self._fixtures_from_html(
                    body,
                    competition_id,
                    source,
                )
            )

        return fixtures

    # ---------------------------------------------------------
    # DEDUPLICATION
    # ---------------------------------------------------------

    @staticmethod
    def _fixture_key(item: Dict[str, Any]) -> Tuple[str, str, str, str]:
        return (
            item.get("competition_id", ""),
            item.get("home_team", "").strip().lower(),
            item.get("away_team", "").strip().lower(),
            item.get("kickoff_at") or "",
        )

    def _deduplicate(
        self,
        fixtures: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        seen = set()
        output = []

        for fixture in fixtures:
            key = self._fixture_key(fixture)

            if key in seen:
                continue

            seen.add(key)
            output.append(fixture)

        return output

    # ---------------------------------------------------------
    # WORLDWIDE DISCOVERY
    # ---------------------------------------------------------

    def discover(
        self,
        target_date: Optional[str] = None,
    ) -> Dict[str, Any]:

        target_date = target_date or date.today().isoformat()

        jobs = []

        for competition in V13_COMPETITION_CATALOGUE:

            competition_id = competition["competition_id"]

            for source in self._competition_sources(
                competition_id
            ):
                jobs.append(
                    (
                        competition_id,
                        source,
                    )
                )

        source_results = []
        fixtures = []

        with ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:

            future_map = {
                executor.submit(
                    self._retrieve_source,
                    competition_id,
                    source,
                    target_date,
                ): (
                    competition_id,
                    source["source_id"],
                )
                for competition_id, source in jobs
            }

            for future in as_completed(future_map):
                try:
                    result = future.result()
                except Exception as exc:
                    competition_id, source_id = future_map[future]

                    result = {
                        "competition_id": competition_id,
                        "source_id": source_id,
                        "state": "UNAVAILABLE",
                        "error": str(exc),
                    }

                source_results.append(result)

                if result.get("state") == "AVAILABLE":
                    fixtures.extend(
                        self._extract_fixtures(result)
                    )

        fixtures = self._deduplicate(fixtures)

        return {
            "status": "COMPLETED",
            "target_date": target_date,
            "competition_count": len(
                V13_COMPETITION_CATALOGUE
            ),
            "source_jobs": len(jobs),
            "sources_available": sum(
                1
                for item in source_results
                if item.get("state") == "AVAILABLE"
            ),
            "sources_unavailable": sum(
                1
                for item in source_results
                if item.get("state") != "AVAILABLE"
            ),
            "fixture_count": len(fixtures),
            "matches": fixtures,
            "source_results": source_results,
            "coverage_status": (
                "AVAILABLE"
                if fixtures
                else "INSUFFICIENT_EVIDENCE"
            ),
        }


def discover_worldwide_fixtures(
    target_date: Optional[str] = None,
) -> Dict[str, Any]:

    return V13WorldwideFixtureDiscovery().discover(
        target_date=target_date
    )
