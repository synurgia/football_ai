from __future__ import annotations

from typing import Any, Dict, Optional

from app.data_registry.v13_global_match_discovery import (
    V13MatchDiscoveryProvider,
)


class V13OfficialCompetitionDiscovery(V13MatchDiscoveryProvider):
    """
    Official competition/federation source provider.

    The competition-specific URL/query is supplied later by the
    source-routing/verification layer. No universal official URL
    is invented here.
    """

    source_id = "official_competition"
    source_name = "Official Competition / Federation"

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
            "reason": "Competition-specific official source routing required",
        }
