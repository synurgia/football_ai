from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class V13MatchDiscoveryProvider(ABC):
    """Provider-neutral interface for discovering one requested football match."""

    source_id: str
    source_name: str

    @abstractmethod
    def discover(
        self,
        *,
        team_a: str,
        team_b: str,
        match_date: Optional[str],
        competition_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError


class V13GlobalMatchDiscovery:
    """
    Global V1.3 match-discovery coordinator.

    It does not assign source priority.
    It does not perform prediction.
    It does not modify Pieces 1-9.
    It preserves every provider result so disagreement can be handled later.
    """

    def __init__(self, providers: Optional[List[V13MatchDiscoveryProvider]] = None):
        self.providers = providers or []

    def discover(
        self,
        *,
        team_a: str,
        team_b: str,
        match_date: Optional[str],
        competition_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = []

        for provider in self.providers:
            try:
                result = provider.discover(
                    team_a=team_a,
                    team_b=team_b,
                    match_date=match_date,
                    competition_id=competition_id,
                )
            except Exception as exc:
                result = {
                    "status": "SOURCE_FAILED",
                    "source_id": provider.source_id,
                    "source_name": provider.source_name,
                    "error": str(exc),
                }

            results.append(result)

        found = [
            result
            for result in results
            if result.get("status") == "FOUND"
        ]

        if not found:
            return {
                "status": "INSUFFICIENT_EVIDENCE",
                "team_a": team_a,
                "team_b": team_b,
                "match_date": match_date,
                "competition_id": competition_id,
                "sources": results,
            }

        return {
            "status": "FOUND",
            "team_a": team_a,
            "team_b": team_b,
            "match_date": match_date,
            "competition_id": competition_id,
            "candidates": found,
            "sources": results,
        }
