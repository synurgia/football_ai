from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, Optional

from app.data_registry.v1_3_competition_catalogue import (
    V13_COMPETITION_CATALOGUE,
)


class V13CompetitionIdentityResolver:
    """
    V1.3 system-wide competition identity resolver.

    Purpose:
        Resolve provider/discovery competition names to the
        authoritative V1.3 competition catalogue.

    Rules:
        1. Never invent competition IDs.
        2. Never modify the authoritative catalogue.
        3. Exact catalogue identity has priority.
        4. Verified aliases are controlled mappings only.
        5. Ambiguous generic names require context.
        6. No unrestricted fuzzy matching.
        7. Unresolved identity remains UNRESOLVED.
    """

    def __init__(self) -> None:

        self._by_id: Dict[str, Dict[str, Any]] = {
            str(item["competition_id"]): item
            for item in V13_COMPETITION_CATALOGUE
        }

        self._by_name: Dict[str, str] = {}

        for item in V13_COMPETITION_CATALOGUE:
            key = self._normalise(item["name"])

            # Do not silently overwrite collisions.
            # Ambiguous names are stored separately.
            existing = self._by_name.get(key)

            if existing is None:
                self._by_name[key] = item["competition_id"]
            elif existing != item["competition_id"]:
                self._by_name[key] = "__AMBIGUOUS__"

        # ------------------------------------------------------------
        # VERIFIED PROVIDER ALIASES
        # ------------------------------------------------------------
        #
        # These are deliberate identity mappings.
        # They do NOT alter the authoritative catalogue.
        #
        ALIASES: Dict[str, str] = {


            # England
            "english premier league": "eng.1",
            "english championship": "eng.2",
              "efl championship": "eng.2",
            "english league one": "eng.3",
            "english league two": "eng.4",
            "english national league": "eng.5",
    "liga de expansion mx": "mex.2",


            # Germany
            "german bundesliga": "de.1",
            "germany bundesliga": "de.1",
            "2 bundesliga": "de.2",
            "german 2 bundesliga": "de.2",
            "3 liga germany": "de.3",

            # France
            "french ligue 1": "fr.1",
            "france ligue 1": "fr.1",
            "french ligue 2": "fr.2",
            "france ligue 2": "fr.2",
            "championnat national france": "fr.3",

            # Italy
            "italian serie a": "ita.1",
            "italy serie a": "ita.1",
            "italian serie b": "ita.2",
            "italy serie b": "ita.2",
            "italian serie c": "ita.3",

            # Spain is intentionally NOT mapped because esp.1
            # is not part of the authoritative 191 catalogue.

            # Portugal
            "liga portugal": "por.1",
            "portuguese primeira liga": "por.1",
            "primeira liga portugal": "por.1",
            "liga portugal 2": "por.2",

            # Netherlands
            "dutch eredivisie": "nl.1",
            "netherlands eredivisie": "nl.1",
            "dutch eerste divisie": "nl.2",
              "keuken kampioen divisie": "nl.2",

            # Belgium intentionally omitted because no Belgian
            # competition exists in the authoritative 191 catalogue.

            # Turkey
            "turkish super lig": "tur.1",
            "turkish süper lig": "tur.1",
            "turkey super lig": "tur.1",
            "turkey süper lig": "tur.1",
            "turkish 1 lig": "tur.2",

            # Greece
            "greek super league": "gre.1",
            "super league greece": "gre.1",
            "greek super league 2": "gre.2",

            # Austria
            "austrian bundesliga": "aut.1",
            "austrian 2 liga": "aut.2",

            # Switzerland
            "swiss super league": "sui.1",
            "switzerland super league": "sui.1",
            "swiss challenge league": "sui.2",

            # Poland
            "polish ekstraklasa": "pol.1",
            "poland ekstraklasa": "pol.1",
            "polish i liga": "pol.2",

            # Romania
            "romanian liga i": "rou.1",
            "romanian liga 1": "rou.1",
            "romanian liga ii": "rou.2",
            "romanian liga 2": "rou.2",

            # Czech Republic
            "czech first league": "cze.1",
            "czech first division": "cze.1",
            "czech national football league": "cze.2",

            # Croatia
            "croatian football league": "cro.1",
            "croatian first league": "cro.1",
            "croatian prva nl": "cro.2",

            # Serbia
            "serbian superliga": "srb.1",
            "serbia superliga": "srb.1",
            "serbian prva liga": "srb.2",

            # Ukraine
            "ukrainian premier league": "ukr.1",
            "ukrainian persha liha": "ukr.2",

            # Scandinavia
            "norwegian eliteserien": "nor.1",
            "norway eliteserien": "nor.1",
            "swedish allsvenskan": "swe.1",
            "sweden allsvenskan": "swe.1",
            "danish superliga": "den.1",
            "denmark superliga": "den.1",
            "finnish veikkausliiga": "fin.1",
            "icelandic besta deild": "isl.1",

            # Ireland / Northern Ireland / Scotland
            "league of ireland premier division": "irl.1",
            "league of ireland first division": "irl.2",
            "nifl premiership": "nir.1",
            "nifl championship": "nir.2",
            "scottish premiership": "sco.1",
            "scottish championship": "sco.2",
              "spfl championship": "sco.2",
            "scottish league one": "sco.3",
            "scottish league two": "sco.4",

            # Asia
            "j league": "jpn.1",
            "japan j1": "jpn.1",
            "japan j1 league": "jpn.1",
            "japan j2 league": "jpn.2",
            "japan j3 league": "jpn.3",

            "k league 1": "kor.1",
            "k league 2": "kor.2",

            "saudi professional league": "sau.1",
            "saudi pro league": "sau.1",
            "saudi first division": "sau.2",

            "uae pro league": "are.1",
            "uae first division": "are.2",

            "qatar stars league": "qat.1",
            "qatar second division": "qat.2",

            "indian super league": "ind.1",
            "i league india": "ind.2",

            "persian gulf pro league": "irn.1",
            "iranian pro league": "irn.1",

            "iraq stars league": "irq.1",

            "malaysia super league": "mys.1",

            "thai league 1": "tha.1",
            "thai league 2": "tha.2",

            "uzbekistan super league": "uzb.1",
            "uzbekistan pro league": "uzb.2",

            "vietnam v league 1": "vnm.1",
            "vietnam v league 2": "vnm.2",

            "chinese super league": "chn.1",
            "china super league": "chn.1",
            "china league one": "chn.2",

            "indonesian liga 1": "idn.1",
            "indonesian liga 2": "idn.2",

            # Africa
            "nigeria premier football league": "nga.1",
            "nigeria premier league": "nga.1",
            "ghana premier league": "gha.1",
            "kenya premier league": "ken.1",
            "tanzania premier league": "tza.1",
            "uganda premier league": "uga.1",
            "zambia super league": "zmb.1",
            "south africa premier soccer league": "zaf.1",
            "south african premier soccer league": "zaf.1",
            "morocco botola pro": "mar.1",
            "botola pro": "mar.1",
            "senegal premier league": "sen.1",
            "egyptian premier league": "egy.1",
            "algeria ligue 1": "dza.1",
            "tunisia ligue 1": "tun.1",

            # Americas
            "argentine lpf": "arg.1",
              "argentine primera b": "arg.2",
            "argentina primera division": "arg.1",
            "brazil serie a": "bra.1",
            "brazilian serie a": "bra.1",
            "brasileirao serie a": "bra.1",
            "brasileirao": "bra.1",
            "brazil serie b": "bra.2",
            "brazilian serie b": "bra.2",

            "chilean primera": "chi.1",
            "chile primera": "chi.1",

            "colombian primera a": "col.1",
              "bolivian liga profesional": "bol.1",
              "honduran liga nacional": "hon.1",
              "paraguayan primera": "par.1",
              "peru liga 1": "per.1",
            "colombia primera a": "col.1",

            "ligapro ecuador": "ecu.1",
            "ecuador ligapro": "ecu.1",

            "liga mx": "mex.1",
            "mexican liga mx": "mex.1",

            "mls": "usa.1",
            "major league soccer": "usa.1",
            "usl championship": "usa.3",
            "usl league one": "usa.4",

            # International
            "afc champions league": "afc.1",
            "afc champions league elite": "afc.1",
            "afc champions league two": "afc.2",

            "caf champions league": "caf.1",
            "caf confederation cup": "caf.2",

            "uefa champions league": "uefa.1",
            "uefa europa league": "uefa.2",
            "uefa conference league": "uefa.3",

            "copa libertadores": "conmebol.1",
            "copa sudamericana": "conmebol.2",

            "concacaf champions cup": "concacaf.1",
            "concacaf champions league": "concacaf.1",
            "leagues cup": "concacaf.2",

            "ofc champions league": "ofc.1",
            "ofc professional league": "ofc.2",

            "fifa world cup": "fifa.1",
            "fifa club world cup": "fifa.2",
            "fifa intercontinental cup": "fifa.3",
        "AFC Champions League Two, Group A": "afc.2",
        "AFC Champions League Two, Group C": "afc.2",
        "AFC Champions League Two, Group D": "afc.2",
        "AFC Champions League Two, Group E": "afc.2",
        "CAF Confederation Cup, First Preliminary Round": "caf.2",
        "UEFA Europa League, League Phase": "uefa.2",
        "CONMEBOL Sudamericana, Quarterfinals": "conmebol.2",
        "CONMEBOL Libertadores, Quarterfinals": "conmebol.1",
        "Russian Premier": "rus.1",
    "LALIGA": "esp.1",
    "Dutch Vrouwen KNVB Beker, Second Qualifying Round": "ned.2",
    "NCAAM Soccer": "usa.5",
    "Liga FUTVE": "ven.1",
    "Argentine Nacional B": "arg.2",
    "Copa Argentina, Quarterfinals": "arg.3",
}

        self._aliases: Dict[str, str] = {}

        for alias, competition_id in ALIASES.items():
            if competition_id in self._by_id:
                self._aliases[self._normalise(alias)] = competition_id

    # ------------------------------------------------------------
    # NORMALISATION
    # ------------------------------------------------------------

    @staticmethod
    def _normalise(value: Any) -> str:
        text = str(value or "").strip().lower()

        text = unicodedata.normalize("NFKD", text)
        text = "".join(
            char for char in text
            if not unicodedata.combining(char)
        )

        text = re.sub(r"[^a-z0-9]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text

    # ------------------------------------------------------------
    # INTERNAL RESULT
    # ------------------------------------------------------------

    def _resolved(
        self,
        competition_id: str,
        method: str,
    ) -> Dict[str, Any]:

        item = self._by_id[competition_id]

        return {
            "competition_id": competition_id,
            "competition_name": item["name"],
            "match_method": method,
            "status": "RESOLVED",
        }

    # ------------------------------------------------------------
    # RESOLVE
    # ------------------------------------------------------------

    def resolve(
        self,
        competition_name: str,
        country: Optional[str] = None,
        competition_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        if not competition_name:
            return {
                "competition_id": None,
                "competition_name": None,
                "match_method": "NONE",
                "status": "UNRESOLVED",
            }

        raw = str(competition_name).strip()

        # --------------------------------------------------------
        # 1. Explicit authoritative ID
        # --------------------------------------------------------

        if competition_id:
            cid = str(competition_id).strip()

            if cid in self._by_id:
                return self._resolved(
                    cid,
                    "EXPLICIT_AUTHORITATIVE_ID",
                )

        normalized = self._normalise(raw)

        if not normalized:
            return {
                "competition_id": None,
                "competition_name": raw,
                "match_method": "NONE",
                "status": "UNRESOLVED",
            }

        # --------------------------------------------------------
        # --------------------------------------------------------
        # Verified aliases are reusable system knowledge.
        # Their target is accepted only if it exists in the
        # authoritative competition catalogue.
        if normalized:
            from app.data_registry.v13_competition_enrichment import get_competition_alias
            alias_id = get_competition_alias(normalized)

            if alias_id and alias_id in self._by_id:
                return self._resolved(
                    alias_id,
                    "VERIFIED_ENRICHMENT_ALIAS",
                )

        # --------------------------------------------------------
        # 2. Exact authoritative name
        # --------------------------------------------------------

        exact = self._by_name.get(normalized)

        if exact and exact != "__AMBIGUOUS__":
            return self._resolved(
                exact,
                "EXACT_NORMALIZED",
            )

        # --------------------------------------------------------
        # 3. Verified controlled alias
        # --------------------------------------------------------

        alias_id = self._aliases.get(normalized)

        if alias_id:
            return self._resolved(
                alias_id,
                "VERIFIED_ALIAS",
            )

        # --------------------------------------------------------
        # 4. Explicit context handling
        #
        # Context is intentionally conservative.
        # It is used only for known ambiguous generic names.
        # --------------------------------------------------------

        country_key = self._normalise(country)

        context_map = {

            # Serie A
            ("serie a", "italy"): "ita.1",
            ("serie a", "italia"): "ita.1",
            ("serie a", "brazil"): "bra.1",
            ("serie a", "brasil"): "bra.1",

            # Ligue 1
            ("ligue 1", "france"): "fr.1",
            ("ligue 1", "tunisia"): "tun.1",
            ("ligue 1", "algeria"): "dza.1",
            ("ligue 1", "cote d ivoire"): "civ.1",

            # Liga 1
            ("liga 1", "indonesia"): "idn.1",
            ("liga 1", "peru"): "per.1",

            # Liga 2
            ("liga 2", "indonesia"): "idn.2",
            ("liga 2", "peru"): "per.2",

            # First League
            ("first league", "armenia"): "arm.2",
            ("first league", "azerbaijan"): "aze.2",
            ("first league", "bosnia"): "bih.2",

            # Championship
            ("championship", "england"): "eng.2",
            ("championship", "tanzania"): "tza.2",
            ("championship", "northern ireland"): "nir.2",
            ("championship", "scotland"): "sco.2",
        }

        context_id = context_map.get(
            (normalized, country_key)
        )

        if context_id:
            return self._resolved(
                context_id,
                "VERIFIED_CONTEXT",
            )

        # --------------------------------------------------------
        # 5. Controlled regional suffixes
        # --------------------------------------------------------

        suffixes = (
            ", west region",
            ", east region",
            " west region",
            " east region",
            " - west region",
            " - east region",
        )

        for suffix in suffixes:

            if normalized.endswith(suffix):

                base = normalized[:-len(suffix)].strip()

                base_id = self._by_name.get(base)

                if (
                    base_id
                    and base_id != "__AMBIGUOUS__"
                ):
                    return self._resolved(
                        base_id,
                        "CONTROLLED_SUFFIX",
                    )

                alias_id = self._aliases.get(base)

                if alias_id:
                    return self._resolved(
                        alias_id,
                        "CONTROLLED_SUFFIX_ALIAS",
                    )

        # --------------------------------------------------------
        # 6. Explicit ambiguity
        # --------------------------------------------------------

        if exact == "__AMBIGUOUS__":
            return {
                "competition_id": None,
                "competition_name": raw,
                "match_method": "AMBIGUOUS",
                "status": "UNRESOLVED",
            }

        # --------------------------------------------------------
        # 7. No identity found
        # --------------------------------------------------------

        return {
            "competition_id": None,
            "competition_name": raw,
            "match_method": "NONE",
            "status": "UNRESOLVED",
        }


if __name__ == "__main__":

    resolver = V13CompetitionIdentityResolver()

    tests = [
        ("Premier League", None),
        ("English Premier League", None),

        ("Brasileirão Série A", None),
        ("Brazil Serie A", None),
        ("Brazilian Serie A", None),

        ("Serie A", "Italy"),
        ("Serie A", "Brazil"),

        ("AFC Champions League", None),
        ("AFC Champions League Elite", None),
        ("CAF Champions League", None),
        ("UEFA Champions League", None),

        ("La Liga", None),

        ("Ligue 1", "France"),
        ("Ligue 1", "Tunisia"),

        ("French Ligue 1", None),
        ("K League 1", None),
        ("Botola Pro", None),
        ("Saudi Professional League", None),
        ("J League", None),
        ("Allsvenskan", None),
    ]

    print("=== V1.3 COMPETITION IDENTITY RESOLVER ===")

    for name, country in tests:

        result = resolver.resolve(
            name,
            country=country,
        )

        context = (
            f" [{country}]"
            if country
            else ""
        )

        print(
            f"{name}{context} -> {result}"
        )

def resolve_competition(label: str):
    """Compatibility wrapper around the existing V1.3 identity resolver."""
    resolver = V13CompetitionIdentityResolver()
    return resolver.resolve(label)

