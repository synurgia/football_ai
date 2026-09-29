"""Mark competitions that have no queryable free source.

Reads the source map and returns which competitions are registry-only.
These should be recorded in the DB with an explicit 'source_unavailable'
state — not silently dropped, and not filled with fabricated data.
"""

from __future__ import annotations
from typing import List, Dict, Any

from app.competition_source_map import (
    FD_CODES, TSDB_LEAGUES, OLDB_LEAGUES, ESPN_SLUGS,
    APIF_LEAGUES, ZAFX_COMPS, OFB_LEAGUES,
)


def _has_direct_source(cid: str) -> bool:
    return any([
        cid in FD_CODES,
        cid in TSDB_LEAGUES,
        cid in OLDB_LEAGUES,
        cid in ESPN_SLUGS,
        cid in APIF_LEAGUES,
        cid in ZAFX_COMPS,
        cid in OFB_LEAGUES,
    ])


def classify_all_competitions() -> Dict[str, List[str]]:
    """Return all competitions grouped by source availability."""
    from app.data_registry.v1_3_competition_catalogue import V13_COMPETITION_CATALOGUE

    direct = []
    registry_only = []
    for comp in V13_COMPETITION_CATALOGUE:
        cid = comp.get("competition_id") or ""
        if not cid:
            continue
        if _has_direct_source(cid):
            direct.append(cid)
        else:
            registry_only.append(cid)

    return {
        "direct_source": sorted(direct),
        "registry_only": sorted(registry_only),
    }


if __name__ == "__main__":
    result = classify_all_competitions()
    print(f"DIRECT SOURCE  : {len(result['direct_source'])} competitions")
    print(f"REGISTRY ONLY  : {len(result['registry_only'])} competitions")
    print()
    print("Registry-only competitions (no free queryable source):")
    for cid in result["registry_only"]:
        print(f"  {cid}")
