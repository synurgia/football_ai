"""
V1.3 On-Demand Fixture Identity Resolver

Purpose:
    Resolve ONE requested match using the authoritative V1.3
    competition source pool.

Rules:
    - Uses the V1.3 competition universe.
    - Uses only sources mapped to the requested competition.
    - No worldwide scan.
    - No ESPN-only authority.
    - No silent substitution.
    - Preserves source disagreement.
    - Does not perform prediction.
"""

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
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


class V13FixtureIdentityResolver:
    def __init__(self, universe: GlobalCompetitionUniverse | None = None):
        self.universe = universe or build_v13_global_competition_universe()
        self.retrieval = V13SourceRetrievalService(self.universe)

    @staticmethod
    def _normalise(value: str) -> str:
        value = value.lower()
        value = re.sub(r"[^a-z0-9]+", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    @classmethod
    def _contains_team(cls, content: str, team: str) -> bool:
        text = cls._normalise(content)
        target = cls._normalise(team)

        if not target:
            return False

        return target in text

    def _source_pool(self, competition_id: str) -> List[Dict[str, str]]:
        seen = set()
        pool = []

        for mapping in V13_COMPETITION_SOURCE_MAP:
            if mapping.competition_id != competition_id:
                continue

            source = V13_SOURCES.get(mapping.source_id)
            if source is None:
                continue

            if source.source_id in seen:
                continue

            seen.add(source.source_id)

            pool.append(
                {
                    "source_id": source.source_id,
                    "source_name": source.name,
                    "source_url": source.base_url,
                }
            )

        return pool

    def resolve(
        self,
        *,
        competition_id: str,
        team_a: str,
        team_b: str,
    ) -> Dict[str, Any]:

        competition = self.universe.get(competition_id)

        if competition is None:
            return {
                "status": "UNKNOWN_COMPETITION",
                "competition_id": competition_id,
            }

        sources = self._source_pool(competition_id)

        if not sources:
            return {
                "status": "INSUFFICIENT_EVIDENCE",
                "competition_id": competition_id,
                "team_a": team_a,
                "team_b": team_b,
                "reason": "No registered source pool for competition.",
                "sources_checked": [],
            }

        def retrieve(source):
            return self.retrieval.retrieve_source(
                competition_id=competition_id,
                source_id=source["source_id"],
                source_name=source["source_name"],
                source_url=source["source_url"],
            )

        results = []

        # On-demand only: retrieve the requested competition's pool concurrently.
        with ThreadPoolExecutor(
            max_workers=min(6, len(sources))
        ) as executor:

            futures = {
                executor.submit(retrieve, source): source
                for source in sources
            }

            for future in as_completed(futures):
                source = futures[future]

                try:
                    result = future.result()
                except Exception as exc:
                    result = {
                        "status": "SOURCE_FAILED",
                        "retrieval_state": "HOLD",
                        "source_id": source["source_id"],
                        "source_name": source["source_name"],
                        "source_url": source["source_url"],
                        "error": str(exc),
                    }

                results.append(result)

        evidence = []

        for result in results:
            if result.get("retrieval_state") != "AVAILABLE":
                continue

            content = result.get("content") or ""

            if not self._contains_team(content, team_a):
                continue

            if not self._contains_team(content, team_b):
                continue

            evidence.append(
                {
                    "source_id": result.get("source_id"),
                    "source_name": result.get("source_name"),
                    "source_url": result.get("source_url"),
                    "evidence_status": "MATCH_CANDIDATE",
                }
            )

        if not evidence:
            return {
                "status": "INSUFFICIENT_EVIDENCE",
                "competition_id": competition_id,
                "team_a": team_a,
                "team_b": team_b,
                "sources_checked": [
                    {
                        "source_id": r.get("source_id"),
                        "status": r.get("status"),
                        "retrieval_state": r.get("retrieval_state"),
                    }
                    for r in results
                ],
                "reason": (
                    "No registered competition source returned evidence "
                    "containing both requested teams."
                ),
            }

        return {
            "status": "FOUND",
            "competition_id": competition_id,
            "team_a": team_a,
            "team_b": team_b,
            "identity_method": "V13_SOURCE_POOL",
            "evidence": evidence,
            "sources_checked": len(results),
        }


def _test():
    resolver = V13FixtureIdentityResolver()

    result = resolver.resolve(
        competition_id="bra.1",
        team_a="Bahia",
        team_b="Remo",
    )

    print("=" * 70)
    print("V1.3 ON-DEMAND FIXTURE IDENTITY TEST")
    print("=" * 70)
    print(result)


if __name__ == "__main__":
    _test()
