"""Team form fetcher with cache — uses ESPN's public team schedule.

For each team name:
  1. Check team_form_cache (24h TTL)
  2. On miss: search ESPN for the team → get ID
  3. Fetch last 25 events → filter finished → extract W/L/D string
  4. Cache result

Returns "WWLDL" (5-char) or "" if unavailable. No fabrication.
"""

from __future__ import annotations
import json
import re
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

import httpx

DB = "data/football_daily.db"
CACHE_HOURS = 24
ESPN_SEARCH = "https://site.api.espn.com/apis/common/v3/search"
ESPN_SCHEDULE = "https://site.api.espn.com/apis/site/v2/sports/soccer/all/teams/{tid}/schedule"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13) FootballAI/1.9",
    "Accept": "application/json",
}


def _ensure_cache():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS team_form_cache (
            team_key     TEXT PRIMARY KEY,
            team_name    TEXT,
            form_string  TEXT,
            espn_team_id TEXT,
            matches_json TEXT,
            fetched_at   TEXT
        )
    """)
    conn.commit()
    conn.close()


def _canonical(name: str) -> str:
    if not name:
        return ""
    s = str(name).lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return " ".join(s.split())


def _cache_get(team_name: str) -> Optional[str]:
    key = _canonical(team_name)
    if not key:
        return None
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT form_string, fetched_at FROM team_form_cache WHERE team_key = ?",
            (key,),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        return None
    try:
        ts = datetime.fromisoformat(row["fetched_at"].replace("Z", "+00:00"))
        if datetime.now(timezone.utc) - ts > timedelta(hours=CACHE_HOURS):
            return None
    except Exception:
        pass
    # Treat empty string as a miss — never cache a failure as success
    if not row["form_string"]:
        return None
    return row["form_string"]


def _cache_put(team_name: str, form: str, tid: str, matches: List[Dict]) -> None:
    key = _canonical(team_name)
    if not key:
        return
    conn = sqlite3.connect(DB)
    try:
        conn.execute(
            "INSERT OR REPLACE INTO team_form_cache "
            "(team_key, team_name, form_string, espn_team_id, matches_json, fetched_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                key, team_name, form, tid,
                json.dumps(matches[:10], default=str),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def _search_team_id(name: str, timeout: float = 6.0) -> Optional[str]:
    """Search ESPN for a soccer team. Returns team ID or None."""
    try:
        r = httpx.get(
            ESPN_SEARCH,
            params={"query": name, "limit": 5, "type": "team", "sport": "soccer"},
            headers=HEADERS,
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json() or {}
    except Exception:
        return None

    results = data.get("results") or data.get("items") or []
    target = _canonical(name)

    # Prefer exact name match
    for item in results:
        display = _canonical(item.get("displayName") or item.get("name") or "")
        sport = (item.get("sport") or "").lower()
        if sport != "soccer":
            continue
        if display == target:
            return str(item.get("id") or "")

    # Fallback: first soccer result
    for item in results:
        if (item.get("sport") or "").lower() == "soccer":
            return str(item.get("id") or "")
    return None


def _parse_schedule_events(data: Dict[str, Any], team_id: str) -> List[Dict[str, Any]]:
    """Return finished events for this team, most recent first."""
    events = data.get("events") or []
    finished = []
    for ev in events:
        comps = ev.get("competitions") or []
        if not comps:
            continue
        comp = comps[0]
        comps_teams = comp.get("competitors") or []

        # Find this team's competitor + opponent
        this_side = opponent = None
        for c in comps_teams:
            cid = str((c.get("team") or {}).get("id") or c.get("id") or "")
            if cid == team_id:
                this_side = c
            else:
                opponent = c
        if not this_side:
            continue

        score = this_side.get("score") or {}
        # Only count finished matches (winner flag set, value present)
        if score.get("value") is None:
            continue

        opponent_name = ((opponent or {}).get("team") or {}).get("displayName") or ""
        home_away = (this_side.get("homeAway") or "").lower()

        winner = score.get("winner")
        if winner is True:
            result = "W"
        elif winner is False:
            # Need to check if opponent won or it was a draw
            opp_score = (opponent or {}).get("score") or {}
            if opp_score.get("value") == score.get("value"):
                result = "D"
            else:
                result = "L"
        else:
            result = None

        if result is None:
            continue

        finished.append({
            "date": ev.get("date") or "",
            "result": result,
            "home_away": home_away,
            "opponent": opponent_name,
            "team_score": score.get("value"),
            "opp_score": ((opponent or {}).get("score") or {}).get("value"),
        })

    # Take last 5 finished matches (no date filter), tag each with days_ago
    from datetime import date as _date, datetime as _dt
    today = _date.today()
    tagged = []
    for f in finished:
        d = (f.get("date") or "")[:10]
        if not d:
            continue
        try:
            mdate = _dt.fromisoformat(d).date()
            days = (today - mdate).days
        except Exception:
            days = None
        f["days_ago"] = days
        tagged.append(f)

    # Require at least 2 finished matches total
    if len(tagged) < 2:
        return []

    return tagged[:5]


def form_metadata(matches):
    """From a list of tagged matches, return (form_str, days_ago_list, staleness_label)."""
    if not matches:
        return "", [], "unknown"
    form = "".join(m.get("result", "") for m in matches)
    days = [m.get("days_ago") for m in matches if m.get("days_ago") is not None]
    if not days:
        return form, [], "unknown"
    most_recent = min(days)
    oldest = max(days)
    if oldest <= 30:
        label = "fresh"
    elif oldest <= 90:
        label = "current"
    elif oldest <= 180:
        label = "aging"
    else:
        label = "stale"
    return form, days, label



def fetch_team_form(team_name: str, timeout: float = 8.0) -> str:
    """Fetch and cache form for one team. Returns 'WWLDL' or ''."""
    if not team_name:
        return ""

    cached = _cache_get(team_name)
    if cached is not None:
        return cached

    tid = _search_team_id(team_name, timeout=timeout)
    if not tid:
        pass  # skip caching empty
        return ""

    url = ESPN_SCHEDULE.format(tid=tid)
    try:
        r = httpx.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        data = r.json() or {}
    except Exception:
        pass  # skip caching empty
        return ""

    events = _parse_schedule_events(data, tid)
    form = "".join(e["result"] for e in events)
    _cache_put(team_name, form, tid, events)
    return form


def fetch_forms_batch(team_names: List[str], max_workers: int = 6,
                      timeout: float = 8.0) -> Dict[str, str]:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    _ensure_cache()
    out: Dict[str, str] = {}
    unique = list({t for t in team_names if t})
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(fetch_team_form, t, timeout): t for t in unique}
        for fut in as_completed(futures):
            t = futures[fut]
            try:
                out[t] = fut.result(timeout=timeout + 5)
            except Exception:
                out[t] = ""
    return out


if __name__ == "__main__":
    tests = ["Czechia", "England", "Spain", "Croatia", "Arsenal", "Papua New Guinea"]
    print(f"Fetching ESPN form for {len(tests)} teams...\n")
    t0 = time.time()
    forms = fetch_forms_batch(tests)
    print(f"Done in {time.time()-t0:.1f}s\n")
    for name, form in forms.items():
        status = form if form else "(no data)"
        print(f"  {name:<24} {status}")
