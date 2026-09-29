from __future__ import annotations

from typing import Any, Dict, Optional


class V13TacticalSourceProvider:
    """
    V1.3 tactical evidence provider.

    Candidate sources:
    - Official match reports
    - Public official match-centre event data
    - Club reports
    - Other verified public tactical evidence

    Tactical conclusions must not be invented when evidence is absent.
    """

    source_id = "tactical_evidence"
    source_name = "Public Tactical Evidence Sources"
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
            "reason": "Verified tactical evidence routing required before activation",
        }
