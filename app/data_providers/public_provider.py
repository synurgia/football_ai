from typing import Any, Dict, List

import httpx

from app.data_providers.base_provider import FootballDataProvider


class PublicFootballProvider(FootballDataProvider):
    """
    Provider for publicly available football data.

    This provider retrieves raw football data and keeps it separate
    from the analytical pipeline.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def get_matches(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Fetch raw match records from the configured public source.
        """

        timeout = kwargs.get("timeout", 20.0)

        response = httpx.get(
            self.base_url,
            timeout=timeout,
            follow_redirects=True,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            raise ValueError("Football data source did not return a JSON object.")

        matches = data.get("matches")

        if not isinstance(matches, list):
            raise ValueError(
                "Football data source did not provide a valid matches list."
            )

        return [
            match
            for match in matches
            if isinstance(match, dict)
        ]
