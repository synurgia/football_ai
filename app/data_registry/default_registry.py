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

    registry.register(
        CompetitionSource(
            competition_id="de.1",
            competition_name="Deutsche Bundesliga 2026/27",
            source_name="openfootball",
            source_url="https://raw.githubusercontent.com/openfootball/football.json/master/2026-27/de.1.json",
            coverage_status="available",
        )
    )

    registry.register(
        CompetitionSource(
            competition_id="es.1",
            competition_name="Spain Primera División 2026/27",
            source_name="openfootball",
            source_url="https://raw.githubusercontent.com/openfootball/football.json/master/2026-27/es.1.json",
            coverage_status="available",
        )
    )

    registry.register(
        CompetitionSource(
            competition_id="fr.1",
            competition_name="French Ligue 1 2026/27",
            source_name="openfootball",
            source_url="https://raw.githubusercontent.com/openfootball/football.json/master/2026-27/fr.1.json",
            coverage_status="available",
        )
    )

    return registry
