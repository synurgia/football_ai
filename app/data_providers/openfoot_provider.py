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
        date = kwargs.get("date")

        if not competition and not date:
            raise ValueError(
                "OpenFoot requires either a competition ID or a date."
            )

        params = {}
        if competition:
            params["competition"] = competition
        if season:
            params["season"] = season
        if date:
            params["date"] = date

        response = httpx.get(
            f"{self.base_url}/matches",
            params=params,
            headers=self._headers(),
            timeout=kwargs.get("timeout", 30.0),
        )
        response.raise_for_status()

        body = response.json()
        data = body.get("data", [])

        if not isinstance(data, list):
            raise ValueError(
                "OpenFoot did not return a valid matches list."
            )

        self.last_matches_meta = body.get("meta", {})

        return [
            item
            for item in data
            if isinstance(item, dict)
        ]

    def get_all_matches(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Retrieve as many matches as OpenFoot permits.

        If pagination is denied by the provider, verified matches already
        retrieved are returned and metadata records that the dataset is
        incomplete. No missing matches are invented.
        """

        competition = kwargs.get("competition")
        season = kwargs.get("season")
        date = kwargs.get("date")

        if not competition and not date:
            raise ValueError(
                "OpenFoot requires either a competition ID or a date."
            )

        params = {}

        if competition:
            params["competition"] = competition

        if season:
            params["season"] = season

        if date:
            params["date"] = date

        all_matches: List[Dict[str, Any]] = []
        seen_cursors = set()
        page_count = 0
        pagination_error = None

        while True:
            response = httpx.get(
                f"{self.base_url}/matches",
                params=params,
                headers=self._headers(),
                timeout=kwargs.get("timeout", 30.0),
            )

            if response.status_code == 403:
                pagination_error = {
                    "status_code": 403,
                    "reason": "pagination_access_denied",
                    "url": str(response.request.url),
                }
                break

            response.raise_for_status()

            body = response.json()
            data = body.get("data", [])
            meta = body.get("meta", {})

            if not isinstance(data, list):
                raise ValueError(
                    "OpenFoot did not return a valid matches list."
                )

            page_count += 1

            all_matches.extend(
                item
                for item in data
                if isinstance(item, dict)
            )

            self.last_matches_meta = meta

            scope = meta.get("scope") or {}
            pagination = meta.get("pagination") or {}

            partial = bool(scope.get("partial", False))
            next_cursor = pagination.get("next_cursor")

            if not partial or not next_cursor:
                break

            if next_cursor in seen_cursors:
                pagination_error = {
                    "reason": "repeated_cursor",
                    "cursor": next_cursor,
                }
                break

            seen_cursors.add(next_cursor)
            params["cursor"] = next_cursor

        final_meta = dict(self.last_matches_meta or {})

        reported_total = final_meta.get("total_count")

        final_meta["retrieval"] = {
            "matches_retrieved": len(all_matches),
            "reported_total": reported_total,
            "complete": (
                pagination_error is None
                and (
                    reported_total is None
                    or len(all_matches) >= reported_total
                )
            ),
            "pages_retrieved": page_count,
            "pagination_error": pagination_error,
        }

        self.last_matches_meta = final_meta

        return all_matches

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
