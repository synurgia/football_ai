from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class RegionalSourceDefinition:
    source_id: str
    name: str
    base_url: str
    authority_level: str
    scope: str
    country_codes: tuple[str, ...] = ()
    competition_patterns: tuple[str, ...] = ()
    evidence_types: tuple[str, ...] = ()
    enabled: bool = True


class RegionalSourceRegistry:
    """
    Registry of football information sources.

    This registry does not claim that a source is currently reachable
    or that a source contains a particular fixture. It only records
    configured routing information.
    """

    def __init__(self) -> None:
        self._sources: Dict[str, RegionalSourceDefinition] = {}

    def register(self, source: RegionalSourceDefinition) -> None:
        if not source.source_id:
            raise ValueError("source_id is required.")

        self._sources[source.source_id] = source

    def get(self, source_id: str) -> Optional[RegionalSourceDefinition]:
        return self._sources.get(source_id)

    def all(self) -> List[RegionalSourceDefinition]:
        return list(self._sources.values())

    def enabled(self) -> List[RegionalSourceDefinition]:
        return [
            source
            for source in self._sources.values()
            if source.enabled
        ]

    def to_dict(self) -> List[Dict[str, Any]]:
        return [
            asdict(source)
            for source in self._sources.values()
        ]


class RegionalSourceResolver:
    """
    Selects appropriate configured sources for a fixture.

    Resolution is based on explicit fixture metadata only.
    It does not guess a country from a team name and does not claim
    that an unconfigured regional source exists.
    """

    def __init__(
        self,
        registry: Optional[RegionalSourceRegistry] = None,
    ) -> None:
        self.registry = registry or build_default_registry()

    @staticmethod
    def _normalise(value: Any) -> str:
        if value is None:
            return ""

        return str(value).strip().lower()

    def resolve(
        self,
        fixture: Dict[str, Any],
    ) -> Dict[str, Any]:
        country = self._normalise(
            fixture.get("country_code")
            or fixture.get("country")
        )

        competition = self._normalise(
            fixture.get("competition")
        )

        regional: List[Dict[str, Any]] = []
        global_sources: List[Dict[str, Any]] = []

        for source in self.registry.enabled():
            country_match = (
                bool(country)
                and country.upper() in source.country_codes
            )

            competition_match = False

            if competition:
                competition_match = any(
                    pattern.lower() in competition
                    for pattern in source.competition_patterns
                )

            if source.scope == "regional" and (
                country_match or competition_match
            ):
                regional.append(self._source_result(
                    source,
                    "MATCHED",
                ))

            elif source.scope == "global":
                global_sources.append(self._source_result(
                    source,
                    "GLOBAL_FALLBACK",
                ))

        status = (
            "REGIONAL_MATCH_FOUND"
            if regional
            else "REGIONAL_SOURCE_NOT_CONFIGURED"
        )

        return {
            "fixture": {
                "home_team": fixture.get("home_team"),
                "away_team": fixture.get("away_team"),
                "competition": fixture.get("competition"),
                "country_code": fixture.get("country_code"),
            },
            "status": status,
            "regional_sources": regional,
            "global_sources": global_sources,
            "source_count": len(regional) + len(global_sources),
        }

    @staticmethod
    def _source_result(
        source: RegionalSourceDefinition,
        routing_status: str,
    ) -> Dict[str, Any]:
        return {
            "source_id": source.source_id,
            "name": source.name,
            "base_url": source.base_url,
            "authority_level": source.authority_level,
            "scope": source.scope,
            "routing_status": routing_status,
            "evidence_types": list(source.evidence_types),
        }


def build_default_registry() -> RegionalSourceRegistry:
    registry = RegionalSourceRegistry()

    # Kenya: official federation source.
    registry.register(
        RegionalSourceDefinition(
            source_id="fkf_official",
            name="Football Kenya Federation",
            base_url="https://footballkenya.org",
            authority_level="OFFICIAL_FEDERATION",
            scope="regional",
            country_codes=("KE", "KEN", "KENYA"),
            competition_patterns=(
                "sportpesa league",
                "national super league",
                "division one",
                "women's premier league",
            ),
            evidence_types=(
                "fixtures",
                "competition_context",
                "league_information",
                "news",
            ),
        )
    )

    # Global discovery/cross-check sources.
    registry.register(
        RegionalSourceDefinition(
            source_id="espn_global_soccer",
            name="ESPN Soccer",
            base_url="https://www.espn.com/soccer/",
            authority_level="GLOBAL_SECONDARY",
            scope="global",
            evidence_types=(
                "fixtures",
                "match_status",
                "teams",
                "results",
            ),
        )
    )

    registry.register(
        RegionalSourceDefinition(
            source_id="openfoot",
            name="OpenFoot",
            base_url="https://openfootapi.com",
            authority_level="GLOBAL_SECONDARY",
            scope="global",
            evidence_types=(
                "fixtures",
                "competition_data",
                "team_data",
            ),
        )
    )

    return registry


if __name__ == "__main__":
    resolver = RegionalSourceResolver()

    print("=== REGIONAL SOURCE RESOLVER TEST ===")
    print("REGISTERED SOURCES:", len(resolver.registry.all()))

    kenya_fixture = {
        "home_team": "Example Kenyan Club",
        "away_team": "Example Kenyan Club 2",
        "competition": "SportPesa League",
        "country_code": "KE",
    }

    result = resolver.resolve(kenya_fixture)

    print()
    print("KENYA TEST")
    print("STATUS:", result["status"])
    print(
        "REGIONAL:",
        [source["source_id"] for source in result["regional_sources"]],
    )
    print(
        "GLOBAL:",
        [source["source_id"] for source in result["global_sources"]],
    )

    if result["status"] != "REGIONAL_MATCH_FOUND":
        raise SystemExit(
            "FAIL: Kenyan regional source was not resolved."
        )

    if not any(
        source["source_id"] == "fkf_official"
        for source in result["regional_sources"]
    ):
        raise SystemExit(
            "FAIL: FKF official source was not selected."
        )

    unknown_fixture = {
        "home_team": "Example Club",
        "away_team": "Example Club 2",
        "competition": "Unknown Competition",
    }

    unknown_result = resolver.resolve(unknown_fixture)

    print()
    print("UNKNOWN-REGION TEST")
    print("STATUS:", unknown_result["status"])

    if unknown_result["status"] != "REGIONAL_SOURCE_NOT_CONFIGURED":
        raise SystemExit(
            "FAIL: unknown regional source was incorrectly classified."
        )

    print()
    print("RESULT: PASS")
    print("REGIONAL SOURCE ROUTING IS WORKING")
    print("NO SOURCE WAS CLAIMED AS VERIFIED")
    print("=== TEST COMPLETE ===")
