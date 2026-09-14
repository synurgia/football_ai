from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class CompetitionSource:
    """
    Describes one legitimate football-data source for one competition.

    Coverage is explicit so the system never silently substitutes
    one competition for another.
    """

    competition_id: str
    competition_name: str
    source_name: str
    source_url: str
    coverage_status: str
    notes: str = ""


class CompetitionRegistry:
    """
    Registry of known football competitions and their data sources.
    """

    def __init__(self) -> None:
        self._sources: Dict[str, CompetitionSource] = {}

    def register(self, source: CompetitionSource) -> None:
        self._sources[source.competition_id] = source

    def get(self, competition_id: str) -> Optional[CompetitionSource]:
        return self._sources.get(competition_id)

    def list_competitions(self) -> List[CompetitionSource]:
        return list(self._sources.values())

    def is_available(self, competition_id: str) -> bool:
        source = self.get(competition_id)

        return (
            source is not None
            and source.coverage_status == "available"
        )
