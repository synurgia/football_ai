from typing import Any, Dict, List
import httpx

from app.data_providers.base_provider import FootballDataProvider


class OpenFootProvider(FootballDataProvider):
    """
    OpenFoot API provider.

    Fetching is isolated here so the analytical engine and
    existing OpenFootball provider remain unchanged.
    """

    def __init__(
        self,
        base_url: str = "https://openfootapi.com/v1",
        api_key: str = "of_demo_openfootapi_docs",
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def get_competitions(self, **kwargs: Any) -> List[Dict[str, Any]]:
        response = httpx.get(
            f"{self.base_url}/competitions",
            headers=self._headers(),
            timeout=kwargs.get("timeout", 30.0),
        )
        response.raise_for_status()

        data = response.json().get("data", [])

        if not isinstance(data, list):
            raise ValueError("OpenFoot did not return a valid competition list.")

        return [item for item in data if isinstance(item, dict)]

    def get_matches(self, **kwargs: Any) -> List[Dict[str, Any]]:
        competition = kwargs.get("competition")
        season = kwargs.get("season")

        if not competition:
            raise ValueError("OpenFoot requires a competition ID.")

        params = {"competition": competition}

        if season:
            params["season"] = season

        response = httpx.get(
            f"{self.base_url}/matches",
            params=params,
            headers=self._headers(),
            timeout=kwargs.get("timeout", 30.0),
        )
        response.raise_for_status()

        data = response.json().get("data", [])

        if not isinstance(data, list):
            raise ValueError("OpenFoot did not return a valid matches list.")

        return [item for item in data if isinstance(item, dict)]


    def get_standings(self, **kwargs: Any) -> List[Dict[str, Any]]:
        competition = kwargs.get("competition")

        if not competition:
            raise ValueError("OpenFoot requires a competition ID.")

        response = httpx.get(
            f"{self.base_url}/standings",
            params={"competition": competition},
            headers=self._headers(),
            timeout=kwargs.get("timeout", 30.0),
        )
        response.raise_for_status()

        data = response.json().get("data", [])

        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]

        if isinstance(data, dict):
            return [data]

        raise ValueError("OpenFoot did not return a valid standings response.")
