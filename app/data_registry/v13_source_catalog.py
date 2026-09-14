"""
V1.3 Global Source Catalog

Stores candidate external sources independently from competition
authority or provider priority.

A source is only VERIFIED after the existing V1.2 verifier
successfully reaches the actual URL.

Source roles describe what a source does.
They do NOT establish source priority.

Allowed roles:
- OFFICIAL_FEDERATION
- OFFICIAL_COMPETITION
- OFFICIAL_CLUB
- REPUTABLE_DATA_PROVIDER
- PUBLIC_DATA_SOURCE
- DISCOVERY_ONLY
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class V13SourceRecord:
    source_id: str
    source_name: str
    source_url: str
    source_role: str
    competition_ids: List[str]
    verification_status: str = "UNVERIFIED"


class V13SourceCatalog:
    """Registry of candidate real-world football data sources."""

    def __init__(self) -> None:
        self._sources: Dict[str, V13SourceRecord] = {}

    def register(self, source: V13SourceRecord) -> None:
        if not source.source_id:
            raise ValueError("source_id is required")

        if not source.source_url.startswith(
            ("http://", "https://")
        ):
            raise ValueError("source_url must use HTTP or HTTPS")

        if source.source_role not in {
            "OFFICIAL_FEDERATION",
            "OFFICIAL_COMPETITION",
            "OFFICIAL_CLUB",
            "REPUTABLE_DATA_PROVIDER",
            "PUBLIC_DATA_SOURCE",
            "DISCOVERY_ONLY",
        }:
            raise ValueError(
                f"Unsupported source role: {source.source_role}"
            )

        self._sources[source.source_id] = source

    def get(self, source_id: str):
        return self._sources.get(source_id)

    def all(self) -> List[V13SourceRecord]:
        return list(self._sources.values())

    def for_competition(
        self,
        competition_id: str,
    ) -> List[V13SourceRecord]:
        return [
            source
            for source in self._sources.values()
            if competition_id in source.competition_ids
        ]

    def verified(self) -> List[V13SourceRecord]:
        return [
            source
            for source in self._sources.values()
            if source.verification_status == "VERIFIED"
        ]


def build_v13_source_catalog() -> V13SourceCatalog:
    """
    Build the initial catalog from sources already present in V1.3.

    IMPORTANT:
    These are candidate records only.
    Verification remains a separate operation.
    """

    catalog = V13SourceCatalog()

    catalog.register(
        V13SourceRecord(
            source_id="openfootball_public",
            source_name="OpenFootball",
            source_url=(
                "https://raw.githubusercontent.com/"
                "openfootball/football.json/master/"
            ),
            source_role="PUBLIC_DATA_SOURCE",
            competition_ids=[
                "eng.1",
                "ita.1",
                "de.1",
                "es.1",
                "fr.1",
                "pt.1",
                "nl.1",
            ],
        )
    )

    return catalog


if __name__ == "__main__":
    catalog = build_v13_source_catalog()

    print("==================================================")
    print("V1.3 SOURCE CATALOG")
    print("==================================================")
    print("TOTAL SOURCES:", len(catalog.all()))

    for source in catalog.all():
        print(
            source.source_id,
            "|",
            source.source_name,
            "|",
            source.source_role,
            "|",
            source.verification_status,
        )

    print("RESULT: PASS")
    print("NO SOURCE PRIORITY ASSIGNED")
