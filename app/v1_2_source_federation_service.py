"""
V1.2 Source Federation Service

Connects the completed external-source components into one controlled
path.

Flow:
    discovered URL
        ↓
    source verification
        ↓
    source content extraction
        ↓
    capability-specific candidate finding
        ↓
    capability evidence envelope
        ↓
    existing canonical evidence admission

Rules:
    - Discovery mechanisms remain discovery-only.
    - The underlying source URL is the provenance source.
    - No Home/Away preference is generated.
    - No football outcome is generated.
    - No question answer is inferred.
    - Pieces 1-9 remain untouched.
"""

from typing import Any, Dict

from app.v1_2_source_verifier import V12SourceVerifier
from app.v1_2_source_content_extractor import V12SourceContentExtractor
from app.v1_2_capability_evidence_finder import (
    V12CapabilityEvidenceFinder,
)
from app.v1_2_capability_evidence_envelope import (
    V12CapabilityEvidenceEnvelopeBuilder,
)
from app.v1_2_external_evidence_admission import (
    V12ExternalEvidenceAdmission,
)
from app.v2_evidence_state import V2EvidenceState


class V12SourceFederationService:
    """Controlled real-source federation path."""

    def __init__(self) -> None:
        self.verifier = V12SourceVerifier()
        self.content_extractor = V12SourceContentExtractor()
        self.evidence_finder = V12CapabilityEvidenceFinder()
        self.envelope_builder = V12CapabilityEvidenceEnvelopeBuilder()
        self.admission = V12ExternalEvidenceAdmission()

    def process_source(
        self,
        state: V2EvidenceState,
        *,
        url: str,
        capability: str,
        source_id: str,
    ) -> Dict[str, Any]:
        verified = self.verifier.verify(url)

        if verified.status != "VERIFIED_SOURCE_REACHED":
            return {
                "status": verified.status,
                "source_id": source_id,
                "url": url,
                "capability": capability,
                "reason": verified.reason,
            }

        source_content = self.content_extractor.extract(verified)

        found = self.evidence_finder.find(
            source_content,
            capability=capability,
        )

        if found["status"] != "CANDIDATE_EVIDENCE_FOUND":
            return {
                "status": "INSUFFICIENT_EVIDENCE",
                "source_id": source_id,
                "url": url,
                "capability": capability,
                "reason": (
                    "Verified source was reached, but no "
                    "capability-specific candidate evidence was found."
                ),
            }

        extracted = dict(source_content)
        extracted["capability"] = capability
        extracted["evidence_status"] = "SOURCE_CONTENT_AVAILABLE"
        extracted["candidate_evidence"] = found["passages"]

        envelope = self.envelope_builder.build(
            extracted,
            source_id=source_id,
        )

        envelope.evidence["candidate_evidence"] = found["passages"]

        admitted = self.admission.admit(
            state,
            envelope,
        )

        return {
            "status": "ADMITTED",
            "source_id": source_id,
            "url": url,
            "capability": capability,
            "candidate_passage_count": found["passage_count"],
            "admission": admitted,
        }


__all__ = ["V12SourceFederationService"]
