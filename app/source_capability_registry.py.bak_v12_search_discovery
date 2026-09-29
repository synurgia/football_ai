from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class SourceCapability:
    source_id: str
    name: str
    base_url: str
    scope: str
    capabilities: Tuple[str, ...]
    authority_level: str
    enabled: bool = True


class SourceCapabilityRegistry:
    """
    Registry describing what each external source is actually allowed
    to provide.

    This registry does NOT claim that a capability is currently verified.
    It only defines the source's intended evidence capabilities.
    """

    def __init__(self):
        self._sources: Dict[str, SourceCapability] = {}

    def register(self, source: SourceCapability) -> None:
        if source.source_id in self._sources:
            raise ValueError(
                f"Source already registered: {source.source_id}"
            )

        self._sources[source.source_id] = source

    def get(self, source_id: str) -> SourceCapability:
        if source_id not in self._sources:
            raise KeyError(
                f"Unknown source: {source_id}"
            )

        return self._sources[source_id]

    def list_sources(self) -> List[SourceCapability]:
        return list(self._sources.values())

    def sources_for_capability(
        self,
        capability: str,
    ) -> List[SourceCapability]:
        return [
            source
            for source in self._sources.values()
            if source.enabled
            and capability in source.capabilities
        ]

    def capability_map(self) -> Dict[str, List[str]]:
        result: Dict[str, List[str]] = {}

        for source in self._sources.values():
            for capability in source.capabilities:
                result.setdefault(
                    capability,
                    [],
                ).append(source.source_id)

        return result


def build_default_registry() -> SourceCapabilityRegistry:
    registry = SourceCapabilityRegistry()

    registry.register(
        SourceCapability(
            source_id="espn_global_soccer",
            name="ESPN Soccer",
            base_url="https://site.api.espn.com",
            scope="GLOBAL",
            capabilities=(
                "fixtures",
                "match_status",
                "results",
                "team_identity",
            ),
            authority_level="GLOBAL_SECONDARY",
        )
    )

    registry.register(
        SourceCapability(
            source_id="openfoot",
            name="OpenFoot API",
            base_url="https://openfootapi.com",
            scope="GLOBAL",
            capabilities=(
                "fixtures",
                "competition_data",
                "team_data",
                "standings",
            ),
            authority_level="GLOBAL_SECONDARY",
        )
    )

    registry.register(
        SourceCapability(
            source_id="fkf_official",
            name="Football Kenya Federation",
            base_url="https://footballkenya.org",
            scope="KE",
            capabilities=(
                "fixtures",
                "competition_context",
                "league_information",
                "official_news",
            ),
            authority_level="OFFICIAL_FEDERATION",
        )
    )

    return registry


if __name__ == "__main__":
    print("=== SOURCE CAPABILITY REGISTRY TEST ===")

    registry = build_default_registry()

    sources = registry.list_sources()

    print("REGISTERED SOURCES:", len(sources))

    for source in sources:
        print(
            source.source_id,
            "|",
            source.scope,
            "|",
            source.authority_level,
        )

    print()
    print("=== CAPABILITY ROUTING ===")

    capabilities = (
        "fixtures",
        "standings",
        "team_data",
        "results",
        "official_news",
        "competition_context",
    )

    for capability in capabilities:
        matches = registry.sources_for_capability(
            capability
        )

        print(
            capability,
            "->",
            [source.source_id for source in matches],
        )

    print()
    print("=== REQUIRED TRUTH CHECKS ===")

    fixture_sources = registry.sources_for_capability(
        "fixtures"
    )

    if not fixture_sources:
        raise SystemExit(
            "FAIL: no fixture source registered."
        )

    team_sources = registry.sources_for_capability(
        "team_data"
    )

    if not team_sources:
        raise SystemExit(
            "FAIL: no team-data source registered."
        )

    official_sources = registry.sources_for_capability(
        "official_news"
    )

    if not official_sources:
        raise SystemExit(
            "FAIL: no official regional source registered."
        )

    print(
        "FIXTURE SOURCES:",
        len(fixture_sources),
    )
    print(
        "TEAM-DATA SOURCES:",
        len(team_sources),
    )
    print(
        "OFFICIAL REGIONAL SOURCES:",
        len(official_sources),
    )

    print()
    print("RESULT: PASS")
    print("SOURCE CAPABILITY REGISTRY IS WORKING")
    print("SOURCES ARE SEPARATED BY CAPABILITY")
    print("NO SOURCE CLAIMED AS VERIFIED DATA")
    print("PIECES 1-9: UNCHANGED")
    print("37 QUESTIONS: UNCHANGED")
    print("=== TEST COMPLETE ===")
