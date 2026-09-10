"""
V1.2 Source Content Extractor

Purpose:
    Extract usable textual content from an already verified web source.

Rules:
    - It receives verified source content only.
    - It does not perform web searches.
    - It does not decide whether information is true.
    - It does not answer the 37 questions.
    - It does not modify Pieces 1-9.
"""

from typing import Any, Dict, Optional

from app.v1_2_source_verifier import VerifiedSource


class V12SourceContentExtractor:
    """Prepare verified source content for later capability-specific extraction."""

    @staticmethod
    def extract(
        verified_source: VerifiedSource,
    ) -> Dict[str, Any]:
        if verified_source.status != "VERIFIED_SOURCE_REACHED":
            raise ValueError(
                "Source content extraction requires a verified source."
            )

        content = verified_source.content

        if not content or not content.strip():
            raise ValueError(
                "Verified source contains no usable content."
            )

        return {
            "source_url": verified_source.url,
            "final_url": verified_source.final_url,
            "content_type": verified_source.content_type,
            "status_code": verified_source.status_code,
            "content_length": verified_source.content_length,
            "content": content,
            "content_status": "AVAILABLE",
        }


__all__ = ["V12SourceContentExtractor"]
