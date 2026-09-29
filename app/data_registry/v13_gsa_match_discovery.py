from __future__ import annotations

from typing import Any, Dict, Optional

from app.data_registry.v13_global_match_discovery import V13MatchDiscoveryProvider


class V13GSAMatchDiscovery(V13MatchDiscoveryProvider):
    """Global Sports Archive discovery provider.

    GSA is an independent evidence source.
    No undocumented endpoint or competition-specific URL is assumed here.
    """

    source_id = "gsa_global_football"
    source_name = "Global Sports Archive"

    def discover(
        self,
        *,
        team_a: str,
        team_b: str,
        match_date: Optional[str],
        competition_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        return {
            "status": "PROVIDER_NOT_YET_WIRED",
            "source_id": self.source_id,
            "source_name": self.source_name,
            "team_a": team_a,
            "team_b": team_b,
            "match_date": match_date,
            "competition_id": competition_id,
            "reason": (
                "GSA provider is registered but no verified "
                "match-query endpoint has been established."
            ),
        }
