from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import httpx


ESPN_LEAGUE_INDEX = (
    "https://sports.core.api.espn.com/v2/sports/soccer/leagues"
)


@dataclass
class ESPNCompetition:
    league_id: str
    slug: str
    name: str
    display_name: str
    country: Optional[str]
    country_code: Optional[str]
    season_year: Optional[int]
    season_start: Optional[str]
    season_end: Optional[str]
    gender: Optional[str]
    has_standings: bool
    has_stats: bool
    metadata_status: str = "VERIFIED"
    source: str = "espn_global_soccer"


class ESPNCompetitionCatalogue:
    """
    Discovers ESPN soccer competitions dynamically.

    This module only describes source coverage.
    It does NOT feed data into Pieces 1-9.
    """

    def __init__(self, timeout: float = 20.0):
        self.timeout = timeout

    def discover_league_ids(self) -> List[str]:
        params = {"limit": 1000}

        response = httpx.get(
            ESPN_LEAGUE_INDEX,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()

        leagues = data.get("items", [])
        ids = []

        for item in leagues:
            league_id = item.get("id")

            if not league_id:
                ref = item.get("$ref", "")
                marker = "/leagues/"
                if marker in ref:
                    league_id = ref.split(marker, 1)[1].split("?", 1)[0].strip("/")

            if league_id:
                ids.append(str(league_id))

        return ids

    def fetch_metadata(self, league_id: str) -> ESPNCompetition:
        url = f"{ESPN_LEAGUE_INDEX}/{league_id}"

        response = httpx.get(
            url,
            timeout=self.timeout,
        )

        if response.status_code != 200:
            return ESPNCompetition(
                league_id=league_id,
                slug=league_id,
                name="",
                display_name="",
                country=None,
                country_code=None,
                season_year=None,
                season_start=None,
                season_end=None,
                gender=None,
                has_standings=False,
                has_stats=False,
                metadata_status=f"HTTP_{response.status_code}",
            )

        data: Dict[str, Any] = response.json()

        country = data.get("country") or {}
        season = data.get("season") or {}
        season_type = season.get("type") or {}

        return ESPNCompetition(
            league_id=str(data.get("id") or league_id),
            slug=str(data.get("slug") or league_id),
            name=str(data.get("name") or ""),
            display_name=str(data.get("displayName") or ""),
            country=country.get("name"),
            country_code=country.get("abbreviation"),
            season_year=season.get("year"),
            season_start=season.get("startDate"),
            season_end=season.get("endDate"),
            gender=data.get("gender"),
            has_standings=bool(season_type.get("hasStandings")),
            has_stats=bool(season_type.get("hasStats")),
            metadata_status="VERIFIED",
        )

    def build(self) -> List[ESPNCompetition]:
        league_ids = self.discover_league_ids()

        catalogue = []

        for league_id in league_ids:
            catalogue.append(self.fetch_metadata(league_id))

        return catalogue

    @staticmethod
    def coverage_summary(
        catalogue: List[ESPNCompetition],
    ) -> Dict[str, Any]:
        countries = sorted(
            {
                item.country
                for item in catalogue
                if item.country
            }
        )

        country_codes = sorted(
            {
                item.country_code
                for item in catalogue
                if item.country_code
            }
        )

        verified = sum(
            item.metadata_status == "VERIFIED"
            for item in catalogue
        )

        failed = len(catalogue) - verified

        return {
            "competitions_discovered": len(catalogue),
            "metadata_verified": verified,
            "metadata_failed": failed,
            "countries_discovered": len(countries),
            "country_codes_discovered": len(country_codes),
            "countries": countries,
            "country_codes": country_codes,
        }

    @staticmethod
    def to_dict_list(
        catalogue: List[ESPNCompetition],
    ) -> List[Dict[str, Any]]:
        return [asdict(item) for item in catalogue]

    @staticmethod
    def save_catalogue(
        catalogue: List[ESPNCompetition],
        output_path: str = "data/espn_competition_catalogue.json",
    ) -> str:
        import json
        from pathlib import Path

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "source": "espn_global_soccer",
            "total_competitions": len(catalogue),
            "catalogue": [asdict(item) for item in catalogue],
        }

        temp = target.with_suffix(target.suffix + ".tmp")
        temp.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temp.replace(target)

        return str(target)

    @staticmethod
    def load_catalogue(
        input_path: str = "data/espn_competition_catalogue.json",
    ) -> List[ESPNCompetition]:
        import json
        from pathlib import Path

        target = Path(input_path)

        if not target.exists():
            return []

        payload = json.loads(target.read_text(encoding="utf-8"))

        return [
            ESPNCompetition(**item)
            for item in payload.get("catalogue", [])
        ]
