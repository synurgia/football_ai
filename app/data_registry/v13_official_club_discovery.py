from __future__ import annotations

from typing import Any, Dict, Optional

from app.data_registry.v13_global_match_discovery import (
    V13MatchDiscoveryProvider,
)


class V13OfficialClubDiscovery(V13MatchDiscoveryProvider):
    """
    Official club source provider.

    Club-specific source routing is supplied later. This provider does
    not invent club URLs or assume that every club exposes the same API.
    """

    source_id = "official_club"
    source_name = "Official Club Sources"

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
            "reason": "Club-specific official source routing required",
        }
