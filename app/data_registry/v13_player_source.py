from __future__ import annotations

from typing import Any, Dict, Optional


class V13PlayerSourceProvider:
    """
    V1.3 player evidence provider.

    Candidate sources: official club/league pages and
    football-data.org where player resources are available.

    No paid API is assumed.
    """

    source_id = "official_player"
    source_name = "Official Club / League Player Sources"
    access_policy = "PUBLIC_FREE_WHERE_AVAILABLE"

    def retrieve(
        self,
        *,
        player_name: str,
        competition_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        return {
            "status": "PROVIDER_NOT_YET_WIRED",
            "source_id": self.source_id,
            "source_name": self.source_name,
            "access_policy": self.access_policy,
            "player_name": player_name,
            "competition_id": competition_id,
            "reason": "Verified player-source routing required before activation",
        }
