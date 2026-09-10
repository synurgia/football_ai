from dataclasses import dataclass
from typing import Any, Optional, Tuple


@dataclass(frozen=True)
class ExternalEvidenceEnvelope:
    capability: str
    source_id: str
    source_type: str
    evidence: Any
    source_ref: Optional[str] = None
    observed_at: Optional[str] = None
    status: str = "UNVERIFIED"
    notes: Optional[str] = None

    def validate(self) -> None:
        if not self.capability.strip():
            raise ValueError("Evidence capability is required.")

        if not self.source_id.strip():
            raise ValueError("Evidence source_id is required.")

        if not self.source_type.strip():
            raise ValueError("Evidence source_type is required.")

        allowed_statuses = {
            "VERIFIED",
            "UNVERIFIED",
            "INSUFFICIENT_EVIDENCE",
            "FAILED",
        }

        if self.status.upper() not in allowed_statuses:
            raise ValueError(
                f"Unsupported evidence status: {self.status}"
            )

        if (
            self.source_type in {
                "google_search",
                "bing_search",
                "brave_search",
                "yandex_search",
            }
            and self.status.upper() == "VERIFIED"
        ):
            raise ValueError(
                "Search-engine discovery sources cannot provide "
                "verified evidence directly."
            )

        if (
            self.status.upper() == "VERIFIED"
            and self.evidence is None
        ):
            raise ValueError(
                "Verified evidence cannot have empty evidence."
            )


def create_external_evidence_envelope(
    *,
    capability: str,
    source_id: str,
    source_type: str,
    evidence: Any,
    source_ref: Optional[str] = None,
    observed_at: Optional[str] = None,
    status: str = "UNVERIFIED",
    notes: Optional[str] = None,
) -> ExternalEvidenceEnvelope:
    envelope = ExternalEvidenceEnvelope(
        capability=capability,
        source_id=source_id,
        source_type=source_type,
        evidence=evidence,
        source_ref=source_ref,
        observed_at=observed_at,
        status=status,
        notes=notes,
    )

    envelope.validate()
    return envelope


if __name__ == "__main__":
    valid = create_external_evidence_envelope(
        capability="match_status",
        source_id="espn_global_soccer",
        source_type="football_data_provider",
        evidence={"fixture": "verified"},
        source_ref="https://example.invalid/source",
        status="VERIFIED",
    )

    print("=== V1.2 EXTERNAL EVIDENCE ENVELOPE ===")
    print("VALID ENVELOPE:", valid.capability)
    print("STATUS:", valid.status)

    try:
        create_external_evidence_envelope(
            capability="match_status",
            source_id="google_search",
            source_type="google_search",
            evidence={"search_result": "not evidence"},
            status="VERIFIED",
        )
    except ValueError as exc:
        print("SEARCH EVIDENCE BLOCKED:", str(exc))

    print("RESULT: PASS")
