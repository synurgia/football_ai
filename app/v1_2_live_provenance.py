from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from app.today_match_aggregator import TodayMatchAggregator
from app.regional_evidence_collector import RegionalEvidenceCollector
from app.v1_2_source_evidence_ledger import V12SourceEvidenceLedger
from app.v1_2_question_capabilities import get_question_capabilities


class V12LiveProvenance:
    """
    Day-level V1.2 live provenance integration.

    This layer:
        1. Discovers ALL canonical fixtures for the requested day.
        2. Fetches the ESPN global scoreboard once for that day.
        3. Matches source events against every canonical fixture.
        4. Routes the canonical 37 questions through their capabilities.
        5. Preserves source reference, observation time and status.
        6. Writes source observations into per-fixture evidence ledgers.

    This layer does NOT answer the 37 questions semantically.
    It does NOT modify Pieces 1-9.
    """

    ESPN_URL = (
        "https://site.api.espn.com/apis/site/v2/"
        "sports/soccer/all/scoreboard"
    )

    def __init__(
        self,
        aggregator=None,
        collector=None,
        timeout: float = 15.0,
    ):
        self.aggregator = aggregator or TodayMatchAggregator()
        self.collector = collector or RegionalEvidenceCollector(
            timeout=timeout
        )
        self.timeout = timeout

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _find_event(
        fixture: Dict[str, Any],
        events: List[Dict[str, Any]],
    ):
        return RegionalEvidenceCollector._find_event(
            fixture,
            events,
        )

    def collect_today(
        self,
        question_capabilities: Optional[Dict[str, str]] = None,
        target_date: Optional[str] = None,
    ) -> Dict[str, Any]:

        if question_capabilities is None:
            question_capabilities = get_question_capabilities()

        if len(question_capabilities) != 37:
            raise RuntimeError(
                "Canonical V1.2 capability map must contain exactly 37 questions."
            )

        aggregate = self.aggregator.load_today(target_date)
        fixtures = aggregate.get("matches", [])

        if not fixtures:
            return {
                "date": aggregate.get("date"),
                "fixtures": [],
                "fixture_count": 0,
                "question_count": len(question_capabilities),
                "ledgers": [],
                "summary": {
                    "fixtures_processed": 0,
                    "verified_fixtures": 0,
                    "unverified_fixtures": 0,
                    "question_records": 0,
                },
            }

        date = aggregate.get("date")
        observed_at = self._now()

        espn_events: List[Dict[str, Any]] = []
        espn_status = "FAILED"
        espn_reference = self.ESPN_URL
        espn_error = None

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    self.ESPN_URL,
                    params={"dates": str(date).replace("-", "")},
                )
                response.raise_for_status()
                payload = response.json()

            espn_events = payload.get("events", [])
            espn_status = "VERIFIED"

        except Exception as exc:
            espn_status = "FAILED"
            espn_error = str(exc)

        results = []

        for fixture in fixtures:
            ledger = V12SourceEvidenceLedger()

            home = fixture.get("home_team")
            away = fixture.get("away_team")

            matched = self._find_event(
                fixture,
                espn_events,
            )

            if matched is not None:
                event_id = matched.get("id")

                source_ref = (
                    f"espn:event:{event_id}"
                    if event_id
                    else espn_reference
                )

                evidence = {
                    "event": matched,
                    "fixture": fixture,
                    "source_response_event_count": len(
                        espn_events
                    ),
                }

                for question_id, capability in (
                    question_capabilities.items()
                ):
                    ledger.add(
                        question_id,
                        "espn_global_soccer",
                        answer="EVIDENCE_AVAILABLE",
                        evidence=evidence,
                        supports="UNKNOWN",
                        confidence=1.0,
                        source_ref=source_ref,
                        observed_at=observed_at,
                        status="VERIFIED",
                        notes=(
                            f"ESPN day-level response matched "
                            f"{home} vs {away}. "
                            f"Capability route: {capability}. "
                            f"This confirms source evidence availability "
                            f"only; it does not semantically answer "
                            f"{question_id}."
                        ),
                    )

                fixture_status = "VERIFIED"

            else:
                for question_id, capability in (
                    question_capabilities.items()
                ):
                    ledger.add(
                        question_id,
                        "espn_global_soccer",
                        answer=None,
                        evidence=None,
                        supports="UNKNOWN",
                        confidence=None,
                        source_ref=espn_reference,
                        observed_at=observed_at,
                        status=(
                            "INSUFFICIENT_EVIDENCE"
                            if espn_status == "VERIFIED"
                            else "FAILED"
                        ),
                        notes=(
                            "ESPN day-level response was received "
                            "but this canonical fixture was not matched."
                            if espn_status == "VERIFIED"
                            else
                            f"ESPN day-level request failed: {espn_error}"
                        ),
                    )

                fixture_status = (
                    "INSUFFICIENT_EVIDENCE"
                    if espn_status == "VERIFIED"
                    else "FAILED"
                )

            results.append(
                {
                    "fixture": fixture,
                    "status": fixture_status,
                    "ledger": ledger,
                    "ledger_count": ledger.count(),
                }
            )

        verified = sum(
            1
            for item in results
            if item["status"] == "VERIFIED"
        )

        total_question_records = sum(
            item["ledger_count"]
            for item in results
        )

        return {
            "date": date,
            "fixtures": results,
            "fixture_count": len(results),
            "question_count": len(question_capabilities),
            "source_fetches": {
                "espn_global_soccer": {
                    "status": espn_status,
                    "events_returned": len(espn_events),
                    "source_reference": espn_reference,
                    "observed_at": observed_at,
                    "error": espn_error,
                }
            },
            "summary": {
                "fixtures_processed": len(results),
                "verified_fixtures": verified,
                "unverified_fixtures": (
                    len(results) - verified
                ),
                "question_records": total_question_records,
            },
        }
