from typing import Any, Dict, List

from app.data_registry.global_competition_universe import (
    GlobalCompetitionUniverse,
    build_v13_global_competition_universe,
)
from app.data_registry.v1_3_source_registry import (
    V13_SOURCES,
    V13_COMPETITION_SOURCE_MAP,
)
from app.data_registry.v13_source_retrieval_service import (
    V13SourceRetrievalService,
)
from app.data_registry.v1_3_coverage_evidence import (
    get_coverage_ledger,
)


class V13CompetitionCoverage:
    """
    V1.3 competition coverage bridge.

    Competition identity comes from the authoritative 191-entry
    V1.3 competition catalogue/universe.

    Source availability comes from the V1.3 source mapping.

    Competition-level verification comes only from explicit
    V1.3 coverage evidence.

    A registered source is NOT automatically treated as verified.
    """

    def __init__(
        self,
        universe: GlobalCompetitionUniverse | None = None,
    ) -> None:
        self.universe = (
            universe
            if universe is not None
            else build_v13_global_competition_universe()
        )
        self.coverage_ledger = get_coverage_ledger()
        self.retrieval_service = V13SourceRetrievalService(self.universe)

    def get(self, competition_id: str) -> Dict[str, Any]:
        competition = self.universe.get(competition_id)

        if competition is None:
            return {
                "competition_id": competition_id,
                "status": "UNKNOWN_COMPETITION",
                "verified": False,
                "sources": [],
            }

        mappings = [
            mapping
            for mapping in V13_COMPETITION_SOURCE_MAP
            if mapping.competition_id == competition_id
        ]

        sources: List[Dict[str, Any]] = []

        for mapping in mappings:
            source = V13_SOURCES.get(mapping.source_id)

            if source is None:
                continue

            evidence = next(
                (
                    item
                    for item in self.coverage_ledger
                    if item["competition_id"] == competition_id
                    and item["source_id"] == mapping.source_id
                ),
                None,
            )

            evidence_status = (
                evidence["status"]
                if evidence is not None
                else "UNVERIFIED"
            )

            if evidence_status == "VERIFIED":
                source_status = "VERIFIED_AVAILABLE"
            else:
                source_status = "SOURCE_REGISTERED"

            sources.append(
                {
                    "source_id": source.source_id,
                    "source_name": source.name,
                    "source_url": source.base_url,
                    "mapping_status": mapping.status,
                    "mapping_coverage_status": mapping.coverage_status,
                    "coverage_status": source_status,
                    "evidence_status": evidence_status,
                }
            )

        verified_sources = [
            source
            for source in sources
            if source["coverage_status"] == "VERIFIED_AVAILABLE"
        ]

        if verified_sources:
            coverage_status = "VERIFIED_AVAILABLE"
        elif sources:
            coverage_status = "SOURCE_REGISTERED"
        else:
            coverage_status = "DISCOVERED_NOT_VERIFIED"

        return {
            "competition_id": competition.competition_id,
            "competition_name": competition.competition_name,
            "country_code": competition.country_code,
            "region": competition.region,
            "tier": competition.tier,
            "gender": competition.gender,
            "format": competition.format,
            "season": competition.season,
            "universe_status": competition.status,
            "status": coverage_status,
            "verified": bool(verified_sources),
            "sources": sources,
        }

    def all(self) -> List[Dict[str, Any]]:
        return [
            self.get(item.competition_id)
            for item in self.universe.all()
        ]

    def retrieve_sources(self, competition_id: str) -> Dict[str, Any]:
        """Retrieve all sources registered for one V1.3 competition."""
        return self.retrieval_service.retrieve_mapped_sources(
            competition_id
        )

    def verified(self) -> List[Dict[str, Any]]:
        return [
            item
            for item in self.all()
            if item["status"] == "VERIFIED_AVAILABLE"
        ]

    def unverified(self) -> List[Dict[str, Any]]:
        return [
            item
            for item in self.all()
            if item["status"] != "VERIFIED_AVAILABLE"
        ]

    def summary(self) -> Dict[str, int]:
        all_items = self.all()

        return {
            "total_competitions": len(all_items),
            "verified_available": sum(
                1
                for item in all_items
                if item["status"] == "VERIFIED_AVAILABLE"
            ),
            "source_registered": sum(
                1
                for item in all_items
                if item["status"] == "SOURCE_REGISTERED"
            ),
            "discovered_not_verified": sum(
                1
                for item in all_items
                if item["status"] == "DISCOVERED_NOT_VERIFIED"
            ),
        }


if __name__ == "__main__":
    coverage = V13CompetitionCoverage()

    print("==================================================")
    print("V1.3 COMPETITION COVERAGE BRIDGE")
    print("==================================================")

    summary = coverage.summary()

    print("TOTAL:", summary["total_competitions"])
    print("VERIFIED AVAILABLE:", summary["verified_available"])
    print("SOURCE REGISTERED:", summary["source_registered"])
    print("DISCOVERED NOT VERIFIED:", summary["discovered_not_verified"])

    if summary["total_competitions"] != 191:
        raise SystemExit(
            "FAIL: expected 191 V1.3 competition identities."
        )

    print("STATUS: PASS")
