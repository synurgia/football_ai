from __future__ import annotations

from typing import Any, Dict, Optional


class V13MatchCentreSourceProvider:
    """
    V1.3 official match-centre evidence provider.

    Intended evidence:
    - fixture identity
    - kickoff/status
    - score
    - lineups
    - events
    - cards
    - substitutions
    - venue
    """

    source_id = "official_match_centre"
    source_name = "Official Competition Match Centres"
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
            "reason": "Verified competition-specific match-centre routing required before activation",
        }
