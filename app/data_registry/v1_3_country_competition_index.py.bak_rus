from typing import Any, Dict, List

from app.data_registry.v1_3_competition_catalogue import V13_COMPETITION_CATALOGUE


# Catalogue prefix -> country name.
# This is the only country-normalization layer.
COUNTRY_BY_PREFIX = {
    "ago": "Angola",
    "are": "United Arab Emirates",
    "arg": "Argentina",
    "arm": "Armenia",
    "aus": "Australia",
    "aut": "Austria",
    "aze": "Azerbaijan",
    "bih": "Bosnia and Herzegovina",
    "bol": "Bolivia",
    "bra": "Brazil",
    "bul": "Bulgaria",
    "chi": "Chile",
    "chn": "China",
    "civ": "Côte d'Ivoire",
    "cod": "DR Congo",
    "col": "Colombia",
    "crc": "Costa Rica",
    "cro": "Croatia",
    "cyp": "Cyprus",
    "cze": "Czech Republic",
    "de": "Germany",
    "den": "Denmark",
    "dom": "Dominican Republic",
    "dza": "Algeria",
    "ecu": "Ecuador",
    "egy": "Egypt",
    "eng": "England",
    "fin": "Finland",
    "fr": "France",
    "fro": "Faroe Islands",
    "geo": "Georgia",
    "gha": "Ghana",
    "gre": "Greece",
    "hon": "Honduras",
    "hun": "Hungary",
    "idn": "Indonesia",
    "ind": "India",
    "irl": "Ireland",
    "irn": "Iran",
    "irq": "Iraq",
    "isl": "Iceland",
    "isr": "Israel",
    "ita": "Italy",
    "jor": "Jordan",
    "jpn": "Japan",
    "kaz": "Kazakhstan",
    "ken": "Kenya",
    "kor": "South Korea",
    "mar": "Morocco",
    "mex": "Mexico",
    "mys": "Malaysia",
    "nga": "Nigeria",
    "nir": "Northern Ireland",
    "nl": "Netherlands",
    "nor": "Norway",
    "pan": "Panama",
    "par": "Paraguay",
    "per": "Peru",
    "pol": "Poland",
    "por": "Portugal",
    "qat": "Qatar",
    "rou": "Romania",
    "sau": "Saudi Arabia",
    "sco": "Scotland",
    "sen": "Senegal",
    "srb": "Serbia",
    "sui": "Switzerland",
    "svk": "Slovakia",
    "svn": "Slovenia",
    "swe": "Sweden",
    "tha": "Thailand",
    "tun": "Tunisia",
    "tur": "Turkey",
    "tza": "Tanzania",
    "uga": "Uganda",
    "ukr": "Ukraine",
    "uru": "Uruguay",
    "usa": "USA",
    "uzb": "Uzbekistan",
    "vnm": "Vietnam",
    "zaf": "South Africa",
    "zmb": "Zambia",
}

# These are deliberately NOT countries.
REGIONAL_PREFIXES = {
    "afc",
    "caf",
    "concacaf",
    "conmebol",
    "fifa",
    "ofc",
    "uefa",
}


def _prefix(competition_id: str) -> str:
    return competition_id.split(".", 1)[0].lower()


def _build_index() -> Dict[str, List[Dict[str, Any]]]:
    index: Dict[str, List[Dict[str, Any]]] = {}

    for competition in V13_COMPETITION_CATALOGUE:
        competition_id = competition["competition_id"]
        prefix = _prefix(competition_id)

        if prefix in REGIONAL_PREFIXES:
            continue

        country = COUNTRY_BY_PREFIX.get(prefix)
        if country is None:
            raise ValueError(
                f"V1.3 country mapping missing for catalogue prefix: {prefix} "
                f"(competition_id={competition_id})"
            )

        index.setdefault(country, []).append(
            {
                "competition_id": competition_id,
                "name": competition["name"],
                "region": competition["region"],
            }
        )

    for competitions in index.values():
        competitions.sort(key=lambda item: item["competition_id"])

    return dict(sorted(index.items()))


COUNTRY_COMPETITION_INDEX = _build_index()


def get_countries() -> List[str]:
    return list(COUNTRY_COMPETITION_INDEX.keys())


def get_competitions_for_country(country: str) -> List[Dict[str, Any]]:
    for name, competitions in COUNTRY_COMPETITION_INDEX.items():
        if name.casefold() == country.strip().casefold():
            return list(competitions)
    return []


def get_competition(competition_id: str) -> Dict[str, Any] | None:
    target = competition_id.strip().casefold()

    for competition in V13_COMPETITION_CATALOGUE:
        if competition["competition_id"].casefold() == target:
            return dict(competition)

    return None


def get_country_for_competition(competition_id: str) -> str | None:
    prefix = _prefix(competition_id)
    return COUNTRY_BY_PREFIX.get(prefix)


# ---------- integrity verification ----------
_catalogue_country_entries = 0
for _competition in V13_COMPETITION_CATALOGUE:
    if _prefix(_competition["competition_id"]) not in REGIONAL_PREFIXES:
        _catalogue_country_entries += 1

_index_entries = sum(
    len(competitions)
    for competitions in COUNTRY_COMPETITION_INDEX.values()
)

if _catalogue_country_entries != _index_entries:
    raise RuntimeError(
        "V1.3 COUNTRY INDEX COVERAGE FAILURE: "
        f"catalogue_country_entries={_catalogue_country_entries}, "
        f"index_entries={_index_entries}"
    )

if len(COUNTRY_COMPETITION_INDEX) == 0:
    raise RuntimeError("V1.3 COUNTRY INDEX IS EMPTY")


if __name__ == "__main__":
    print("=== V1.3 COUNTRY → COMPETITION INDEX ===")
    print(f"CATALOGUE ENTRIES: {len(V13_COMPETITION_CATALOGUE)}")
    print(f"COUNTRIES: {len(COUNTRY_COMPETITION_INDEX)}")
    print(f"COUNTRY-MAPPED COMPETITIONS: {_index_entries}")
    print(f"REGIONAL/INTERNATIONAL EXCLUDED: "
          f"{len(V13_COMPETITION_CATALOGUE) - _catalogue_country_entries}")
    print("STATUS: PASS")

    print("\n=== ARGENTINA ===")
    for item in get_competitions_for_country("Argentina"):
        print(
            f"{item['competition_id']} | "
            f"{item['name']} | {item['region']}"
        )

    print("\n=== NETHERLANDS ===")
    for item in get_competitions_for_country("Netherlands"):
        print(
            f"{item['competition_id']} | "
            f"{item['name']} | {item['region']}"
        )

    print("\n=== SAMPLE COUNTRY LOOKUP ===")
    print("arg.1 =>", get_country_for_competition("arg.1"))
    print("nl.1  =>", get_country_for_competition("nl.1"))
    print("uefa.1 =>", get_country_for_competition("uefa.1"))

