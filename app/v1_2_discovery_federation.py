"""
V1.2 Discovery Federation

Purpose:
    Provide a common discovery interface for Google, Bing, Brave, and Yandex.

Rules:
    - Search engines are discovery-only.
    - Search results are NOT evidence.
    - Missing credentials/configuration are reported honestly.
    - Failed requests are reported separately.
    - No Piece 1-9 logic is touched.
    - No 37-question answers are generated here.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import os
import httpx


@dataclass
class DiscoveryCandidate:
    engine: str
    title: Optional[str] = None
    url: Optional[str] = None
    snippet: Optional[str] = None
    status: str = "DISCOVERED"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class V12DiscoveryFederation:
    """
    Common discovery layer for configured search engines.

    This component discovers candidate source pages only.
    It never promotes a search result to authoritative evidence.
    """

    ENGINES = (
        "google_search",
        "bing_search",
        "brave_search",
        "yandex_search",
    )

    ENV_KEYS = {
        "google_search": "V12_GOOGLE_SEARCH_URL",
        "bing_search": "V12_BING_SEARCH_URL",
        "brave_search": "V12_BRAVE_SEARCH_URL",
        "yandex_search": "V12_YANDEX_SEARCH_URL",
    }

    KEY_ENV_KEYS = {
        "google_search": "V12_GOOGLE_SEARCH_API_KEY",
        "bing_search": "V12_BING_SEARCH_API_KEY",
        "brave_search": "V12_BRAVE_SEARCH_API_KEY",
        "yandex_search": "V12_YANDEX_SEARCH_API_KEY",
    }

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout

    def configured_engines(self) -> List[str]:
        return [
            engine
            for engine in self.ENGINES
            if os.getenv(self.ENV_KEYS[engine])
            and os.getenv(self.KEY_ENV_KEYS[engine])
        ]

    def status(self) -> Dict[str, str]:
        result: Dict[str, str] = {}

        for engine in self.ENGINES:
            url_configured = bool(os.getenv(self.ENV_KEYS[engine]))
            key_configured = bool(os.getenv(self.KEY_ENV_KEYS[engine]))

            if url_configured and key_configured:
                result[engine] = "CONFIGURED"
            elif url_configured or key_configured:
                result[engine] = "PARTIALLY_CONFIGURED"
            else:
                result[engine] = "NOT_CONFIGURED"

        return result

    def discover(
        self,
        query: str,
        engines: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if not query or not query.strip():
            raise ValueError("Discovery query cannot be empty.")

        requested = engines or list(self.ENGINES)

        invalid = [engine for engine in requested if engine not in self.ENGINES]
        if invalid:
            raise ValueError(
                f"Unsupported discovery engine(s): {', '.join(invalid)}"
            )

        candidates: List[DiscoveryCandidate] = []
        engine_results: Dict[str, Dict[str, Any]] = {}

        for engine in requested:
            endpoint = os.getenv(self.ENV_KEYS[engine])
            api_key = os.getenv(self.KEY_ENV_KEYS[engine])

            if not endpoint or not api_key:
                engine_results[engine] = {
                    "status": "NOT_CONFIGURED",
                    "candidate_count": 0,
                }
                continue

            try:
                response = httpx.get(
                    endpoint,
                    params={"q": query},
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Accept": "application/json",
                    },
                    timeout=self.timeout,
                    follow_redirects=True,
                )
                response.raise_for_status()

                payload = response.json()
                discovered = self._normalize(engine, payload)

                candidates.extend(discovered)

                engine_results[engine] = {
                    "status": "DISCOVERED",
                    "candidate_count": len(discovered),
                }

            except Exception as exc:
                engine_results[engine] = {
                    "status": "FAILED",
                    "candidate_count": 0,
                    "reason": str(exc),
                }

        return {
            "query": query,
            "engines_requested": requested,
            "engines_configured": self.configured_engines(),
            "engine_results": engine_results,
            "candidate_count": len(candidates),
            "candidates": [
                candidate.to_dict()
                for candidate in candidates
            ],
            "evidence_status": "DISCOVERY_ONLY",
        }

    @staticmethod
    def _normalize(
        engine: str,
        payload: Any,
    ) -> List[DiscoveryCandidate]:
        """
        Normalize common search-result shapes.

        The normalized objects remain discovery candidates.
        They are not authoritative evidence.
        """

        if not isinstance(payload, dict):
            return []

        raw_items = (
            payload.get("items")
            or payload.get("results")
            or payload.get("webPages", {}).get("value")
            or payload.get("organic")
            or []
        )

        if not isinstance(raw_items, list):
            return []

        candidates: List[DiscoveryCandidate] = []

        for item in raw_items:
            if not isinstance(item, dict):
                continue

            url = (
                item.get("url")
                or item.get("link")
                or item.get("href")
            )

            title = item.get("title")
            snippet = (
                item.get("snippet")
                or item.get("description")
            )

            if not url:
                continue

            candidates.append(
                DiscoveryCandidate(
                    engine=engine,
                    title=title,
                    url=url,
                    snippet=snippet,
                )
            )

        return candidates


__all__ = [
    "DiscoveryCandidate",
    "V12DiscoveryFederation",
]
