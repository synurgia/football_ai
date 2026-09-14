"""
V1.3 AUTHORITATIVE COMPETITION CATALOGUE

Ground-truth catalogue derived from the V1.3 Global Football Competition Map PDF.

IMPORTANT:
- Exactly 195 catalogue entries.
- This is a reference catalogue, NOT a live-source registry.
- Source coverage is handled separately by v1_3_source_registry.py.
- Missing live source coverage must never remove a competition from this catalogue.
"""

from typing import Dict, List, TypedDict


class V13Competition(TypedDict):
    competition_id: str
    name: str
    region: str


V13_COMPETITION_CATALOGUE: List[V13Competition] = [
    # ============================================================
    # AFRICA
    # ============================================================
    {"competition_id": "ago.1", "name": "Girabola", "region": "AFRICA"},
    {"competition_id": "ago.2", "name": "Segundona", "region": "AFRICA"},
    {"competition_id": "civ.1", "name": "Ligue 1", "region": "AFRICA"},
    {"competition_id": "civ.2", "name": "Ligue 2", "region": "AFRICA"},
    {"competition_id": "cod.1", "name": "Linafoot / Ligue 1", "region": "AFRICA"},
    {"competition_id": "cod.2", "name": "Ligue 2", "region": "AFRICA"},
    {"competition_id": "dza.1", "name": "Ligue Professionnelle 1", "region": "AFRICA"},
    {"competition_id": "dza.2", "name": "Ligue Professionnelle 2", "region": "AFRICA"},
    {"competition_id": "egy.1", "name": "Egyptian Premier League", "region": "AFRICA"},
    {"competition_id": "egy.2", "name": "Egyptian Second Division", "region": "AFRICA"},
    {"competition_id": "gha.1", "name": "Ghana Premier League", "region": "AFRICA"},
    {"competition_id": "gha.2", "name": "Division One League", "region": "AFRICA"},
    {"competition_id": "ken.1", "name": "Kenya Premier League", "region": "AFRICA"},
    {"competition_id": "ken.2", "name": "National Super League", "region": "AFRICA"},
    {"competition_id": "mar.1", "name": "Botola Pro", "region": "AFRICA"},
    {"competition_id": "mar.2", "name": "Botola 2", "region": "AFRICA"},
    {"competition_id": "nga.1", "name": "Nigeria Premier Football League", "region": "AFRICA"},
    {"competition_id": "nga.2", "name": "Nigeria National League", "region": "AFRICA"},
    {"competition_id": "sen.1", "name": "Senegal Premier League", "region": "AFRICA"},
    {"competition_id": "sen.2", "name": "Ligue 2", "region": "AFRICA"},
    {"competition_id": "tza.1", "name": "Tanzania Premier League", "region": "AFRICA"},
    {"competition_id": "tza.2", "name": "Championship", "region": "AFRICA"},
    {"competition_id": "tun.1", "name": "Ligue Professionnelle 1", "region": "AFRICA"},
    {"competition_id": "tun.2", "name": "Ligue Professionnelle 2", "region": "AFRICA"},
    {"competition_id": "uga.1", "name": "Uganda Premier League", "region": "AFRICA"},
    {"competition_id": "uga.2", "name": "FUFA Big League", "region": "AFRICA"},
    {"competition_id": "zaf.1", "name": "Premier Soccer League", "region": "AFRICA"},
    {"competition_id": "zaf.2", "name": "Motsepe Foundation Championship", "region": "AFRICA"},
    {"competition_id": "zmb.1", "name": "Zambia Super League", "region": "AFRICA"},
    {"competition_id": "zmb.2", "name": "National Division One", "region": "AFRICA"},

    # ============================================================
    # ASIA
    # ============================================================
    {"competition_id": "are.1", "name": "UAE Pro League", "region": "ASIA"},
    {"competition_id": "are.2", "name": "UAE First Division", "region": "ASIA"},
    {"competition_id": "chn.1", "name": "Chinese Super League", "region": "ASIA"},
    {"competition_id": "chn.2", "name": "China League One", "region": "ASIA"},
    {"competition_id": "idn.1", "name": "Liga 1", "region": "ASIA"},
    {"competition_id": "idn.2", "name": "Liga 2", "region": "ASIA"},
    {"competition_id": "ind.1", "name": "Indian Super League", "region": "ASIA"},
    {"competition_id": "ind.2", "name": "I-League", "region": "ASIA"},
    {"competition_id": "irn.1", "name": "Persian Gulf Pro League", "region": "ASIA"},
    {"competition_id": "irn.2", "name": "Azadegan League", "region": "ASIA"},
    {"competition_id": "irq.1", "name": "Iraq Stars League", "region": "ASIA"},
    {"competition_id": "irq.2", "name": "Iraq Premier Division", "region": "ASIA"},
    {"competition_id": "isr.1", "name": "Israeli Premier League", "region": "ASIA"},
    {"competition_id": "isr.2", "name": "Liga Leumit", "region": "ASIA"},
    {"competition_id": "jor.1", "name": "Jordan Pro League", "region": "ASIA"},
    {"competition_id": "jor.2", "name": "Jordan Division 1", "region": "ASIA"},
    {"competition_id": "jpn.1", "name": "J1 League", "region": "ASIA"},
    {"competition_id": "jpn.2", "name": "J2 League", "region": "ASIA"},
    {"competition_id": "jpn.3", "name": "J3 League", "region": "ASIA"},
    {"competition_id": "kaz.1", "name": "Kazakhstan Premier League", "region": "ASIA"},
    {"competition_id": "kaz.2", "name": "Kazakhstan First Division", "region": "ASIA"},
    {"competition_id": "kor.1", "name": "K League 1", "region": "ASIA"},
    {"competition_id": "kor.2", "name": "K League 2", "region": "ASIA"},
    {"competition_id": "mys.1", "name": "Malaysia Super League", "region": "ASIA"},
    {"competition_id": "mys.2", "name": "A1 Semi-Pro League", "region": "ASIA"},
    {"competition_id": "qat.1", "name": "Qatar Stars League", "region": "ASIA"},
    {"competition_id": "qat.2", "name": "Qatar Second Division", "region": "ASIA"},
    {"competition_id": "sau.1", "name": "Saudi Pro League", "region": "ASIA"},
    {"competition_id": "sau.2", "name": "Saudi First Division", "region": "ASIA"},
    {"competition_id": "tha.1", "name": "Thai League 1", "region": "ASIA"},
    {"competition_id": "tha.2", "name": "Thai League 2", "region": "ASIA"},
    {"competition_id": "uzb.1", "name": "Uzbekistan Super League", "region": "ASIA"},
    {"competition_id": "uzb.2", "name": "Uzbekistan Pro League", "region": "ASIA"},
    {"competition_id": "vnm.1", "name": "V.League 1", "region": "ASIA"},
    {"competition_id": "vnm.2", "name": "V.League 2", "region": "ASIA"},

    # ============================================================
    # OCEANIA
    # ============================================================
    {"competition_id": "aus.1", "name": "A-League Men", "region": "OCEANIA"},

    # ============================================================
    # EUROPE
    # ============================================================
    {"competition_id": "arm.1", "name": "Armenian Premier League", "region": "EUROPE"},
    {"competition_id": "arm.2", "name": "First League", "region": "EUROPE"},
    {"competition_id": "aut.1", "name": "Austrian Bundesliga", "region": "EUROPE"},
    {"competition_id": "aut.2", "name": "2. Liga", "region": "EUROPE"},
    {"competition_id": "aut.3", "name": "Regionalliga", "region": "EUROPE"},
    {"competition_id": "aze.1", "name": "Azerbaijan Premier League", "region": "EUROPE"},
    {"competition_id": "aze.2", "name": "First Division", "region": "EUROPE"},
    {"competition_id": "bih.1", "name": "Bosnia Premier League", "region": "EUROPE"},
    {"competition_id": "bih.2", "name": "First League", "region": "EUROPE"},
    {"competition_id": "bul.1", "name": "First Professional League", "region": "EUROPE"},
    {"competition_id": "bul.2", "name": "Second Professional League", "region": "EUROPE"},
    {"competition_id": "cro.1", "name": "Croatian Football League", "region": "EUROPE"},
    {"competition_id": "cro.2", "name": "Prva NL", "region": "EUROPE"},
    {"competition_id": "cyp.1", "name": "Cyprus First Division", "region": "EUROPE"},
    {"competition_id": "cyp.2", "name": "Cyprus Second Division", "region": "EUROPE"},
    {"competition_id": "cze.1", "name": "Czech First League", "region": "EUROPE"},
    {"competition_id": "cze.2", "name": "National Football League", "region": "EUROPE"},
    {"competition_id": "den.1", "name": "Danish Superliga", "region": "EUROPE"},
    {"competition_id": "den.2", "name": "1st Division", "region": "EUROPE"},
    {"competition_id": "de.1", "name": "Bundesliga", "region": "EUROPE"},
    {"competition_id": "de.2", "name": "2. Bundesliga", "region": "EUROPE"},
    {"competition_id": "de.3", "name": "3. Liga", "region": "EUROPE"},
    {"competition_id": "de.4", "name": "Regionalliga", "region": "EUROPE"},
    {"competition_id": "eng.1", "name": "Premier League", "region": "EUROPE"},
    {"competition_id": "eng.2", "name": "Championship", "region": "EUROPE"},
    {"competition_id": "eng.3", "name": "League One", "region": "EUROPE"},
    {"competition_id": "eng.4", "name": "League Two", "region": "EUROPE"},
    {"competition_id": "eng.5", "name": "National League", "region": "EUROPE"},
    {"competition_id": "fin.1", "name": "Veikkausliiga", "region": "EUROPE"},
    {"competition_id": "fin.2", "name": "Ykkösliiga", "region": "EUROPE"},
    {"competition_id": "fin.3", "name": "Ykkönen", "region": "EUROPE"},
    {"competition_id": "fr.1", "name": "Ligue 1", "region": "EUROPE"},
    {"competition_id": "fr.2", "name": "Ligue 2", "region": "EUROPE"},
    {"competition_id": "fr.3", "name": "National", "region": "EUROPE"},
    {"competition_id": "fro.1", "name": "Faroe Islands Premier League", "region": "EUROPE"},
    {"competition_id": "fro.2", "name": "1. Deild", "region": "EUROPE"},
    {"competition_id": "geo.1", "name": "Erovnuli Liga", "region": "EUROPE"},
    {"competition_id": "geo.2", "name": "Erovnuli Liga 2", "region": "EUROPE"},
    {"competition_id": "gre.1", "name": "Super League Greece", "region": "EUROPE"},
    {"competition_id": "gre.2", "name": "Super League 2", "region": "EUROPE"},
    {"competition_id": "hun.1", "name": "NB I", "region": "EUROPE"},
    {"competition_id": "hun.2", "name": "NB II", "region": "EUROPE"},
    {"competition_id": "isl.1", "name": "Besta deild karla", "region": "EUROPE"},
    {"competition_id": "isl.2", "name": "1. deild", "region": "EUROPE"},
    {"competition_id": "irl.1", "name": "League of Ireland Premier Division", "region": "EUROPE"},
    {"competition_id": "irl.2", "name": "League of Ireland First Division", "region": "EUROPE"},
    {"competition_id": "ita.1", "name": "Serie A", "region": "EUROPE"},
    {"competition_id": "ita.2", "name": "Serie B", "region": "EUROPE"},
    {"competition_id": "ita.3", "name": "Serie C", "region": "EUROPE"},
    {"competition_id": "nor.1", "name": "Eliteserien", "region": "EUROPE"},
    {"competition_id": "nor.2", "name": "OBOS-ligaen", "region": "EUROPE"},
    {"competition_id": "nor.3", "name": "2. divisjon", "region": "EUROPE"},
    {"competition_id": "nir.1", "name": "NIFL Premiership", "region": "EUROPE"},
    {"competition_id": "nir.2", "name": "NIFL Championship", "region": "EUROPE"},
    {"competition_id": "nl.1", "name": "Eredivisie", "region": "EUROPE"},
    {"competition_id": "nl.2", "name": "Eerste Divisie", "region": "EUROPE"},
    {"competition_id": "pol.1", "name": "Ekstraklasa", "region": "EUROPE"},
    {"competition_id": "pol.2", "name": "I Liga", "region": "EUROPE"},
    {"competition_id": "por.1", "name": "Primeira Liga", "region": "EUROPE"},
    {"competition_id": "por.2", "name": "Liga Portugal 2", "region": "EUROPE"},
    {"competition_id": "rou.1", "name": "Liga I", "region": "EUROPE"},
    {"competition_id": "rou.2", "name": "Liga II", "region": "EUROPE"},
    {"competition_id": "sco.1", "name": "Scottish Premiership", "region": "EUROPE"},
    {"competition_id": "sco.2", "name": "Scottish Championship", "region": "EUROPE"},
    {"competition_id": "sco.3", "name": "Scottish League One", "region": "EUROPE"},
    {"competition_id": "sco.4", "name": "Scottish League Two", "region": "EUROPE"},
    {"competition_id": "srb.1", "name": "Serbia SuperLiga", "region": "EUROPE"},
    {"competition_id": "srb.2", "name": "Prva Liga", "region": "EUROPE"},
    {"competition_id": "sui.1", "name": "Swiss Super League", "region": "EUROPE"},
    {"competition_id": "sui.2", "name": "Challenge League", "region": "EUROPE"},
    {"competition_id": "svk.1", "name": "Niké Liga", "region": "EUROPE"},
    {"competition_id": "svk.2", "name": "2. Liga", "region": "EUROPE"},
    {"competition_id": "svn.1", "name": "PrvaLiga", "region": "EUROPE"},
    {"competition_id": "svn.2", "name": "2. SNL", "region": "EUROPE"},
    {"competition_id": "swe.1", "name": "Allsvenskan", "region": "EUROPE"},
    {"competition_id": "swe.2", "name": "Superettan", "region": "EUROPE"},
    {"competition_id": "swe.3", "name": "Ettan", "region": "EUROPE"},
    {"competition_id": "tur.1", "name": "Süper Lig", "region": "EUROPE"},
    {"competition_id": "tur.2", "name": "1. Lig", "region": "EUROPE"},
    {"competition_id": "ukr.1", "name": "Ukrainian Premier League", "region": "EUROPE"},
    {"competition_id": "ukr.2", "name": "Persha Liha", "region": "EUROPE"},

    # ============================================================
    # AMERICAS
    # ============================================================
    {"competition_id": "arg.1", "name": "Liga Profesional", "region": "AMERICAS"},
    {"competition_id": "arg.2", "name": "Primera Nacional", "region": "AMERICAS"},
    {"competition_id": "bol.1", "name": "División de Fútbol Profesional", "region": "AMERICAS"},
    {"competition_id": "bra.1", "name": "Série A", "region": "AMERICAS"},
    {"competition_id": "bra.2", "name": "Série B", "region": "AMERICAS"},
    {"competition_id": "bra.3", "name": "Série C", "region": "AMERICAS"},
    {"competition_id": "chi.1", "name": "Primera", "region": "AMERICAS"},
    {"competition_id": "chi.2", "name": "Primera B", "region": "AMERICAS"},
    {"competition_id": "col.1", "name": "Primera A", "region": "AMERICAS"},
    {"competition_id": "col.2", "name": "Primera B", "region": "AMERICAS"},
    {"competition_id": "crc.1", "name": "Liga FPD", "region": "AMERICAS"},
    {"competition_id": "dom.1", "name": "Liga Dominicana", "region": "AMERICAS"},
    {"competition_id": "ecu.1", "name": "LigaPro A", "region": "AMERICAS"},
    {"competition_id": "ecu.2", "name": "LigaPro B", "region": "AMERICAS"},
    {"competition_id": "hon.1", "name": "Liga Nacional", "region": "AMERICAS"},
    {"competition_id": "mex.1", "name": "Liga MX", "region": "AMERICAS"},
    {"competition_id": "mex.2", "name": "Liga de Expansión", "region": "AMERICAS"},
    {"competition_id": "pan.1", "name": "Liga Panameña", "region": "AMERICAS"},
    {"competition_id": "par.1", "name": "Primera", "region": "AMERICAS"},
    {"competition_id": "par.2", "name": "División Intermedia", "region": "AMERICAS"},
    {"competition_id": "per.1", "name": "Liga 1", "region": "AMERICAS"},
    {"competition_id": "per.2", "name": "Liga 2", "region": "AMERICAS"},
    {"competition_id": "uru.1", "name": "Liga AUF", "region": "AMERICAS"},
    {"competition_id": "uru.2", "name": "Segunda", "region": "AMERICAS"},
    {"competition_id": "usa.1", "name": "MLS", "region": "AMERICAS"},
    {"competition_id": "usa.2", "name": "Canadian Premier League", "region": "AMERICAS"},
    {"competition_id": "usa.3", "name": "USL Championship", "region": "AMERICAS"},
    {"competition_id": "usa.4", "name": "USL League One", "region": "AMERICAS"},

    # ============================================================
    # INTERNATIONAL / CONTINENTAL
    # ============================================================
    {"competition_id": "uefa.1", "name": "UEFA Champions League", "region": "INTERNATIONAL"},
    {"competition_id": "uefa.2", "name": "UEFA Europa League", "region": "INTERNATIONAL"},
    {"competition_id": "uefa.3", "name": "UEFA Conference League", "region": "INTERNATIONAL"},
    {"competition_id": "conmebol.1", "name": "Copa Libertadores", "region": "INTERNATIONAL"},
    {"competition_id": "conmebol.2", "name": "Copa Sudamericana", "region": "INTERNATIONAL"},
    {"competition_id": "concacaf.1", "name": "Concacaf Champions Cup", "region": "INTERNATIONAL"},
    {"competition_id": "concacaf.2", "name": "Leagues Cup", "region": "INTERNATIONAL"},
    {"competition_id": "afc.1", "name": "AFC Champions League Elite", "region": "INTERNATIONAL"},
    {"competition_id": "afc.2", "name": "AFC Champions League Two", "region": "INTERNATIONAL"},
    {"competition_id": "caf.1", "name": "CAF Champions League", "region": "INTERNATIONAL"},
    {"competition_id": "caf.2", "name": "CAF Confederation Cup", "region": "INTERNATIONAL"},
    {"competition_id": "ofc.1", "name": "OFC Champions League", "region": "INTERNATIONAL"},
    {"competition_id": "ofc.2", "name": "OFC Professional League", "region": "INTERNATIONAL"},
    {"competition_id": "fifa.1", "name": "FIFA World Cup", "region": "INTERNATIONAL"},
    {"competition_id": "fifa.2", "name": "FIFA Club World Cup", "region": "INTERNATIONAL"},
    {"competition_id": "fifa.3", "name": "FIFA Intercontinental Cup", "region": "INTERNATIONAL"},
]


V13_COMPETITION_CATALOGUE_BY_ID: Dict[str, V13Competition] = {
    item["competition_id"]: item
    for item in V13_COMPETITION_CATALOGUE
}


def get_all_competitions() -> List[V13Competition]:
    return list(V13_COMPETITION_CATALOGUE)


def get_competition(competition_id: str) -> V13Competition:
    return V13_COMPETITION_CATALOGUE_BY_ID[competition_id]


def competition_count() -> int:
    return len(V13_COMPETITION_CATALOGUE)


def get_competitions_by_region(region: str) -> List[V13Competition]:
    return [
        item for item in V13_COMPETITION_CATALOGUE
        if item["region"] == region
    ]


def catalogue_integrity() -> Dict[str, object]:
    ids = [item["competition_id"] for item in V13_COMPETITION_CATALOGUE]
    duplicates = sorted({
        cid for cid in ids
        if ids.count(cid) > 1
    })

    return {
        "expected": 195,
        "actual": len(ids),
        "unique": len(set(ids)),
        "duplicates": duplicates,
        "status": (
            "PASS"
            if len(ids) == 195
            and len(set(ids)) == 195
            and not duplicates
            else "FAIL"
        ),
    }


if __name__ == "__main__":
    result = catalogue_integrity()

    print("=== V1.3 TERMUX COMPETITION CATALOGUE ===")
    print(f"EXPECTED: {result['expected']}")
    print(f"ACTUAL:   {result['actual']}")
    print(f"UNIQUE:   {result['unique']}")
    print(f"DUPLICATES: {result['duplicates']}")
    print(f"STATUS: {result['status']}")

    print("\n=== BY REGION ===")
    for region in ("AFRICA", "ASIA", "EUROPE", "OCEANIA", "AMERICAS", "INTERNATIONAL"):
        print(f"{region}: {len(get_competitions_by_region(region))}")

    if result["status"] != "PASS":
        raise SystemExit(1)
