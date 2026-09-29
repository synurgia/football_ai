"""Worldwide fixture sources — all queried in parallel.

Rule: no source is primary. Every source that returns data contributes.
Sources can be added or removed by editing WORLDWIDE_SOURCES below.
Failures are recorded, not fatal. Nothing here is privileged.

Each source returns a list of dicts with a uniform shape:
    {home_team, away_team, kickoff_at, tournament, tournament_id, source}
"""

from __future__ import annotations
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from typing import Any, Dict, List

import httpx


def _today_iso() -> str:
    return date.today().isoformat()


def _ok(source, matches):
    return {"source": source, "status": "OK", "matches": matches, "error": None}


def _failed(source, err):
    return {"source": source, "status": "FAILED", "matches": [], "error": str(err)}


def _empty(source, reason):
    return {"source": source, "status": "EMPTY", "matches": [], "error": reason}


def _shape(home, away, kickoff, tournament, tournament_id, source, raw=None):
    return {
        "home_team": home,
        "away_team": away,
        "kickoff_at": kickoff,
        "tournament": tournament or "",
        "tournament_id": str(tournament_id or ""),
        "source": source,
        "raw": raw or {},
    }


# ================================================================
# SOURCE 1 — API-Football (one call = every fixture worldwide)
# ================================================================

def src_api_football(timeout=12.0):
    key = os.environ.get("API_FOOTBALL_KEY", "")
    if not key:
        return _empty("api_football", "no key")
    try:
        r = httpx.get(
            "https://v3.football.api-sports.io/fixtures",
            params={"date": _today_iso()},
            headers={"x-apisports-key": key},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return _failed("api_football", exc)

    out = []
    for f in data.get("response", []) or []:
        t = f.get("teams") or {}
        l = f.get("league") or {}
        home = (t.get("home") or {}).get("name") or ""
        away = (t.get("away") or {}).get("name") or ""
        if not home or not away:
            continue
        out.append(_shape(
            home, away,
            (f.get("fixture") or {}).get("date") or "",
            l.get("name") or "",
            l.get("id") or "",
            "api_football",
            raw=f,
        ))
    return _ok("api_football", out)


# ================================================================
# SOURCE 2 — ESPN (bulk all-soccer scoreboard)
# ================================================================

def src_espn(timeout=8.0):
    try:
        r = httpx.get(
            "https://site.api.espn.com/apis/site/v2/sports/soccer/all/scoreboard",
            params={"dates": date.today().strftime("%Y%m%d")},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return _failed("espn", exc)

    out = []
    for ev in data.get("events", []) or []:
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
        lg = ((ev.get("competitions") or [{}])[0].get("league") or {})
        out.append(_shape(
            home, away,
            ev.get("date") or "",
            lg.get("name") or ev.get("season", {}).get("slug", ""),
            lg.get("id") or "",
            "espn",
            raw=ev,
        ))
    return _ok("espn", out)


# ================================================================
# SOURCE 3 — TheSportsDB eventsday (all soccer for date)
# ================================================================

def src_thesportsdb(timeout=8.0):
    try:
        r = httpx.get(
            "https://www.thesportsdb.com/api/v1/json/3/eventsday.php",
            params={"d": _today_iso(), "s": "Soccer"},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return _failed("thesportsdb", exc)

    out = []
    for ev in data.get("events") or []:
        home = ev.get("strHomeTeam") or ""
        away = ev.get("strAwayTeam") or ""
        if not home or not away:
            continue
        t = ev.get("strTime") or "00:00:00"
        out.append(_shape(
            home, away,
            f"{ev.get('dateEvent','')}T{t}Z",
            ev.get("strLeague") or "",
            ev.get("idLeague") or "",
            "thesportsdb",
            raw=ev,
        ))
    return _ok("thesportsdb", out)


# ================================================================
# SOURCE 4 — openfootball (public GitHub JSON, no key)
# ================================================================

def src_openfootball(timeout=6.0):
    """Public GitHub JSON — one file per league. Multi-league scan."""
    y = date.today().year
    m = date.today().month
    season = f"{y}-{(y+1) % 100:02d}" if m >= 7 else f"{y-1}-{y % 100:02d}"

    leagues = ["en.1", "en.2", "de.1", "de.2", "es.1", "it.1", "fr.1"]
    out = []
    today = _today_iso()

    for lg in leagues:
        url = (
            "https://raw.githubusercontent.com/openfootball/football.json/"
            f"master/{season}/{lg}.json"
        )
        try:
            r = httpx.get(url, timeout=timeout)
            if r.status_code != 200:
                continue
            data = r.json() or {}
        except Exception:
            continue
        for match in data.get("matches", []) or []:
            if match.get("date") != today:
                continue
            home = match.get("team1") or ""
            away = match.get("team2") or ""
            if not home or not away:
                continue
            out.append(_shape(
                home, away,
                f"{match.get('date')}T{match.get('time','00:00')}Z",
                data.get("name") or lg,
                lg,
                "openfootball",
                raw=match,
            ))
    return _ok("openfootball", out)


# ================================================================
# SOURCE 5 — Bzzoiro (free token, wide coverage)
# ================================================================

def src_bzzoiro(timeout=10.0):
    key = os.environ.get("BZZOIRO_TOKEN", "")
    if not key:
        return _empty("bzzoiro", "no token")
    try:
        r = httpx.get(
            "https://sports.bzzoiro.com/api/v2/events/",
            params={"date_from": _today_iso(), "date_to": _today_iso()},
            headers={"Authorization": f"Token {key}"},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return _failed("bzzoiro", exc)

    out = []
    results = data.get("results") if isinstance(data, dict) else data
    for m in results or []:
        home = m.get("home_team") or ""
        away = m.get("away_team") or ""
        if not home or not away:
            continue
        out.append(_shape(
            home, away,
            m.get("event_date") or "",
            m.get("league_name") or "",
            m.get("league_id") or "",
            "bzzoiro",
            raw=m,
        ))
    return _ok("bzzoiro", out)


# ================================================================
# SOURCE 6 — SportsAPI Pro (free tier, 6,473 competitions)
# ================================================================

def src_sportsapipro(timeout=12.0):
    key = os.environ.get("SPORTSAPIPRO_KEY", "")
    if not key:
        return _empty("sportsapipro", "no key")
    try:
        r = httpx.get(
            "https://api.sportsapipro.com/v6/football/today",
            params={"tz": "00:00"},
            headers={"x-api-key": key},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return _failed("sportsapipro", exc)

    out = []
    for m in data.get("matches", []) or []:
        home = (m.get("homeTeam") or {}).get("name") or ""
        away = (m.get("awayTeam") or {}).get("name") or ""
        if not home or not away:
            continue
        comp = m.get("competition") or {}
        out.append(_shape(
            home, away,
            m.get("matchTime") or "",
            comp.get("name") or "",
            comp.get("id") or "",
            "sportsapipro",
            raw=m,
        ))
    return _ok("sportsapipro", out)


# ================================================================
# REGISTRY — all sources, all equal
# ================================================================



# ================================================================
# SOURCE 7 — FotMob (no key, worldwide)
# ================================================================

def src_fotmob(timeout=10.0):
    """FotMob unofficial JSON API. No key. Worldwide matches.

    Returns all football matches for a date, grouped by league.
    Endpoint: https://www.fotmob.com/api/matches?date=YYYYMMDD
    """
    date_str = date.today().strftime("%Y%m%d")
    url = f"https://www.fotmob.com/api/matches?date={date_str}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13) FootballAI/1.7",
        "Accept": "application/json",
    }
    try:
        r = httpx.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return _failed("fotmob", exc)

    out = []
    leagues = data.get("leagues") or []
    for lg in leagues:
        lg_name = lg.get("name") or ""
        lg_id = lg.get("id") or ""
        for m in lg.get("matches") or []:
            home = (m.get("home") or {}).get("name") or ""
            away = (m.get("away") or {}).get("name") or ""
            if not home or not away:
                continue
            # FotMob gives status {started, cancelled, finished}
            kickoff_ts = m.get("status", {}).get("utcTime") if isinstance(m.get("status"), dict) else None
            kickoff = kickoff_ts or m.get("time") or ""
            out.append(_shape(
                home, away,
                str(kickoff),
                lg_name,
                lg_id,
                "fotmob",
                raw=m,
            ))
    return _ok("fotmob", out)


# ================================================================
# SOURCE 8 — LiveScore (no key, worldwide)
# ================================================================

def src_livescore(timeout=10.0):
    """LiveScore unofficial JSON API. No key. Worldwide matches.

    Endpoint: https://prod-cdn-mev-api.livescore.com/v1/api/app/date/soccer/YYYYMMDD/0
    """
    date_str = date.today().strftime("%Y%m%d")
    url = (
        "https://prod-cdn-mev-api.livescore.com/v1/api/app/date/"
        f"soccer/{date_str}/0"
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13) FootballAI/1.7",
        "Accept": "application/json",
    }
    try:
        r = httpx.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        data = r.json() or {}
    except Exception as exc:
        return _failed("livescore", exc)

    out = []
    # LiveScore shape: {"Stages": [{"Events": [...], "Cnm": "League Name"}]}
    stages = data.get("Stages") or data.get("stages") or []
    for stage in stages:
        lg_name = stage.get("Cnm") or stage.get("Snm") or ""
        lg_id = str(stage.get("Sid") or "")
        for ev in stage.get("Events") or stage.get("events") or []:
            home = (ev.get("T1") or [{}])[0].get("Nm") if isinstance(ev.get("T1"), list) else None
            away = (ev.get("T2") or [{}])[0].get("Nm") if isinstance(ev.get("T2"), list) else None
            if not home or not away:
                # alternate shape
                home = ev.get("home_team") or ev.get("home") or ""
                away = ev.get("away_team") or ev.get("away") or ""
            if not home or not away:
                continue
            kickoff = ev.get("Esd") or ev.get("date") or ""
            out.append(_shape(
                home, away,
                str(kickoff),
                lg_name,
                lg_id,
                "livescore",
                raw=ev,
            ))
    return _ok("livescore", out)



WORLDWIDE_SOURCES = [
    ("espn",         src_espn),
    ("thesportsdb",  src_thesportsdb),
    ("openfootball", src_openfootball),
    ("livescore",   src_livescore),
]


def add_source(name: str, fn) -> None:
    """Add a source at runtime. No restart needed."""
    WORLDWIDE_SOURCES.append((name, fn))


def remove_source(name: str) -> None:
    global WORLDWIDE_SOURCES
    WORLDWIDE_SOURCES = [(n, f) for n, f in WORLDWIDE_SOURCES if n != name]


def scan_worldwide(timeout: float = 10.0, max_workers: int = 6) -> Dict[str, Any]:
    """Query every registered source in parallel. Merge. Never fatal."""
    results: List[Dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(fn, timeout): name for name, fn in WORLDWIDE_SOURCES}
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                results.append(fut.result())
            except Exception as exc:
                results.append(_failed(name, exc))

    # Merge — dedupe by team-name tokens
    import re
    def _toks(s):
        s = re.sub(r"[^a-z0-9 ]+", " ", str(s or "").lower())
        stop = {"fc", "sc", "ac", "cf", "afc", "the", "of", "and", "de"}
        return frozenset(w for w in s.split() if w and w not in stop)

    seen = set()
    merged = []
    for r in results:
        for m in r.get("matches", []):
            k = (_toks(m["home_team"]), _toks(m["away_team"]))
            if not k[0] or not k[1] or k in seen:
                continue
            seen.add(k)
            m["sources"] = [r["source"]]
            merged.append(m)

    return {
        "date": _today_iso(),
        "matches": merged,
        "total": len(merged),
        "source_status": [
            {"source": r["source"], "status": r["status"],
             "count": len(r.get("matches", [])), "error": r.get("error")}
            for r in results
        ],
    }


if __name__ == "__main__":
    import time
    t0 = time.time()
    r = scan_worldwide()
    print(f"date: {r['date']}  total: {r['total']}  in {time.time()-t0:.1f}s\n")
    for s in r["source_status"]:
        print(f"  {s['source']:<14} {s['status']:<10} {s['count']:>4} matches  {s.get('error') or ''}")
