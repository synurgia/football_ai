from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.data_providers.openfoot_provider import OpenFootProvider


class TodayMatchAggregator:
    """
    Aggregate today's football fixtures from multiple independent sources.

    This layer is for fixture discovery only.
    It does not modify Pieces 1-9 or the V1.2 question framework.

    Coverage is never assumed to be complete merely because a source
    returned data.
    """

    ESPN_URL = (
        "https://site.api.espn.com/apis/site/v2/"
        "sports/soccer/all/scoreboard"
    )

    def __init__(
        self,
        openfoot_provider: Optional[OpenFootProvider] = None,
    ) -> None:
        self.openfoot = openfoot_provider or OpenFootProvider()

    def load_today(
        self,
        target_date: Optional[str] = None,
    ) -> Dict[str, Any]:

        target_date = target_date or date.today().isoformat()

        source_results: Dict[str, Dict[str, Any]] = {}

        # ------------------------------------------------------------
        # SOURCE 1: OPENFOOT
        # ------------------------------------------------------------
        try:
            raw_openfoot = self.openfoot.get_all_matches(
                date=target_date
            )

            openfoot_meta = dict(
                getattr(
                    self.openfoot,
                    "last_matches_meta",
                    {},
                )
                or {}
            )

            openfoot_matches = [
                self._normalize_openfoot_match(match)
                for match in raw_openfoot
                if isinstance(match, dict)
            ]

            retrieval = (
                openfoot_meta.get("retrieval", {})
                or {}
            )

            source_results["openfoot"] = {
                "status": "SUCCESS",
                "matches": openfoot_matches,
                "returned_count": len(openfoot_matches),
                "reported_total": openfoot_meta.get(
                    "total_count"
                ),
                "coverage_complete": retrieval.get(
                    "complete"
                ),
                "retrieval": retrieval,
            }

        except Exception as exc:
            source_results["openfoot"] = {
                "status": "FAILED",
                "matches": [],
                "returned_count": 0,
                "reported_total": None,
                "coverage_complete": False,
                "error": f"{type(exc).__name__}: {exc}",
            }

        # ------------------------------------------------------------
        # SOURCE 2: ESPN PUBLIC SOCCER SCOREBOARD
        # ------------------------------------------------------------
        try:
            compact_date = target_date.replace("-", "")

            response = httpx.get(
                self.ESPN_URL,
                params={"dates": compact_date},
                timeout=30.0,
                follow_redirects=True,
            )

            response.raise_for_status()

            body = response.json()

            events = body.get("events", [])

            if not isinstance(events, list):
                raise ValueError(
                    "ESPN did not return a valid events list."
                )

            espn_matches = [
                self._normalize_espn_event(event)
                for event in events
                if isinstance(event, dict)
            ]

            espn_matches = [
                match
                for match in espn_matches
                if match["home_team"]
                and match["away_team"]
            ]

            source_results["espn"] = {
                "status": "SUCCESS",
                "matches": espn_matches,
                "returned_count": len(espn_matches),
                "reported_total": len(espn_matches),
                # ESPN's public endpoint does not establish that
                # this is the complete worldwide football universe.
                "coverage_complete": None,
                "coverage_note": (
                    "Public ESPN soccer scoreboard returned "
                    "these events; worldwide completeness is "
                    "not claimed."
                ),
            }

        except Exception as exc:
            source_results["espn"] = {
                "status": "FAILED",
                "matches": [],
                "returned_count": 0,
                "reported_total": None,
                "coverage_complete": False,
                "error": f"{type(exc).__name__}: {exc}",
            }

        # ------------------------------------------------------------
        # MERGE + DEDUPLICATE
        # ------------------------------------------------------------
        all_source_matches: List[Dict[str, Any]] = []

        for source_name, result in source_results.items():
            for match in result["matches"]:

                # Never allow an incomplete fixture into the
                # canonical today's-match dataset.
                if not self._valid_fixture(match):
                    continue

                enriched = dict(match)
                enriched["discovery_sources"] = [
                    source_name
                ]
                all_source_matches.append(enriched)

        unique_matches: List[Dict[str, Any]] = []
        key_to_index: Dict[
            Tuple[str, str, str],
            int,
        ] = {}

        duplicate_count = 0

        for match in all_source_matches:

            key = self._fixture_key(match)

            if key in key_to_index:

                duplicate_count += 1

                existing = unique_matches[
                    key_to_index[key]
                ]

                sources = existing.get(
                    "discovery_sources",
                    [],
                )

                for source in match.get(
                    "discovery_sources",
                    [],
                ):
                    if source not in sources:
                        sources.append(source)

                existing["discovery_sources"] = sources

            else:
                key_to_index[key] = len(
                    unique_matches
                )
                unique_matches.append(match)

        unique_matches.sort(
            key=lambda item: (
                item.get("kickoff_at") or "",
                item.get("home_team") or "",
                item.get("away_team") or "",
            )
        )

        successful_sources = [
            source
            for source, result in source_results.items()
            if result["status"] == "SUCCESS"
        ]

        failed_sources = [
            source
            for source, result in source_results.items()
            if result["status"] != "SUCCESS"
        ]

        coverage_status = self._coverage_status(
            source_results
        )

        return {
            "date": target_date,
            "matches": unique_matches,
            "unique_match_count": len(unique_matches),
            "duplicate_count": duplicate_count,
            "source_results": source_results,
            "successful_sources": successful_sources,
            "failed_sources": failed_sources,
            "coverage_status": coverage_status,
            "coverage_note": (
                "Aggregated coverage from configured sources. "
                "This does not claim worldwide completeness "
                "unless a source explicitly establishes it."
            ),
        }

    @staticmethod
    def _normalize_openfoot_match(
        match: Dict[str, Any],
    ) -> Dict[str, Any]:

        return {
            "source": "openfoot",
            "source_match_id": match.get(
                "id"
            ) or match.get(
                "source_match_id"
            ),
            "competition": match.get(
                "competition"
            ),
            "season": match.get("season"),
            "kickoff_at": match.get(
                "kickoff_at"
            ),
            "home_team": match.get(
                "home_team"
            ),
            "away_team": match.get(
                "away_team"
            ),
            "status": match.get("status"),
            "raw_source_refs": match.get(
                "source_refs"
            ),
        }

    @staticmethod
    def _normalize_espn_event(
        event: Dict[str, Any],
    ) -> Dict[str, Any]:

        competitions = (
            event.get("competitions")
            or []
        )

        competition = (
            competitions[0]
            if competitions
            else {}
        )

        competitors = (
            competition.get("competitors")
            or []
        )

        home = next(
            (
                item
                for item in competitors
                if item.get("homeAway") == "home"
            ),
            {},
        )

        away = next(
            (
                item
                for item in competitors
                if item.get("homeAway") == "away"
            ),
            {},
        )

        home_team = (
            home.get("team", {})
            or {}
        )

        away_team = (
            away.get("team", {})
            or {}
        )

        league = (
            event.get("league")
            or {}
        )

        season = (
            event.get("season")
            or {}
        )

        competition_name = (
            league.get("name")
            or competition.get("altGameNote")
            or competition.get("name")
        )

        return {
            "source": "espn",
            "source_match_id": event.get(
                "id"
            ),
            "competition": competition_name,
            "season": (
                str(season.get("year"))
                if season.get("year") is not None
                else None
            ),
            "kickoff_at": event.get(
                "date"
            ),
            "home_team": home_team.get(
                "displayName"
            ),
            "away_team": away_team.get(
                "displayName"
            ),
            "status": (
                event.get("status", {})
                .get("type", {})
                .get("name")
            ),
            "raw_source_refs": {
                "espn_event_id": event.get(
                    "id"
                ),
            },
        }

    @staticmethod
    def _valid_fixture(
        match: Dict[str, Any],
    ) -> bool:
        """
        Accept only records with the minimum identity required
        for a real football fixture.

        This prevents malformed provider records from entering
        the canonical dataset.
        """
        home = str(
            match.get("home_team") or ""
        ).strip()

        away = str(
            match.get("away_team") or ""
        ).strip()

        kickoff = str(
            match.get("kickoff_at") or ""
        ).strip()

        if not home or not away or not kickoff:
            return False

        if home.lower() in {"none", "null"}:
            return False

        if away.lower() in {"none", "null"}:
            return False

        if kickoff.lower() in {"none", "null"}:
            return False

        return True

    @staticmethod
    def _fixture_key(
        match: Dict[str, Any],
    ) -> Tuple[str, str, str]:

        home = (
            str(match.get("home_team") or "")
            .strip()
            .lower()
        )

        away = (
            str(match.get("away_team") or "")
            .strip()
            .lower()
        )

        kickoff = (
            str(match.get("kickoff_at") or "")
            .strip()
        )

        return (
            home,
            away,
            kickoff,
        )

    @staticmethod
    def _coverage_status(
        source_results: Dict[str, Dict[str, Any]],
    ) -> str:

        if not source_results:
            return "NO_SOURCES"

        successful = [
            result
            for result in source_results.values()
            if result["status"] == "SUCCESS"
        ]

        if not successful:
            return "FAILED"

        # We deliberately do not call the combined worldwide
        # dataset COMPLETE merely because sources responded.
        explicit_complete = any(
            result.get("coverage_complete") is True
            for result in successful
        )

        if explicit_complete:
            return "SOURCE_VERIFIED_COMPLETE"

        if any(
            result.get("coverage_complete") is False
            for result in successful
        ):
            return "PARTIAL"

        return "UNKNOWN_WORLDWIDE_COVERAGE"
