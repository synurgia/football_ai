"""Worldwide daily scanner — writes matches + verdicts to DB.

Flow:
  1. Query all registered sources in parallel
  2. Merge + dedupe
  3. Resolve competition_id via V1.3 identity resolver
  4. Preserve raw payload for reasoning
  5. Compute verdict (HOME/DRAW/AWAY/HELD) via app.verdicts.universal
  6. Write both to `matches` and `match_outcomes`
"""

from __future__ import annotations
import json
import re
import sqlite3
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

DB = "data/football_daily.db"

_STOP = {"fc", "sc", "ac", "cf", "afc", "the", "of", "and", "de", "club"}


def _tokens(name: str) -> set:
    if not name:
        return set()
    s = str(name).lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return {w for w in s.split() if w and w not in _STOP}


def _ensure_tables():
    conn = sqlite3.connect(DB)
    # matches
    conn.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id       TEXT PRIMARY KEY,
            match_date     TEXT,
            day_role       TEXT,
            competition    TEXT,
            competition_id TEXT,
            season         TEXT,
            home_team      TEXT,
            away_team      TEXT,
            kickoff_at     TEXT,
            status         TEXT,
            source         TEXT,
            source_match_id TEXT,
            payload        TEXT,
            first_seen_at  TEXT,
            last_seen_at   TEXT
        )
    """)
    # match_outcomes
    conn.execute("""
        CREATE TABLE IF NOT EXISTS match_outcomes (
            match_id     TEXT PRIMARY KEY,
            match_date   TEXT,
            competition  TEXT,
            home_team    TEXT,
            away_team    TEXT,
            kickoff_at   TEXT,
            verdict      TEXT,
            asserted     INTEGER,
            confidence   TEXT,
            source       TEXT,
            outcome_json TEXT,
            created_at   TEXT
        )
    """)
    # Ensure matches has the columns we need
    cols = {r[1] for r in conn.execute("PRAGMA table_info(matches)")}
    for col, typ in (("competition_id", "TEXT"), ("payload", "TEXT"), ("venue", "TEXT")):
        if col not in cols:
            conn.execute(f"ALTER TABLE matches ADD COLUMN {col} {typ}")
    conn.commit()
    conn.close()


def _resolve_competition(tournament_name: str) -> Optional[str]:
    if not tournament_name:
        return None
    try:
        from app.data_registry.v13_competition_identity_resolver import (
            V13CompetitionIdentityResolver,
        )
        r = V13CompetitionIdentityResolver().resolve(tournament_name.strip())
        return r.get("competition_id")
    except Exception:
        return None


def _extract_venue(source, raw):
    """Pull venue from any source's payload shape. Returns '' if unknown."""
    if not isinstance(raw, dict):
        return ""
    s = (source or "").lower()

    # TheSportsDB
    if "thesportsdb" in s:
        return str(raw.get("strVenue") or "").strip()

    # ESPN — venue lives at raw.competitions[0].venue (fullest data)
    # fallback to raw.venue.displayName
    if "espn" in s:
        # Try nested path first (has fullName + address)
        comps = raw.get("competitions") or []
        if comps and isinstance(comps[0], dict):
            v = comps[0].get("venue")
            if isinstance(v, dict):
                name = v.get("fullName") or v.get("displayName") or v.get("name") or ""
                if name:
                    return str(name).strip()
        # Fallback to top-level
        v = raw.get("venue")
        if isinstance(v, dict):
            name = v.get("fullName") or v.get("displayName") or v.get("name") or ""
            return str(name).strip()
        return ""

    # LiveScore — venue absent in the free events feed
    if "livescore" in s:
        return ""

    return ""



def _make_match_id(date_str, home, away, source) -> str:
    base = f"{date_str}-{home}-{away}".lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return f"{base}-{source}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def scan_today(write_to_db: bool = True) -> Dict[str, Any]:
    date_str = date.today().isoformat()

    try:
        from app.sources.worldwide import scan_worldwide
        result = scan_worldwide()
    except Exception as exc:
        return {
            "date": date_str,
            "source_status": [{"source": "worldwide", "status": "FAILED",
                               "count": 0, "error": str(exc)}],
            "total_unique": 0,
            "written_to_db": 0,
            "verdicts_written": 0,
            "verdict_counts": {"HOME": 0, "DRAW": 0, "AWAY": 0, "HELD": 0},
            "sample": [],
        }

    merged = result.get("matches", [])
    source_status = result.get("source_status", [])

    # Annotate + resolve competition
    for m in merged:
        m["_source"] = ",".join(m.get("sources") or ["unknown"])
        cid = _resolve_competition(m.get("tournament") or "")
        m["competition_id"] = cid

    # --- Fetch team forms for teams that will need them ---
    try:
        from app.pipeline.team_form import fetch_forms_batch
        all_teams = set()
        for m in merged:
            h = m.get("home_team") or ""
            a = m.get("away_team") or ""
            if h: all_teams.add(h)
            if a: all_teams.add(a)
        if all_teams:
            print(f"  fetching team form for {len(all_teams)} teams...", flush=True)
            fetch_forms_batch(list(all_teams), max_workers=4, timeout=8.0)
    except Exception as exc:
        print(f"  team_form prefetch failed: {exc}", flush=True)

    # Compute verdicts — with cross-source join
    from collections import defaultdict
    from app.verdicts.universal import compute_verdict

    # Group by team-pair tokens so we can offer each match its siblings
    groups = defaultdict(list)
    for m in merged:
        key = (
            frozenset(_tokens(m.get("home_team") or "")),
            frozenset(_tokens(m.get("away_team") or "")),
        )
        if key[0] and key[1]:
            groups[key].append(m)

    verdict_counts = {"HOME": 0, "DRAW": 0, "AWAY": 0, "HELD": 0}
    sibling_rescues = 0

    for m in merged:
        key = (
            frozenset(_tokens(m.get("home_team") or "")),
            frozenset(_tokens(m.get("away_team") or "")),
        )
        siblings = [g for g in groups.get(key, []) if g is not m]

        v = compute_verdict(
            {
                "home_team": m.get("home_team") or "",
                "away_team": m.get("away_team") or "",
                "competition_id": m.get("competition_id"),
                "kickoff_at": m.get("kickoff_at") or "",
                "source": m.get("_source") or "",
                "raw": m.get("raw") or {},
            },
            siblings=[
                {
                    "source": s.get("_source") or "",
                    "raw": s.get("raw") or {},
                }
                for s in siblings
            ],
        )
        m["_verdict"] = v
        verdict_counts[v["verdict"]] = verdict_counts.get(v["verdict"], 0) + 1
        if "_VIA_" in str(v.get("method") or ""):
            sibling_rescues += 1

    written = 0
    verdicts_written = 0
    if write_to_db:
        _ensure_tables()
        now = _now_iso()
        conn = sqlite3.connect(DB)
        try:
            for m in merged:
                home = m.get("home_team") or ""
                away = m.get("away_team") or ""
                kickoff = m.get("kickoff_at") or ""
                source = m.get("_source") or "unknown"
                comp_display = m.get("tournament") or m.get("competition") or ""
                comp_id = m.get("competition_id")
                mid = _make_match_id(date_str, home, away, source)

                # Full payload — includes everything we have
                payload = json.dumps({
                    "tournament": m.get("tournament"),
                    "tournament_id": m.get("tournament_id"),
                    "category": m.get("category") if "category" in m else None,
                    "raw": m.get("raw") or {},
                })

                venue = _extract_venue(source, m.get("raw") or {})

                conn.execute("""
                    INSERT INTO matches
                    (match_id, match_date, day_role, competition, competition_id,
                     season, home_team, away_team, kickoff_at, status,
                     source, source_match_id, payload, venue,
                     first_seen_at, last_seen_at)
                    VALUES (?, ?, 'today', ?, ?, ?, ?, ?, ?, 'scheduled',
                            ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(match_id) DO UPDATE SET
                        last_seen_at = excluded.last_seen_at,
                        kickoff_at   = excluded.kickoff_at,
                        competition  = excluded.competition,
                        competition_id = COALESCE(excluded.competition_id, matches.competition_id),
                        payload      = excluded.payload,
                        venue        = COALESCE(excluded.venue, matches.venue)
                """, (
                    mid, date_str, comp_display, comp_id,
                    date.today().year, home, away, kickoff,
                    source, "", payload, venue,
                    now, now,
                ))
                written += 1

                # Verdict row
                v = m.get("_verdict") or {}
                conn.execute("""
                    INSERT OR REPLACE INTO match_outcomes
                    (match_id, match_date, competition, home_team, away_team,
                     kickoff_at, verdict, asserted, confidence, source,
                     outcome_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    mid, date_str, comp_display, home, away,
                    kickoff,
                    v.get("verdict", "HELD"),
                    1 if v.get("asserted") else 0,
                    v.get("confidence"),
                    v.get("method"),
                    json.dumps(v),
                    now,
                ))
                verdicts_written += 1

            conn.commit()
        finally:
            conn.close()

    return {
        "date": date_str,
        "source_status": source_status,
        "total_unique": len(merged),
        "written_to_db": written,
        "verdicts_written": verdicts_written,
        "verdict_counts": verdict_counts,
        "sibling_rescues": sibling_rescues,
        "sample": merged[:5],
    }


if __name__ == "__main__":
    r = scan_today()
    print(f"Date:              {r['date']}")
    print(f"Matches found:     {r['total_unique']}")
    print(f"Matches written:   {r['written_to_db']}")
    print(f"Verdicts written:  {r['verdicts_written']}")
    print(f"Verdict counts:    {r['verdict_counts']}")
    print()
    print("Per source:")
    for s in r["source_status"]:
        err = f"  err={str(s.get('error'))[:50]}" if s.get("error") else ""
        print(f"  {s['source']:<14} {s['status']:<8} {s['count']:>4}{err}")
