"""
V1.3 Source Verification Service

Connects the V1.3 Competition Registry to the existing
V1.2 real-source verification machinery.

Rules:
- The Competition Registry remains the source inventory.
- V1.2 SourceVerifier performs the real HTTP request.
- A configured URL is NOT automatically verified.
- Verification records what was actually observed.
- No prediction logic is touched.
- No Pieces 1-9 are modified.
"""

from typing import Any, Dict, List

from app.data_registry.v1_3_source_registry import (
    V13_SOURCES,
    V13_COMPETITION_SOURCE_MAP,
)
from app.v1_2_source_verifier import V12SourceVerifier


class V13SourceVerificationService:
    """Verify registered competition sources against the real network."""

    def __init__(self, timeout: float = 20.0) -> None:
        self.verifier = V12SourceVerifier(timeout=timeout)

    def verify_source(
        self,
        competition_id: str,
        source_url: str,
    ) -> Dict[str, Any]:
        result = self.verifier.verify(source_url)

        return {
            "competition_id": competition_id,
            "url": result.url,
            "final_url": result.final_url,
            "status": result.status,
            "status_code": result.status_code,
            "content_type": result.content_type,
            "content_length": result.content_length,
            "reason": result.reason,
            "reachable": result.status == "VERIFIED_SOURCE_REACHED",
        }

    def verify_registered_competition(
        self,
        competition_id: str,
    ) -> List[Dict[str, Any]]:
        registry = V13_SOURCES

        sources = registry.get_all(competition_id)

        if not sources:
            return [{
                "competition_id": competition_id,
                "status": "NO_REGISTERED_SOURCE",
                "reachable": False,
            }]

        results: List[Dict[str, Any]] = []

        for source in sources:
            result = self.verify_source(
                competition_id=competition_id,
                source_url=source.source_url,
            )

            result["source_name"] = source.source_name
            result["source_role"] = source.source_role
            result["authority_level"] = source.authority_level
            result["verification_status_before"] = (
                source.verification_status
            )

            results.append(result)

        return results

    def verify_all_registered_sources(self) -> List[Dict[str, Any]]:
        registry = V13_SOURCES

        results: List[Dict[str, Any]] = []

        for competition in registry.list_competitions():
            results.extend(
                self.verify_registered_competition(
                    competition.competition_id
                )
            )

        return results


__all__ = ["V13SourceVerificationService"]
