from __future__ import annotations

from typing import Any, Dict, Optional


class V13ResultsStatisticsSourceProvider:
    """
    V1.3 results/statistics evidence provider.

    Candidate sources:
    - football-data.org where covered
    - official league/federation results
    - public official match centres

    No paid API is assumed.
    """

    source_id = "results_statistics"
    source_name = "Results / Statistics Sources"
    access_policy = "PUBLIC_FREE_WHERE_AVAILABLE"

    def retrieve(
        self,
        *,
        team_a: str,
        team_b: str,
        match_date: Optional[str] = None,
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
            "reason": "Verified competition/source routing required before activation",
        }
