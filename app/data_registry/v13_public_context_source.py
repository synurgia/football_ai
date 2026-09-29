from __future__ import annotations

from typing import Any, Dict, Optional


class V13PublicContextSourceProvider:
    """
    V1.3 public-context provider.

    Covers lawful public context such as market/public information.
    This evidence class is kept separate from football-performance evidence.
    """

    source_id = "public_context"
    source_name = "Lawful Public Context Sources"
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
            "reason": "Verified lawful public-context routing required before activation",
        }
