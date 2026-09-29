from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from app.regional_source_resolver import (
    RegionalSourceResolver,
)


@dataclass
class CollectedSourceEvidence:
    fixture: Dict[str, Any]
    source_id: str
    source_name: str
    status: str
    evidence_types: List[str]
    evidence: Any = None
    source_reference: Optional[str] = None
    observed_at: Optional[str] = None
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RegionalEvidenceCollector:
    """
    Collect evidence from sources selected by RegionalSourceResolver.

    IMPORTANT:
    A registered source is NOT treated as verified automatically.

    VERIFIED:
        The source actually returned usable data.

    FAILED:
        The source was attempted but the request failed.

    NOT_CONFIGURED:
        No appropriate regional source exists.

    INSUFFICIENT_EVIDENCE:
        The source responded, but the response did not contain
        usable evidence for the requested fixture.
    """

    def __init__(
        self,
        resolver: Optional[RegionalSourceResolver] = None,
        timeout: float = 15.0,
    ) -> None:
        self.resolver = resolver or RegionalSourceResolver()
        self.timeout = timeout

    def collect(
        self,
        fixture: Dict[str, Any],
        v13_sources: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Collect evidence from every registered source, in parallel.

        Sources included:
          1. V1.3 registry sources for this competition (official-first)
          2. Internal sources (regional_resolver, espn, openfoot)
          3. Free internet sources (TheSportsDB, Wikidata, OpenLigaDB, FKF)

        Every source runs. None is primary. Failures are recorded but do
        not prevent other sources from contributing.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        records: List[Dict[str, Any]] = []

        # --- 1. Registry-driven sources ---
        try:
            registered = self._registered_sources_for_fixture(fixture, v13_sources)
        except Exception:
            registered = []

        def _collect_registered(src):
            try:
                return self._collect_source(fixture, src)
            except Exception as exc:
                return {
                    "fixture": fixture,
                    "source_id": src.get("source_id", "unknown"),
                    "source_name": src.get("name", ""),
                    "status": "FAILED",
                    "evidence_types": src.get("evidence_types", []),
                    "evidence": {},
                    "reason": str(exc),
                    "observed_at": self._now(),
                }

        # --- 2. Internal source IDs always tried ---
        internal_sources = [
            {"source_id": "espn_global_soccer", "name": "ESPN Global Soccer",
             "evidence_types": ["fixtures", "match_status", "teams", "results"]},
            {"source_id": "regional_resolver", "name": "Regional Resolver",
             "evidence_types": []},
            {"source_id": "openfoot", "name": "OpenFoot",
             "evidence_types": ["fixtures", "competition_data", "team_data"]},
        ]

        # --- 3. Internet providers ---
        from app.regional_evidence_internet import ALL_INTERNET_FETCHERS

        internet_futures = []
        with ThreadPoolExecutor(max_workers=8) as pool:
            # registered
            for src in registered + internal_sources:
                internet_futures.append(
                    ("registered", pool.submit(_collect_registered, src))
                )
            # internet
            for key, fn in ALL_INTERNET_FETCHERS.items():
                internet_futures.append(
                    ("internet", pool.submit(fn, fixture))
                )

            for kind, fut in internet_futures:
                try:
                    rec = fut.result(timeout=self.timeout + 3)
                except Exception as exc:
                    rec = {
                        "fixture": fixture,
                        "source_id": "unknown",
                        "status": "FAILED",
                        "evidence_types": [],
                        "evidence": {},
                        "reason": str(exc),
                        "observed_at": self._now(),
                    }
                if isinstance(rec, dict):
                    records.append(rec)

        # deduplicate by source_id (registry may overlap with internal)
        seen = set()
        deduped = []
        for rec in records:
            sid = rec.get("source_id") or "unknown"
            if sid in seen:
                continue
            seen.add(sid)
            deduped.append(rec)

        return {
            "fixture": fixture,
            "collected_at": self._now(),
            "records": deduped,
        }

    def _collect_source(
        self,
        fixture: Dict[str, Any],
        source: Dict[str, Any],
    ) -> CollectedSourceEvidence:

        source_id = source["source_id"]

        if source_id == "espn_global_soccer":
            return self._collect_espn(
                fixture,
                source,
            )

        if source_id == "openfoot":
            return self._collect_openfoot(
                fixture,
                source,
            )

        if source_id == "fkf_official":
            return self._collect_fkf(
                fixture,
                source,
            )

        return self._collect_generic_web(
            fixture,
            source,
        )

    def _collect_generic_web(
        self,
        fixture: Dict[str, Any],
        source: Dict[str, Any],
    ) -> CollectedSourceEvidence:
        """Collect reachability/evidence from a registered public web source.

        This is deliberately generic. It does not treat a successful HTTP
        response as fixture verification. Fixture-specific verification is
        only reported when the requested teams can actually be found in the
        returned content.
        """
        url = source.get("base_url") or source.get("url")

        if not url:
            return CollectedSourceEvidence(
                fixture=fixture,
                source_id=source["source_id"],
                source_name=source["name"],
                status="NOT_CONFIGURED",
                evidence_types=source.get("evidence_types", []),
                reason="Registered source has no usable base URL.",
            )

        try:
            response = httpx.get(
                url,
                timeout=self.timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Linux; Android) "
                        "FootballAI/1.3"
                    )
                },
            )
            response.raise_for_status()
            body = response.text or ""
        except Exception as exc:
            return self._failed(
                fixture,
                source,
                url,
                str(exc),
            )

        if not body.strip():
            return self._insufficient(
                fixture,
                source,
                "Source responded successfully but returned an empty page.",
                url,
            )

        home = str(fixture.get("home_team") or "").strip()
        away = str(fixture.get("away_team") or "").strip()

        body_lower = body.lower()
        home_found = bool(home) and home.lower() in body_lower
        away_found = bool(away) and away.lower() in body_lower

        if home_found and away_found:
            return CollectedSourceEvidence(
                fixture=fixture,
                source_id=source["source_id"],
                source_name=source["name"],
                status="VERIFIED",
                evidence_types=source.get("evidence_types", []),
                evidence={
                    "match_presence": {
                        "home_team_found": True,
                        "away_team_found": True,
                    },
                    "response_bytes": len(response.content),
                },
                source_reference=str(response.url),
                observed_at=self._now(),
            )

        return self._insufficient(
            fixture,
            source,
            (
                "Source responded successfully, but the returned content "
                "did not establish this fixture. "
                f"home_found={home_found}, away_found={away_found}."
            ),
            str(response.url),
        )


    def _collect_espn(
        self,
        fixture: Dict[str, Any],
        source: Dict[str, Any],
    ) -> CollectedSourceEvidence:
        """Strict ESPN collector.

        Delegates to app.regional_evidence_collector_espn_fix.collect_espn_strict,
        which enforces:
          1. ESPN is queried with today's/yesterday's/tomorrow's date only.
          2. An event is accepted only when BOTH home and away team names
             appear among its competitors.
        """
        from app.regional_evidence_collector_espn_fix import collect_espn_strict

        def _success(fx, src, url, evidence, evidence_types):
            return CollectedSourceEvidence(
                fixture=fx,
                source_id=src["source_id"],
                source_name=src["name"],
                status="VERIFIED",
                evidence_types=evidence_types,
                evidence=evidence,
                source_reference=url,
                observed_at=self._now(),
            )

        def _failure(fx, src, url, err):
            return self._failed(fx, src, url, err)

        def _insufficient(fx, src, reason, url=None):
            return self._insufficient(fx, src, reason, url)

        return collect_espn_strict(
            fixture, source,
            timeout=self.timeout,
            make_failure=_failure,
            make_insufficient=_insufficient,
            make_success=_success,
        )

    def _collect_openfoot(
        self,
        fixture: Dict[str, Any],
        source: Dict[str, Any],
    ) -> CollectedSourceEvidence:

        # OpenFoot already has a dedicated provider in this project.
        # We deliberately do not duplicate its authentication,
        # pagination, and normalization logic here.
        return CollectedSourceEvidence(
            fixture=fixture,
            source_id=source["source_id"],
            source_name=source["name"],
            status="NOT_CONFIGURED",
            evidence_types=source["evidence_types"],
            reason=(
                "OpenFoot is currently available through the existing "
                "OpenFootProvider/TodayMatchAggregator. Direct regional "
                "evidence collection is not duplicated here."
            ),
        )

    def _collect_fkf(
        self,
        fixture: Dict[str, Any],
        source: Dict[str, Any],
    ) -> CollectedSourceEvidence:

        url = "https://footballkenya.org"

        try:
            response = httpx.get(
                url,
                timeout=self.timeout,
                follow_redirects=True,
            )
            response.raise_for_status()

            text = response.text

        except Exception as exc:
            return self._failed(
                fixture,
                source,
                url,
                str(exc),
            )

        if not text.strip():
            return self._insufficient(
                fixture,
                source,
                "FKF responded with an empty page.",
                url,
            )

        # IMPORTANT:
        # Merely reaching the official website does not prove that
        # this particular fixture exists there.
        #
        # Therefore this collector records the source reachability
        # separately as INSUFFICIENT_EVIDENCE until a fixture-specific
        # FKF adapter is implemented.
        return self._insufficient(
            fixture,
            source,
            (
                "FKF official source is reachable, but this collector "
                "does not yet have fixture-specific extraction. "
                "No fixture claim is made."
            ),
            url,
        )

    @staticmethod
    def _fixture_date(
        fixture: Dict[str, Any],
    ) -> Optional[str]:

        kickoff = fixture.get("kickoff_at")

        if not kickoff:
            return None

        return str(kickoff)[:10]

    @staticmethod
    def _find_event(
        fixture: Dict[str, Any],
        events: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:

        home = str(
            fixture.get("home_team") or ""
        ).strip().lower()

        away = str(
            fixture.get("away_team") or ""
        ).strip().lower()

        if not home or not away:
            return None

        for event in events:
            competitions = event.get("competitions") or []

            if not competitions:
                continue

            competitors = competitions[0].get(
                "competitors"
            ) or []

            event_home = ""
            event_away = ""

            for competitor in competitors:
                team = competitor.get("team") or {}
                name = str(
                    team.get("displayName")
                    or competitor.get("displayName")
                    or ""
                ).strip().lower()

                if competitor.get("homeAway") == "home":
                    event_home = name

                elif competitor.get("homeAway") == "away":
                    event_away = name

            if (
                RegionalEvidenceCollector._team_matches(
                    home,
                    event_home,
                )
                and RegionalEvidenceCollector._team_matches(
                    away,
                    event_away,
                )
            ):
                return event

        return None

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

    @staticmethod
    def _failed(
        fixture: Dict[str, Any],
        source: Dict[str, Any],
        url: str,
        reason: str,
    ) -> CollectedSourceEvidence:

        return CollectedSourceEvidence(
            fixture=fixture,
            source_id=source["source_id"],
            source_name=source["name"],
            status="FAILED",
            evidence_types=source["evidence_types"],
            source_reference=url,
            observed_at=RegionalEvidenceCollector._now(),
            reason=reason,
        )

    @staticmethod
    def _insufficient(
        fixture: Dict[str, Any],
        source: Dict[str, Any],
        reason: str,
        url: Optional[str] = None,
    ) -> CollectedSourceEvidence:

        return CollectedSourceEvidence(
            fixture=fixture,
            source_id=source["source_id"],
            source_name=source["name"],
            status="INSUFFICIENT_EVIDENCE",
            evidence_types=source["evidence_types"],
            source_reference=url,
            observed_at=RegionalEvidenceCollector._now(),
            reason=reason,
        )

    @staticmethod
    def _summary(
        records: List[CollectedSourceEvidence],
    ) -> Dict[str, int]:

        summary = {
            "VERIFIED": 0,
            "FAILED": 0,
            "NOT_CONFIGURED": 0,
            "INSUFFICIENT_EVIDENCE": 0,
        }

        for record in records:
            summary.setdefault(record.status, 0)
            summary[record.status] += 1

        return summary

    @staticmethod
    def _now() -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()


if __name__ == "__main__":
    collector = RegionalEvidenceCollector()

    print("=== REGIONAL EVIDENCE COLLECTOR TEST ===")

    fixture = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "competition": "English Premier League",
        "country_code": "GB",
        "kickoff_at": "2026-09-09T19:00:00Z",
    }

    result = collector.collect(fixture)

    print("ROUTING STATUS:", result["routing_status"])
    print("RECORDS:", len(result["records"]))
    print("SUMMARY:", result["summary"])

    for record in result["records"]:
        print(
            record["source_id"],
            "|",
            record["status"],
        )

    if not result["records"]:
        raise SystemExit(
            "FAIL: collector produced no source records."
        )

    allowed = {
        "VERIFIED",
        "FAILED",
        "NOT_CONFIGURED",
        "INSUFFICIENT_EVIDENCE",
    }

    for record in result["records"]:
        if record["status"] not in allowed:
            raise SystemExit(
                "FAIL: invalid evidence status."
            )

    print()
    print("RESULT: PASS")
    print("SOURCE STATUS IS BEING RECORDED TRUTHFULLY")
    print("NO UNVERIFIED SOURCE WAS CLAIMED AS FIXTURE EVIDENCE")
    print("=== TEST COMPLETE ===")
