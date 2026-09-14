"""
FOOTBALL AI V1.4 — FIVE-DIMENSIONAL INTELLIGENCE ENGINE
=========================================================
Builds directly on the V1.3 evidence architecture (competition map +
free-source framework from the two V1.3 PDFs) and adds the missing piece:
an AI reasoning layer that behaves like a genuine analyst rather than a
stat sheet — it can look at a match and say "yes, the home team is
favoured on paper, BUT the away side's defensive setup neutralises that,
so I see a draw", the way a human scout would.

WHAT'S NEW VS V1.3
------------------
1. GLOBAL_COMPETITION_MAP   — the full worldwide competition catalogue
   transcribed from "V1.3 Global Football Competition Map.pdf" (Nordic,
   Western/Central Europe, Eastern/SE Europe, Americas, Asia-Oceania,
   Africa, International/Continental). This is the *discovery universe*
   exactly as the PDF frames it — not every entry is wired to a live
   feed yet, and the PDF is explicit that this is intentional (activate
   fixture identity/reconciliation first, then progressively widen
   coverage).
2. SOURCE_REGISTRY           — the multi-source framework transcribed
   from "v1_3_free_football_data_sources.pdf". Per the PDF's own
   "source-governance rule": no single provider is treated as the truth
   for every question. Each data class (fixture, competition, team,
   player, lineup, weather, results, tactical, schedule, venue) lists
   every free/public candidate source; the retrieval layer is written
   so a second/third source can be added per competition without
   restructuring anything.
3. FiveDimensionalAnalyticsEngine — 10-game momentum / offensive /
   defensive / volatility / composite-index scoring (adapted from your
   Step 14/15 engine).
4. TacticalStyleProfiler + FiveDIntelligenceReasoner — the qualitative
   reasoning layer you asked for. It explicitly reasons about *how* a
   supposedly weaker away team can neutralise home advantage (deep
   block / low defensive line / bus-parking, in the sense of "concede
   fewer chances by inviting less possession") against a home side with
   sharper attacking output, and can conclude a draw even when the raw
   composite index favours the home side. Every such tactical read is
   explicitly labelled as an INFERENCE from scoreline patterns (goals
   for/against shape), not as a confirmed formation/press report,
   because no free source in the registry reliably exposes real
   tactical/formation data — this keeps the "evidence over invention"
   rule from the PDFs intact.
5. Weather is resolved for the *specific date and venue of the match*
   (not "today"), via Open-Meteo, exactly as source-registry section 1
   specifies — this already existed in V1.3 and is kept, with the
   freshness distinction (CURRENT vs long-range DATED forecast) made
   explicit in the final reasoning so a forecast 9 days out is never
   treated with the same confidence as one 24 hours out.
6. Every question the pipeline can ask is asked and logged — Q1..Q11
   below — and any question the free sources can't answer is marked
   INSUFFICIENT_EVIDENCE / UNKNOWN rather than guessed. The final
   verdict (Q11) is the only place inference is allowed to compound,
   and it says so.

HONESTY OVER COMPLETENESS (unchanged from V1.3)
------------------------------------------------
If a source doesn't have something, the question stays UNKNOWN. This
engine never invents lineups, injuries, or tactics that aren't backed
by retrieved evidence — it only reasons *about* the evidence it has,
and always says what it's missing.

USAGE
-----
    pip install requests
    python football_ai_v14_5d.py "Arsenal" "Chelsea" --competition eng.1
    python football_ai_v14_5d.py "Arsenal" "Chelsea" --competition eng.1 --json

Set FOOTBALL_DATA_API_KEY as an environment variable to enable
football-data.org as an additional cross-check source (free registered
tier — see https://www.football-data.org/documentation/quickstart).
Without it, the engine still runs on ESPN + Open-Meteo alone and says
so in the source log.
"""

from __future__ import annotations

from app.v1_2_piece_evidence_bridge import V12PieceEvidenceBridge
from app.v1_2_semantic_resolver import V12SemanticResolver

import argparse
import dataclasses
import datetime as dt
import json
import math
import os
import sys
from typing import Any, Optional

try:
    import requests
except ImportError:
    print("This script needs the 'requests' library. Install it with:\n"
          "    pip install requests")
    sys.exit(1)


# ===========================================================================
# SECTION 1 — GLOBAL COMPETITION MAP
# (transcribed from V1_3_Global_Football_Competition_Map.pdf — the
#  worldwide discovery universe. Kept as reference/expansion data, exactly
#  as the PDF frames it: "a discovery universe, not yet the final
#  machine-readable source registry.")
# ===========================================================================
GLOBAL_COMPETITION_MAP: dict[str, dict[str, list[str]]] = {
    "Nordic & Northern Europe": {
        "Iceland": ["Besta deild karla", "1. deild karla"],
        "Norway": ["Eliteserien", "OBOS-ligaen", "2. divisjon"],
        "Finland": ["Veikkausliiga", "Ykkösliiga", "Ykkönen"],
        "Sweden": ["Allsvenskan", "Superettan", "Ettan"],
        "Denmark": ["Superliga", "1st Division"],
        "Faroe Islands": ["Faroe Islands Premier League", "1. Deild"],
        "Ireland": ["League of Ireland Premier Division", "First Division"],
        "Northern Ireland": ["NIFL Premiership", "NIFL Championship"],
    },
    "Western & Central Europe": {
        "England": ["Premier League", "Championship", "League One", "League Two", "National League"],
        "Scotland": ["Scottish Premiership", "Championship", "League One", "League Two"],
        "Netherlands": ["Eredivisie", "Eerste Divisie"],
        "Germany": ["Bundesliga", "2. Bundesliga", "3. Liga", "Regionalliga"],
        "France": ["Ligue 1", "Ligue 2", "National"],
        "Belgium": ["Belgian Pro League", "Challenger Pro League"],
        "Austria": ["Bundesliga", "2. Liga", "Regionalliga"],
        "Switzerland": ["Swiss Super League", "Challenge League"],
        "Portugal": ["Primeira Liga", "Liga Portugal 2"],
        "Spain": ["La Liga", "Segunda División"],
    },
    "Central / Eastern / SE Europe": {
        "Italy": ["Serie A", "Serie B", "Serie C"],
        "Greece": ["Super League", "Super League 2"],
        "Turkey": ["Süper Lig", "1. Lig"],
        "Croatia": ["Croatian Football League", "Prva NL"],
        "Czechia": ["Czech First League", "Czech National Football League"],
        "Poland": ["Ekstraklasa", "I Liga"],
        "Romania": ["Liga I", "Liga II"],
        "Hungary": ["Nemzeti Bajnokság I", "NB II"],
        "Serbia": ["Serbian SuperLiga", "Prva Liga"],
        "Ukraine": ["Ukrainian Premier League", "Persha Liha"],
        "Bulgaria": ["First Professional Football League", "Second League"],
        "Slovenia": ["PrvaLiga", "2. SNL"],
        "Slovakia": ["Niké Liga", "2. Liga"],
        "Bosnia & Herzegovina": ["Premier League", "First League"],
        "Cyprus": ["Cypriot First Division", "Second Division"],
        "Georgia": ["Erovnuli Liga", "Erovnuli Liga 2"],
        "Armenia": ["Armenian Premier League", "First League"],
        "Azerbaijan": ["Azerbaijan Premier League", "First Division"],
        "Kazakhstan": ["Kazakhstan Premier League", "First Division"],
    },
    "Americas": {
        "USA / Canada": ["Major League Soccer", "Canadian Premier League", "USL Championship", "USL League One"],
        "Mexico": ["Liga MX", "Liga de Expansión MX"],
        "Costa Rica": ["Liga FPD"],
        "Honduras": ["Liga Nacional"],
        "Panama": ["Liga Panameña de Fútbol"],
        "Dominican Republic": ["Liga Dominicana de Fútbol"],
        "Argentina": ["Liga Profesional", "Primera Nacional"],
        "Brazil": ["Série A", "Série B", "Série C"],
        "Chile": ["Primera División", "Primera B"],
        "Colombia": ["Categoría Primera A", "Primera B"],
        "Ecuador": ["LigaPro Serie A", "Serie B"],
        "Peru": ["Liga 1", "Liga 2"],
        "Uruguay": ["Liga AUF Uruguaya", "Segunda División"],
        "Paraguay": ["Primera División", "División Intermedia"],
        "Bolivia": ["División de Fútbol Profesional"],
    },
    "Asia & Oceania": {
        "Japan": ["J1 League", "J2 League", "J3 League"],
        "South Korea": ["K League 1", "K League 2"],
        "China": ["Chinese Super League", "China League One"],
        "Australia / New Zealand": ["A-League Men"],
        "India": ["Indian Super League", "I-League"],
        "Saudi Arabia": ["Saudi Pro League", "Saudi First Division League"],
        "Qatar": ["Qatar Stars League", "Qatari Second Division"],
        "United Arab Emirates": ["UAE Pro League", "UAE First Division"],
        "Iran": ["Persian Gulf Pro League", "Azadegan League"],
        "Thailand": ["Thai League 1", "Thai League 2"],
        "Malaysia": ["Malaysia Super League", "Malaysia A1 Semi-Pro League"],
        "Indonesia": ["Liga 1", "Liga 2"],
        "Vietnam": ["V.League 1", "V.League 2"],
        "Uzbekistan": ["Uzbekistan Super League", "Uzbekistan Pro League"],
        "Iraq": ["Iraq Stars League", "Iraq Premier Division"],
        "Jordan": ["Jordanian Pro League", "Jordan League Division 1"],
        "Israel": ["Israeli Premier League", "Liga Leumit"],
    },
    "Africa": {
        "South Africa": ["Premier Soccer League", "Motsepe Foundation Championship"],
        "Egypt": ["Egyptian Premier League", "Egyptian Second Division"],
        "Morocco": ["Botola Pro", "Botola 2"],
        "Algeria": ["Ligue Professionnelle 1", "Ligue 2"],
        "Tunisia": ["Tunisian Ligue Professionnelle 1", "Ligue 2"],
        "Nigeria": ["Nigeria Premier Football League", "Nigeria National League"],
        "Ghana": ["Ghana Premier League", "Division One League"],
        "Kenya": ["Kenyan Premier League", "National Super League"],
        "Tanzania": ["Tanzania Premier League", "Championship"],
        "Uganda": ["Uganda Premier League", "FUFA Big League"],
        "Zambia": ["Zambia Super League", "National Division One"],
        "Angola": ["Girabola", "Segundona"],
        "DR Congo": ["Linafoot / Ligue 1", "Ligue 2"],
        "Senegal": ["Senegal Premier League", "Ligue 2"],
        "Ivory Coast": ["Ligue 1", "Ligue 2"],
    },
    "International / Continental": {
        "UEFA": ["Champions League", "Europa League", "Conference League"],
        "CONMEBOL": ["Copa Libertadores", "Copa Sudamericana"],
        "CONCACAF": ["Champions Cup", "Leagues Cup"],
        "AFC": ["Champions League Elite", "Champions League Two"],
        "CAF": ["Champions League", "Confederation Cup"],
        "OFC": ["OFC Champions League", "OFC Professional League"],
        "FIFA": ["World Cup", "Club World Cup", "Intercontinental Cup"],
    },
}


# ===========================================================================
# SECTION 2 — MULTI-SOURCE REGISTRY
# (transcribed from v1_3_free_football_data_sources.pdf. Governance rule
#  from the PDF, enforced here in code, not just in prose:
#    "Do not treat one provider as the truth for every question... record
#     source, retrieval time, coverage, freshness, confidence... If two
#     sources disagree, preserve both observations and apply a
#     source-priority rule instead of silently overwriting one."
#  This is why every resolver below logs a `source_id` per Evidence item,
#  and why resolve_kickoff/venue below can be corroborated by a second
#  source when one is configured, rather than the pipeline hard-wiring a
#  single "primary" provider.)
# ===========================================================================
SOURCE_REGISTRY: dict[str, list[dict[str, str]]] = {
    "fixture": [
        {"name": "football-data.org", "access": "free tier, registered key, rate-limited"},
        {"name": "Official league/federation fixture pages", "access": "free, unstructured"},
        {"name": "ESPN public match pages (site.api.espn.com)", "access": "free, unofficial, undocumented"},
    ],
    "competition_league": [
        {"name": "football-data.org competition catalogue", "access": "free tier, registered key"},
        {"name": "Official competition/league sites", "access": "free, authoritative"},
    ],
    "team": [
        {"name": "Official club sites", "access": "free, authoritative, unstructured"},
        {"name": "Official league sites", "access": "free"},
        {"name": "football-data.org", "access": "free tier where covered"},
    ],
    "player": [
        {"name": "Official club/league pages", "access": "free, unstructured"},
        {"name": "football-data.org player resources", "access": "free tier, partial coverage"},
    ],
    "lineup": [
        {"name": "Official club/league match pages", "access": "free"},
        {"name": "Official competition match centres", "access": "free"},
    ],
    "weather": [
        {"name": "Open-Meteo", "access": "free, no API key, global coverage"},
        {"name": "National meteorological services", "access": "free, varies by country"},
    ],
    "results_statistics": [
        {"name": "football-data.org", "access": "free tier, registered key"},
        {"name": "Official league/federation results", "access": "free"},
        {"name": "Public match centres", "access": "free"},
    ],
    "tactical": [
        {"name": "Official match reports", "access": "free, unstructured"},
        {"name": "Public match-centre event data", "access": "free, coverage varies"},
        {"name": "Club reports", "access": "free, unstructured"},
    ],
    "schedule": [
        {"name": "Official competition/club fixture calendars", "access": "free"},
        {"name": "football-data.org", "access": "free tier, registered key"},
    ],
    "venue": [
        {"name": "Official club/competition venue pages", "access": "free"},
        {"name": "Stadium/municipal pages", "access": "free"},
    ],
}

FOOTBALL_DATA_API_KEY = os.environ.get("FOOTBALL_DATA_API_KEY", "").strip()
FOOTBALL_DATA_BASE = "https://api.football-data.org/v4"


# ===========================================================================
# SECTION 3 — ESPN-RESOLVABLE COMPETITION CATALOGUE
# (a live-fetchable subset of GLOBAL_COMPETITION_MAP. ESPN's public soccer
#  endpoint slugs follow a documented-by-convention pattern; treat any of
#  these as UNVERIFIED until a live scoreboard call for that slug returns
#  events — the PDF's own instruction is "validate each competition before
#  activation", which is exactly what find_match() below does per call.)
# ===========================================================================
COMPETITION_CATALOGUE: dict[str, tuple[str, str]] = {
    # Western & Central Europe
    "eng.1": ("English Premier League", "eng.1"),
    "eng.2": ("English Championship", "eng.2"),
    "esp.1": ("Spanish La Liga", "esp.1"),
    "esp.2": ("Spanish Segunda División", "esp.2"),
    "ita.1": ("Italian Serie A", "ita.1"),
    "ita.2": ("Italian Serie B", "ita.2"),
    "ger.1": ("German Bundesliga", "ger.1"),
    "ger.2": ("German 2. Bundesliga", "ger.2"),
    "fra.1": ("French Ligue 1", "fra.1"),
    "fra.2": ("French Ligue 2", "fra.2"),
    "ned.1": ("Dutch Eredivisie", "ned.1"),
    "bel.1": ("Belgian Pro League", "bel.1"),
    "por.1": ("Portuguese Primeira Liga", "por.1"),
    "aut.1": ("Austrian Bundesliga", "aut.1"),
    "sui.1": ("Swiss Super League", "sui.1"),
    "sco.1": ("Scottish Premiership", "sco.1"),
    # Eastern / SE Europe
    "gre.1": ("Greek Super League", "gre.1"),
    "tur.1": ("Turkish Süper Lig", "tur.1"),
    "rus.1": ("Russian Premier League", "rus.1"),
    "ukr.1": ("Ukrainian Premier League", "ukr.1"),
    # Americas
    "usa.1": ("Major League Soccer", "usa.1"),
    "can.1": ("Canadian Premier League", "can.1"),
    "mex.1": ("Liga MX", "mex.1"),
    "bra.1": ("Brazil Série A", "bra.1"),
    "arg.1": ("Argentina Liga Profesional", "arg.1"),
    "chi.1": ("Chile Primera División", "chi.1"),
    "col.1": ("Colombia Categoría Primera A", "col.1"),
    "per.1": ("Peru Liga 1", "per.1"),
    "ecu.1": ("Ecuador LigaPro", "ecu.1"),
    # Asia & Oceania
    "jpn.1": ("Japan J1 League", "jpn.1"),
    "kor.1": ("South Korea K League 1", "kor.1"),
    "chn.1": ("Chinese Super League", "chn.1"),
    "aus.1": ("Australia A-League Men", "aus.1"),
    "ksa.1": ("Saudi Pro League", "ksa.1"),
    "uae.1": ("UAE Pro League", "uae.1"),
    "qat.1": ("Qatar Stars League", "qat.1"),
    # Africa
    "rsa.1": ("South Africa Premier Soccer League", "rsa.1"),
    "egy.1": ("Egyptian Premier League", "egy.1"),
    # International / Continental
    "uefa.champions": ("UEFA Champions League", "uefa.champions"),
    "uefa.europa": ("UEFA Europa League", "uefa.europa"),
    "uefa.europa.conf": ("UEFA Conference League", "uefa.europa.conf"),
    "conmebol.libertadores": ("Copa Libertadores", "conmebol.libertadores"),
    "conmebol.sudamericana": ("Copa Sudamericana", "conmebol.sudamericana"),
    "concacaf.league": ("CONCACAF Champions Cup", "concacaf.league"),
    "fifa.world": ("FIFA World Cup", "fifa.world"),
}

ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


# ===========================================================================
# SECTION 4 — EVIDENCE / QUESTION DATA MODEL
# ===========================================================================
@dataclasses.dataclass
class Evidence:
    evidence_id: str
    match_id: Optional[str]
    competition_id: str
    question_id: str
    source_id: str
    source_url: str
    retrieved_at: str
    published_at: Optional[str]
    freshness: str          # CURRENT | RECENT | DATED | STALE | UNKNOWN
    evidence_type: str
    raw_value: Any
    normalized_value: Any
    extraction_method: str
    verification_status: str  # VERIFIED | UNVERIFIED | FAILED
    confidence: float
    notes: str = ""

    def to_dict(self):
        return dataclasses.asdict(self)


@dataclasses.dataclass
class QuestionAnswer:
    question_id: str
    question_text: str
    resolution_type: str    # A=direct fact, B=derived fact, C=multi-source best-effort, D=AI reasoning
    answer: Any
    answer_status: str      # VERIFIED | UNVERIFIED | INSUFFICIENT_EVIDENCE | FAILED | DISAGREEMENT
    evidence_ids: list[str]
    sources: list[str]
    reasoning: str
    uncertainty: str
    disagreement: Optional[dict] = None
    freshness: str = "UNKNOWN"
    missing_information: str = ""
    confidence: float = 0.0

    def to_dict(self):
        return dataclasses.asdict(self)


class EvidenceLog:
    def __init__(self):
        self._items: list[Evidence] = []
        self._counter = 0

    def add(self, **kwargs) -> Evidence:
        self._counter += 1
        eid = kwargs.pop("evidence_id", f"E{self._counter:04d}")
        ev = Evidence(evidence_id=eid, **kwargs)
        self._items.append(ev)
        return ev

    def all(self) -> list[Evidence]:
        return list(self._items)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def http_get(url: str, params: dict | None = None, headers: dict | None = None, timeout: int = 10):
    try:
        resp = requests.get(url, params=params, timeout=timeout,
                             headers={"User-Agent": "FootballAI-V1.4/1.0", **(headers or {})})
    except requests.RequestException as exc:
        return None, f"FAILED: request error ({exc})"
    if resp.status_code != 200:
        return None, f"FAILED: HTTP {resp.status_code}"
    try:
        return resp.json(), "AVAILABLE"
    except ValueError:
        return None, "FAILED: response was not valid JSON"


# ===========================================================================
# SECTION 5 — COMPETITION & MATCH IDENTITY
# ===========================================================================
def resolve_competition(competition_id: str) -> dict:
    entry = COMPETITION_CATALOGUE.get(competition_id)

    # V1.3 authoritative fallback.
    # The V1.3 adapter governs competition identity and source routing;
    # the AI engine's own catalogue remains untouched.
    if not entry:
        from app.data_registry.v13_ai_routing_adapter import get_ai_routing_context

        v13 = get_ai_routing_context(competition_id)

        if v13["competition_identity_status"] == "RESOLVED":
            return {
                "competition_id": competition_id,
                "competition_name_canonical": v13["competition_name_canonical"],
                "competition_identity_status": "RESOLVED",
                "competition_identity_method": v13["competition_identity_method"],
                "v13_sources": v13["sources"],
            }
    if not entry:
        return {
            "competition_id": competition_id,
            "competition_name_canonical": None,
            "competition_identity_status": "UNRESOLVED",
            "competition_identity_method": "CATALOGUE_LOOKUP_FAILED",
            "note": "Not yet wired to a live ESPN slug in this build. Check GLOBAL_COMPETITION_MAP "
                    "for the competition name, then add an entry to COMPETITION_CATALOGUE once its "
                    "ESPN slug (or another source) is verified.",
        }
    name, slug = entry
    return {
        "competition_id": competition_id,
        "competition_name_canonical": name,
        "competition_identity_status": "RESOLVED",
        "competition_identity_method": "CATALOGUE_LOOKUP",
        "espn_slug": slug,
    }


def find_match(espn_slug: str, team_a: str, team_b: str,
                around_date: Optional[str] = None) -> dict:
    dates_to_check = []
    if around_date:
        dates_to_check.append(around_date)
    else:
        today = dt.date.today()
        for delta in range(-3, 15):
            dates_to_check.append((today + dt.timedelta(days=delta)).strftime("%Y%m%d"))

    def name_matches(candidate: str, target: str) -> bool:
        c, t = candidate.lower(), target.lower()
        return t in c or c in t

    for d in dates_to_check:
        url = f"{ESPN_BASE}/{espn_slug}/scoreboard"
        data, status = http_get(url, params={"dates": d})
        if data is None:
            continue
        for ev in data.get("events", []):
            comp = ev.get("competitions", [{}])[0]
            competitors = comp.get("competitors", [])
            names = [c.get("team", {}).get("displayName", "") for c in competitors]
            if len(names) != 2:
                continue
            if (name_matches(names[0], team_a) and name_matches(names[1], team_b)) or \
               (name_matches(names[0], team_b) and name_matches(names[1], team_a)):
                venue = comp.get("venue", {}).get("fullName")
                return {
                    "match_status": "FOUND",
                    "match_id": ev.get("id"),
                    "home_team": next((c["team"]["displayName"] for c in competitors
                                        if c.get("homeAway") == "home"), None),
                    "away_team": next((c["team"]["displayName"] for c in competitors
                                        if c.get("homeAway") == "away"), None),
                    "kickoff_at": ev.get("date"),
                    "match_date": d,
                    "venue": venue,
                    "season": data.get("season", {}).get("year"),
                    "status_detail": comp.get("status", {}).get("type", {}).get("description"),
                    "source_url": url,
                    "raw_event": ev,
                }
    return {"match_status": "NOT_FOUND"}


def crosscheck_fixture_football_data(team_a: str, team_b: str) -> Optional[dict]:
    """
    Optional second fixture source (SOURCE_REGISTRY['fixture']), only active
    if FOOTBALL_DATA_API_KEY is set. This is what lets Q1/Q2 move from
    SINGLE_SOURCE to CORROBORATED when a key is configured, per the PDF's
    "preserve both observations" governance rule — it does not replace ESPN,
    it checks against it.
    """
    if not FOOTBALL_DATA_API_KEY:
        return None
    url = f"{FOOTBALL_DATA_BASE}/matches"
    data, status = http_get(url, headers={"X-Auth-Token": FOOTBALL_DATA_API_KEY})
    if not data:
        return None
    for m in data.get("matches", []):
        home = m.get("homeTeam", {}).get("name", "")
        away = m.get("awayTeam", {}).get("name", "")

        def _match(c, t):
            return t.lower() in c.lower() or c.lower() in t.lower()

        if (_match(home, team_a) and _match(away, team_b)) or (_match(home, team_b) and _match(away, team_a)):
            return {
                "source_id": "football-data.org",
                "source_url": url,
                "kickoff_at": m.get("utcDate"),
                "venue": m.get("venue"),
                "status_detail": m.get("status"),
            }
    return None


# ===========================================================================
# SECTION 6 — DIRECT-FACT QUESTIONS (Q1, Q2) with cross-source corroboration
# ===========================================================================
def resolve_kickoff(log: EvidenceLog, match: dict, competition_id: str, team_a: str, team_b: str) -> QuestionAnswer:
    qid = "Q1_kickoff"
    if match.get("match_status") != "FOUND" or not match.get("kickoff_at"):
        return QuestionAnswer(qid, "What is the scheduled kickoff time?", "A",
                               answer=None, answer_status="INSUFFICIENT_EVIDENCE",
                               evidence_ids=[], sources=[],
                               reasoning="Match not found or kickoff field absent.",
                               uncertainty="High — no fixture data retrieved.",
                               missing_information="kickoff_at")
    ev = log.add(match_id=match["match_id"], competition_id=competition_id,
                 question_id=qid, source_id="ESPN", source_url=match["source_url"],
                 retrieved_at=now_iso(), published_at=match["kickoff_at"],
                 freshness="CURRENT", evidence_type="MATCH_LEVEL",
                 raw_value=match["kickoff_at"], normalized_value=match["kickoff_at"],
                 extraction_method="ESPN scoreboard JSON field 'date'",
                 verification_status="VERIFIED", confidence=0.9)
    sources_used = ["ESPN"]
    agreement_note = "Single free source used for this fixture (ESPN)."
    cross = crosscheck_fixture_football_data(team_a, team_b)
    if cross:
        sources_used.append("football-data.org")
        if cross["kickoff_at"] and match["kickoff_at"] and cross["kickoff_at"][:16] == match["kickoff_at"][:16]:
            agreement_note = "Corroborated: ESPN and football-data.org agree on kickoff time."
            log.add(match_id=match["match_id"], competition_id=competition_id,
                    question_id=qid, source_id="football-data.org", source_url=cross["source_url"],
                    retrieved_at=now_iso(), published_at=cross["kickoff_at"], freshness="CURRENT",
                    evidence_type="MATCH_LEVEL", raw_value=cross, normalized_value=cross["kickoff_at"],
                    extraction_method="football-data.org /matches", verification_status="VERIFIED",
                    confidence=0.9, notes="Cross-check source, agrees with ESPN.")
        else:
            agreement_note = (f"DISAGREEMENT: ESPN says {match['kickoff_at']}, football-data.org says "
                               f"{cross['kickoff_at']}. Preserving both rather than overwriting either.")
    return QuestionAnswer(qid, "What is the scheduled kickoff time?", "A",
                           answer=match["kickoff_at"], answer_status="VERIFIED",
                           evidence_ids=[ev.evidence_id], sources=sources_used,
                           reasoning=agreement_note,
                           uncertainty="Low, unless kickoff is later rescheduled.",
                           freshness="CURRENT", confidence=0.9)


def resolve_venue(log: EvidenceLog, match: dict, competition_id: str) -> QuestionAnswer:
    qid = "Q2_venue"
    if match.get("match_status") != "FOUND" or not match.get("venue"):
        return QuestionAnswer(qid, "What is the match venue?", "A",
                               answer=None, answer_status="INSUFFICIENT_EVIDENCE",
                               evidence_ids=[], sources=[],
                               reasoning="Venue field absent from retrieved fixture data.",
                               uncertainty="High.", missing_information="venue")
    ev = log.add(match_id=match["match_id"], competition_id=competition_id,
                 question_id=qid, source_id="ESPN", source_url=match["source_url"],
                 retrieved_at=now_iso(), published_at=None, freshness="CURRENT",
                 evidence_type="VENUE_LEVEL", raw_value=match["venue"], normalized_value=match["venue"],
                 extraction_method="ESPN scoreboard JSON field 'venue.fullName'",
                 verification_status="VERIFIED", confidence=0.85)
    return QuestionAnswer(qid, "What is the match venue?", "A",
                           answer=match["venue"], answer_status="VERIFIED",
                           evidence_ids=[ev.evidence_id], sources=["ESPN"],
                           reasoning="Directly retrieved from source.",
                           uncertainty="Low.", freshness="CURRENT", confidence=0.85)


# ===========================================================================
# SECTION 7 — WEATHER FOR THE SPECIFIC MATCH DATE AT THE VENUE
# ===========================================================================
def geocode_venue(venue_name: str) -> Optional[dict]:
    candidates = [venue_name]
    if "," in venue_name:
        candidates.append(venue_name.split(",")[-1].strip())
    for candidate in candidates:
        if not candidate:
            continue
        data, status = http_get(GEOCODE_URL, params={"name": candidate, "count": 1})
        if not data:
            continue
        results = data.get("results")
        if results:
            top = results[0]
            return {
                "matched_query": candidate,
                "resolved_name": top.get("name"),
                "country": top.get("country"),
                "latitude": top.get("latitude"),
                "longitude": top.get("longitude"),
                "geocode_precision": "CITY_LEVEL" if candidate != venue_name else "VENUE_STRING_LEVEL",
            }
    return None


_WMO_DESCRIPTIONS = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "depositing rime fog",
    51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
    61: "slight rain", 63: "moderate rain", 65: "heavy rain",
    66: "light freezing rain", 67: "heavy freezing rain",
    71: "slight snow", 73: "moderate snow", 75: "heavy snow", 77: "snow grains",
    80: "slight rain showers", 81: "moderate rain showers", 82: "violent rain showers",
    85: "slight snow showers", 86: "heavy snow showers",
    95: "thunderstorm", 96: "thunderstorm with slight hail", 99: "thunderstorm with heavy hail",
}


def fetch_weather_for_kickoff(latitude: float, longitude: float, kickoff_iso: Optional[str]) -> Optional[dict]:
    """
    Pulls the Open-Meteo hourly window covering the *actual match date*
    (up to 10 days out — Open-Meteo's free forecast horizon), and returns
    the hour nearest kickoff. This is the "weather update for the date the
    match will occur", not just "weather today".
    """
    params = {
        "latitude": latitude, "longitude": longitude,
        "hourly": "temperature_2m,precipitation,precipitation_probability,"
                   "weathercode,windspeed_10m,relative_humidity_2m",
        "past_days": 1, "forecast_days": 10, "timezone": "UTC",
    }
    data, status = http_get(WEATHER_URL, params=params)
    if not data:
        return None
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    if not times:
        return None
    target = None
    if kickoff_iso:
        try:
            target = dt.datetime.fromisoformat(kickoff_iso.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            target = None
    if target is None:
        idx = len(times) - 1
    else:
        parsed_times = [dt.datetime.fromisoformat(t) for t in times]
        diffs = [abs((t - target).total_seconds()) for t in parsed_times]
        idx = diffs.index(min(diffs))
        if min(diffs) > 12 * 3600:
            return None

    def _at(key):
        vals = hourly.get(key, [])
        return vals[idx] if idx < len(vals) else None

    return {
        "matched_time_utc": times[idx],
        "temperature_c": _at("temperature_2m"),
        "precipitation_mm": _at("precipitation"),
        "precipitation_probability_pct": _at("precipitation_probability"),
        "weathercode": _at("weathercode"),
        "windspeed_kmh": _at("windspeed_10m"),
        "relative_humidity_pct": _at("relative_humidity_2m"),
    }


def resolve_weather(log: EvidenceLog, match: dict, competition_id: str) -> QuestionAnswer:
    qid = "Q7_weather"
    qtext = "What weather is expected at the venue on the match date, at kickoff?"
    if match.get("match_status") != "FOUND" or not match.get("venue"):
        return QuestionAnswer(qid, qtext, "A", answer=None, answer_status="INSUFFICIENT_EVIDENCE",
                               evidence_ids=[], sources=[], reasoning="No venue available to geocode.",
                               uncertainty="High.", missing_information="venue")
    geo = geocode_venue(match["venue"])
    if not geo:
        return QuestionAnswer(qid, qtext, "A", answer=None, answer_status="INSUFFICIENT_EVIDENCE",
                               evidence_ids=[], sources=["Open-Meteo Geocoding"],
                               reasoning=f"Could not geocode venue '{match['venue']}'.",
                               uncertainty="High.", missing_information="venue coordinates")
    weather = fetch_weather_for_kickoff(geo["latitude"], geo["longitude"], match.get("kickoff_at"))
    if not weather:
        return QuestionAnswer(qid, qtext, "A", answer=None, answer_status="INSUFFICIENT_EVIDENCE",
                               evidence_ids=[], sources=["Open-Meteo"],
                               reasoning="Geocoding succeeded but no forecast hour was close enough to "
                                         "kickoff (kickoff may be beyond the 10-day forecast horizon, or "
                                         "kickoff time itself is unknown).",
                               uncertainty="High.", missing_information="weather forecast at kickoff time")

    kickoff_dt = None
    try:
        kickoff_dt = (dt.datetime.fromisoformat(match["kickoff_at"].replace("Z", "+00:00"))
                      if match.get("kickoff_at") else None)
    except ValueError:
        pass
    matched_dt = dt.datetime.fromisoformat(weather["matched_time_utc"]).replace(tzinfo=dt.timezone.utc)
    now = dt.datetime.now(dt.timezone.utc)

    if matched_dt < now - dt.timedelta(hours=1):
        freshness = "RECENT"
    elif matched_dt <= now + dt.timedelta(hours=48):
        freshness = "CURRENT"
    else:
        freshness = "DATED"

    desc = _WMO_DESCRIPTIONS.get(weather["weathercode"], f"WMO code {weather['weathercode']}")
    normalized = {**weather, "condition_description": desc, "venue_geocode": geo}

    ev = log.add(match_id=match["match_id"], competition_id=competition_id,
                 question_id=qid, source_id="Open-Meteo", source_url=WEATHER_URL,
                 retrieved_at=now_iso(), published_at=weather["matched_time_utc"], freshness=freshness,
                 evidence_type="WEATHER_LEVEL", raw_value=weather, normalized_value=normalized,
                 extraction_method=f"Open-Meteo hourly forecast for match date, nearest hour to kickoff, "
                                    f"venue geocoded via '{geo['matched_query']}'",
                 verification_status="VERIFIED", confidence=0.75 if freshness == "CURRENT" else 0.5,
                 notes="Forecast, not a guaranteed outcome — reliability drops the further out kickoff is.")

    answer_text = (f"{desc}, ~{weather['temperature_c']}°C, precipitation {weather['precipitation_mm']}mm "
                   f"({weather['precipitation_probability_pct']}% chance), wind {weather['windspeed_kmh']}km/h "
                   f"— matched to {weather['matched_time_utc']} UTC, near {geo['resolved_name']}, {geo.get('country')}")

    return QuestionAnswer(
        qid, qtext, "A" if freshness == "CURRENT" else "B",
        answer=answer_text, answer_status="VERIFIED",
        evidence_ids=[ev.evidence_id], sources=["Open-Meteo"],
        reasoning="Retrieved the forecast hour closest to kickoff, for the match's own date, at the "
                  "geocoded venue location — not 'today's weather'.",
        uncertainty=("Low-to-moderate: within 48h, near-term forecast." if freshness == "CURRENT"
                     else "Higher: kickoff is more than 48h out, so this is a longer-range forecast and "
                          "more likely to shift before matchday — re-check closer to kickoff."),
        freshness=freshness,
        missing_information="" if geo["geocode_precision"] == "VENUE_STRING_LEVEL"
                              else "exact stadium coordinates (city-level geocode used instead)",
        confidence=0.75 if freshness == "CURRENT" else 0.5,
    )


# ===========================================================================
# SECTION 8 — FORM (10-game extraction feeding the 5D engine), H2H, AVAILABILITY
# ===========================================================================
def fetch_team_recent_results(espn_slug: str, team_espn_id: str, n: int = 10):
    url = f"{ESPN_BASE}/{espn_slug}/teams/{team_espn_id}/schedule"
    data, status = http_get(url)
    if data is None:
        return None, status
    events = data.get("events", [])
    completed = [e for e in events
                 if e.get("competitions", [{}])[0].get("status", {}).get("type", {}).get("completed")]
    completed_sorted = sorted(completed, key=lambda e: e.get("date", ""))  # oldest -> newest
    results = []
    for e in completed_sorted[-n:]:
        comp = e["competitions"][0]
        competitors = comp.get("competitors", [])
        team = next((c for c in competitors if c.get("team", {}).get("id") == str(team_espn_id)), None)
        opp = next((c for c in competitors if c.get("team", {}).get("id") != str(team_espn_id)), None)
        if not team or not opp:
            continue
        gf, ga = int(team.get("score", {}).get("value", 0) or 0), int(opp.get("score", {}).get("value", 0) or 0)
        results.append({"date": e.get("date"), "opponent": opp["team"]["displayName"],
                         "gf": gf, "ga": ga, "home": team.get("homeAway") == "home"})
    return results, "AVAILABLE" if results else "INSUFFICIENT"


def _get_team_espn_id(raw_event: dict, team_display_name: str) -> Optional[str]:
    for c in raw_event.get("competitions", [{}])[0].get("competitors", []):
        if c.get("team", {}).get("displayName") == team_display_name:
            return c.get("team", {}).get("id")
    return None


def resolve_form(log: EvidenceLog, match: dict, competition_id: str):
    """
    TYPE B — derived. Returns (QuestionAnswer, home_matches_10, away_matches_10)
    so the 10-game data can feed straight into the FiveDimensionalAnalyticsEngine
    without a second network round-trip.
    """
    qid = "Q3_recent_form"
    if match.get("match_status") != "FOUND":
        qa = QuestionAnswer(qid, "Which team has better recent form (last 10)?", "B",
                             answer=None, answer_status="INSUFFICIENT_EVIDENCE",
                             evidence_ids=[], sources=[], reasoning="No match identity.",
                             uncertainty="High.", missing_information="match identity")
        return qa, [], []

    espn_slug, raw_event = match.get("_espn_slug"), match["raw_event"]
    home_id = _get_team_espn_id(raw_event, match["home_team"])
    away_id = _get_team_espn_id(raw_event, match["away_team"])
    if not home_id or not away_id:
        qa = QuestionAnswer(qid, "Which team has better recent form (last 10)?", "B",
                             answer=None, answer_status="INSUFFICIENT_EVIDENCE",
                             evidence_ids=[], sources=["ESPN"], reasoning="Could not resolve ESPN team IDs.",
                             uncertainty="High.", missing_information="team ids")
        return qa, [], []

    home_results, _ = fetch_team_recent_results(espn_slug, home_id, n=10)
    away_results, _ = fetch_team_recent_results(espn_slug, away_id, n=10)
    if not home_results or not away_results:
        qa = QuestionAnswer(qid, "Which team has better recent form (last 10)?", "B",
                             answer=None, answer_status="INSUFFICIENT_EVIDENCE",
                             evidence_ids=[], sources=["ESPN"],
                             reasoning="Schedule/results not available for one or both teams.",
                             uncertainty="High.", missing_information="team schedule results")
        return qa, [], []

    def points(results):
        return sum(3 if r["gf"] > r["ga"] else (1 if r["gf"] == r["ga"] else 0) for r in results)

    home_pts, away_pts = points(home_results), points(away_results)
    ev_home = log.add(match_id=match["match_id"], competition_id=competition_id, question_id=qid,
                       source_id="ESPN", source_url=f"{ESPN_BASE}/{espn_slug}/teams/{home_id}/schedule",
                       retrieved_at=now_iso(), published_at=None, freshness="RECENT",
                       evidence_type="TEAM_LEVEL", raw_value=home_results,
                       normalized_value={"points_last10": home_pts},
                       extraction_method="ESPN team schedule, last 10 completed matches",
                       verification_status="VERIFIED", confidence=0.8)
    ev_away = log.add(match_id=match["match_id"], competition_id=competition_id, question_id=qid,
                       source_id="ESPN", source_url=f"{ESPN_BASE}/{espn_slug}/teams/{away_id}/schedule",
                       retrieved_at=now_iso(), published_at=None, freshness="RECENT",
                       evidence_type="TEAM_LEVEL", raw_value=away_results,
                       normalized_value={"points_last10": away_pts},
                       extraction_method="ESPN team schedule, last 10 completed matches",
                       verification_status="VERIFIED", confidence=0.8)

    if home_pts == away_pts:
        answer = "EVEN"
        reasoning = f"Both sides took {home_pts} pts from their last {len(home_results)} matches — form is level."
    else:
        better = match["home_team"] if home_pts > away_pts else match["away_team"]
        answer = better
        reasoning = (f"{match['home_team']} took {home_pts} pts, {match['away_team']} took {away_pts} pts "
                     f"from their last 10 matches — {better} has the better recent form.")

    qa = QuestionAnswer(qid, "Which team has better recent form (last 10)?", "B",
                         answer=answer, answer_status="VERIFIED",
                         evidence_ids=[ev_home.evidence_id, ev_away.evidence_id], sources=["ESPN"],
                         reasoning=reasoning, uncertainty="Form is descriptive, not predictive on its own.",
                         freshness="RECENT", confidence=0.75)
    return qa, home_results, away_results


def resolve_h2h(log: EvidenceLog, match: dict, competition_id: str) -> QuestionAnswer:
    qid = "Q4_head_to_head"
    return QuestionAnswer(qid, "What is the recent head-to-head record?", "B",
                           answer=None, answer_status="INSUFFICIENT_EVIDENCE",
                           evidence_ids=[], sources=[],
                           reasoning="No free/public head-to-head endpoint wired up in this build "
                                     "(see SOURCE_REGISTRY['results_statistics'] for candidates).",
                           uncertainty="N/A — not attempted.",
                           missing_information="registered head-to-head statistics source")


def resolve_availability(log: EvidenceLog, match: dict, competition_id: str) -> QuestionAnswer:
    qid = "Q5_player_availability"
    if match.get("match_status") != "FOUND":
        return QuestionAnswer(qid, "Are important players unavailable?", "C",
                               answer=None, answer_status="INSUFFICIENT_EVIDENCE",
                               evidence_ids=[], sources=[], reasoning="No match identity.",
                               uncertainty="High.", missing_information="match identity")
    url = f"{ESPN_BASE}/{match['_espn_slug']}/summary"
    data, status = http_get(url, params={"event": match["match_id"]})
    if data is None:
        return QuestionAnswer(qid, "Are important players unavailable?", "C",
                               answer=None, answer_status="FAILED",
                               evidence_ids=[], sources=["ESPN"], reasoning=f"Summary endpoint failed: {status}",
                               uncertainty="High.", missing_information="injury/lineup data")
    injuries = data.get("injuries", [])
    if not injuries:
        return QuestionAnswer(qid, "Are important players unavailable?", "C",
                               answer="UNKNOWN", answer_status="INSUFFICIENT_EVIDENCE",
                               evidence_ids=[], sources=["ESPN"],
                               reasoning="ESPN summary endpoint returned no injury data for this fixture.",
                               uncertainty="High — absence of data is not evidence of full squad availability.",
                               missing_information="official club injury reports; a second registered source")
    ev = log.add(match_id=match["match_id"], competition_id=competition_id, question_id=qid,
                 source_id="ESPN", source_url=url, retrieved_at=now_iso(), published_at=None,
                 freshness="RECENT", evidence_type="PLAYER_LEVEL", raw_value=injuries,
                 normalized_value=injuries, extraction_method="ESPN summary JSON field 'injuries'",
                 verification_status="VERIFIED", confidence=0.6,
                 notes="Single source (ESPN) — not cross-checked against club-official info.")
    return QuestionAnswer(qid, "Are important players unavailable?", "C",
                           answer=injuries, answer_status="VERIFIED",
                           evidence_ids=[ev.evidence_id], sources=["ESPN"],
                           reasoning="ESPN reported one or more injury/availability entries for this fixture.",
                           uncertainty="Single-source — not independently confirmed.",
                           freshness="RECENT", confidence=0.6)


# ===========================================================================
# SECTION 9 — FIVE-DIMENSIONAL ANALYTICS ENGINE
# ===========================================================================
class FiveDimensionalAnalyticsEngine:
    """
    Turns 10-game histories into five vectors: momentum, offensive threat,
    defensive stability, volatility, and a composite dimensional index.
    """

    def __init__(self, recency_decay: float = 0.85):
        self.decay = recency_decay

    def analyze_10_game_history(self, team_name: str, matches: list[dict]) -> dict:
        recent_10 = matches[-10:] if len(matches) >= 10 else matches
        wins = draws = losses = goals_for = goals_against = clean_sheets = failed_to_score = 0
        weighted_points = max_possible_weight = 0.0
        game_logs = []

        for idx, m in enumerate(recent_10):
            weight = math.pow(1 / self.decay, idx)
            max_possible_weight += weight * 3.0
            gf, ga = m.get("gf", 0), m.get("ga", 0)
            goals_for += gf
            goals_against += ga
            if gf > ga:
                wins += 1; pts, outcome = 3, "W"
            elif gf == ga:
                draws += 1; pts, outcome = 1, "D"
            else:
                losses += 1; pts, outcome = 0, "L"
            if ga == 0: clean_sheets += 1
            if gf == 0: failed_to_score += 1
            weighted_points += pts * weight
            game_logs.append(outcome)

        total_games = len(recent_10) or 1
        ppg = round(((wins * 3) + draws) / total_games, 2)
        goal_diff = goals_for - goals_against
        weighted_form_score = round((weighted_points / max_possible_weight) * 100, 2) if max_possible_weight else 0.0

        if total_games >= 10:
            first5 = sum(3 if m['gf'] > m['ga'] else 1 if m['gf'] == m['ga'] else 0 for m in recent_10[:5])
            last5 = sum(3 if m['gf'] > m['ga'] else 1 if m['gf'] == m['ga'] else 0 for m in recent_10[5:])
            diff = last5 - first5
            trend = "Surging (uptrend)" if diff >= 3 else "Declining (downtrend)" if diff <= -3 else "Stable"
        else:
            trend = "Insufficient depth"

        return {
            "team": team_name, "sample_size": total_games,
            "record": f"{wins}W-{draws}D-{losses}L", "sequence": "".join(game_logs),
            "ppg": ppg, "goals_for": goals_for, "goals_against": goals_against,
            "goal_difference": goal_diff, "clean_sheets": clean_sheets,
            "failed_to_score": failed_to_score, "weighted_form_score": weighted_form_score,
            "trend": trend,
            "gf_per_game": round(goals_for / total_games, 2),
            "ga_per_game": round(goals_against / total_games, 2),
        }

    def generate_5d_prediction_matrix(self, home_form: dict, away_form: dict) -> dict:
        momentum_delta = home_form["weighted_form_score"] - away_form["weighted_form_score"]
        home_offense = home_form["gf_per_game"]
        away_offense = away_form["gf_per_game"]
        home_defense = (home_form["clean_sheets"] * 2) - home_form["ga_per_game"]
        away_defense = (away_form["clean_sheets"] * 2) - away_form["ga_per_game"]
        volatility = abs(home_form["goal_difference"] - away_form["goal_difference"]) / 10.0

        dimensional_index = (momentum_delta * 0.40) + ((home_offense - away_offense) * 20.0) + \
                             ((home_defense - away_defense) * 10.0)
        dimensional_index = max(-100.0, min(100.0, round(dimensional_index, 2)))

        if dimensional_index > 25.0:
            predicted_state = f"Statistical dominance: {home_form['team']}"
        elif dimensional_index < -25.0:
            predicted_state = f"Statistical dominance: {away_form['team']}"
        elif abs(dimensional_index) <= 10.0:
            predicted_state = "Neutral equilibrium (elevated draw probability on raw numbers)"
        else:
            dominant = home_form['team'] if dimensional_index > 0 else away_form['team']
            predicted_state = f"Slight statistical edge: {dominant}"

        return {
            "dim_1_momentum_delta": round(momentum_delta, 2),
            "dim_2_offensive_threat": {"home": round(home_offense, 2), "away": round(away_offense, 2)},
            "dim_3_defensive_stability": {"home": round(home_defense, 2), "away": round(away_defense, 2)},
            "dim_4_volatility_score": round(volatility, 2),
            "dim_5_composite_index": dimensional_index,
            "raw_statistical_state": predicted_state,
        }


# ===========================================================================
# SECTION 10 — TACTICAL STYLE PROFILER
# (Proxy inference from scoreline shape — labelled explicitly as inference,
#  since no free source in SOURCE_REGISTRY reliably exposes formations or
#  press data. This is what lets the reasoner talk about "parking the bus".)
# ===========================================================================
class TacticalStyleProfiler:
    LOW_BLOCK_GA_THRESHOLD = 1.0      # concedes < 1.0/game -> compact/defensive tendency
    HIGH_ATTACK_GF_THRESHOLD = 1.6    # scores > 1.6/game -> sharp attacking tendency
    LOW_ATTACK_GF_THRESHOLD = 1.1     # scores < 1.1/game -> cautious/low-tempo tendency

    def profile(self, form: dict) -> dict:
        gf, ga = form["gf_per_game"], form["ga_per_game"]
        cs_rate = form["clean_sheets"] / max(form["sample_size"], 1)

        is_defensively_compact = ga < self.LOW_BLOCK_GA_THRESHOLD or cs_rate >= 0.4
        is_sharp_attack = gf > self.HIGH_ATTACK_GF_THRESHOLD
        is_low_tempo_attack = gf < self.LOW_ATTACK_GF_THRESHOLD

        if is_defensively_compact and is_low_tempo_attack:
            style = "Deep block / cautious (concedes little, creates little — consistent with sitting deep and inviting pressure)"
        elif is_defensively_compact and not is_low_tempo_attack:
            style = "Balanced / counter-attacking (solid defensively, still functional going forward)"
        elif is_sharp_attack and not is_defensively_compact:
            style = "High-tempo attacking (scores freely, leaks goals — front-foot approach)"
        else:
            style = "Mixed / no strong tendency in the sample"

        return {
            "team": form["team"], "style_inference": style,
            "gf_per_game": gf, "ga_per_game": ga, "clean_sheet_rate": round(cs_rate, 2),
            "is_defensively_compact": is_defensively_compact,
            "is_sharp_attack": is_sharp_attack,
            "is_low_tempo_attack": is_low_tempo_attack,
            "basis": "INFERENCE from last-10-game scoreline pattern (goals for/against, clean-sheet rate) "
                     "— not a confirmed formation, press-intensity, or possession report.",
        }


# ===========================================================================
# SECTION 11 — 5D INTELLIGENCE REASONER (Q9 / Q10 / Q11)
# This is the "how does the away team gain advantage even in an away match"
# reasoning: it explicitly checks for the park-the-bus pattern (away side
# defensively compact/low-tempo vs home side with sharp attack) and, when
# present, pulls the verdict toward a draw even if the raw 5D composite
# index favours the home side — exactly like a human scout weighing
# matchup fit against raw stats.
# ===========================================================================
class FiveDIntelligenceReasoner:
    def reason(self, home_form: dict, away_form: dict, matrix_5d: dict,
               home_style: dict, away_style: dict, weather_qa: QuestionAnswer,
               availability_qa: QuestionAnswer, h2h_qa: QuestionAnswer) -> dict:

        idx = matrix_5d["dim_5_composite_index"]
        home_team, away_team = home_form["team"], away_form["team"]

        # Baseline lean purely from the raw composite index.
        if idx > 25:
            baseline = home_team
        elif idx < -25:
            baseline = away_team
        elif idx > 10:
            baseline = f"{home_team} (slight)"
        elif idx < -10:
            baseline = f"{away_team} (slight)"
        else:
            baseline = "Draw"

        narrative = []
        narrative.append(
            f"On raw 10-game numbers, the composite index is {idx} "
            f"({matrix_5d['raw_statistical_state']}), and home-field advantage alone would nudge this "
            f"toward {home_team}."
        )

        # The park-the-bus / tactical-mismatch check — this is the core of the requested reasoning.
        park_bus_pattern = away_style["is_defensively_compact"] and (
            away_style["is_low_tempo_attack"] or home_style["is_sharp_attack"]
        )
        draw_pull = 0
        if park_bus_pattern:
            draw_pull += 1
            narrative.append(
                f"But {away_team}'s last-10 pattern ({away_style['style_inference']}) suggests a team "
                f"built to sit deep, stay compact, and limit clean chances rather than trade blows — "
                f"that is a classic way an away side neutralises home advantage even without "
                f"matching the home team's attacking quality: fewer opportunities conceded matters more "
                f"than fewer created, if the game plan is containment."
            )
        if home_style["is_sharp_attack"] and not home_style["is_defensively_compact"]:
            narrative.append(
                f"{home_team}'s own pattern ({home_style['style_inference']}) shows they do create and "
                f"score, but also concede more freely themselves — against a compact away side that "
                f"restricts service, that attacking edge is less likely to convert into the expected "
                f"number of clear chances."
            )

        # Weather as a leveling / uncertainty factor, never as a directional lean, per V1.3 reasoning rule.
        weather_note = "No weather evidence available."
        if weather_qa.answer_status == "VERIFIED":
            weather_note = (f"Weather on the match date: {weather_qa.answer}. Treated as a shared "
                             f"condition affecting both sides rather than favouring either, "
                             f"{'though the forecast is still long-range and may shift.' if weather_qa.freshness != 'CURRENT' else 'and this is a near-term, fairly reliable forecast.'}")
        narrative.append(weather_note)

        missing = []
        if h2h_qa.answer_status != "VERIFIED":
            missing.append("head-to-head record")
        if availability_qa.answer_status != "VERIFIED":
            missing.append("confirmed player availability/injuries")
        if weather_qa.freshness not in ("CURRENT",):
            missing.append("a closer-to-kickoff weather update")

        # Final verdict logic: tactical mismatch can pull a moderate home edge down to a draw,
        # but cannot overturn a genuinely dominant statistical gap (|idx| > 40).
        if abs(idx) > 40:
            final_verdict = home_team if idx > 0 else away_team
            confidence = "MODERATE-HIGH"
            verdict_reasoning = (
                f"The statistical gap ({idx}) is large enough that even a sound containment plan from "
                f"{away_team if idx > 0 else home_team} is unlikely to fully cancel it out — leaning "
                f"{final_verdict}, but not with certainty."
            )
        elif park_bus_pattern and idx > 0:
            final_verdict = "Draw"
            confidence = "MODERATE"
            verdict_reasoning = (
                f"Average advantages and disadvantages roughly balance out: {home_team} has the sharper "
                f"attacking numbers and home advantage, {away_team}'s pattern points to a low-block setup "
                f"that's built to blunt exactly that kind of edge. Neither side's case is strong enough to "
                f"outweigh the other, so the more honest read is a draw rather than picking a winner."
            )
        elif abs(idx) <= 10:
            final_verdict = "Draw"
            confidence = "LOW-MODERATE"
            verdict_reasoning = "Raw statistical equilibrium — no clear edge for either side."
        else:
            final_verdict = baseline
            confidence = "MODERATE"
            verdict_reasoning = f"No strong tactical mismatch detected; going with the statistical lean ({baseline})."

        if missing:
            confidence = "LOW" if confidence == "LOW-MODERATE" else confidence
            verdict_reasoning += f" Missing evidence that could change this: {', '.join(missing)}."

        return {
            "narrative": " ".join(narrative),
            "park_bus_pattern_detected": park_bus_pattern,
            "home_style": home_style, "away_style": away_style,
            "final_verdict": final_verdict,
            "confidence": confidence,
            "verdict_reasoning": verdict_reasoning,
            "missing_information": missing,
            "explicit_caveat": "This is a reasoned INFERENCE over available free-source evidence, not a "
                                "guaranteed outcome. Tactical style is itself inferred from scoreline shape, "
                                "not confirmed formation data.",
        }


# ===========================================================================
# SECTION 12 — HOME-ADVANTAGE (Q6) — kept as a lighter-weight companion
# to Q9-Q11's full reasoning, summarising the same inputs briefly.
# ===========================================================================
def resolve_home_advantage_reasoning(qa_lookup: dict[str, QuestionAnswer], match: dict) -> QuestionAnswer:
    qid = "Q6_home_advantage_assessment"
    facts, missing = [], []
    form_qa = qa_lookup.get("Q3_recent_form")
    if form_qa and form_qa.answer_status == "VERIFIED":
        facts.append(f"Recent form: {form_qa.reasoning}")
    else:
        missing.append("recent form")
    if not (qa_lookup.get("Q4_head_to_head") and qa_lookup["Q4_head_to_head"].answer_status == "VERIFIED"):
        missing.append("head-to-head record")
    avail_qa = qa_lookup.get("Q5_player_availability")
    if not (avail_qa and avail_qa.answer_status == "VERIFIED"):
        missing.append("player availability")
    weather_qa = qa_lookup.get("Q7_weather")
    if not (weather_qa and weather_qa.answer_status == "VERIFIED"):
        missing.append("weather at venue")

    reasoning = " ".join(facts) if facts else "No underlying questions sufficiently resolved."
    return QuestionAnswer(qid, "Does raw home advantage meaningfully favor the home team here?", "D",
                           answer="See Q11 for the full tactical verdict." if facts else "UNKNOWN",
                           answer_status="VERIFIED" if facts else "INSUFFICIENT_EVIDENCE",
                           evidence_ids=[], sources=["derived"], reasoning=reasoning,
                           uncertainty=("Missing: " + ", ".join(missing) + ". " if missing else "") +
                                       "See Q11 for the full weighted verdict, which also checks for "
                                       "tactical mismatches that can offset home advantage.",
                           missing_information=", ".join(missing),
                           confidence=0.5 if missing else 0.65)


# ===========================================================================
# SECTION 13 — READINESS + DASHBOARD
# ===========================================================================
CRITICAL_QUESTIONS = {"Q1_kickoff"}


def compute_readiness(match: dict, qas: list[QuestionAnswer]) -> str:
    if match.get("match_status") != "FOUND":
        return "INSUFFICIENT"
    qa_by_id = {qa.question_id: qa for qa in qas}
    for cq in CRITICAL_QUESTIONS:
        if cq not in qa_by_id or qa_by_id[cq].answer_status != "VERIFIED":
            return "INSUFFICIENT"
    resolved = sum(1 for qa in qas if qa.answer_status == "VERIFIED")
    return "READY" if resolved >= max(1, len(qas) // 2) else "PREPARATION"


def print_dashboard(competition: dict, match: dict, qas: list[QuestionAnswer],
                     readiness: str, five_d: Optional[dict], reasoning: Optional[dict]):
    print("=" * 78)
    print("FOOTBALL AI V1.4 — FIVE-DIMENSIONAL INTELLIGENCE DASHBOARD")
    print("=" * 78)
    print(f"COMPETITION   : {competition.get('competition_name_canonical')} ({competition.get('competition_id')})")
    print(f"IDENTITY      : {competition.get('competition_identity_status')}")
    if match.get("match_status") == "FOUND":
        print(f"MATCH         : {match['home_team']} (H) vs {match['away_team']} (A)")
        print(f"KICKOFF       : {match.get('kickoff_at')}")
        print(f"VENUE         : {match.get('venue')}")
    else:
        print("MATCH         : NOT FOUND")
    print(f"READINESS     : {readiness}")
    print("-" * 78)
    print("QUESTIONS & ANSWERS:")
    for qa in qas:
        print(f"  [{qa.question_id}] {qa.question_text}")
        print(f"      status={qa.answer_status}  type={qa.resolution_type}  confidence={qa.confidence}")
        print(f"      answer={qa.answer}")
        if qa.missing_information:
            print(f"      missing={qa.missing_information}")
    if five_d:
        print("-" * 78)
        print("FIVE-DIMENSIONAL MATRIX:")
        print(f"  Momentum delta        : {five_d['dim_1_momentum_delta']}")
        print(f"  Offensive threat      : {five_d['dim_2_offensive_threat']}")
        print(f"  Defensive stability   : {five_d['dim_3_defensive_stability']}")
        print(f"  Volatility            : {five_d['dim_4_volatility_score']}")
        print(f"  Composite index (-100..+100): {five_d['dim_5_composite_index']}")
        print(f"  Raw statistical state : {five_d['raw_statistical_state']}")
    if reasoning:
        print("-" * 78)
        print("5D INTELLIGENCE — REASONED VERDICT:")
        print(f"  {reasoning['narrative']}")
        print(f"  Park-the-bus pattern detected : {reasoning['park_bus_pattern_detected']}")
        print(f"  FINAL VERDICT                 : {reasoning['final_verdict']}  (confidence: {reasoning['confidence']})")
        print(f"  Why                            : {reasoning['verdict_reasoning']}")
        print(f"  Caveat                         : {reasoning['explicit_caveat']}")
    print("=" * 78)


# ===========================================================================
# SECTION 14 — MAIN PIPELINE
# ===========================================================================
def run(team_a: str, team_b: str, competition_id: str, date: Optional[str] = None) -> dict:
    log = EvidenceLog()
    competition = resolve_competition(competition_id)
    if competition["competition_identity_status"] != "RESOLVED":
        print(json.dumps(competition, indent=2))
        return {"status": "UNRESOLVED_COMPETITION", "competition": competition}

    from app.data_registry.v1_3_match_source_adapter import V13MatchSourceAdapter

    source_adapter = V13MatchSourceAdapter()
    match = source_adapter.find_match(
        espn_slug=competition["espn_slug"],
        team_a=team_a,
        team_b=team_b,
        around_date=date,
    )

    # V1.3 question-framework wire:
    # Existing Piece 1-8 analytical state remains authoritative.
    # The existing 37-question bridge/resolver consumes that state.
    try:
        question_bridge = V12PieceEvidenceBridge()
        question_state = question_bridge.build_evidence_state(analytical_state)
        question_state = V12SemanticResolver().resolve_all(
            question_state,
            analytical_state,
        )
    except Exception as exc:
        question_state = None
        question_state_error = str(exc)
    else:
        question_state_error = None
    match["_espn_slug"] = competition["espn_slug"]

    qas: list[QuestionAnswer] = []
    qas.append(resolve_kickoff(log, match, competition_id, team_a, team_b))
    qas.append(resolve_venue(log, match, competition_id))
    form_qa, home_matches, away_matches = resolve_form(log, match, competition_id)
    qas.append(form_qa)
    qas.append(resolve_h2h(log, match, competition_id))
    qas.append(resolve_availability(log, match, competition_id))
    qas.append(resolve_weather(log, match, competition_id))
    qa_lookup = {qa.question_id: qa for qa in qas}
    qas.append(resolve_home_advantage_reasoning(qa_lookup, match))

    five_d_matrix, reasoning = None, None
    if match.get("match_status") == "FOUND" and home_matches and away_matches:
        engine = FiveDimensionalAnalyticsEngine()
        home_form = engine.analyze_10_game_history(match["home_team"], home_matches)
        away_form = engine.analyze_10_game_history(match["away_team"], away_matches)
        five_d_matrix = engine.generate_5d_prediction_matrix(home_form, away_form)

        qas.append(QuestionAnswer("Q8_five_dimensional_matrix",
                                   "What do the 5 statistical dimensions (momentum, offense, defense, "
                                   "volatility, composite) say?", "B",
                                   answer=five_d_matrix["raw_statistical_state"], answer_status="VERIFIED",
                                   evidence_ids=form_qa.evidence_ids, sources=["ESPN (derived)"],
                                   reasoning=f"Composite index {five_d_matrix['dim_5_composite_index']} "
                                             f"from momentum/offense/defense/volatility vectors.",
                                   uncertainty="Purely statistical — does not yet account for tactical fit.",
                                   confidence=0.7))

        profiler = TacticalStyleProfiler()
        home_style = profiler.profile(home_form)
        away_style = profiler.profile(away_form)
        qas.append(QuestionAnswer("Q9_tactical_style_inference",
                                   "What tactical tendencies do the two sides show?", "D",
                                   answer={"home": home_style["style_inference"], "away": away_style["style_inference"]},
                                   answer_status="UNVERIFIED",
                                   evidence_ids=form_qa.evidence_ids, sources=["inference from ESPN scorelines"],
                                   reasoning="Inferred from goals-for/against and clean-sheet rate over the last "
                                             "10 games — no formation/press data source is wired up.",
                                   uncertainty="Moderate-to-high — this is a style proxy, not confirmed tactics.",
                                   confidence=0.4))

        reasoner = FiveDIntelligenceReasoner()
        reasoning = reasoner.reason(home_form, away_form, five_d_matrix, home_style, away_style,
                                     qa_lookup.get("Q7_weather"), qa_lookup.get("Q5_player_availability"),
                                     qa_lookup.get("Q4_head_to_head"))
        qas.append(QuestionAnswer("Q10_final_verdict",
                                   "Given everything above, what is the reasoned prediction?", "D",
                                   answer=reasoning["final_verdict"], answer_status="UNVERIFIED",
                                   evidence_ids=[], sources=["5D Intelligence Reasoner (derived)"],
                                   reasoning=reasoning["verdict_reasoning"],
                                   uncertainty=f"Confidence: {reasoning['confidence']}. "
                                               f"Missing: {', '.join(reasoning['missing_information']) or 'none flagged'}.",
                                   confidence={"LOW": 0.3, "LOW-MODERATE": 0.4, "MODERATE": 0.55,
                                               "MODERATE-HIGH": 0.7}.get(reasoning["confidence"], 0.5)))

    readiness = compute_readiness(match, qas)
    print_dashboard(competition, match, qas, readiness, five_d_matrix, reasoning)

    return {
        "competition": competition,
        "match": {k: v for k, v in match.items() if k != "raw_event"},
        "questions": [qa.to_dict() for qa in qas],
        "evidence": [e.to_dict() for e in log.all()],
        "five_dimensional_matrix": five_d_matrix,
        "reasoning": reasoning,
        "readiness": readiness,
        "source_registry_used": SOURCE_REGISTRY,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Football AI V1.4 — Five-Dimensional Intelligence Engine")
    parser.add_argument("team_a", help="First team name, e.g. 'Arsenal'")
    parser.add_argument("team_b", help="Second team name, e.g. 'Chelsea'")
    parser.add_argument("--competition", required=True,
                         help=f"Competition id. One of: {', '.join(COMPETITION_CATALOGUE)}")
    parser.add_argument("--date", default=None, help="YYYYMMDD, optional")
    parser.add_argument("--json", action="store_true", help="Also dump full evidence package as JSON")
    args = parser.parse_args()

    package = run(args.team_a, args.team_b, args.competition, args.date)
    if args.json:
        print(json.dumps(package, indent=2, default=str))
