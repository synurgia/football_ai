"""Competition → free-source map for daily fixture fetching.

Rules:
  1. Every source listed here is free (no card, no paid tier).
  2. Coverage is per-competition. No source is primary — all are queried.
  3. Fallback is always the V1.3 registry (official federation URLs).
  4. Sources are queried for TODAY'S date only, never past dates.

Sources:
  fd   — football-data.org  (/v4/matches returns today by default)
  tsdb — TheSportsDB        (eventsday.php?d=YYYY-MM-DD)
  oldb — OpenLigaDB         (getmatchdata/{league})
  espn — ESPN Hidden        (scoreboard?dates=YYYYMMDD)
  apif — API-Football       (fixtures?date=YYYY-MM-DD, 100 req/day)
  zafx — Zafronix           (fixtures by date, 50 req/day)
  ofb  — openfootball JSON  (daily updated at 05:00 UTC, no key)
  reg  — V1.3 registry      (official federation URLs, always appended)
"""

from typing import Dict, List, Tuple

# football-data.org free tier (12 competitions) — codes are for /v4/
FD_CODES: Dict[str, str] = {
    "eng.1": "PL",
    "eng.2": "ELC",
    "esp.1": "PD",
    "ita.1": "SA",
    "ger.1": "BL1",
    "fra.1": "FL1",
    "ned.1": "DED",
    "por.1": "PPL",
    "bra.1": "BSA",
    "uefa.1": "CL",
    "fifa.1": "WC",
}

# TheSportsDB — league IDs (free tier, key "3")
TSDB_LEAGUES: Dict[str, int] = {
    "eng.1": 4328, "eng.2": 4329, "eng.3": 4330, "eng.4": 4331,
    "eng.cup": 4482, "eng.trophy": 4483,
    "esp.1": 4335, "esp.2": 4336, "esp.cup": 4483,
    "ita.1": 4332, "ita.2": 4333, "ita.cup": 4505,
    "ger.1": 4331, "ger.2": 4332,  # overwritten below with correct values
    "fra.1": 4334, "fra.2": 4335,
    "ned.1": 4337, "por.1": 4344,
    "sco.1": 4338,
    "tur.1": 4339,
    "bel.1": 4341,
    "rus.1": 4343,
    "usa.1": 4346,
    "mex.1": 4350,
    "bra.1": 4351,
    "arg.1": 4352,
    "jpn.1": 4355,
    "kor.1": 4356,
    "chn.1": 4357,
    "sau.1": 4358,
    "aus.1": 4359,
    "uefa.1": 4480, "uefa.2": 4481, "uefa.3": 4482,
    "fifa.1": 4429,
}
# Correct overrides for German leagues
TSDB_LEAGUES["ger.1"] = 4331
TSDB_LEAGUES["ger.2"] = 4332
TSDB_LEAGUES["ger.3"] = 4333

# OpenLigaDB — free, keyless, German leagues only
OLDB_LEAGUES: Dict[str, str] = {
    "de.1": "bl1",
    "de.2": "bl2",
    "de.3": "liga3",
}

# ESPN Hidden API — league slugs
ESPN_SLUGS: Dict[str, str] = {
    "eng.1": "eng.1", "eng.2": "eng.2", "eng.3": "eng.3", "eng.4": "eng.4",
    "eng.5": "eng.5", "eng.cup": "eng.fa", "eng.trophy": "eng.efl.trophy",
    "esp.1": "esp.1", "esp.2": "esp.2", "esp.cup": "esp.copa_del_rey",
    "esp.w.1": "esp.w.1", "esp.w.cup": "esp.w.copa_reina",
    "ita.1": "ita.1", "ita.2": "ita.2", "ita.3": "ita.3", "ita.cup": "ita.coppa_italia",
    "ger.1": "ger.1", "ger.2": "ger.2", "ger.3": "ger.3",
    "fra.1": "fra.1", "fra.2": "fra.2", "fr.w.1": "fra.w.1",
    "ned.1": "ned.1", "ned.2": "ned.2",
    "por.1": "por.1", "por.2": "por.2", "por.cup": "por.taca_portugal",
    "sco.1": "sco.1", "sco.2": "sco.2", "sco.3": "sco.3", "sco.4": "sco.4",
    "sco.cup": "sco.tennents_cup", "sco.challenge": "sco.challenge_cup",
    "bel.1": "bel.1",
    "tur.1": "tur.1", "tur.2": "tur.2",
    "rus.1": "rus.1",
    "gre.1": "gre.1",
    "aut.1": "aut.1",
    "sui.1": "sui.1",
    "ukr.1": "ukr.1",
    "pol.1": "pol.1",
    "rou.1": "rou.1",
    "cze.1": "cze.1",
    "cro.1": "cro.1",
    "srb.1": "srb.1",
    "den.1": "den.1",
    "nor.1": "nor.1",
    "swe.1": "swe.1",
    "fin.1": "fin.1",
    "irl.1": "irl.1",
    "nir.1": "nir.1",
    "isl.1": "isl.1",
    "isr.1": "isr.1",
    "usa.1": "usa.1", "usa.2": "usa.canadian", "usa.3": "usa.usl.1",
    "usa.4": "usa.usl.l1", "usa.cup": "usa.open",
    "usa.w.1": "usa.nwsl", "usa.w.2": "usa.usl.w",
    "usa.ncaaw": "usa.ncaa.w",
    "mex.1": "mex.1", "mex.2": "mex.2",
    "bra.1": "bra.1", "bra.2": "bra.2", "bra.3": "bra.3",
    "arg.1": "arg.1", "arg.2": "arg.2", "arg.3": "arg.copa",
    "chi.1": "chi.1", "chi.cup": "chi.copa",
    "col.1": "col.1", "col.cup": "col.copa",
    "jpn.1": "jpn.1", "jpn.2": "jpn.2", "jpn.3": "jpn.3",
    "kor.1": "kor.1", "kor.2": "kor.2",
    "chn.1": "chn.1", "chn.2": "chn.2",
    "sau.1": "sau.1", "sau.2": "sau.2",
    "aus.1": "aus.1",
    "ind.1": "ind.1", "ind.2": "ind.2",
    "tha.1": "tha.1", "tha.2": "tha.2",
    "idn.1": "idn.1", "idn.2": "idn.2",
    "mys.1": "mys.1",
    "vnm.1": "vnm.1", "vnm.2": "vnm.2",
    "irn.1": "irn.1", "irn.2": "irn.2",
    "irq.1": "irq.1", "irq.2": "irq.2",
    "jor.1": "jor.1", "jor.2": "jor.2",
    "qat.1": "qat.1", "qat.2": "qat.2",
    "are.1": "uae.1", "are.2": "uae.2",
    "uzb.1": "uzb.1", "uzb.2": "uzb.2",
    "kaz.1": "kaz.1", "kaz.2": "kaz.2",
    # Continental
    "uefa.1": "uefa.champions", "uefa.2": "uefa.europa",
    "uefa.3": "uefa.europa.conf", "uefa.nations": "uefa.nations",
    "uefa.u21q": "uefa.euro_u21_qualifiers", "uefa.w.cup": "uefa.wchampions",
    "fifa.1": "fifa.world", "fifa.2": "fifa.cwc", "fifa.3": "fifa.confederations",
    "caf.1": "caf.champions", "caf.2": "caf.confed", "caf.afconq": "caf.afcon_qualifiers",
    "afc.1": "afc.champions", "afc.2": "afc.cup", "afc.cup": "afc.cup",
    "concacaf.1": "concacaf.champions", "concacaf.2": "concacaf.leagues_cup",
    "concacaf.nations": "concacaf.nations", "gulf.cup": "concacaf.gulf",
    "conmebol.1": "conmebol.libertadores", "conmebol.2": "conmebol.sudamericana",
    "ofc.1": "ofc.champions", "ofc.2": "ofc.pro_league",
    # Friendly
    "friendly.club": "friendly.club",
    "friendly.intl.men": "fifa.friendly.men",  # falls back to /all/ on 404
    "friendly.intl.women": "fifa.friendly.women",  # falls back to /all/ on 404
}

# API-Football — league IDs (free tier, 100 req/day)
APIF_LEAGUES: Dict[str, int] = {
    "eng.1": 39, "eng.2": 40, "eng.3": 41, "eng.4": 42,
    "esp.1": 140, "esp.2": 141, "ita.1": 135, "ita.2": 136,
    "ger.1": 78, "ger.2": 79, "fra.1": 61, "fra.2": 62,
    "ned.1": 88, "por.1": 94, "sco.1": 179, "tur.1": 203,
    "bel.1": 144, "rus.1": 235, "usa.1": 253, "mex.1": 262,
    "bra.1": 71, "arg.1": 128, "jpn.1": 98, "kor.1": 292,
    "chn.1": 169, "sau.1": 307, "aus.1": 188,
    "uefa.1": 2, "uefa.2": 3, "uefa.3": 848,
    "fifa.1": 1, "caf.1": 12, "afc.1": 17,
}

# Zafronix — competitions with free key (50 req/day)
ZAFX_COMPS: Dict[str, str] = {
    "fifa.1": "fifa/worldcup/v1",
    "uefa.1": "uefa/championsleague/v1",
    "uefa.2": "uefa/europaleague/v1",
    "uefa.nations": "uefa/nationsleague/v1",
}

# openfootball football.json — free public domain, auto-updated daily 05:00 UTC
OFB_LEAGUES: Dict[str, str] = {
    "eng.1": "en.1", "eng.2": "en.2",
    "de.1": "de.1", "de.2": "de.2",
    "es.1": "es.1", "esp.1": "es.1",
    "it.1": "it.1", "ita.1": "it.1",
    "fr.1": "fr.1", "fra.1": "fr.1",
    "at.1": "at.1", "aut.1": "at.1",
    "nl.1": "nl.1", "ned.1": "nl.1",
    "pt.1": "pt.1", "por.1": "pt.1",
    "ro.1": "ro.1", "rou.1": "ro.1",
    "sc.1": "sc.1", "sco.1": "sc.1",
}


def sources_for_competition(competition_id: str) -> List[Tuple[str, str]]:
    """Return the ordered list of (source_key, source_arg) for a competition.

    Order is by coverage depth, not by authority — all sources are queried
    in parallel by the collector. The caller is responsible for merging.
    """
    if not competition_id:
        return []
    cid = str(competition_id).strip().lower()
    out: List[Tuple[str, str]] = []

    if cid in FD_CODES:
        out.append(("fd", FD_CODES[cid]))
    if cid in TSDB_LEAGUES:
        out.append(("tsdb", str(TSDB_LEAGUES[cid])))
    if cid in OLDB_LEAGUES:
        out.append(("oldb", OLDB_LEAGUES[cid]))
    if cid in ESPN_SLUGS:
        out.append(("espn", ESPN_SLUGS[cid]))
    if cid in APIF_LEAGUES:
        out.append(("apif", str(APIF_LEAGUES[cid])))
    if cid in ZAFX_COMPS:
        out.append(("zafx", ZAFX_COMPS[cid]))
    if cid in OFB_LEAGUES:
        out.append(("ofb", OFB_LEAGUES[cid]))

    # Always append the V1.3 registry fallback
    out.append(("reg", cid))
    return out


def describe_coverage() -> Dict[str, int]:
    """Return how many competitions each source covers."""
    return {
        "football-data.org": len(FD_CODES),
        "TheSportsDB": len(TSDB_LEAGUES),
        "OpenLigaDB": len(OLDB_LEAGUES),
        "ESPN": len(ESPN_SLUGS),
        "API-Football": len(APIF_LEAGUES),
        "Zafronix": len(ZAFX_COMPS),
        "openfootball": len(OFB_LEAGUES),
    }
