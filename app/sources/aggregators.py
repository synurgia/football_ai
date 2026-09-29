"""Layer 1 — Global aggregator APIs.

7 fetchers. Every one:
  - queries today only (never past dates)
  - has a hard 3s per-source timeout
  - returns a uniform shape
  - fails open (empty on any error, never raises)

Nothing here scrapes HTML. Nothing here decides authority.
Every source is queried in parallel and merged downstream.
"""

from __future__ import annotations
import os
import re
from datetime import date, timedelta
from typing import Any, Dict, List

import httpx


def _today_iso() -> str:
    return date.today().isoformat()


def _today_yyyymmdd() -> str:
    return date.today().strftime("%Y%m%d")


def _yesterday_yyyymmdd() -> str:
    return (date.today() - timedelta(days=1)).strftime("%Y%m%d")


def _tokens(name: str) -> set:
    if not name:
        return set()
    s = str(name).lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    stop = {"fc", "sc", "ac", "cf", "afc", "the", "of", "and"}
    return {w for w in s.split() if w and w not in stop}


def _names_match(a: str, b: str) -> bool:
    ta, tb = _tokens(a), _tokens(b)
    return bool(ta & tb)


def _ok(source, matches):
    return {"source": source, "status": "OK", "matches": matches, "error": None}


def _no_key(source):
    return {"source": source, "status": "NO_KEY", "matches": [], "error": None}


def _empty(source, reason):
    return {"source": source, "status": "EMPTY", "matches": [], "error": reason}


def _failed(source, err):
    return {"source": source, "status": "FAILED", "matches": [], "error": err}


def _match(home, away, kickoff, competition_id, **extra):
    d = {
        "home_team": home,
        "away_team": away,
        "kickoff_at": kickoff,
        "competition_id": competition_id,
    }
    d.update(extra)
    return d


def fetch_apif(competition_id, arg, timeout=3.0):
    key = os.environ.get("API_FOOTBALL_KEY", "")
    if not key:
        return _no_key("apif")
    if arg is True:
        return _empty("apif", "no league id")
    try:
        r = httpx.get(
            "https://v3.football.api-sports.io/fixtures",
            params={"date": _today_iso(), "league": arg, "season": date.today().year},
            headers={"x-apisports-key": key},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return _failed("apif", str(exc))

    out = []
    for f in data.get("response", []) or []:
        home = ((f.get("teams") or {}).get("home") or {}).get("name") or ""
        away = ((f.get("teams") or {}).get("away") or {}).get("name") or ""
        if not home or not away:
            continue
        out.append(_match(
            home, away,
            (f.get("fixture") or {}).get("date") or "",
            competition_id, raw=f,
        ))
    return _ok("apif", out)


def fetch_espn(competition_id, arg, timeout=3.0):
    if not arg or arg is True:
        return _empty("espn", "no slug")
    slug = str(arg)

    urls = [
        f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard",
        "https://site.api.espn.com/apis/site/v2/sports/soccer/all/scoreboard",
    ]
    payload = None
    for url in urls:
        try:
            r = httpx.get(url, params={"dates": _today_yyyymmdd()}, timeout=timeout)
            if r.status_code == 404:
                continue
            r.raise_for_status()
            payload = r.json() or {}
            break
        except Exception:
            continue
    if payload is None:
        return _failed("espn", "all endpoints failed")

    out = []
    for ev in payload.get("events", []) or []:
        comps = (ev.get("competitions") or [{}])[0].get("competitors") or []
        home = away = None
        for c in comps:
            name = (c.get("team") or {}).get("displayName") or ""
            if c.get("homeAway") == "home":
                home = name
            elif c.get("homeAway") == "away":
                away = name
        if not home or not away:
            continue
        out.append(_match(home, away, ev.get("date") or "", competition_id, raw=ev))
    return _ok("espn", out)


_TSDB_RULES = {
    "eng.1": {"exact": "English Premier League"},
    "eng.2": {"exact": "English League Championship"},
    "esp.1": {"exact": "Spanish La Liga"},
    "ita.1": {"exact": "Italian Serie A"},
    "ger.1": {"exact": "German Bundesliga"},
    "fra.1": {"exact": "French Ligue 1"},
    "ned.1": {"exact": "Dutch Eredivisie"},
    "por.1": {"exact": "Portuguese Primeira Liga"},
    "sco.1": {"exact": "Scottish Premiership"},
    "tur.1": {"exact": "Turkish Super Lig"},
    "usa.1": {"exact": "American Major League Soccer"},
    "mex.1": {"exact": "Mexican Primera League"},
    "bra.1": {"exact": "Brazilian Serie A"},
    "jpn.1": {"exact": "Japanese J1 League"},
    "chn.1": {"exact": "Chinese Super League"},
    "aus.1": {"exact": "Australian A-League"},
    "uefa.1": {"exact": "UEFA Champions League"},
    "uefa.2": {"exact": "UEFA Europa League"},
    "fifa.1": {"exact": "FIFA World Cup"},
}


def _tsdb_ok(rule, league):
    if not rule or not league:
        return False
    if "exact" in rule:
        return league.lower().strip() == rule["exact"].lower()
    return False


def fetch_tsdb(competition_id, arg, timeout=3.0):
    rule = _TSDB_RULES.get(competition_id)
    if not rule:
        return _empty("tsdb", "no filter rule")

    try:
        r = httpx.get(
            "https://www.thesportsdb.com/api/v1/json/3/eventsday.php",
            params={"d": _today_iso(), "s": "Soccer"},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return _failed("tsdb", str(exc))

    out = []
    for ev in data.get("events") or []:
        if not _tsdb_ok(rule, ev.get("strLeague") or ""):
            continue
        home = ev.get("strHomeTeam") or ""
        away = ev.get("strAwayTeam") or ""
        if not home or not away:
            continue
        t = ev.get("strTime") or "00:00:00"
        out.append(_match(
            home, away,
            f"{ev.get('dateEvent','')}T{t}Z",
            competition_id,
            league=ev.get("strLeague"),
            raw=ev,
        ))
    return _ok("tsdb", out)


def fetch_fd(competition_id, arg, timeout=3.0):
    key = os.environ.get("FOOTBALL_DATA_API_KEY", "")
    if not key:
        return _no_key("fd")
    try:
        r = httpx.get(
            "https://api.football-data.org/v4/matches",
            params={"competitions": arg, "dateFrom": _today_iso(), "dateTo": _today_iso()},
            headers={"X-Auth-Token": key},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return _failed("fd", str(exc))

    out = []
    for m in data.get("matches", []) or []:
        home = (m.get("homeTeam") or {}).get("name") or ""
        away = (m.get("awayTeam") or {}).get("name") or ""
        if not home or not away:
            continue
        out.append(_match(home, away, m.get("utcDate") or "", competition_id, raw=m))
    return _ok("fd", out)


def fetch_oldb(competition_id, arg, timeout=3.0):
    if not arg or arg is True:
        return _empty("oldb", "no league code")
    try:
        r = httpx.get(f"https://api.openligadb.de/getmatchdata/{arg}", timeout=timeout)
        r.raise_for_status()
        rows = r.json() or []
    except Exception as exc:
        return _failed("oldb", str(exc))

    if not isinstance(rows, list):
        return _empty("oldb", "not a list")

    today = _today_iso()
    out = []
    for m in rows:
        if (m.get("matchDateTimeUTC") or "")[:10] != today:
            continue
        home = (m.get("team1") or {}).get("teamName") or ""
        away = (m.get("team2") or {}).get("teamName") or ""
        if not home or not away:
            continue
        out.append(_match(home, away, m.get("matchDateTimeUTC") or "",
                          competition_id, raw=m))
    return _ok("oldb", out)


def fetch_ofb(competition_id, arg, timeout=3.0):
    if not arg or arg is True:
        return _empty("ofb", "no file")
    y = date.today().year
    m = date.today().month
    season = f"{y}-{(y+1) % 100:02d}" if m >= 7 else f"{y-1}-{y % 100:02d}"
    url = (
        "https://raw.githubusercontent.com/openfootball/football.json/"
        f"master/{season}/{arg}.json"
    )
    try:
        r = httpx.get(url, timeout=timeout)
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return _failed("ofb", str(exc))

    today = _today_iso()
    out = []
    for m in data.get("matches", []) or []:
        if m.get("date") != today:
            continue
        home = m.get("team1") or ""
        away = m.get("team2") or ""
        if not home or not away:
            continue
        out.append(_match(
            home, away,
            f"{m.get('date')}T{m.get('time','00:00')}Z",
            competition_id, raw=m,
        ))
    return _ok("ofb", out)


def fetch_zafx(competition_id, arg, timeout=3.0):
    key = os.environ.get("ZAFRONIX_API_KEY", "")
    if not key:
        return _no_key("zafx")
    if not arg or arg is True:
        return _empty("zafx", "no endpoint")
    try:
        r = httpx.get(
            f"https://api.zafronix.com/{arg}/fixtures",
            params={"date": _today_iso()},
            headers={"x-api-key": key},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return _failed("zafx", str(exc))

    out = []
    for f in (data.get("fixtures") or data.get("matches") or []):
        home = f.get("home") or f.get("homeTeam") or ""
        away = f.get("away") or f.get("awayTeam") or ""
        if not home or not away:
            continue
        out.append(_match(home, away, f.get("date") or "",
                          competition_id, raw=f))
    return _ok("zafx", out)




# ----------------------------------------------------------------
# 8. Sofascore (no key, worldwide, 500-1000+ matches/day)
# ----------------------------------------------------------------

_SOFA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13) FootballAI/1.6",
    "Accept": "application/json",
    "Referer": "https://www.sofascore.com/",
}


def _sofa_get(url, timeout=8.0):
    try:
        r = httpx.get(url, headers=_SOFA_HEADERS, timeout=timeout)
        if r.status_code == 403:
            return None, "403 forbidden"
        r.raise_for_status()
        return r.json() or {}, None
    except Exception as exc:
        return None, str(exc)


def fetch_sofascore_worldwide(timeout=8.0):
    """Fetch every scheduled football match worldwide for today.

    Returns a flat list. No key. No auth. 500-1000+ matches per day.
    """
    date_str = _today_iso()
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{date_str}"
    data, err = _sofa_get(url, timeout=timeout)
    if err:
        return _failed("sofascore", err)

    events = data.get("events") or []
    if not events:
        return _empty("sofascore", "no events")

    out = []
    for ev in events:
        home = (ev.get("homeTeam") or {}).get("name") or ""
        away = (ev.get("awayTeam") or {}).get("name") or ""
        if not home or not away:
            continue
        tour = ev.get("tournament") or {}
        unique = tour.get("uniqueTournament") or {}
        out.append({
            "home_team": home,
            "away_team": away,
            "kickoff_at": str(ev.get("startTimestamp") or ""),
            "competition_id": "__worldwide__",
            "tournament": tour.get("name") or "",
            "tournament_id": str(unique.get("id") or ""),
            "category": (tour.get("category") or {}).get("name") or "",
            "source": "sofascore",
            "raw": ev,
        })
    return _ok("sofascore", out)


def fetch_sofascore(competition_id, arg, timeout=8.0):
    """Filtered Sofascore — kept for compatibility with the dispatcher."""
    return fetch_sofascore_worldwide(timeout=timeout)


FETCHERS = {
    "apif": fetch_apif,
    "espn": fetch_espn,
    "tsdb": fetch_tsdb,
    "fd":   fetch_fd,
    "oldb": fetch_oldb,
    "ofb":  fetch_ofb,
    "zafx": fetch_zafx,
    "sofascore": fetch_sofascore,
}


def fetch_one(source_key, competition_id, arg, timeout=3.0):
    fn = FETCHERS.get(source_key)
    if fn is None:
        return _empty(source_key, "no fetcher")
    try:
        return fn(competition_id, arg, timeout=timeout)
    except Exception as exc:
        return _failed(source_key, str(exc))
