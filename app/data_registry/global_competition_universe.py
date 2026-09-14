from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from app.data_registry.v1_3_competition_catalogue import V13_COMPETITION_CATALOGUE


@dataclass(frozen=True)
class CompetitionDefinition:
    competition_id: str
    competition_name: str
    country_code: Optional[str]
    region: str
    tier: str
    gender: str
    format: str
    season: str
    status: str = "DISCOVERED"


class GlobalCompetitionUniverse:
    """
    V1.3 catalogue of known football competitions.

    IMPORTANT:
    This catalogue records competition identity/discovery only.
    It does NOT claim that a data source is reachable or that
    fixtures are currently available.
    """

    def __init__(self) -> None:
        self._competitions: Dict[str, CompetitionDefinition] = {}

    def register(self, competition: CompetitionDefinition) -> None:
        if not competition.competition_id:
            raise ValueError("competition_id is required.")

        self._competitions[competition.competition_id] = competition

    def get(self, competition_id: str) -> Optional[CompetitionDefinition]:
        return self._competitions.get(competition_id)

    def all(self) -> List[CompetitionDefinition]:
        return list(self._competitions.values())

    def by_region(self, region: str) -> List[CompetitionDefinition]:
        return [
            competition
            for competition in self._competitions.values()
            if competition.region.lower() == region.lower()
        ]

    def by_country(self, country_code: str) -> List[CompetitionDefinition]:
        code = country_code.upper()

        return [
            competition
            for competition in self._competitions.values()
            if competition.country_code
            and competition.country_code.upper() == code
        ]

    def to_dict(self) -> List[Dict[str, object]]:
        return [
            asdict(competition)
            for competition in self._competitions.values()
        ]


def build_v13_global_competition_universe() -> GlobalCompetitionUniverse:
    """
    Build the V1.3 competition universe directly from the authoritative
    191-entry V1.3 competition catalogue.

    This layer records competition identity/discovery only. It does not
    claim source reachability, fixture availability, or verified coverage.
    """
    universe = GlobalCompetitionUniverse()

    for item in V13_COMPETITION_CATALOGUE:
        universe.register(
            CompetitionDefinition(
                competition_id=item["competition_id"],
                competition_name=item["name"],
                country_code=None,
                region=item["region"],
                tier="UNKNOWN",
                gender="UNKNOWN",
                format="UNKNOWN",
                season="UNKNOWN",
                status="DISCOVERED",
            )
        )

    return universe
