from datetime import date
from typing import Any, Dict, Optional

from app.worldwide_daily_scanner import WorldwideDailyMatchScanner
from app.worldwide_readiness_service import WorldwideReadinessService
from app.worldwide_team_enrichment import WorldwideTeamEnrichment
from app.data_registry.rolling_match_store import RollingMatchStore
from app.worldwide_daily_prediction_service import WorldwideDailyPredictionService
from app.regional_evidence_collector import RegionalEvidenceCollector
from app.v1_2_multi_source_evidence_orchestrator import V12MultiSourceEvidenceOrchestrator
from app.v1_2_external_evidence_adapter import adapt_collected_source_evidence
from app.v2_live_evidence_collector import V2LiveEvidenceCollector
from app.v13_ai_daily_bridge import analyze_daily_matches
from app.data_registry.evidence_state_store import EvidenceStateStore


class WorldwideDailyDataManager:

    async def run_once(self, target_date=None):
        """Compatibility entry point for one V1.3 daily pipeline execution."""
        if hasattr(self, "run_daily"):
            return await self.run_daily(target_date=target_date)
        if hasattr(self, "run"):
            result = self.run(target_date=target_date)
            return await result if hasattr(result, "__await__") else result
        if hasattr(self, "execute_daily"):
            result = self.execute_daily(target_date=target_date)
            return await result if hasattr(result, "__await__") else result
        raise AttributeError("No daily execution method available")
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
        matches: list[Dict[str, Any]], unified_sources=None) -> Dict[str, Any]:
        # --- defensive default (auto-inserted) ---
        prediction_result = locals().get('prediction_result', None)
        collector = RegionalEvidenceCollector(timeout=3.0)
        live_collector = V2LiveEvidenceCollector()
        multisource_orchestrator = V12MultiSourceEvidenceOrchestrator()


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
        multisource_packets = []

        for index, match in enumerate(matches, start=1):
            home_team = match.get("home_team")
            away_team = match.get("away_team")

            if not home_team or not away_team:
                continue

            # --------------------------------------------------------
            # V1.3 → V1.2 MULTI-SOURCE QUESTION PIPELINE
            # --------------------------------------------------------
            multisource_packet = multisource_orchestrator.collect(match)
            multisource_packets.append(multisource_packet)

            collected = collector.collect(match, v13_sources=unified_sources)

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
            "prediction_result": prediction_result,

            "matches": collected_matches,
            "applied_items": applied_items,
            "verified_sources": verified_sources,
            "failed_sources": failed_sources,
            "insufficient_sources": insufficient_sources,
            "states": states,
            "persisted_states": evidence_store.count(),
            "multisource_packets": multisource_packets,
            "multisource_matches": len(multisource_packets),
            "multisource_question_states": [
                packet.get("v1_2_evidence_state")
                for packet in multisource_packets
                if packet.get("v1_2_evidence_state") is not None
            ],
            "multisource_reasoning": [
                packet.get("v1_2_reasoning")
                for packet in multisource_packets
                if packet.get("v1_2_reasoning") is not None
            ],
        }

    def run(
        self,
        target_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute the complete daily scanner lifecycle.

        Order:
        1. Discover today's matches.
        2. Persist discovered matches.
        3. Enrich teams.
        4. Run V1.3 AI bridge.
        5. Collect existing external evidence.
        6. Apply existing readiness gate.
        7. Run existing prediction service for READY matches.
        8. Return the complete lifecycle result.
        """
        if target_date is None:
            target = date.today()
        else:
            target = date.fromisoformat(target_date)

        target_date = target.isoformat()

        # ------------------------------------------------------------
        # 1. DAILY MATCH SCAN
        # ------------------------------------------------------------
        scan = self.scanner.scan(
            target_date=target_date,
            include_tomorrow=True,
        )

        today_matches = list(scan.get("today", []))
        tomorrow_matches = list(scan.get("tomorrow", []))

        # ------------------------------------------------------------
        # 2. PERSIST DISCOVERED MATCHES FIRST
        # ------------------------------------------------------------
        today_ids = self.store.upsert_many(
            today_matches,
            "today",
        )

        tomorrow_ids = self.store.upsert_many(
            tomorrow_matches,
            "tomorrow",
        )

        # ------------------------------------------------------------
        # 3. TEAM ENRICHMENT
        # ------------------------------------------------------------
        try:
            enrichment_result = WorldwideTeamEnrichment().enrich_matches(
                today_matches
            )
        except Exception as exc:
            enrichment_result = {
                "status": "FAILED",
                "error": str(exc),
                "matches": [],
            }

        # ------------------------------------------------------------
        # 4. V1.3 -> AI INTELLIGENCE BRIDGE
        # ------------------------------------------------------------
        try:
            v13_ai_result = analyze_daily_matches(today_matches)

            v13_matches = v13_ai_result.get("matches", [])

            # Preserve the enriched V1.3 state on the scanned matches.
            for original, enriched in zip(today_matches, v13_matches):
                if isinstance(enriched, dict):
                    original.update({
                        "v13_ai": enriched.get("v13_ai"),
                    })

        except Exception as exc:
            v13_ai_result = {
                "status": "FAILED",
                "total": len(today_matches),
                "completed": 0,
                "insufficient": len(today_matches),
                "failed": 0,
                "error": str(exc),
                "matches": today_matches,
            }

        # ------------------------------------------------------------
        # 5. EXISTING EXTERNAL EVIDENCE PIPELINE
        # ------------------------------------------------------------
        try:
            external_evidence = self._collect_external_evidence(
                today_matches,
                unified_sources=scan.get("unified_sources", []),
            )
        except Exception as exc:
            external_evidence = {
                "status": "FAILED",
                "error": str(exc),
                "matches": 0,
                "applied_items": 0,
                "verified_sources": 0,
                "failed_sources": 0,
                "insufficient_sources": 0,
                "states": [],
                "persisted_states": 0,
            }

        # ------------------------------------------------------------
        # 6. EXISTING READINESS GATE
        # ------------------------------------------------------------
        prediction_result = {
            "status": "NOT_PROCESSED",
            "processed": 0,
            "predictions": [],
        }

        try:
            readiness_service = WorldwideReadinessService()

            if hasattr(readiness_service, "evaluate_daily"):
                readiness_result = readiness_service.evaluate_daily(
                    today_matches
                )
            else:
                readiness_result = readiness_service.evaluate(
                    today_matches
                )

            if isinstance(readiness_result, dict):
                if hasattr(self.prediction_service, "process_all_matches"):
                    prediction_result = (
                        self.prediction_service.process_all_matches(
                            readiness_result
                        )
                    )
                else:
                    prediction_result = (
                        self.prediction_service.process_ready_matches(
                            readiness_result
                        )
                    )

        except Exception as exc:
            prediction_result = {
                "status": "FAILED",
                "processed": 0,
                "predictions": [],
                "error": str(exc),
            }

        # ------------------------------------------------------------
        # 6b. PERSIST OUTCOMES FOR EVERY SCANNED MATCH
        # ------------------------------------------------------------
        try:
            import sqlite3, json
            from datetime import datetime, timezone
            conn = sqlite3.connect("data/football_daily.db")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS match_outcomes (
                    match_id TEXT PRIMARY KEY,
                    match_date TEXT,
                    competition TEXT,
                    home_team TEXT,
                    away_team TEXT,
                    kickoff_at TEXT,
                    verdict TEXT,
                    asserted INTEGER,
                    confidence TEXT,
                    source TEXT,
                    outcome_json TEXT,
                    created_at TEXT
                )
            """)
            now = datetime.now(timezone.utc).isoformat()
            cards = (prediction_result or {}).get("reasoning_cards", []) or []
            saved = 0
            for card in cards:
                mid = str(card.get("match_id") or "")
                if not mid:
                    continue
                outcome = card.get("outcome") or {}
                conn.execute(
                    "INSERT OR REPLACE INTO match_outcomes "
                    "(match_id, match_date, competition, home_team, away_team, "
                    " kickoff_at, verdict, asserted, confidence, source, "
                    " outcome_json, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        mid,
                        target_date,
                        card.get("competition"),
                        card.get("home_team"),
                        card.get("away_team"),
                        card.get("kickoff_at"),
                        card.get("verdict"),
                        1 if card.get("outcome_asserted") else 0,
                        card.get("outcome_confidence"),
                        card.get("outcome_source"),
                        json.dumps(outcome),
                        now,
                    ),
                )
                saved += 1
            conn.commit()
            conn.close()
            outcome_persistence = {"status": "OK", "saved": saved}
        except Exception as exc:
            outcome_persistence = {"status": "FAILED", "error": str(exc)}

        # ------------------------------------------------------------
        # 7. COMPLETE DAILY RESULT
        # ------------------------------------------------------------
        return {
            "status": "COMPLETED",
            "date": target_date,

            "today": today_matches,
            "tomorrow": tomorrow_matches,

            "today_count": len(today_matches),
            "tomorrow_count": len(tomorrow_matches),

            "today_ids": today_ids,
            "tomorrow_ids": tomorrow_ids,

            "enrichment": enrichment_result,

            "v13": v13_ai_result,

            "external_evidence": external_evidence,

            "prediction": prediction_result,

            "scanner": {
                "status": "COMPLETED",
                "today_matches": len(today_matches),
                "tomorrow_matches": len(tomorrow_matches),
            },
        }
