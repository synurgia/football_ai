from app.data_registry.competition_registry import (
    CompetitionRegistry,
    CompetitionSource,
)


def build_default_registry() -> CompetitionRegistry:
    """
    Build the default competition registry from verified sources.

    Only competitions whose real external source has been tested
    successfully are registered as available.
    """

    registry = CompetitionRegistry()

    registry.register(
        CompetitionSource(
            competition_id="eng.1",
            competition_name="English Premier League 2026/27",
            source_name="openfootball",
            source_url="https://raw.githubusercontent.com/openfootball/football.json/master/2026-27/en.1.json",
            coverage_status="available",
        )
    )

    registry.register(
        CompetitionSource(
            competition_id="ita.1",
            competition_name="Italian Serie A 2026/27",
            source_name="openfootball",
            source_url="https://raw.githubusercontent.com/openfootball/football.json/master/2026-27/it.1.json",
            coverage_status="available",
        )
    )

    return registry
