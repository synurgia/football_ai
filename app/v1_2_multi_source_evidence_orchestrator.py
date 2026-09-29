from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.regional_evidence_collector import RegionalEvidenceCollector
from app.data_registry.v13_source_retrieval_service import V13SourceRetrievalService
from app.data_registry.global_competition_universe import (
    build_v13_global_competition_universe,
)
from app.v1_2_v13_evidence_bridge import V12V13EvidenceBridge


class V12MultiSourceEvidenceOrchestrator:
    """
    V1.2 multi-source evidence collection layer.

    Responsibilities:
    - use the existing V1.3 competition/source mapping
    - collect evidence from all applicable configured sources
    - preserve source provenance
    - group evidence by capability
    - expose conflicts and coverage gaps
    - route collected evidence into the V1.2 question state
    - NEVER invent answers
    - NEVER replace the existing V1.2 routing logic
    """

    def __init__(self):
        self.collector = RegionalEvidenceCollector()
        self.retrieval = V13SourceRetrievalService(
            build_v13_global_competition_universe()
        )
        self.bridge = V12V13EvidenceBridge()

    @staticmethod
    def _source_record(item: Any) -> Dict[str, Any]:
        if hasattr(item, "__dict__"):
            return dict(item.__dict__)

        if isinstance(item, dict):
            return dict(item)

        return {"value": str(item)}

    @staticmethod
    def _evidence_key(item: Dict[str, Any]) -> str:
        return "|".join(
            [
                str(item.get("source_id") or ""),
                str(item.get("source_reference") or ""),
                str(item.get("status") or ""),
            ]
        )

    @staticmethod
    def _build_conflict_groups(
        evidence: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Detect potentially conflicting evidence without deciding
        which source is correct.
        """
        groups = defaultdict(list)

        for item in evidence:
            capability = item.get("capability")

            if not capability:
                for evidence_type in item.get("evidence_types", []) or []:
                    groups[evidence_type].append(item)
            else:
                groups[capability].append(item)

        conflicts = []

        for capability, items in groups.items():
            statuses = {
                str(item.get("status"))
                for item in items
                if item.get("status")
            }

            if "VERIFIED" in statuses and "FAILED" in statuses:
                conflicts.append(
                    {
                        "capability": capability,
                        "type": "STATUS_CONFLICT",
                        "sources": [
                            item.get("source_id")
                            for item in items
                        ],
                    }
                )

        return conflicts

    def collect(self, fixture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect all currently available evidence for one fixture,
        then route that evidence into the canonical V1.2 question state.
        """

        competition_id = fixture.get("competition_id")

        mapped_sources: List[Dict[str, Any]] = []

        if competition_id:
            try:
                retrieval = self.retrieval.retrieve_mapped_sources(
                    competition_id
                )

                mapped_sources = list(
                    retrieval.get("results", []) or []
                )

            except Exception as exc:
                retrieval = {
                    "competition_id": competition_id,
                    "source_count": 0,
                    "results": [],
                    "retrieved": False,
                    "held": True,
                    "error": str(exc),
                }

        else:
            retrieval = {
                "competition_id": None,
                "source_count": 0,
                "results": [],
                "retrieved": False,
                "held": True,
                "reason": "Competition identity unresolved",
            }

        collected = []

        try:
            results = self.collector.collect(
                fixture,
                v13_sources=mapped_sources,
            )

            for item in results or []:
                record = self._source_record(item)

                if "capability" not in record:
                    evidence_types = record.get(
                        "evidence_types",
                        [],
                    ) or []

                    if isinstance(evidence_types, str):
                        evidence_types = [evidence_types]

                    record["capability"] = (
                        evidence_types[0]
                        if evidence_types
                        else None
                    )

                collected.append(record)

        except Exception as exc:
            collected.append(
                {
                    "source_id": "orchestrator",
                    "status": "FAILED",
                    "reason": str(exc),
                    "capability": None,
                }
            )

        unique = []
        seen = set()

        for item in collected:
            key = self._evidence_key(item)

            if key in seen:
                continue

            seen.add(key)
            unique.append(item)

        by_capability = defaultdict(list)

        for item in unique:
            capability = item.get("capability")

            if capability:
                by_capability[capability].append(item)

        verified = [
            item
            for item in unique
            if item.get("status") == "VERIFIED"
        ]

        insufficient = [
            item
            for item in unique
            if item.get("status") == "INSUFFICIENT_EVIDENCE"
        ]

        failed = [
            item
            for item in unique
            if item.get("status") == "FAILED"
        ]

        conflicts = self._build_conflict_groups(unique)

        packet = {
            "fixture": fixture,
            "collected_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "competition_id": competition_id,
            "mapped_source_count": len(mapped_sources),
            "retrieval": retrieval,
            "total_evidence": len(unique),
            "verified_evidence": len(verified),
            "insufficient_evidence": len(insufficient),
            "failed_evidence": len(failed),
            "evidence": unique,
            "by_capability": dict(by_capability),
            "conflicts": conflicts,
            "coverage": {
                "has_evidence": bool(unique),
                "has_verified": bool(verified),
                "has_conflicts": bool(conflicts),
                "identity_resolved": bool(competition_id),
            },
        }

        # V1.3 → V1.2 QUESTION STATE
        #
        # The original multi-source packet remains intact.
        # The bridge adds the canonical 37-question evidence state
        # and reasoning output without changing source retrieval.
        bridge_result = self.bridge.process(
            fixture,
            packet,
        )

        packet["v1_2_evidence_state"] = bridge_result.get(
            "evidence_state"
        )

        packet["v1_2_reasoning"] = bridge_result.get(
            "reasoning"
        )

        return packet
