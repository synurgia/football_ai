from typing import Any, Dict, List

from app.data_registry.v1_3_competition_catalogue import V13_COMPETITION_CATALOGUE
from app.data_registry.v1_3_source_registry import (
    V13_COMPETITION_SOURCE_MAP,
    V13_SOURCES,
)


def get_ai_routing_context(competition_id: str) -> Dict[str, Any]:
    """
    Thin V1.3 -> AI routing adapter.

    V1.3 remains authoritative for:
      - competition identity
      - competition name
      - source pool
      - source status

    The AI engine remains responsible for intelligence/reasoning.
    """

    competition = next(
        (
            item
            for item in V13_COMPETITION_CATALOGUE
            if item["competition_id"] == competition_id
        ),
        None,
    )

    if competition is None:
        return {
            "competition_id": competition_id,
            "competition_name_canonical": None,
            "competition_identity_status": "UNRESOLVED",
            "competition_identity_method": "V13_CATALOGUE_LOOKUP_FAILED",
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

        sources.append(
            {
                "source_id": source.source_id,
                "name": source.name,
                "base_url": source.base_url,
                "layer": source.layer,
                "data_classes": source.data_classes,
                "access_type": source.access_type,
                "free": source.free,
                "coverage_scope": source.coverage_scope,
                "priority": mapping.priority,
                "coverage_status": mapping.coverage_status,
                "status": mapping.status,
            }
        )

    return {
        "competition_id": competition_id,
        "competition_name_canonical": competition["name"],
        "competition_identity_status": "RESOLVED",
        "competition_identity_method": "V13_AUTHORITATIVE_CATALOGUE",
        "sources": sources,
    }
