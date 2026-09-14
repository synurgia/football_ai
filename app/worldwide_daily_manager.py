from datetime import date
from typing import Any, Dict, Optional

from app.worldwide_daily_scanner import WorldwideDailyMatchScanner
from app.worldwide_readiness_service import WorldwideReadinessService
from app.worldwide_team_enrichment import WorldwideTeamEnrichment
from app.data_registry.rolling_match_store import RollingMatchStore
from app.worldwide_daily_prediction_service import WorldwideDailyPredictionService
from app.regional_evidence_collector import RegionalEvidenceCollector
from app.v1_2_external_evidence_adapter import adapt_collected_source_evidence
from app.v2_live_evidence_collector import V2LiveEvidenceCollector
from app.data_registry.evidence_state_store import EvidenceStateStore


class WorldwideDailyDataManager:
    """
    Controls the daily worldwide football data workflow.

    TODAY:
        Discover matches and identify candidates that may be processed.

    TOMORROW:
        Discover matches for preparation only.

    This manager does not run predictions and does not modify Pieces 1-9.
    """

    def __init__(
        self,
        scanner: Optional[WorldwideDailyMatchScanner] = None,
        store=None,
        prediction_service: Optional[WorldwideDailyPredictionService] = None,
    ):
        self.scanner = scanner or WorldwideDailyMatchScanner()
        self.store = store or RollingMatchStore()
        self.prediction_service = (
            prediction_service or WorldwideDailyPredictionService()
        )

    def _collect_external_evidence(
        self,
        matches: list[Dict[str, Any]],
    ) -> Dict[str, Any]:
        collector = RegionalEvidenceCollector(timeout=3.0)
        live_collector = V2LiveEvidenceCollector()

        capability_by_type = {
            "fixtures": "schedule",
            "match_status": "match_status",
            "teams": "team_identity",
            "results": "results",
        }

        states = []
        collected_matches = 0
        applied_items = 0
        verified_sources = 0
        failed_sources = 0
        insufficient_sources = 0

        for index, match in enumerate(matches, start=1):
            home_team = match.get("home_team")
            away_team = match.get("away_team")

            if not home_team or not away_team:
                continue

            collected = collector.collect(match)

            state = live_collector.create_match_state(
                match_id=str(
                    match.get(
                        "match_id",
                        f"{match.get('kickoff_at', 'unknown')}-{home_team}-{away_team}-{index}",
                    )
                ),
                competition=str(match.get("competition", "UNKNOWN")),
                home_team=str(home_team),
                away_team=str(away_team),
            )

            match_applied = 0

            for record in collected.get("records", []):
                status = str(record.get("status", "")).upper()

                if status == "VERIFIED":
                    verified_sources += 1
                elif status == "FAILED":
                    failed_sources += 1
                elif status in {"INSUFFICIENT_EVIDENCE", "NOT_CONFIGURED"}:
                    insufficient_sources += 1

                if record.get("source_id") != "espn_global_soccer":
                    continue

                for evidence_type in record.get("evidence_types", []):
                    capability = capability_by_type.get(evidence_type)

                    if capability is None:
                        continue

                    envelope = adapt_collected_source_evidence(
                        record,
                        capability=capability,
                    )

                    applied = live_collector.apply_external_evidence(
                        state,
                        envelope,
                    )

                    match_applied += len(applied)

            states.append(state)
            collected_matches += 1
            applied_items += match_applied

        evidence_store = EvidenceStateStore()
        evidence_store.save_states(states)

        return {
            "matches": collected_matches,
            "applied_items": applied_items,
            "verified_sources": verified_sources,
            "failed_sources": failed_sources,
            "insufficient_sources": insufficient_sources,
            "states": states,
            "persisted_states": evidence_store.count(),
        }

    def run(
        self,
        target_date: Optional[str] = None,
    ) -> Dict[str, Any]:

        if target_date is None:
            target = date.today()
            target_date = target.isoformat()
        else:
            target = date.fromisoformat(target_date)

        target_date = target.isoformat()

        scan = self.scanner.scan(
            target_date=target_date,
            include_tomorrow=True,
        )

        # Store discovered matches FIRST.
        # Evidence failures must never remove a match from the dashboard.
        today_ids = self.store.upsert_many(
            scan.get("today", []),
            "today",
        )

        tomorrow_ids = self.store.upsert_many(
            scan.get("tomorrow", []),
            "tomorrow",
        )

        try:
            enrichment_result = WorldwideTeamEnrichment().enrich_matches(
                scan.get("today", [])
            )
        except Exception as exc:
            enrichment_result = {
                "status": "failed",
                "error": str(exc),
                "matches": [],
            }

        try:
            external_evidence = self._collect_external_evidence(
                scan.get("today", [])
            )
        except Exception as exc:
            external_evidence = {
                "status": "failed",
                "error": str(exc),
                "matches": [],
            }

        try:
            readiness = WorldwideReadinessService().evaluate_daily(
                scan.get("today", []),
                scan.get("tomorrow", []),
            )
        except Exception as exc:
            readiness = {
                "today_ready": [],
                "today_insufficient": scan.get("today", []),
                "tomorrow_ready": [],
                "tomorrow_insufficient": scan.get("tomorrow", []),
                "status": "failed",
                "error": str(exc),
            }

        prediction_run = self.prediction_service.process_ready_matches(
            readiness
        )

        return {
            "date": target_date,
            "today": {
                "discovered": len(scan.get("today", [])),
                "ready": len(readiness["today_ready"]),
                "held": len(readiness["today_insufficient"]),
            },
            "tomorrow": {
                "discovered": len(scan.get("tomorrow", [])),
                "preparation": len(
                    readiness["tomorrow_preparation"]
                ),
            },
            "today_ready_matches": readiness["today_ready"],
            "today_held_matches": readiness["today_insufficient"],
            "tomorrow_preparation": readiness[
                "tomorrow_preparation"
            ],
            "predictions": prediction_run,
            "external_evidence": {
                "matches": external_evidence["matches"],
                "applied_items": external_evidence["applied_items"],
                "verified_sources": external_evidence["verified_sources"],
                "failed_sources": external_evidence["failed_sources"],
                "insufficient_sources": external_evidence[
                    "insufficient_sources"
                ],
            },
            "stored": {
                "today": len(today_ids),
                "tomorrow": len(tomorrow_ids),
                "total_records": self.store.count(),
            },
            "provenance": scan.get("provenance", {}),
        }
