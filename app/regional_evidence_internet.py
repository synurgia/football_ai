"""Internet evidence providers that emit CollectedSourceEvidence.

Each function queries one free, trusted source and returns a record in
the same shape ESPN produces. That way the existing applier + extractor
handle them without new plumbing.

Sources:
  - TheSportsDB     team identity, venue, manager, country
  - Wikidata        country, league membership
  - OpenLigaDB      full standings (German leagues only)
  - ESPN Public     team identity, venue (per-competition, not scoreboard)
  - football-data   team identity, venue (needs API key)
  - footballkenya  FKF official (Kenyan fixtures/standings)

None is primary. Each returns a record with its own source_id.
Failures return a failed record — never fabricate.
"""

from __future__ import annotations
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _record(
    fixture, source_id, source_name, status, evidence_types,
    evidence=None, reason=None, source_reference=None,
):
    return {
        "fixture": fixture,
        "source_id": source_id,
        "source_name": source_name,
        "status": status,
        "evidence_types": evidence_types,
        "evidence": evidence or {},
        "reason": reason,
        "source_reference": source_reference,
        "observed_at": _now(),
    }


def _tokens(name: str) -> set:
    if not name:
        return set()
    s = str(name).lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    stop = {"fc", "sc", "ac", "cf", "afc", "the", "of", "and"}
    return {w for w in s.split() if w and w not in stop}


def _names_match(a: str, b: str) -> bool:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return False
    return bool(ta & tb)


# ---------- TheSportsDB ----------

def fetch_thesportsdb(fixture, *, timeout=8.0):
    home = fixture.get("home_team") or ""
    away = fixture.get("away_team") or ""
    if not home and not away:
        return _record(fixture, "thesportsdb", "TheSportsDB", "NOT_CONFIGURED",
                       ["teams"], reason="No team names to look up")

    out_teams = []
    for side, name in (("home", home), ("away", away)):
        if not name:
            continue
        try:
            r = httpx.get(
                "https://www.thesportsdb.com/api/v1/json/3/searchteams.php",
                params={"t": name}, timeout=timeout,
            )
            r.raise_for_status()
            payload = r.json() or {}
        except Exception as exc:
            return _record(fixture, "thesportsdb", "TheSportsDB", "FAILED",
                           ["teams"], reason=str(exc))

        teams = payload.get("teams") or []
        if not teams:
            continue
        # Prefer soccer
        chosen = None
        for t in teams:
            if (t.get("strSport") or "").lower() == "soccer":
                chosen = t
                break
        if chosen is None:
            chosen = teams[0]

        out_teams.append({
            "side": side,
            "team_name": chosen.get("strTeam"),
            "country": chosen.get("strCountry"),
            "league": chosen.get("strLeague"),
            "venue": chosen.get("strStadium"),
            "manager": chosen.get("strManager"),
            "id": chosen.get("idTeam"),
        })

    if not out_teams:
        return _record(fixture, "thesportsdb", "TheSportsDB", "INSUFFICIENT_EVIDENCE",
                       ["teams"], reason="No matching team found")

    return _record(
        fixture, "thesportsdb", "TheSportsDB", "VERIFIED",
        ["teams", "venue", "manager"],
        evidence={"teams": out_teams},
        source_reference="https://www.thesportsdb.com/api/v1/json/3/searchteams.php",
    )


# ---------- Wikidata ----------

def fetch_wikidata(fixture, *, timeout=8.0):
    home = fixture.get("home_team") or ""
    away = fixture.get("away_team") or ""
    if not home and not away:
        return _record(fixture, "wikidata", "Wikidata", "NOT_CONFIGURED",
                       ["teams"], reason="No team names")

    out = []
    for side, name in (("home", home), ("away", away)):
        if not name:
            continue
        query = (
            'SELECT ?club ?clubLabel ?countryLabel WHERE { '
            '?club wdt:P31/wdt:P279* wd:Q476028 . '
            f'?club rdfs:label "{name}"@en . '
            'OPTIONAL { ?club wdt:P17 ?country . } '
            'SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . } '
            '} LIMIT 3'
        )
        try:
            r = httpx.get(
                "https://query.wikidata.org/sparql",
                params={"query": query, "format": "json"},
                headers={"Accept": "application/sparql-results+json",
                         "User-Agent": "FootballAI/1.5"},
                timeout=timeout,
            )
            r.raise_for_status()
            payload = r.json() or {}
        except Exception as exc:
            return _record(fixture, "wikidata", "Wikidata", "FAILED",
                           ["teams"], reason=str(exc))

        rows = (payload.get("results") or {}).get("bindings") or []
        if not rows:
            continue
        country = ((rows[0].get("countryLabel") or {}).get("value") or "").strip()
        out.append({"side": side, "team_name": name, "country": country})

    if not out:
        return _record(fixture, "wikidata", "Wikidata", "INSUFFICIENT_EVIDENCE",
                       ["teams"], reason="No matching entries")

    return _record(
        fixture, "wikidata", "Wikidata", "VERIFIED",
        ["teams"],
        evidence={"teams": out},
        source_reference="https://query.wikidata.org/sparql",
    )


# ---------- OpenLigaDB (German leagues only) ----------

_OLDB_LEAGUE = {"de.1": "bl1", "de.2": "bl2", "de.3": "liga3"}

def fetch_openligadb(fixture, *, timeout=8.0):
    cid = (fixture.get("competition_id") or "").strip().lower()
    league = _OLDB_LEAGUE.get(cid)
    if not league:
        return _record(fixture, "openligadb", "OpenLigaDB", "NOT_CONFIGURED",
                       [], reason=f"No OpenLigaDB mapping for {cid}")

    season = str(fixture.get("season") or "2025")
    try:
        r = httpx.get(
            f"https://api.openligadb.de/getbltable/{league}/{season}",
            timeout=timeout,
        )
        r.raise_for_status()
        rows = r.json() or []
    except Exception as exc:
        return _record(fixture, "openligadb", "OpenLigaDB", "FAILED",
                       [], reason=str(exc))

    if not isinstance(rows, list) or not rows:
        return _record(fixture, "openligadb", "OpenLigaDB", "INSUFFICIENT_EVIDENCE",
                       [], reason="No table data")

    home = fixture.get("home_team") or ""
    away = fixture.get("away_team") or ""
    out_teams = []

    for side, name in (("home", home), ("away", away)):
        if not name:
            continue
        for row in rows:
            if _names_match(name, row.get("teamName") or "") or \
               _names_match(name, row.get("shortName") or ""):
                out_teams.append({
                    "side": side,
                    "team_name": row.get("teamName"),
                    "standings_position": row.get("tableRank"),
                    "standings_points": row.get("points"),
                    "standings_played": row.get("matches"),
                    "standings_wins": row.get("wins"),
                    "standings_draws": row.get("draws"),
                    "standings_losses": row.get("losses"),
                    "standings_goals_for": row.get("goals"),
                    "standings_goals_against": row.get("opponentGoals"),
                    "standings_goal_difference": row.get("goalDiff"),
                })
                break

    if not out_teams:
        return _record(fixture, "openligadb", "OpenLigaDB", "INSUFFICIENT_EVIDENCE",
                       ["standings"], reason="Neither team found in table")

    return _record(
        fixture, "openligadb", "OpenLigaDB", "VERIFIED",
        ["standings", "teams"],
        evidence={"teams": out_teams, "league": league},
        source_reference=f"https://api.openligadb.de/getbltable/{league}/{season}",
    )


# ---------- FKF (footballkenya.org) ----------

def fetch_fkf(fixture, *, timeout=8.0):
    cid = (fixture.get("competition_id") or "").strip().lower()
    comp = (fixture.get("competition") or "").lower()
    if "ken" not in cid and "kenya" not in comp and "fkf" not in comp:
        return _record(fixture, "fkf_official", "Football Kenya Federation",
                       "NOT_CONFIGURED", [],
                       reason="Not a Kenyan competition")

    try:
        r = httpx.get(
            "https://footballkenya.org/",
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (Linux; Android) FootballAI/1.5"},
            follow_redirects=True,
        )
        r.raise_for_status()
        body = r.text or ""
    except Exception as exc:
        return _record(fixture, "fkf_official", "Football Kenya Federation",
                       "FAILED", [], reason=str(exc))

    home = (fixture.get("home_team") or "").strip()
    away = (fixture.get("away_team") or "").strip()
    low = body.lower()
    if home and away and home.lower() in low and away.lower() in low:
        return _record(
            fixture, "fkf_official", "Football Kenya Federation", "VERIFIED",
            ["fixtures", "competition_data"],
            evidence={"page_length": len(body), "home_seen": True, "away_seen": True},
            source_reference="https://footballkenya.org/",
        )
    return _record(fixture, "fkf_official", "Football Kenya Federation",
                   "INSUFFICIENT_EVIDENCE", ["fixtures"],
                   reason="Neither/both teams not found on FKF front page")




# ---------- TheSportsDB recent form ----------

def fetch_tsdb_recent_form(fixture, *, timeout=8.0):
    """Fetch last 5 matches for each team from TheSportsDB.

    Gives real form data for Q3, Q15, Q30.
    """
    home = fixture.get("home_team") or ""
    away = fixture.get("away_team") or ""
    out_teams = []

    for side, name in (("home", home), ("away", away)):
        if not name:
            continue
        # 1. find team id
        try:
            r = httpx.get(
                "https://www.thesportsdb.com/api/v1/json/3/searchteams.php",
                params={"t": name}, timeout=timeout,
            )
            r.raise_for_status()
            tdata = r.json() or {}
        except Exception:
            continue
        teams = tdata.get("teams") or []
        chosen = None
        for t in teams:
            if (t.get("strSport") or "").lower() == "soccer":
                chosen = t
                break
        if not chosen:
            continue
        team_id = chosen.get("idTeam")
        if not team_id:
            continue

        # 2. get last 5 events
        try:
            r = httpx.get(
                "https://www.thesportsdb.com/api/v1/json/3/eventslast.php",
                params={"id": team_id}, timeout=timeout,
            )
            r.raise_for_status()
            edata = r.json() or {}
        except Exception:
            continue

        events = edata.get("results") or []
        form = []
        for ev in events[:5]:
            home_ev = ev.get("strHomeTeam") or ""
            away_ev = ev.get("strAwayTeam") or ""
            hs = ev.get("intHomeScore")
            as_ = ev.get("intAwayScore")
            if hs is None or as_ is None:
                continue
            try:
                hs = int(hs); as_ = int(as_)
            except (ValueError, TypeError):
                continue
            is_home = _names_match(name, home_ev)
            if is_home:
                if hs > as_: form.append("W")
                elif hs < as_: form.append("L")
                else: form.append("D")
            else:
                if as_ > hs: form.append("W")
                elif as_ < hs: form.append("L")
                else: form.append("D")

        if form:
            out_teams.append({
                "side": side,
                "team_name": name,
                "recent_form": "".join(form),
                "matches_analysed": len(form),
                "team_id": team_id,
            })

    if not out_teams:
        return _record(
            fixture, "thesportsdb_form", "TheSportsDB Recent Form",
            "INSUFFICIENT_EVIDENCE", ["results"],
            reason="No recent form data found for either team",
        )

    return _record(
        fixture, "thesportsdb_form", "TheSportsDB Recent Form", "VERIFIED",
        ["results"],
        evidence={"teams": out_teams},
        source_reference="https://www.thesportsdb.com/api/v1/json/3/eventslast.php",
    )


ALL_INTERNET_FETCHERS = {
    "thesportsdb": fetch_thesportsdb,
    "wikidata": fetch_wikidata,
    "openligadb": fetch_openligadb,
    "fkf_official": fetch_fkf,
    "thesportsdb_form": fetch_tsdb_recent_form,
}
