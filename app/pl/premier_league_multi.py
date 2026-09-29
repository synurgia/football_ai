"""Premier League — reads from the worldwide registry, not just ESPN."""

from __future__ import annotations
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from app.pl.premier_league import (
    find_matchdays, fetch_matches_for, verdict_for,
)


PL_NAME_HINTS = {"premier league", "english premier league", "epl"}


def _is_pl(tournament: str, source: str) -> bool:
    if not tournament:
        return False
    if source == "espn" and tournament == "eng.1":
        return True
    low = tournament.lower()
    return any(h in low for h in PL_NAME_HINTS)


def fetch_worldwide_pl() -> List[Dict[str, Any]]:
    try:
        from app.sources.worldwide import scan_worldwide
        result = scan_worldwide()
    except Exception:
        return []

    out = []
    for m in result.get("matches", []):
        tour = m.get("tournament") or ""
        src = (m.get("sources") or ["?"])[0] if m.get("sources") else "?"
        if not _is_pl(tour, src):
            continue
        out.append({
            "match_id": f"ww-{hash((m['home_team'], m['away_team']))}",
            "home_team": m["home_team"],
            "away_team": m["away_team"],
            "kickoff_at": m.get("kickoff_at") or "",
            "status": "scheduled",
            "source": src,
            "raw": {},
        })
    return out


def build_multi_report(for_date: Optional[str] = None) -> Dict[str, Any]:
    md = find_matchdays()
    today = md["today"]

    if md["has_matchday_today"] and not for_date:
        ww = fetch_worldwide_pl()
        if ww:
            matches, target, mode = ww, today, "today_worldwide"
        else:
            matches, target, mode = fetch_matches_for(today), today, "today_espn"
    elif for_date:
        matches, target, mode = fetch_matches_for(for_date), for_date, "explicit"
    else:
        target = md["next_matchday"]
        matches = fetch_matches_for(target) if target else []
        mode = "next_matchday_espn"

    out = []
    for m in matches:
        v = verdict_for(m)
        out.append({
            "match_id": m["match_id"],
            "home_team": m["home_team"],
            "away_team": m["away_team"],
            "kickoff_at": m["kickoff_at"],
            "source": m.get("source"),
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
    print(json.dumps(build_multi_report(), indent=2))
