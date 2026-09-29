from typing import Dict, List


from app.data_registry.v13_africa_north_sources import V13_AFRICA_NORTH_SOURCE_CANDIDATES
from app.data_registry.v13_africa_wafu_a_sources import V13_AFRICA_WAFU_A_SOURCE_CANDIDATES
from app.data_registry.v13_africa_wafu_b_sources import V13_AFRICA_WAFU_B_SOURCE_CANDIDATES
from app.data_registry.v13_africa_uniffac_sources import V13_AFRICA_UNIFFAC_SOURCE_CANDIDATES
from app.data_registry.v13_africa_cecafa_sources import V13_AFRICA_CECAFA_SOURCE_CANDIDATES
from app.data_registry.v13_africa_cosafa_sources import V13_AFRICA_COSAFA_SOURCE_CANDIDATES
from app.data_registry.v13_africa_cosafa2_sources import V13_AFRICA_COSAFA2_SOURCE_CANDIDATES

from app.data_registry.v13_asia_asean_sources import V13_ASIA_ASEAN_SOURCE_CANDIDATES
from app.data_registry.v13_asia_east_sources import V13_ASIA_EAST_SOURCE_CANDIDATES
from app.data_registry.v13_asia_central_sources import V13_ASIA_CENTRAL_SOURCE_CANDIDATES
from app.data_registry.v13_asia_west_sources import V13_ASIA_WEST_SOURCE_CANDIDATES
from app.data_registry.v13_asia_south_sources import V13_ASIA_SOUTH_SOURCE_CANDIDATES

from app.data_registry.v13_europe_chunk01_sources import V13_EUROPE_CHUNK01_SOURCE_CANDIDATES
from app.data_registry.v13_europe_chunk02_sources import V13_EUROPE_CHUNK02_SOURCE_CANDIDATES
from app.data_registry.v13_europe_chunk03_sources import V13_EUROPE_CHUNK03_SOURCE_CANDIDATES
from app.data_registry.v13_europe_chunk04_sources import V13_EUROPE_CHUNK04_SOURCE_CANDIDATES
from app.data_registry.v13_europe_chunk05_sources import V13_EUROPE_CHUNK05_SOURCE_CANDIDATES
from app.data_registry.v13_europe_competition_sources import V13_EUROPE_COMPETITION_SOURCE_CANDIDATES
from app.data_registry.v13_europe_domestic_league_sources import V13_EUROPE_DOMESTIC_LEAGUE_SOURCE_CANDIDATES
from app.data_registry.v13_europe_uefa_competition_families import V13_EUROPE_UEFA_COMPETITION_FAMILY_SOURCE_CANDIDATES

from app.data_registry.v13_americas_conmebol_chunk01_sources import V13_AMERICAS_CONMEBOL_CHUNK01_SOURCE_CANDIDATES
from app.data_registry.v13_americas_concacaf_chunk01_sources import V13_AMERICAS_CONCACAF_CHUNK01_SOURCE_CANDIDATES
from app.data_registry.v13_americas_south_sources import V13_AMERICAS_SOUTH_SOURCE_CANDIDATES
from app.data_registry.v13_americas_south2_sources import V13_AMERICAS_SOUTH2_SOURCE_CANDIDATES
from app.data_registry.v13_americas_north_central_sources import V13_AMERICAS_NORTH_CENTRAL_SOURCE_CANDIDATES
from app.data_registry.v13_americas_caribbean_sources import V13_AMERICAS_CARIBBEAN_SOURCE_CANDIDATES

from app.data_registry.v13_oceania_chunk01_sources import V13_OCEANIA_CHUNK01_SOURCE_CANDIDATES
from app.data_registry.v13_oceania_sources import V13_OCEANIA_SOURCE_CANDIDATES


V13_CANDIDATE_SOURCE_GROUPS = [
    V13_AFRICA_NORTH_SOURCE_CANDIDATES,
    V13_AFRICA_WAFU_A_SOURCE_CANDIDATES,
    V13_AFRICA_WAFU_B_SOURCE_CANDIDATES,
    V13_AFRICA_UNIFFAC_SOURCE_CANDIDATES,
    V13_AFRICA_CECAFA_SOURCE_CANDIDATES,
    V13_AFRICA_COSAFA_SOURCE_CANDIDATES,
    V13_AFRICA_COSAFA2_SOURCE_CANDIDATES,
    V13_ASIA_ASEAN_SOURCE_CANDIDATES,
    V13_ASIA_EAST_SOURCE_CANDIDATES,
    V13_ASIA_CENTRAL_SOURCE_CANDIDATES,
    V13_ASIA_WEST_SOURCE_CANDIDATES,
    V13_ASIA_SOUTH_SOURCE_CANDIDATES,
    V13_EUROPE_CHUNK01_SOURCE_CANDIDATES,
    V13_EUROPE_CHUNK02_SOURCE_CANDIDATES,
    V13_EUROPE_CHUNK03_SOURCE_CANDIDATES,
    V13_EUROPE_CHUNK04_SOURCE_CANDIDATES,
    V13_EUROPE_CHUNK05_SOURCE_CANDIDATES,
    V13_EUROPE_COMPETITION_SOURCE_CANDIDATES,
    V13_EUROPE_DOMESTIC_LEAGUE_SOURCE_CANDIDATES,
    V13_EUROPE_UEFA_COMPETITION_FAMILY_SOURCE_CANDIDATES,
    V13_AMERICAS_CONMEBOL_CHUNK01_SOURCE_CANDIDATES,
    V13_AMERICAS_CONCACAF_CHUNK01_SOURCE_CANDIDATES,
    V13_AMERICAS_SOUTH_SOURCE_CANDIDATES,
    V13_AMERICAS_SOUTH2_SOURCE_CANDIDATES,
    V13_AMERICAS_NORTH_CENTRAL_SOURCE_CANDIDATES,
    V13_AMERICAS_CARIBBEAN_SOURCE_CANDIDATES,
    V13_OCEANIA_CHUNK01_SOURCE_CANDIDATES,
    V13_OCEANIA_SOURCE_CANDIDATES,
]


def get_all_candidate_sources() -> List[Dict]:
    """Return one deduplicated worldwide candidate source catalogue."""
    sources: Dict[str, Dict] = {}

    for group in V13_CANDIDATE_SOURCE_GROUPS:
        for source in group:
            source_id = source["source_id"]
            if source_id not in sources:
                sources[source_id] = dict(source)

    return list(sources.values())


def get_candidate_source(source_id: str) -> Dict | None:
    for source in get_all_candidate_sources():
        if source["source_id"] == source_id:
            return source
    return None


def candidate_source_count() -> int:
    return len(get_all_candidate_sources())


if __name__ == "__main__":
    sources = get_all_candidate_sources()
    print("V1.3 CANDIDATE SOURCE CATALOG")
    print("==============================")
    print("TOTAL UNIQUE CANDIDATES:", len(sources))
    print("DUPLICATE SOURCE IDS:", sum(
        len(group) for group in V13_CANDIDATE_SOURCE_GROUPS
    ) - len(sources))
