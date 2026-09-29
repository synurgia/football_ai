from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List

import httpx

from app.data_registry.v13_candidate_source_catalog import get_all_candidate_sources


RESULT_FILE = Path("data/v13_candidate_source_verification_results.json")


class V13CandidateSourceVerification:
    """
    V1.3 Phase 2 URL verification.

    Verifies actual HTTP reachability and returned content.
    Uses bounded concurrency and persists every result immediately.
    Does not infer football coverage, freshness, or evidence usefulness.
    """

    def __init__(self, timeout: float = 20.0, workers: int = 12) -> None:
        self.timeout = timeout
        self.workers = workers
        RESULT_FILE.parent.mkdir(parents=True, exist_ok=True)

    def verify_source(self, source: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "source_id": source["source_id"],
            "name": source["name"],
            "base_url": source["base_url"],
            "region": source.get("region", ""),
            "layer": source.get("layer", ""),
            "coverage_scope": source.get("coverage_scope", ""),
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            response = httpx.get(
                source["base_url"],
                headers={
                    "Accept": "text/html,application/json,text/plain",
                    "User-Agent": "FootballAI-V1.3-SourceVerifier/1.0",
                },
                timeout=self.timeout,
                follow_redirects=True,
            )

            content_type = response.headers.get("content-type")
            content = response.text

            if response.status_code >= 400:
                status = "FAILED"
                reason = f"HTTP {response.status_code}"
            elif not content.strip():
                status = "PARTIAL"
                reason = "Source returned an empty response."
            else:
                status = "VERIFIED"
                reason = None

            result.update({
                "status": status,
                "verification_status": (
                    "VERIFIED_SOURCE_REACHED"
                    if status == "VERIFIED"
                    else "INSUFFICIENT_EVIDENCE"
                    if status == "PARTIAL"
                    else "FAILED"
                ),
                "reachable": status == "VERIFIED",
                "final_url": str(response.url),
                "status_code": response.status_code,
                "content_type": content_type,
                "content_length": len(content),
                "reason": reason,
            })

        except Exception as exc:
            result.update({
                "status": "FAILED",
                "verification_status": "FAILED",
                "reachable": False,
                "final_url": None,
                "status_code": None,
                "content_type": None,
                "content_length": None,
                "reason": str(exc),
            })

        return result

    def save_result(self, result: Dict[str, Any]) -> None:
        existing = {}

        if RESULT_FILE.exists():
            try:
                existing = {
                    x["source_id"]: x
                    for x in json.loads(RESULT_FILE.read_text())
                }
            except Exception:
                existing = {}

        existing[result["source_id"]] = result

        RESULT_FILE.write_text(
            json.dumps(
                list(existing.values()),
                indent=2,
                ensure_ascii=False,
            )
        )

    def verify_all(self) -> List[Dict[str, Any]]:
        sources = get_all_candidate_sources()
        results = []

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {
                executor.submit(self.verify_source, source): source
                for source in sources
            }

            for future in as_completed(futures):
                result = future.result()
                self.save_result(result)
                results.append(result)
                print(
                    f"[{len(results)}/{len(sources)}] "
                    f"{result['status']} | "
                    f"{result['source_id']}"
                )

        return results


if __name__ == "__main__":
    verifier = V13CandidateSourceVerification()
    results = verifier.verify_all()

    counts = {}
    for result in results:
        status = result["status"]
        counts[status] = counts.get(status, 0) + 1

    print()
    print("V1.3 CANDIDATE SOURCE VERIFICATION")
    print("===================================")
    print("TOTAL:", len(results))
    print("VERIFIED:", counts.get("VERIFIED", 0))
    print("PARTIAL:", counts.get("PARTIAL", 0))
    print("FAILED:", counts.get("FAILED", 0))
    print("SAVED:", RESULT_FILE)
