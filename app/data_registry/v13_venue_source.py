from __future__ import annotations

from typing import Any, Dict, Optional


class V13VenueSourceProvider:
    """
    V1.3 venue/stadium evidence provider.

    Source routing is supplied later from verified official club,
    competition, stadium, or municipal pages.

    No paid API is assumed and no URL is invented.
    """

    source_id = "official_venue"
    source_name = "Official Venue / Stadium Sources"
    access_policy = "PUBLIC_FREE_WHERE_AVAILABLE"

    def retrieve(
        self,
        *,
        venue_name: str,
        country: Optional[str] = None,
    ) -> Dict[str, Any]:

        return {
            "status": "PROVIDER_NOT_YET_WIRED",
            "source_id": self.source_id,
            "source_name": self.source_name,
            "access_policy": self.access_policy,
            "venue_name": venue_name,
            "country": country,
            "reason": (
                "Verified official venue/stadium routing required "
                "before activation"
            ),
        }
