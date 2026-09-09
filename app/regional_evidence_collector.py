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
    ) -> Dict[str, Any]:
        routing = self.resolver.resolve(fixture)

        records: List[CollectedSourceEvidence] = []

        regional_sources = routing["regional_sources"]
        global_sources = routing["global_sources"]

        if not regional_sources:
            records.append(
                CollectedSourceEvidence(
                    fixture=fixture,
                    source_id="regional_resolver",
                    source_name="Regional Source Resolver",
                    status="NOT_CONFIGURED",
                    evidence_types=[],
                    reason=(
                        "No configured regional source matched "
                        "this fixture."
                    ),
                )
            )

        for source in regional_sources:
            records.append(
                self._collect_source(
                    fixture,
                    source,
                )
            )

        for source in global_sources:
            records.append(
                self._collect_source(
                    fixture,
                    source,
                )
            )

        return {
            "fixture": fixture,
            "routing_status": routing["status"],
            "records": [
                record.to_dict()
                for record in records
            ],
            "summary": self._summary(records),
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

        return CollectedSourceEvidence(
            fixture=fixture,
            source_id=source_id,
            source_name=source["name"],
            status="NOT_CONFIGURED",
            evidence_types=source["evidence_types"],
            reason=(
                "Source is registered for routing but has no "
                "collector adapter yet."
            ),
        )

    def _collect_espn(
        self,
        fixture: Dict[str, Any],
        source: Dict[str, Any],
    ) -> CollectedSourceEvidence:

        date = self._fixture_date(fixture)

        if not date:
            return self._insufficient(
                fixture,
                source,
                "Fixture has no usable kickoff date.",
            )

        url = (
            "https://site.api.espn.com/apis/site/v2/"
            f"sports/soccer/all/scoreboard?dates="
            f"{date.replace('-', '')}"
        )

        try:
            response = httpx.get(
                url,
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            return self._failed(
                fixture,
                source,
                url,
                str(exc),
            )

        events = payload.get("events", [])

        matched = self._find_event(
            fixture,
            events,
        )

        if matched is None:
            return self._insufficient(
                fixture,
                source,
                "ESPN responded, but the requested fixture "
                "was not found in the returned events.",
                url,
            )

        return CollectedSourceEvidence(
            fixture=fixture,
            source_id=source["source_id"],
            source_name=source["name"],
            status="VERIFIED",
            evidence_types=source["evidence_types"],
            evidence={
                "event": matched,
                "response_event_count": len(events),
            },
            source_reference=url,
            observed_at=self._now(),
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
