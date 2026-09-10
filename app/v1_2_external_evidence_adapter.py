from typing import Any, Optional, Mapping

from app.regional_evidence_collector import CollectedSourceEvidence
from app.v1_2_external_evidence_envelope import (
    ExternalEvidenceEnvelope,
    create_external_evidence_envelope,
)


STATUS_MAP = {
    "VERIFIED": "VERIFIED",
    "FAILED": "FAILED",
    "INSUFFICIENT_EVIDENCE": "INSUFFICIENT_EVIDENCE",
    "NOT_CONFIGURED": "UNVERIFIED",
    "UNVERIFIED": "UNVERIFIED",
}


def adapt_collected_source_evidence(
    record: CollectedSourceEvidence,
    *,
    capability: str,
) -> ExternalEvidenceEnvelope:
    if isinstance(record, Mapping):
        status_value = record.get("status", "UNVERIFIED")
        source_id = record.get("source_id")
        evidence = record.get("evidence")
        source_reference = record.get("source_reference")
        observed_at = record.get("observed_at")
        reason = record.get("reason")
    else:
        status_value = record.status
        source_id = record.source_id
        evidence = record.evidence
        source_reference = record.source_reference
        observed_at = record.observed_at
        reason = record.reason

    status = STATUS_MAP.get(
        str(status_value).upper(),
        "UNVERIFIED",
    )

    source_type = _source_type(source_id)

    return create_external_evidence_envelope(
        capability=capability,
        source_id=source_id,
        source_type=source_type,
        evidence=evidence,
        source_ref=source_reference,
        observed_at=observed_at,
        status=status,
        notes=reason,
    )

def _source_type(source_id: str) -> str:
    if source_id in {
        "google_search",
        "bing_search",
        "brave_search",
        "yandex_search",
    }:
        return source_id

    if source_id == "fkf_official":
        return "official_federation"

    if source_id in {
        "espn_global_soccer",
        "openfoot",
    }:
        return "football_data_provider"

    return "unknown_source_type"


if __name__ == "__main__":
    record = CollectedSourceEvidence(
        fixture={
            "home_team": "Test Home",
            "away_team": "Test Away",
        },
        source_id="espn_global_soccer",
        source_name="ESPN Soccer",
        status="VERIFIED",
        evidence_types=["fixture"],
        evidence={"fixture": "verified"},
        source_reference="https://example.invalid/fixture",
        observed_at="2026-09-10T00:00:00+00:00",
    )

    envelope = adapt_collected_source_evidence(
        record,
        capability="match_status",
    )

    print("=== V1.2 EXTERNAL EVIDENCE ADAPTER ===")
    print("CAPABILITY:", envelope.capability)
    print("SOURCE:", envelope.source_id)
    print("SOURCE TYPE:", envelope.source_type)
    print("STATUS:", envelope.status)
    print("RESULT: PASS")
