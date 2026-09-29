from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class SearchCandidate:
    query: str
    url: str
    title: str = ""
    snippet: str = ""
    provider: str = ""
    discovered_at: str = ""
    access_type: str = "PUBLIC_WEB"


class V13SearchDiscovery:
    """
    V1.3 additive search-discovery layer.

    Search providers discover public information.
    They do not become authoritative football-data providers.

    No competition ID is invented here.
    Verification belongs to the existing evidence layer.
    """

    def __init__(self) -> None:
        self.providers: List[str] = []

    @staticmethod
    def needs_identity_enrichment(fixture):
        """
        Return True when the fixture lacks a usable V1.3 competition ID.
        Never invents or infers an ID.
        """
        return not bool(
            fixture.get("competition_id")
        )

    @staticmethod
    def build_queries(
        home_team: str,
        away_team: str,
        competition: Optional[str] = None,
    ) -> List[str]:
        queries = [
            f'"{home_team}" "{away_team}" football',
            f'"{home_team}" vs "{away_team}" football',
            f'"{home_team}" "{away_team}" fixture',
            f'"{home_team}" "{away_team}" competition',
        ]

        if competition:
            queries.append(
                f'"{home_team}" "{away_team}" "{competition}"'
            )

        return queries

    @staticmethod
    def candidate_from_result(
        query: str,
        result: Dict[str, Any],
        provider: str,
    ) -> Optional[SearchCandidate]:
        url = result.get("url")

        if not url:
            return None

        return SearchCandidate(
            query=query,
            url=str(url),
            title=str(result.get("title") or ""),
            snippet=str(result.get("snippet") or ""),
            provider=provider,
            discovered_at=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def serialize(
        candidates: List[SearchCandidate],
    ) -> List[Dict[str, Any]]:
        return [asdict(candidate) for candidate in candidates]
