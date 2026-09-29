from __future__ import annotations

from typing import Any, Dict, Optional


class V13NationalMeteorologicalWeatherProvider:
    """
    V1.3 national meteorological-service evidence provider.

    This is a provider-neutral slot for official national weather services.
    Activation is country-specific and only occurs where the official
    service exposes usable public/free data.

    No paid API is assumed.
    No API key is invented.
    """

    source_id = "national_meteorological_service"
    source_name = "National Meteorological Services"
    access_policy = "PUBLIC_FREE_WHERE_AVAILABLE"

    def retrieve(
        self,
        *,
        country: str,
        latitude: float,
        longitude: float,
        match_date: str,
    ) -> Dict[str, Any]:

        return {
            "status": "PROVIDER_NOT_YET_WIRED",
            "source_id": self.source_id,
            "source_name": self.source_name,
            "access_policy": self.access_policy,
            "country": country,
            "latitude": latitude,
            "longitude": longitude,
            "match_date": match_date,
            "reason": (
                "Country-specific official meteorological routing must be "
                "verified before activation"
            ),
        }
