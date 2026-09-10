"""
V1.2 Capability Evidence Extractor

Purpose:
    Prepare evidence from a verified source for one explicitly
    requested external capability.

Rules:
    - The underlying source must already be verified.
    - The caller must explicitly identify the capability.
    - No question is answered here.
    - No inference is made about missing information.
    - No evidence is applied to V2EvidenceState here.
    - Pieces 1-9 remain untouched.
"""

from typing import Any, Dict

from app.v1_2_source_verifier import VerifiedSource


class V12CapabilityEvidenceExtractor:
    """Package verified source content for a specific capability."""

    SUPPORTED_CAPABILITIES = {
        "competition_context",
        "competition_rules",
        "financial_context",
        "geopolitical_context",
        "market_context",
        "match_status",
        "motivation",
        "pitch_conditions",
        "public_context",
        "results",
        "schedule",
        "standings",
        "team_changes",
        "team_identity",
        "weather_venue",
    }

    @classmethod
    def extract(
        cls,
        verified_source: VerifiedSource,
        *,
        capability: str,
    ) -> Dict[str, Any]:
        if verified_source.status != "VERIFIED_SOURCE_REACHED":
            raise ValueError(
                "Capability extraction requires a verified source."
            )

        if capability not in cls.SUPPORTED_CAPABILITIES:
            raise ValueError(
                f"Unsupported external capability: {capability}"
            )

        if not verified_source.content:
            raise ValueError(
                "Verified source contains no usable content."
            )

        return {
            "capability": capability,
            "source_url": verified_source.url,
            "final_url": verified_source.final_url,
            "content_type": verified_source.content_type,
            "status_code": verified_source.status_code,
            "content_length": verified_source.content_length,
            "content": verified_source.content,
            "evidence_status": "SOURCE_CONTENT_AVAILABLE",
        }


__all__ = ["V12CapabilityEvidenceExtractor"]
