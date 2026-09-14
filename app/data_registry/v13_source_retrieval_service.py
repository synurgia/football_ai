"""
V1.3 Source Retrieval Service

Connects:
    Competition Universe
        +
    V1.3 Source Mappings
        +
    Explicit Source URLs
        +
    V1.3 URL Source Gateway

Rules:
- Competition identity comes from the V1.3 universe.
- Sources are explicit.
- No source priority is assigned here.
- Search engines are never treated as data sources.
- OpenFoot and ESPN are not automatically primary.
- A source is usable only after direct retrieval succeeds.
- Failed/unverified sources remain HOLD.
- No source failure causes silent substitution.
- No analytical prediction is performed here.
"""

from typing import Any, Dict, List

from app.data_registry.global_competition_universe import (
    GlobalCompetitionUniverse,
    build_v13_global_competition_universe,
)
from app.data_registry.v13_url_source_gateway import (
    V13URLSourceGateway,
)
from app.data_registry.v1_3_source_registry import (
    V13_SOURCES,
    V13_COMPETITION_SOURCE_MAP,
)


class V13SourceRetrievalService:
    """Retrieve data only from explicitly supplied source URLs."""

    def __init__(self, universe: GlobalCompetitionUniverse) -> None:
        self.universe = universe
        self.gateway = V13URLSourceGateway()

    def retrieve_source(
        self,
        *,
        competition_id: str,
        source_id: str,
        source_name: str,
        source_url: str,
    ) -> Dict[str, Any]:
        competition = self.universe.get(competition_id)

        if competition is None:
            return {
                "status": "UNKNOWN_COMPETITION",
                "competition_id": competition_id,
                "source_id": source_id,
                "data_available": False,
            }

        result = self.gateway.retrieve(
            source_id=source_id,
            source_name=source_name,
            source_url=source_url,
            competition_id=competition.competition_id,
            competition_name=competition.competition_name,
        )

        if result["status"] == "SOURCE_RETRIEVED":
            result["retrieval_state"] = "AVAILABLE"
        else:
            result["retrieval_state"] = "HOLD"

        return result

    def retrieve_mapped_sources(
        self,
        competition_id: str,
    ) -> Dict[str, Any]:
        """
        Retrieve the complete V1.3 source pool registered for one competition.

        Source mappings are read from the authoritative V1.3 source registry.
        No source is promoted or substituted because another source fails.
        """
        mapped_sources = [
            mapping
            for mapping in V13_COMPETITION_SOURCE_MAP
            if mapping.competition_id == competition_id
        ]

        sources: List[Dict[str, str]] = []

        for mapping in mapped_sources:
            source = V13_SOURCES.get(mapping.source_id)

            if source is None:
                continue

            sources.append(
                {
                    "source_id": source.source_id,
                    "source_name": source.name,
                    "source_url": source.base_url,
                }
            )

        return self.retrieve_sources(
            competition_id,
            sources,
        )

    def retrieve_sources(
        self,
        competition_id: str,
        sources: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Retrieve all explicitly configured sources for one competition.

        Each source is independent. One failure does not cause
        another source to be silently promoted.
        """

        results = []

        for source in sources:
            results.append(
                self.retrieve_source(
                    competition_id=competition_id,
                    source_id=source["source_id"],
                    source_name=source["source_name"],
                    source_url=source["source_url"],
                )
            )

        return {
            "competition_id": competition_id,
            "source_count": len(results),
            "results": results,
            "retrieved": sum(
                1 for item in results
                if item["status"] == "SOURCE_RETRIEVED"
            ),
            "held": sum(
                1 for item in results
                if item["status"] != "SOURCE_RETRIEVED"
            ),
        }


def _test() -> None:
    universe = build_v13_global_competition_universe()

    # Locate the actual universe records without creating
    # any source preference or substitution.
    competitions = universe.all()

    if not competitions:
        raise RuntimeError(
            "V1.3 competition universe is empty."
        )

    service = V13SourceRetrievalService(universe)

    first = competitions[0]

    result = service.retrieve_sources(
        first.competition_id,
        [
            {
                "source_id": "v13_test_source",
                "source_name": "Direct URL Test",
                "source_url": "https://example.com",
            }
        ],
    )

    print("=" * 50)
    print("V1.3 SOURCE RETRIEVAL SERVICE TEST")
    print("=" * 50)
    print("COMPETITION:", first.competition_id)
    print("SOURCES TESTED:", result["source_count"])
    print("RETRIEVED:", result["retrieved"])
    print("HELD:", result["held"])

    if result["retrieved"] != 1:
        raise RuntimeError(
            "V1.3 source retrieval service failed."
        )

    item = result["results"][0]

    if item["retrieval_state"] != "AVAILABLE":
        raise RuntimeError(
            "Retrieved source was not marked AVAILABLE."
        )

    if not item.get("content"):
        raise RuntimeError(
            "Retrieved source content was not preserved."
        )

    print("SOURCE STATUS:", item["status"])
    print("RETRIEVAL STATE:", item["retrieval_state"])
    print("RESULT: PASS")


if __name__ == "__main__":
    _test()
