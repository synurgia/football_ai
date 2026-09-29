from __future__ import annotations

from typing import Any, Dict, Optional


class V13ScheduleSourceProvider:
    """
    V1.3 schedule evidence provider.

    Candidate sources:
    - Official competition calendars
    - Official club fixture calendars
    - football-data.org where covered

    No paid API is assumed.
    """

    source_id = "official_schedule"
    source_name = "Official Competition / Club Schedule Sources"
    access_policy = "PUBLIC_FREE_WHERE_AVAILABLE"

    def retrieve(
        self,
        *,
        team_name: Optional[str] = None,
        competition_id: Optional[str] = None,
        match_date: Optional[str] = None,
    ) -> Dict[str, Any]:

        return {
            "status": "PROVIDER_NOT_YET_WIRED",
            "source_id": self.source_id,
            "source_name": self.source_name,
            "access_policy": self.access_policy,
            "team_name": team_name,
            "competition_id": competition_id,
            "match_date": match_date,
            "reason": "Verified competition/club schedule routing required before activation",
        }
