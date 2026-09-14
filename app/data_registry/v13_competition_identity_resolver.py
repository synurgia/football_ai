from typing import Any, Dict, Optional

from app.data_registry.v1_3_competition_catalogue import (
    V13_COMPETITION_CATALOGUE,
)


class V13CompetitionIdentityResolver:
    """Resolve live competition names to authoritative V1.3 competition IDs."""

    def __init__(self) -> None:
        self._by_name = {
            str(item["name"]).strip().lower(): item["competition_id"]
            for item in V13_COMPETITION_CATALOGUE
        }

    def resolve(self, competition_name: str) -> Optional[Dict[str, Any]]:
        if not competition_name:
            return None

        raw = str(competition_name).strip()
        normalized = raw.lower()

        # Exact catalogue match.
        competition_id = self._by_name.get(normalized)
        if competition_id:
            return {
                "competition_id": competition_id,
                "competition_name": next(
                    item["name"]
                    for item in V13_COMPETITION_CATALOGUE
                    if item["competition_id"] == competition_id
                ),
                "match_method": "EXACT",
                "status": "RESOLVED",
            }

        # Controlled provider-name aliases.
        # These aliases were verified against the authoritative V1.3 catalogue.
        aliases = {
            "norwegian eliteserien": "nor.1",
            "swedish allsvenskan": "swe.1",
            "turkish super lig": "tur.1",
            "liga portugal": "por.1",
            "argentine lpf": "arg.1",
            "liga auf uruguaya": "uru.1",
            "brazil serie a": "bra.1",
            "brazil serie b": "bra.2",
            "chilean primera": "chi.1",
            "ligapro ecuador": "ecu.1",
            "colombian primera a": "col.1",
            "english premier league": "eng.1",
        }

        competition_id = aliases.get(normalized)
        if competition_id:
            competition_name = next(
                item["name"]
                for item in V13_COMPETITION_CATALOGUE
                if item["competition_id"] == competition_id
            )
            return {
                "competition_id": competition_id,
                "competition_name": competition_name,
                "match_method": "VERIFIED_ALIAS",
                "status": "RESOLVED",
            }

        # Controlled regional/phase suffix handling.
        suffixes = (
            ", west region",
            ", east region",
            " - west region",
            " - east region",
        )

        for suffix in suffixes:
            if normalized.endswith(suffix):
                base_name = normalized[: -len(suffix)].strip()
                competition_id = self._by_name.get(base_name)
                if competition_id:
                    return {
                        "competition_id": competition_id,
                        "competition_name": next(
                            item["name"]
                            for item in V13_COMPETITION_CATALOGUE
                            if item["competition_id"] == competition_id
                        ),
                        "match_method": "CONTROLLED_SUFFIX",
                        "status": "RESOLVED",
                    }

        return {
            "competition_id": None,
            "competition_name": raw,
            "match_method": "NONE",
            "status": "UNRESOLVED",
        }


if __name__ == "__main__":
    resolver = V13CompetitionIdentityResolver()

    result = resolver.resolve(
        "AFC Champions League Elite, West Region"
    )

    print("=== V1.3 COMPETITION IDENTITY CHECK ===")
    print(result)
