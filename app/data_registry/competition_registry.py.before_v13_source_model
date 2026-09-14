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
    Registry of football competitions and their available data sources.

    Multiple sources may be registered for the same competition.
    Legacy get() behavior is preserved for existing consumers.
    Federation-aware consumers should use get_all().
    """

    def __init__(self) -> None:
        self._sources: Dict[str, List[CompetitionSource]] = {}

    def register(self, source: CompetitionSource) -> None:
        sources = self._sources.setdefault(source.competition_id, [])

        for index, existing in enumerate(sources):
            if (
                existing.source_name == source.source_name
                and existing.source_url == source.source_url
            ):
                sources[index] = source
                return

        sources.append(source)

    def get(self, competition_id: str) -> Optional[CompetitionSource]:
        """
        Backward-compatible accessor.

        Returns the first registered source for legacy consumers.
        Federation-aware code should use get_all() so no source is discarded.
        """
        sources = self._sources.get(competition_id, [])
        return sources[0] if sources else None

    def get_all(self, competition_id: str) -> List[CompetitionSource]:
        """
        Return all registered sources for a competition.
        """
        return list(self._sources.get(competition_id, []))

    def list_competitions(self) -> List[CompetitionSource]:
        """
        Preserve the legacy flattened competition listing.
        """
        return [
            source
            for sources in self._sources.values()
            for source in sources
        ]

    def is_available(self, competition_id: str) -> bool:
        """
        A competition is available when at least one registered source
        explicitly reports available coverage.
        """
        return any(
            source.coverage_status == "available"
            for source in self._sources.get(competition_id, [])
        )
