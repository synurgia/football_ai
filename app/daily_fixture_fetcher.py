"""Daily fixture fetcher — today only.

Queries every free source that covers a competition and returns matches
for TODAY'S date. Never past dates. Never future beyond tomorrow.

Every source is optional. Failures are recorded but do not stop others.
"""

from __future__ import annotations
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

import httpx

from app.competition_source_map import sources_for_competition


def _today() -> str:
    return date.today().isoformat()


def _yyyymmdd() -> str:
    return date.today().strftime("%Y%m%d")


def _tokens(name: str) -> set:
    if not name:
        return set()
    s = str(name).lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    stop = {"fc", "sc", "ac", "cf", "afc", "the", "of", "and", "de"}
    return {w for w in s.split() if w and w not in stop}


def _names_match(a: str, b: str) -> bool:
    ta, tb = _tokens(a), _tokens(b)
    return bool(ta & tb)


# ---------- Source-specific fetchers ----------

def _fetch_fd(comp_id, arg, timeout=8.0):
    """football-data.org /v4/matches returns today's matches by default."""
    key = os.environ.get("FOOTBALL_DATA_API_KEY", "")
    if not key:
        return {"source": "football-data.org", "status": "NO_KEY", "matches": []}
    try:
        r = httpx.get(
            "https://api.football-data.org/v4/matches",
            params={"competitions": arg, "dateFrom": _today(), "dateTo": _today()},
            headers={"X-Auth-Token": key},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return {"source": "football-data.org", "status": "FAILED", "error": str(exc), "matches": []}

    out = []
    for m in data.get("matches", []) or []:
        home = (m.get("homeTeam") or {}).get("name") or ""
        away = (m.get("awayTeam") or {}).get("name") or ""
        utc = m.get("utcDate") or ""
        if not home or not away:
            continue
        out.append({
            "home_team": home, "away_team": away,
            "kickoff_at": utc, "competition_id": comp_id,
            "raw": m,
        })
    return {"source": "football-data.org", "status": "OK", "matches": out}


# TheSportsDB free eventsday.php ignores the league id and returns ALL
# global soccer for a date. We enforce strict client-side filtering:
#   require_exact : the strLeague value must equal (case-insensitive) this string
#   require_all   : every token here must be present in strLeague
#   forbid        : none of these may appear in strLeague
#
# This prevents 'eng.2' from matching 'American USL Championship'
# and 'esp.1' from matching 'Brazilian Serie A'.
_TSDB_RULES = {
    "eng.1": {"require_exact": "English Premier League"},
    "eng.2": {"require_exact": "English League Championship"},
    "eng.3": {"require_exact": "English League One"},
    "eng.4": {"require_exact": "English League Two"},
    "esp.1": {"require_exact": "Spanish La Liga"},
    "esp.2": {"require_exact": "Spanish La Liga 2"},
    "ita.1": {"require_exact": "Italian Serie A"},
    "ita.2": {"require_exact": "Italian Serie B"},
    "ger.1": {"require_exact": "German Bundesliga"},
    "ger.2": {"require_exact": "German 2. Bundesliga"},
    "fra.1": {"require_exact": "French Ligue 1"},
    "fra.2": {"require_exact": "French Ligue 2"},
    "ned.1": {"require_exact": "Dutch Eredivisie"},
    "por.1": {"require_exact": "Portuguese Primeira Liga"},
    "sco.1": {"require_exact": "Scottish Premiership"},
    "tur.1": {"require_exact": "Turkish Super Lig"},
    "bel.1": {"require_exact": "Belgian Pro League"},
    "usa.1": {"require_exact": "American Major League Soccer"},
    "mex.1": {"require_exact": "Mexican Primera League"},
    "bra.1": {"require_exact": "Brazilian Serie A"},
    "arg.1": {"require_exact": "Argentinian Primera Division"},
    "jpn.1": {"require_exact": "Japanese J1 League"},
    "kor.1": {"require_exact": "South Korean K League 1"},
    "chn.1": {"require_exact": "Chinese Super League"},
    "sau.1": {"require_exact": "Saudi Pro League"},
    "aus.1": {"require_all": ["a-league"], "forbid": ["women"]},
    "uefa.1": {"require_exact": "UEFA Champions League"},
    "uefa.2": {"require_exact": "UEFA Europa League"},
    "uefa.3": {"require_exact": "UEFA Europa Conference League"},
    "fifa.1": {"require_exact": "FIFA World Cup"},
    "caf.1": {"require_exact": "CAF Champions League"},
    "afc.1": {"require_exact": "AFC Champions League"},
}


def _tsdb_league_matches(rule, league_str):
    if not rule or not league_str:
        return False
    low = league_str.lower().strip()

    forbid = rule.get("forbid") or []
    for bad in forbid:
        if bad.lower() in low:
            return False

    exact = rule.get("require_exact")
    if exact:
        return low == exact.lower().strip()

    all_tokens = rule.get("require_all") or []
    for tok in all_tokens:
        if tok.lower() not in low:
            return False
    return bool(all_tokens)


def _fetch_tsdb(comp_id, arg, timeout=8.0):
    """TheSportsDB eventsday.php — fetch today, then filter by league name.

    Free eventsday.php returns ALL soccer globally for a date. The league id
    argument is ignored on free tier, so filtering happens here using the
    strLeague field. If no league hint is known, return EMPTY (do not
    contaminate other competitions with unrelated matches).
    """
    rule = _TSDB_RULES.get(comp_id)
    if not rule:
        return {"source": "TheSportsDB", "status": "NO_FILTER", "matches": []}

    try:
        r = httpx.get(
            "https://www.thesportsdb.com/api/v1/json/3/eventsday.php",
            params={"d": _today(), "s": "Soccer"},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return {"source": "TheSportsDB", "status": "FAILED", "error": str(exc), "matches": []}

    events = data.get("events") or []
    out = []
    for ev in events:
        league = ev.get("strLeague") or ""
        if not _tsdb_league_matches(rule, league):
            continue
        home = ev.get("strHomeTeam") or ""
        away = ev.get("strAwayTeam") or ""
        if not home or not away:
            continue
        out.append({
            "home_team": home, "away_team": away,
            "kickoff_at": f"{ev.get('dateEvent','')}T{ev.get('strTime','') or '00:00:00'}Z",
            "competition_id": comp_id,
            "league": ev.get("strLeague"),
            "raw": ev,
        })
    return {"source": "TheSportsDB", "status": "OK", "matches": out}


def _fetch_oldb(comp_id, arg, timeout=8.0):
    """OpenLigaDB getmatchdata/{league} — current matchday (contains today)."""
    try:
        r = httpx.get(
            f"https://api.openligadb.de/getmatchdata/{arg}",
            timeout=timeout,
        )
        r.raise_for_status()
        rows = r.json() or []
    except Exception as exc:
        return {"source": "OpenLigaDB", "status": "FAILED", "error": str(exc), "matches": []}

    if not isinstance(rows, list):
        return {"source": "OpenLigaDB", "status": "EMPTY", "matches": []}

    today_str = _today()
    out = []
    for m in rows:
        dt = (m.get("matchDateTimeUTC") or "")[:10]
        if dt != today_str:
            continue
        home = ((m.get("team1") or {}).get("teamName")) or ""
        away = ((m.get("team2") or {}).get("teamName")) or ""
        if not home or not away:
            continue
        out.append({
            "home_team": home, "away_team": away,
            "kickoff_at": m.get("matchDateTimeUTC") or "",
            "competition_id": comp_id,
            "raw": m,
        })
    return {"source": "OpenLigaDB", "status": "OK", "matches": out}


def _fetch_espn(comp_id, arg, timeout=8.0):
    """ESPN scoreboard with TODAY's date only.

    For 'fifa.friendly.men' and 'fifa.friendly.women', the ESPN endpoint
    is different (scoreboard for the international friendlies is not
    published per league). Fall back to a broader soccer scoreboard and
    filter by date.
    """
    slug = arg
    try:
        r = httpx.get(
            f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard",
            params={"dates": _yyyymmdd()},
            timeout=timeout,
        )
        if r.status_code == 404:
            # Fallback to generic all-soccer scoreboard
            r = httpx.get(
                "https://site.api.espn.com/apis/site/v2/sports/soccer/all/scoreboard",
                params={"dates": _yyyymmdd()},
                timeout=timeout,
            )
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return {"source": "ESPN", "status": "FAILED", "error": str(exc), "matches": []}

    out = []
    for ev in data.get("events", []) or []:
        comps = (ev.get("competitions") or [{}])[0].get("competitors") or []
        home = away = None
        for c in comps:
            t = (c.get("team") or {}).get("displayName") or ""
            if c.get("homeAway") == "home":
                home = t
            elif c.get("homeAway") == "away":
                away = t
        if not home or not away:
            continue
        out.append({
            "home_team": home, "away_team": away,
            "kickoff_at": ev.get("date") or "",
            "competition_id": comp_id,
            "raw": ev,
        })
    return {"source": "ESPN", "status": "OK", "matches": out}


def _fetch_apif(comp_id, arg, timeout=8.0):
    key = os.environ.get("API_FOOTBALL_KEY", "")
    if not key:
        return {"source": "API-Football", "status": "NO_KEY", "matches": []}
    try:
        r = httpx.get(
            "https://v3.football.api-sports.io/fixtures",
            params={"date": _today(), "league": arg, "season": date.today().year},
            headers={"x-apisports-key": key},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return {"source": "API-Football", "status": "FAILED", "error": str(exc), "matches": []}

    out = []
    for f in data.get("response", []) or []:
        home = ((f.get("teams") or {}).get("home") or {}).get("name") or ""
        away = ((f.get("teams") or {}).get("away") or {}).get("name") or ""
        if not home or not away:
            continue
        out.append({
            "home_team": home, "away_team": away,
            "kickoff_at": (f.get("fixture") or {}).get("date") or "",
            "competition_id": comp_id,
            "raw": f,
        })
    return {"source": "API-Football", "status": "OK", "matches": out}


def _fetch_zafx(comp_id, arg, timeout=8.0):
    key = os.environ.get("ZAFRONIX_API_KEY", "")
    if not key:
        return {"source": "Zafronix", "status": "NO_KEY", "matches": []}
    try:
        r = httpx.get(
            f"https://api.zafronix.com/{arg}/fixtures",
            params={"date": _today()},
            headers={"x-api-key": key},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return {"source": "Zafronix", "status": "FAILED", "error": str(exc), "matches": []}

    out = []
    for f in (data.get("fixtures") or data.get("matches") or []):
        home = f.get("home") or f.get("homeTeam") or ""
        away = f.get("away") or f.get("awayTeam") or ""
        if not home or not away:
            continue
        out.append({
            "home_team": home, "away_team": away,
            "kickoff_at": f.get("date") or f.get("kickoff") or "",
            "competition_id": comp_id,
            "raw": f,
        })
    return {"source": "Zafronix", "status": "OK", "matches": out}


def _fetch_ofb(comp_id, arg, timeout=8.0):
    """openfootball/football.json — season folder is 'YYYY-YY' (e.g. 2025-26)."""
    y = date.today().year
    m = date.today().month
    # Season starts mid-year for most European leagues
    if m >= 7:
        season = f"{y}-{(y+1) % 100:02d}"
    else:
        season = f"{y-1}-{y % 100:02d}"
    url = (
        "https://raw.githubusercontent.com/openfootball/football.json/"
        f"master/{season}/{arg}.json"
    )
    try:
        r = httpx.get(url, timeout=timeout)
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return {"source": "openfootball", "status": "FAILED", "error": str(exc), "matches": []}

    out = []
    today_str = _today()
    for m in data.get("matches", []) or []:
        if m.get("date") != today_str:
            continue
        home = m.get("team1") or ""
        away = m.get("team2") or ""
        if not home or not away:
            continue
        out.append({
            "home_team": home, "away_team": away,
            "kickoff_at": f"{m.get('date')}T{m.get('time','00:00')}Z",
            "competition_id": comp_id,
            "raw": m,
        })
    return {"source": "openfootball", "status": "OK", "matches": out}


_FETCHERS = {
    "fd": _fetch_fd,
    "tsdb": _fetch_tsdb,
    "oldb": _fetch_oldb,
    "espn": _fetch_espn,
    "apif": _fetch_apif,
    "zafx": _fetch_zafx,
    "ofb": _fetch_ofb,
}


# ---------- Public API ----------

def fetch_today(competition_id: str, *, timeout: float = 8.0) -> Dict[str, Any]:
    """Fetch today's fixtures for one competition from all covering sources."""
    sources = sources_for_competition(competition_id)
    if not sources:
        return {"competition_id": competition_id, "date": _today(),
                "matches": [], "sources": [], "status": "NO_SOURCE"}

    # Skip the registry source in this fetcher (it uses different mechanics)
    network_sources = [(k, a) for k, a in sources if k != "reg"]
    if not network_sources:
        return {"competition_id": competition_id, "date": _today(),
                "matches": [], "sources": [], "status": "REGISTRY_ONLY"}

    results = []
    with ThreadPoolExecutor(max_workers=min(6, len(network_sources))) as pool:
        futures = {
            pool.submit(_FETCHERS[k], competition_id, a, timeout): (k, a)
            for k, a in network_sources
        }
        for fut in as_completed(futures):
            k, a = futures[fut]
            try:
                results.append(fut.result())
            except Exception as exc:
                results.append({"source": k, "status": "FAILED",
                                "error": str(exc), "matches": []})

    # Merge — dedupe by (home, away) normalised tokens
    merged: List[Dict[str, Any]] = []
    seen = set()
    for r in results:
        for m in r.get("matches", []):
            key = (
                frozenset(_tokens(m["home_team"])),
                frozenset(_tokens(m["away_team"])),
            )
            if key in seen:
                continue
            seen.add(key)
            m["sources"] = [r["source"]]
            merged.append(m)

    return {
        "competition_id": competition_id,
        "date": _today(),
        "status": "OK",
        "sources": [{"source": r["source"], "status": r["status"],
                     "count": len(r.get("matches", []))} for r in results],
        "matches": merged,
    }


def fetch_all_today(competition_ids: List[str], *, timeout: float = 8.0) -> Dict[str, Any]:
    """Fetch today's fixtures for many competitions in parallel."""
    out: Dict[str, List[Dict[str, Any]]] = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch_today, cid, timeout=timeout): cid
                   for cid in competition_ids}
        for fut in as_completed(futures):
            cid = futures[fut]
            try:
                r = fut.result()
                out[cid] = r.get("matches", [])
            except Exception:
                out[cid] = []
    return {"date": _today(), "by_competition": out,
            "total": sum(len(v) for v in out.values())}
