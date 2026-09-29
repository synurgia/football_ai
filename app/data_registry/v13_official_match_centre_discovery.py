from __future__ import annotations

from typing import Any, Dict, Optional

from app.data_registry.v13_global_match_discovery import (
    V13MatchDiscoveryProvider,
)


class V13OfficialMatchCentreDiscovery(V13MatchDiscoveryProvider):
    """
    Official match-centre provider.

    Match-centre URLs and query patterns vary by competition, so this
    provider deliberately waits for verified source routing.
    """

    source_id = "official_match_centre"
    source_name = "Official Match Centres"

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
            "reason": "Competition-specific match-centre routing required",
        }
