from __future__ import annotations

from typing import Any, Dict, Optional

from app.v13_ai_intelligence_engine import http_get


class V13OpenMeteoWeatherProvider:
    """
    V1.3 weather evidence provider.

    Open-Meteo is free, requires no API key for the free non-commercial API,
    and provides global weather coverage.

    This provider collects weather evidence only.
    It does not discover matches, assign source priority, or predict outcomes.
    """

    source_id = "open_meteo"
    source_name = "Open-Meteo"

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def retrieve(
        self,
        *,
        latitude: float,
        longitude: float,
        match_date: str,
    ) -> Dict[str, Any]:

        try:
            response = http_get(
                self.BASE_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "start_date": match_date,
                    "end_date": match_date,
                    "hourly": (
                        "temperature_2m,"
                        "relative_humidity_2m,"
                        "precipitation,"
                        "precipitation_probability,"
                        "wind_speed_10m,"
                        "weather_code"
                    ),
                },
                timeout=15,
            )
        except Exception as exc:
            return {
                "status": "SOURCE_FAILED",
                "source_id": self.source_id,
                "source_name": self.source_name,
                "error": str(exc),
            }

        if response.status_code != 200:
            return {
                "status": "SOURCE_UNAVAILABLE",
                "source_id": self.source_id,
                "source_name": self.source_name,
                "http_status": response.status_code,
            }

        try:
            payload = response.json()
        except Exception as exc:
            return {
                "status": "SOURCE_FAILED",
                "source_id": self.source_id,
                "source_name": self.source_name,
                "error": f"Invalid JSON response: {exc}",
            }

        return {
            "status": "FOUND",
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_url": self.BASE_URL,
            "match_date": match_date,
            "latitude": latitude,
            "longitude": longitude,
            "weather": payload,
        }
