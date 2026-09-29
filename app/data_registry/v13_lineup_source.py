from __future__ import annotations

from typing import Any, Dict, Optional


class V13LineupSourceProvider:
    """
    V1.3 lineup evidence provider.

    Candidate sources:
    - Official competition match centres
    - Official club match pages
    - Public match-centre pages where legally/publicly accessible

    No paid API is assumed.
    """

    source_id = "official_lineup"
    source_name = "Official Match-Centre Lineup Sources"
    access_policy = "PUBLIC_FREE_WHERE_AVAILABLE"

    def retrieve(
        self,
        *,
        team_a: str,
        team_b: str,
        match_date: str,
        competition_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        return {
            "status": "PROVIDER_NOT_YET_WIRED",
            "source_id": self.source_id,
            "source_name": self.source_name,
            "access_policy": self.access_policy,
            "team_a": team_a,
            "team_b": team_b,
            "match_date": match_date,
            "competition_id": competition_id,
            "reason": "Verified competition-specific lineup routing required before activation",
        }
