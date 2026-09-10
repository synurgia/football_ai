"""
V1.2 Capability Evidence Envelope Builder

Purpose:
    Convert capability-specific extracted source content into the
    existing ExternalEvidenceEnvelope.

Rules:
    - Source must already be verified.
    - Capability must already be explicitly extracted.
    - Provenance is preserved.
    - No football conclusion is generated.
    - No home/away preference is generated.
    - No 37-question answer is generated here.
    - Existing V2EvidenceManager and V12ExternalEvidenceApplier
      remain unchanged.
"""

from typing import Any, Dict

from app.v1_2_external_evidence_envelope import (
    ExternalEvidenceEnvelope,
    create_external_evidence_envelope,
)


class V12CapabilityEvidenceEnvelopeBuilder:
    """Build an external evidence envelope from extracted capability data."""

    def build(
        self,
        extracted: Dict[str, Any],
        *,
        source_id: str,
    ) -> ExternalEvidenceEnvelope:
        if not isinstance(extracted, dict):
            raise ValueError(
                "Extracted capability evidence must be a dictionary."
            )

        capability = extracted.get("capability")
        if not capability:
            raise ValueError(
                "Extracted capability evidence must identify a capability."
            )

        if extracted.get("evidence_status") != "SOURCE_CONTENT_AVAILABLE":
            raise ValueError(
                "Capability evidence must come from available verified source content."
            )

        source_url = extracted.get("source_url")
        final_url = extracted.get("final_url")
        content = extracted.get("content")

        if not source_url:
            raise ValueError(
                "Extracted capability evidence must preserve the source URL."
            )

        if not content or not str(content).strip():
            raise ValueError(
                "Extracted capability evidence contains no usable source content."
            )

        evidence: Dict[str, Any] = {
            "capability": capability,
            "source_url": source_url,
            "final_url": final_url,
            "content_type": extracted.get("content_type"),
            "status_code": extracted.get("status_code"),
            "content_length": extracted.get("content_length"),
            "content": content,
        }

        return create_external_evidence_envelope(
            capability=capability,
            source_id=source_id,
            source_type="verified_web_source",
            evidence=evidence,
            source_ref=final_url or source_url,
            status="VERIFIED",
            notes=(
                "Capability-specific source content was admitted with "
                "preserved provenance. No football outcome or question "
                "answer was inferred by this layer."
            ),
        )


__all__ = ["V12CapabilityEvidenceEnvelopeBuilder"]
