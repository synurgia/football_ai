"""Premier League — fixtures + verdicts.

Single competition. Single source (ESPN). Calendar-aware.
Finds today's matchday if it exists, otherwise reports the next matchday.
"""

from __future__ import annotations
import os
import re
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

import httpx


ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard"
APIF_KEY = os.environ.get("API_FOOTBALL_KEY", "")
APIF_URL = "https://v3.football.api-sports.io/fixtures"


def _today_iso() -> str:
    return date.today().isoformat()


# ----------------------------------------------------------------
# Calendar
# ----------------------------------------------------------------

def fetch_calendar(timeout: float = 6.0) -> List[str]:
    """Return all ESPN calendar dates (matchdays) as YYYY-MM-DD strings."""
    try:
        r = httpx.get(ESPN_URL, timeout=timeout)
        r.raise_for_status()
        data = r.json() or {}
    except Exception:
        return []

    leagues = data.get("leagues") or [{}]
    cal = leagues[0].get("calendar") or []
    return [str(d)[:10] for d in cal if d]


def find_matchdays(timeout: float = 6.0) -> Dict[str, Any]:
    """Find today's matchday or the next one after today."""
    cal = fetch_calendar(timeout=timeout)
    today = _today_iso()
    past = [d for d in cal if d < today]
    future = [d for d in cal if d >= today]

    return {
        "today": today,
        "has_matchday_today": today in cal,
        "next_matchday": future[0] if future else None,
        "last_matchday": past[-1] if past else None,
        "all_upcoming": future[:5],
    }


# ----------------------------------------------------------------
# Fetch matches for a specific date
# ----------------------------------------------------------------

def fetch_matches_for(date_iso: str, timeout: float = 6.0) -> List[Dict[str, Any]]:
    """Fetch ESPN matches for a specific YYYY-MM-DD date."""
    yyyymmdd = date_iso.replace("-", "")
    try:
        r = httpx.get(ESPN_URL, params={"dates": yyyymmdd}, timeout=timeout)
        r.raise_for_status()
        data = r.json() or {}
    except Exception:
        return []

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
        out.append({
            "match_id": str(ev.get("id") or ""),
            "home_team": home,
            "away_team": away,
            "kickoff_at": ev.get("date") or "",
            "status": ((ev.get("status") or {}).get("type") or {}).get("state") or "scheduled",
            "source": "espn",
            "raw": ev,
        })
    return out


def fetch_from_apif(date_iso: str, timeout: float = 8.0) -> List[Dict[str, Any]]:
    if not APIF_KEY:
        return []
    try:
        r = httpx.get(
            APIF_URL,
            params={"date": date_iso, "league": 39, "season": date.today().year},
            headers={"x-apisports-key": APIF_KEY},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json() or {}
    except Exception:
        return []

    out = []
    for f in data.get("response", []) or []:
        teams = f.get("teams") or {}
        home = (teams.get("home") or {}).get("name") or ""
        away = (teams.get("away") or {}).get("name") or ""
        if not home or not away:
            continue
        out.append({
            "match_id": str((f.get("fixture") or {}).get("id") or ""),
            "home_team": home,
            "away_team": away,
            "kickoff_at": (f.get("fixture") or {}).get("date") or "",
            "status": ((f.get("fixture") or {}).get("status") or {}).get("short") or "NS",
            "source": "apif",
            "raw": f,
        })
    return out


def fetch_for_date(date_iso: str) -> List[Dict[str, Any]]:
    """Merge ESPN + APIF for a date, deduped."""
    espn = fetch_matches_for(date_iso)
    apif = fetch_from_apif(date_iso)

    seen = set()
    out = []
    for m in espn + apif:
        key = (m["home_team"].lower(), m["away_team"].lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(m)
    out.sort(key=lambda m: m.get("kickoff_at") or "")
    return out


# ----------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------

def verdict_for(match: Dict[str, Any]) -> Dict[str, Any]:
    raw = match.get("raw") or {}
    comp = ((raw.get("competitions") or [{}])[0]) if raw.get("competitions") else {}

    # Odds
    odds_list = comp.get("odds") or []
    if odds_list:
        odds = odds_list[0] if isinstance(odds_list[0], dict) else {}
        def _implied(team_odds):
            ml = team_odds.get("moneyLine")
            if isinstance(ml, (int, float)) and ml != 0:
                return 100.0/(ml+100.0) if ml > 0 else abs(ml)/(abs(ml)+100.0)
            return None

        p_home = _implied(odds.get("homeTeamOdds") or {})
        p_away = _implied(odds.get("awayTeamOdds") or {})
        p_draw = _implied(odds.get("drawOdds") or {})

        if p_home and p_away:
            if p_draw is None:
                p_draw = max(0.05, 1.0 - (p_home + p_away))
            t = p_home + p_draw + p_away
            p_home, p_draw, p_away = p_home/t, p_draw/t, p_away/t
            ranked = sorted(
                [("HOME", p_home), ("DRAW", p_draw), ("AWAY", p_away)],
                key=lambda x: -x[1],
            )
            winner, _ = ranked[0]
            gap = ranked[0][1] - ranked[1][1]
            band = "HIGH" if gap >= 0.20 else ("MODERATE" if gap >= 0.10 else "LOW")
            return {
                "verdict": winner,
                "confidence": band,
                "method": "ESPN_ODDS_IMPLIED",
                "asserted": band in ("HIGH", "MODERATE"),
                "probabilities": {
                    "HOME": round(p_home, 3),
                    "DRAW": round(p_draw, 3),
                    "AWAY": round(p_away, 3),
                },
                "reason": f"H {p_home:.2f} / D {p_draw:.2f} / A {p_away:.2f}",
            }

    # Form
    forms = {}
    for c in comp.get("competitors") or []:
        side, form = c.get("homeAway"), c.get("form") or ""
        if side and form:
            forms[side] = form
    if "home" in forms and "away" in forms:
        hf, af = forms["home"], forms["away"]
        hw, aw = hf.count("W"), af.count("W")
        winner = "HOME" if hw > aw else ("AWAY" if aw > hw else "DRAW")
        return {
            "verdict": winner,
            "confidence": "LOW",
            "method": "RECENT_FORM_LEAN",
            "asserted": False,
            "reason": f"Form: home {hf} | away {af}",
        }

    return {
        "verdict": "HELD",
        "confidence": None,
        "method": "NONE",
        "asserted": False,
        "reason": "No odds and no recent form.",
    }


# ----------------------------------------------------------------
# Report
# ----------------------------------------------------------------

def build_report(for_date: Optional[str] = None) -> Dict[str, Any]:
    """Build PL report. If for_date is None, use today (or next matchday)."""
    md = find_matchdays()

    if for_date:
        target = for_date
        mode = "explicit"
    elif md["has_matchday_today"]:
        target = md["today"]
        mode = "today"
    elif md["next_matchday"]:
        target = md["next_matchday"]
        mode = "next_matchday"
    else:
        return {
            "competition": "eng.1",
            "name": "Premier League",
            "date": md["today"],
            "mode": "no_matchday",
            "total": 0,
            "counts": {"HOME": 0, "DRAW": 0, "AWAY": 0, "HELD": 0},
            "matches": [],
            "calendar": md,
        }

    matches = fetch_for_date(target)
    out = []
    for m in matches:
        v = verdict_for(m)
        out.append({
            "match_id": m["match_id"],
            "home_team": m["home_team"],
            "away_team": m["away_team"],
            "kickoff_at": m["kickoff_at"],
            "status": m["status"],
            "source": m["source"],
            "verdict": v["verdict"],
            "confidence": v.get("confidence"),
            "asserted": v.get("asserted", False),
            "method": v.get("method"),
            "reason": v.get("reason"),
            "probabilities": v.get("probabilities"),
        })

    counts = {"HOME": 0, "DRAW": 0, "AWAY": 0, "HELD": 0}
    for m in out:
        counts[m["verdict"]] = counts.get(m["verdict"], 0) + 1

    return {
        "competition": "eng.1",
        "name": "Premier League",
        "date": target,
        "mode": mode,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(out),
        "counts": counts,
        "matches": out,
        "calendar": md,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_report(), indent=2))
