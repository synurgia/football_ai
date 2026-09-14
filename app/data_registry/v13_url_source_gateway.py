"""
V1.3 URL Source Gateway

Purpose:
- Accept an explicit source URL.
- Retrieve the underlying source directly.
- Never use search engines as data sources.
- Never assign source priority.
- Never claim a source is verified merely because it is registered.
- Preserve successful source content.
- Return a controlled failure when the URL is unavailable.
- Do not modify analytical Pieces 1-9.
"""

from typing import Any, Dict
from app.v1_2_source_verifier import V12SourceVerifier


class V13URLSourceGateway:
    """Controlled gateway for explicit football-data source URLs."""

    def __init__(self, timeout: float = 20.0) -> None:
        self.verifier = V12SourceVerifier(timeout=timeout)

    def retrieve(
        self,
        *,
        source_id: str,
        source_name: str,
        source_url: str,
        competition_id: str,
        competition_name: str,
    ) -> Dict[str, Any]:
        verified = self.verifier.verify(source_url)

        if verified.status != "VERIFIED_SOURCE_REACHED":
            return {
                "status": "SOURCE_UNAVAILABLE",
                "source_id": source_id,
                "source_name": source_name,
                "source_url": source_url,
                "competition_id": competition_id,
                "competition_name": competition_name,
                "verification_status": verified.status,
                "status_code": verified.status_code,
                "content_type": verified.content_type,
                "reason": verified.reason,
                "data_available": False,
            }

        return {
            "status": "SOURCE_RETRIEVED",
            "source_id": source_id,
            "source_name": source_name,
            "source_url": source_url,
            "final_url": verified.final_url,
            "competition_id": competition_id,
            "competition_name": competition_name,
            "verification_status": verified.status,
            "status_code": verified.status_code,
            "content_type": verified.content_type,
            "content_length": verified.content_length,
            "content": verified.content,
            "data_available": True,
        }


def _test() -> None:
    gateway = V13URLSourceGateway(timeout=10.0)

    result = gateway.retrieve(
        source_id="test_source",
        source_name="Explicit URL Test",
        source_url="https://example.com",
        competition_id="test.1",
        competition_name="V1.3 Test Competition",
    )

    print("=" * 50)
    print("V1.3 URL SOURCE GATEWAY TEST")
    print("=" * 50)
    print("STATUS:", result["status"])
    print("SOURCE:", result["source_name"])
    print("VERIFICATION:", result["verification_status"])
    print("DATA AVAILABLE:", result["data_available"])

    if result["status"] != "SOURCE_RETRIEVED":
        raise RuntimeError("V1.3 URL source gateway failed.")

    if not result.get("content"):
        raise RuntimeError("Gateway retrieved no source content.")

    print("RESULT: PASS")


if __name__ == "__main__":
    _test()
