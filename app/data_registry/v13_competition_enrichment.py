from typing import Dict, Optional

V13_COMPETITION_ALIASES: Dict[str, str] = {
    "ncaaw soccer": "usa.ncaaw",
    "club friendly": "friendly.club",
    "uefa nations league": "uefa.nations",
    "men's international friendly": "friendly.intl.men",
    "liga f": "esp.w.1",
    "taca de portugal, 2nd round": "por.cup",
    "laliga 2": "esp.2",
    "women's super league": "eng.w.1",
    "première ligue": "fr.w.1",
    "copa de la reina, first round": "esp.w.cup",
    "carabao cup, third round": "eng.cup",
    "copa del rey, qualifying round": "esp.cup",
    "nwsl": "usa.w.1",
    "copa chile, round of 16": "chi.cup",
    "usl super league": "usa.w.2",
    "euro u-21 qualifying, group c": "uefa.u21q",
    "women's international friendly": "friendly.intl.women",
    "northern super league": "can.w.1",
    "euro u-21 qualifying, group a": "uefa.u21q",
    "uefa nations league, group c1": "uefa.nations",
    "uefa nations league, group a1": "uefa.nations",
    "salvadoran primera": "slv.1",
    "guatemalan liga nacional": "gtm.1",
    "english fa cup qualifying, first round qualifying": "eng.fa.cup.q",
    "euro u-21 qualifying, group d": "uefa.u21q",
    "euro u-21 qualifying, group b": "uefa.u21q",
    "scottish league cup, quarterfinals": "sco.cup",
    "copa bolivia, group c": "bol.cup",
    "copa bolivia, group b": "bol.cup",
    "concacaf nations league, league b, group d": "concacaf.nations",
    "concacaf nations league, league b, group a": "concacaf.nations",
    "afcon qualifying, group f": "caf.afconq",
    "afcon qualifying, 2027 africa cup of nations qualifying - group d": "caf.afconq",
    "comp_superliga_kos": "kos.1",
    "uefa nations league, group c4": "uefa.nations",
    "uefa nations league, group c3": "uefa.nations",
    "uefa nations league, group b3": "uefa.nations",
    "uefa nations league, group b1": "uefa.nations",
    "uefa nations league, group a4": "uefa.nations",
    "uefa nations league, group a3": "uefa.nations",
    "uefa nations league, group a2": "uefa.nations",
    "english fa cup qualifying, second round qualifying": "eng.fa.cup.q",
    "euro u-21 qualifying, group g": "uefa.u21q",
    "dutch vrouwen eredivisie": "ned.w.1",
    "coppa italia, second round": "ita.cup",
    "copa colombia, round of 16": "col.cup",
    "copa bolivia, group a": "bol.cup",
    "concacaf nations league, league b, group b": "concacaf.nations",
    "concacaf nations league, league b - group d": "concacaf.nations",
    "concacaf nations league, league b - group b": "concacaf.nations",
    "concacaf nations league, league b - group a": "concacaf.nations",
    "belgian pro league": "bel.1",
    "arabian gulf cup, group a": "gulf.cup",
    "afcon qualifying, group l": "caf.afconq",
    "afcon qualifying, group i": "caf.afconq",
    "afcon qualifying, group e": "caf.afconq",
    "afcon qualifying, group d": "caf.afconq",
    "afcon qualifying, 2027 africa cup of nations qualifying - group l": "caf.afconq",
    "afcon qualifying, 2027 africa cup of nations qualifying - group j": "caf.afconq",
    "afcon qualifying, 2027 africa cup of nations qualifying - group i": "caf.afconq",
    "afcon qualifying, 2027 africa cup of nations qualifying - group h": "caf.afconq",
    "afcon qualifying, 2027 africa cup of nations qualifying - group g": "caf.afconq",
    "afcon qualifying, 2027 africa cup of nations qualifying - group f": "caf.afconq",
    "afcon qualifying, 2027 africa cup of nations qualifying - group e": "caf.afconq",
    "afcon qualifying, 2027 africa cup of nations qualifying - group c": "caf.afconq",
    "afcon qualifying, 2027 africa cup of nations qualifying - group a": "caf.afconq",
    "comp_premium_liiga_est": "est.1",
    "comp_premier_league_blr": "blr.1",
    "women's europa cup, second qualifying round": "uefa.w.cup",
    "uefa nations league, group d2": "uefa.nations",
    "uefa nations league, group d1": "uefa.nations",
    "u.s. open cup, semifinals": "usa.cup",
    "scottish cup qualifying, preliminary round three": "sco.cup.q",
    "spfl challenge cup, league phase": "sco.challenge",
    "euro u-21 qualifying, group i": "uefa.u21q",
    "euro u-21 qualifying, group h": "uefa.u21q",
    "euro u-21 qualifying": "uefa.u21q",
    "efl trophy, southern group f": "eng.trophy",
    "efl trophy, southern group e": "eng.trophy",
    "efl trophy, southern group c": "eng.trophy",
    "efl trophy, northern group d": "eng.trophy",
    "efl trophy, northern group c": "eng.trophy",
    "copa colombia, stage 1b": "col.cup",
    "copa bolivia, group d": "bol.cup",
    "concacaf nations league, league c, group c": "concacaf.nations",
    "concacaf nations league, league c, group b": "concacaf.nations",
    "concacaf nations league, league c, group a": "concacaf.nations",
    "concacaf nations league, league b, group c": "concacaf.nations",
    "concacaf nations league, league a, group a": "concacaf.nations",
    "arabian gulf cup, group b": "gulf.cup",
    "afcon qualifying, group k": "caf.afconq",
    "afcon qualifying, group j": "caf.afconq",
    "afcon qualifying, group h": "caf.afconq",
    "afcon qualifying, group c": "caf.afconq",
    "afcon qualifying, group b": "caf.afconq",
    "afcon qualifying, group a": "caf.afconq",
    "afcon qualifying, 2027 africa cup of nations qualifying - group b": "caf.afconq",
    "serie a": "ita.1",
    "ligue 1": "fr.1",
    "comp primera division crc": "crc.1",
    "south african premier": "zaf.1",
    "afc champions league two group b": "afc.2",
    "afc champions league two group h": "afc.2",
    "liga auf uruguaya": "uru.1",
    "caf champions league first preliminary round": "caf.1",
    "afc champions league two group g": "afc.2",
    "afc champions league two group f": "afc.2",

    "comp primera division bol": "bol.1",
    "comp egyptian prem egy": "egy.1",
    "comp k league 1 kor": "kor.1",
    "comp serie b bra": "bra.2",
    "comp copa sudamericana": "conmebol.2",
    "comp copa libertadores": "conmebol.1",
    "comp uae pro league uae": "are.1",
    "comp v league vie": "vnm.1",
    "japanese j1 league": "jpn.1",
    "efl league one": "eng.3",
    "spfl premiership": "sco.1",
    "ligue 2": "fr.2",
    "uefa champions league league phase": "uefa.1",
}


def _normalise_alias_key(value):
    """Match V13CompetitionIdentityResolver._normalise exactly."""
    import re
    import unicodedata
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# Normalised index built once at import time.
# Keys are stored in resolver-compatible form so lookups work
# regardless of punctuation, case, or accents on either side.
_NORMALISED_ALIASES = {
    _normalise_alias_key(k): v for k, v in V13_COMPETITION_ALIASES.items()
}


def get_competition_alias(name):
    if not name:
        return None
    return _NORMALISED_ALIASES.get(_normalise_alias_key(name))


def get_all_competition_aliases() -> Dict[str, str]:
    return dict(V13_COMPETITION_ALIASES)
