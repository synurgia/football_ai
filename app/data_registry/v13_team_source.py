from __future__ import annotations

from typing import Any, Dict, Optional


class V13TeamSourceProvider:
    """
    V1.3 team evidence provider.

    Candidate sources: official club pages, official league pages,
    and football-data.org where the competition is covered.

    No paid API is assumed.
    """

    source_id = "official_team"
    source_name = "Official Club / League Team Sources"
    access_policy = "PUBLIC_FREE_WHERE_AVAILABLE"

    def retrieve(
        self,
        *,
        team_name: str,
        competition_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        return {
            "status": "PROVIDER_NOT_YET_WIRED",
            "source_id": self.source_id,
            "source_name": self.source_name,
            "access_policy": self.access_policy,
            "team_name": team_name,
            "competition_id": competition_id,
            "reason": "Verified team-source routing required before activation",
        }
