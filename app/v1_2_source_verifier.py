"""
V1.2 Source Verifier

Purpose:
    Validate and fetch an underlying source page discovered by a
    discovery mechanism.

Rules:
    - Search engines remain discovery-only.
    - The candidate URL itself is not treated as verified merely
      because it came from a search engine.
    - Verification means the underlying URL was successfully reached.
    - This layer does not answer the 37 questions.
    - This layer does not modify Pieces 1-9.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx


@dataclass
class VerifiedSource:
    url: str
    status: str
    final_url: Optional[str] = None
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    content_length: Optional[int] = None
    content: Optional[str] = None
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class V12SourceVerifier:
    """
    Fetches an underlying source page and records what was actually
    observed. It does not determine whether the page's claims are true.
    """

    def __init__(self, timeout: float = 20.0):
        self.timeout = timeout

    @staticmethod
    def _validate_url(url: str) -> None:
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Source URL must use HTTP or HTTPS.")

        if not parsed.netloc:
            raise ValueError("Source URL must contain a valid host.")

    def verify(self, url: str) -> VerifiedSource:
        self._validate_url(url)

        try:
            response = httpx.get(
                url,
                headers={
                    "Accept": "text/html,application/json,text/plain",
                    "User-Agent": "FootballAI-V1.2-SourceVerifier/1.0",
                },
                timeout=httpx.Timeout(self.timeout, connect=min(self.timeout, 5.0), read=min(self.timeout, 5.0), write=min(self.timeout, 5.0), pool=min(self.timeout, 5.0)),
                follow_redirects=True,
            )

            content_type = response.headers.get("content-type")
            content = response.text

            if response.status_code >= 400:
                return VerifiedSource(
                    url=url,
                    status="FAILED",
                    final_url=str(response.url),
                    status_code=response.status_code,
                    content_type=content_type,
                    content_length=len(content),
                    reason=f"HTTP {response.status_code}",
                )

            if not content.strip():
                return VerifiedSource(
                    url=url,
                    status="INSUFFICIENT_EVIDENCE",
                    final_url=str(response.url),
                    status_code=response.status_code,
                    content_type=content_type,
                    content_length=0,
                    reason="Source returned an empty response.",
                )

            return VerifiedSource(
                url=url,
                status="VERIFIED_SOURCE_REACHED",
                final_url=str(response.url),
                status_code=response.status_code,
                content_type=content_type,
                content_length=len(content),
                content=content,
            )

        except Exception as exc:
            return VerifiedSource(
                url=url,
                status="FAILED",
                reason=str(exc),
            )


__all__ = [
    "VerifiedSource",
    "V12SourceVerifier",
]
