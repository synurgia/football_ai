"""
V1.2 Verified Source Bridge

Connects a verified underlying source to the existing
ExternalEvidenceEnvelope.

Rules:
    - Search engines remain discovery-only.
    - The underlying URL is the provenance source.
    - Reaching a URL does not mean its content answers a question.
    - This bridge records verified source content only.
    - It does not answer questions.
    - It does not modify Pieces 1-9.
"""

from typing import Any, Dict

from app.v1_2_external_evidence_envelope import (
    ExternalEvidenceEnvelope,
    create_external_evidence_envelope,
)
from app.v1_2_source_verifier import VerifiedSource


class V12VerifiedSourceBridge:
    """Convert a successfully verified source into an evidence envelope."""

    def build_envelope(
        self,
        verified_source: VerifiedSource,
        *,
        capability: str,
        source_id: str,
    ) -> ExternalEvidenceEnvelope:
        if verified_source.status != "VERIFIED_SOURCE_REACHED":
            raise ValueError(
                "Only successfully verified sources can enter the evidence bridge."
            )

        if not verified_source.content:
            raise ValueError(
                "Verified source has no content to place in the envelope."
            )

        evidence: Dict[str, Any] = {
            "url": verified_source.url,
            "final_url": verified_source.final_url,
            "status_code": verified_source.status_code,
            "content_type": verified_source.content_type,
            "content_length": verified_source.content_length,
            "content": verified_source.content,
        }

        return create_external_evidence_envelope(
            capability=capability,
            source_id=source_id,
            source_type="verified_web_source",
            evidence=evidence,
            source_ref=verified_source.final_url or verified_source.url,
            status="VERIFIED",
            notes=(
                "Underlying source was successfully reached. "
                "Content is preserved as source evidence; "
                "no semantic question answer is inferred here."
            ),
        )


__all__ = ["V12VerifiedSourceBridge"]
