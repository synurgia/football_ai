from typing import Any, Dict

import httpx

from app.data_providers.base_provider import FootballDataProvider


class PublicFootballProvider(FootballDataProvider):
    """
    Provider for publicly available football data.

    This provider retrieves the complete raw dataset and keeps
    source-specific fetching separate from the analytical pipeline.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def get_dataset(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Fetch the complete raw football dataset.
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
            raise ValueError(
                "Football data source did not return a JSON object."
            )

        matches = data.get("matches")

        if not isinstance(matches, list):
            raise ValueError(
                "Football data source did not provide a valid matches list."
            )

        return data

    def get_matches(self, **kwargs: Any):
        """
        Backward-compatible method returning only match records.
        """

        data = self.get_dataset(**kwargs)

        return [
            match
            for match in data["matches"]
            if isinstance(match, dict)
        ]
