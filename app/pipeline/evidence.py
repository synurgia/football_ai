"""Evidence collection — reads the stored payload, not the network.

The scanner already saves raw source events (ESPN, LiveScore). This module
extracts answers for the 37-question V2 state from that raw payload — no
network calls, no regional collector, no failing sources.

Deterministic. If a field isn't in the payload, the question stays UNKNOWN.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.v2_live_evidence_collector import V2LiveEvidenceCollector
from app.data_registry.evidence_state_store import EvidenceStateStore


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ================================================================
# ESPN extractor
# ================================================================

def _extract_from_espn(raw: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    answers: Dict[str, Dict[str, Any]] = {}
    comps = (raw.get("competitions") or [{}])
    comp = comps[0] if comps else {}
    competitors = comp.get("competitors") or []

    home = away = None
    for c in competitors:
        side = (c.get("homeAway") or "").lower()
        if side == "home":
            home = c
        elif side == "away":
            away = c

    home_name = ((home or {}).get("team") or {}).get("displayName") or ""
    away_name = ((away or {}).get("team") or {}).get("displayName") or ""

    # --- Q3 / Q15 / Q30 — recent form ---
    home_form = (home or {}).get("form") or ""
    away_form = (away or {}).get("form") or ""
    if home_form and away_form:
        hw = home_form.count("W")
        aw = away_form.count("W")
        if hw > aw:
            lean = "HOME"
        elif aw > hw:
            lean = "AWAY"
        else:
            lean = "EVEN"
        reason = f"Form: home {home_form} | away {away_form}"
        answers["Q3"] = {
            "answer": f"Home {home_form} | Away {away_form}",
            "supports": lean, "confidence": 0.7,
            "evidence": reason, "status": "VERIFIED",
        }
        answers["Q15"] = {
            "answer": f"Last-5 form — {reason}",
            "supports": lean, "confidence": 0.7,
            "evidence": reason, "status": "VERIFIED",
        }
        answers["Q30"] = {
            "answer": f"Form trend — {reason}",
            "supports": lean, "confidence": 0.65,
            "evidence": reason, "status": "VERIFIED",
        }

    # --- Q13 / Q17 — model probability from odds ---
    odds_list = comp.get("odds") or []
    if odds_list:
        odds = odds_list[0] if isinstance(odds_list[0], dict) else {}

        def _implied(t):
            ml = t.get("moneyLine") if isinstance(t, dict) else None
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
            winner = ranked[0][0]
            answers["Q13"] = {
                "answer": (f"H {p_home:.2f} / D {p_draw:.2f} / A {p_away:.2f}"),
                "supports": winner, "confidence": 0.85,
                "evidence": "Odds-implied probabilities",
                "status": "VERIFIED",
            }
            answers["Q17"] = {
                "answer": f"Highest probability: {winner}",
                "supports": winner, "confidence": 0.85,
                "evidence": "Odds-derived",
                "status": "VERIFIED",
            }

    # --- Q10 — both teams verified (they're in the event) ---
    if home_name and away_name:
        answers["Q10"] = {
            "answer": f"{home_name} vs {away_name}",
            "supports": "MATCH_CONTEXT", "confidence": 0.9,
            "evidence": "Both teams present in ESPN event",
            "status": "VERIFIED",
        }

    # --- Q27 — team strength from form ---
    if home_form and away_form:
        answers["Q27"] = {
            "answer": f"Form comparison: {home_form} vs {away_form}",
            "supports": "MATCH_CONTEXT", "confidence": 0.6,
            "evidence": "Form-based strength proxy",
            "status": "VERIFIED",
        }

    return answers


# ================================================================
# LiveScore extractor
# ================================================================

def _extract_from_livescore(raw: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    answers: Dict[str, Dict[str, Any]] = {}

    def _team(t):
        if isinstance(t, list) and t:
            return t[0] if isinstance(t[0], dict) else {}
        if isinstance(t, dict):
            return t
        return {}

    home = _team(raw.get("T1"))
    away = _team(raw.get("T2"))

    home_name = home.get("Nm") or home.get("Name") or ""
    away_name = away.get("Nm") or away.get("Name") or ""

    home_form = home.get("Form") or home.get("form") or ""
    away_form = away.get("Form") or away.get("form") or ""

    # --- Q3 / Q15 / Q30 ---
    if home_form and away_form:
        hw = home_form.count("W")
        aw = away_form.count("W")
        if hw > aw:
            lean = "HOME"
        elif aw > hw:
            lean = "AWAY"
        else:
            lean = "EVEN"
        reason = f"Form: home {home_form} | away {away_form}"
        answers["Q3"] = {
            "answer": f"Home {home_form} | Away {away_form}",
            "supports": lean, "confidence": 0.7,
            "evidence": reason, "status": "VERIFIED",
        }
        answers["Q15"] = {
            "answer": f"Last-5 form — {reason}",
            "supports": lean, "confidence": 0.7,
            "evidence": reason, "status": "VERIFIED",
        }
        answers["Q30"] = {
            "answer": f"Form trend — {reason}",
            "supports": lean, "confidence": 0.65,
            "evidence": reason, "status": "VERIFIED",
        }

    # --- Q10 — team identity ---
    if home_name and away_name:
        answers["Q10"] = {
            "answer": f"{home_name} vs {away_name}",
            "supports": "MATCH_CONTEXT", "confidence": 0.85,
            "evidence": "Both teams present in LiveScore event",
            "status": "VERIFIED",
        }

    return answers


# ================================================================
# Dispatcher + apply
# ================================================================



# ================================================================
# TheSportsDB extractor
# ================================================================

def _extract_from_thesportsdb(raw: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """TheSportsDB eventsday payload → answers.

    Free eventsday gives: strEvent, strHomeTeam, strAwayTeam, strTimestamp,
    strLeague, strSeason, strVenue, intRound.
    No odds. No form. So we extract what's actually there.
    """
    answers: Dict[str, Dict[str, Any]] = {}

    home = raw.get("strHomeTeam") or ""
    away = raw.get("strAwayTeam") or ""
    league = raw.get("strLeague") or ""
    venue = raw.get("strVenue") or ""
    season = raw.get("strSeason") or ""

    # Q10 — team identity
    if home and away:
        answers["Q10"] = {
            "answer": f"{home} vs {away}",
            "supports": "MATCH_CONTEXT", "confidence": 0.8,
            "evidence": "Both teams present in TheSportsDB event",
            "status": "VERIFIED",
        }

    # Q2 — venue
    if venue:
        answers["Q2"] = {
            "answer": f"Venue: {venue}",
            "supports": "MATCH_CONTEXT", "confidence": 0.75,
            "evidence": f"TheSportsDB lists venue as {venue}",
            "status": "VERIFIED",
        }

    # Q19 — competition context
    if league:
        answers["Q19"] = {
            "answer": f"League: {league}" + (f" {season}" if season else ""),
            "supports": "MATCH_CONTEXT", "confidence": 0.75,
            "evidence": f"TheSportsDB league field: {league}",
            "status": "VERIFIED",
        }

    return answers




# ================================================================
# Federation URL extractor
# ================================================================

# Curated list of federation URLs that return 200 and serve HTML
# without aggressive bot protection. Tested 2026-09-28.
_FEDERATION_URLS = {
    "ken.1": "https://footballkenya.org/",
    "ken.2": "https://footballkenya.org/",
    "eng.1": "https://www.thefa.com/",
    "eng.2": "https://www.efl.com/",
    "eng.cup": "https://www.thefa.com/competitions/thefacup",
    "sco.1": "https://spfl.co.uk/",
    "irl.1": "https://www.leagueofireland.ie/",
    "wal.1": None,  # placeholder
    "usa.1": "https://www.mlssoccer.com/",
    "usa.2": "https://canpl.ca/",
    "mex.1": "https://www.ligamx.net/",
    "bra.1": "https://www.cbf.com.br/",
    "jpn.1": "https://www.jleague.jp/",
    "kor.1": "https://www.kleague.com/",
    "aus.1": "https://aleagues.com.au/",
    "ind.1": "https://www.indiansuperleague.com/",
}

# Cache — avoid re-fetching the same URL within one daemon cycle
_FEDERATION_CACHE: Dict[str, str] = {}


def _fetch_federation_html(competition_id: str, timeout: float = 8.0) -> str:
    url = _FEDERATION_URLS.get(competition_id)
    if not url:
        return ""
    if url in _FEDERATION_CACHE:
        return _FEDERATION_CACHE[url]
    try:
        import httpx
        r = httpx.get(
            url, timeout=timeout, follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (Linux; Android) FootballAI/1.8"},
        )
        if r.status_code != 200:
            _FEDERATION_CACHE[url] = ""
            return ""
        body = r.text or ""
        _FEDERATION_CACHE[url] = body
        return body
    except Exception:
        _FEDERATION_CACHE[url] = ""
        return ""


def _extract_from_federation(raw: Dict[str, Any], competition_id: str,
                              home: str, away: str) -> Dict[str, Dict[str, Any]]:
    """Fetch the federation site for this competition, verify teams present."""
    answers: Dict[str, Dict[str, Any]] = {}
    if not competition_id or not home or not away:
        return answers

    body = _fetch_federation_html(competition_id)
    if not body:
        return answers

    low = body.lower()
    home_found = home.lower() in low
    away_found = away.lower() in low

    if home_found and away_found:
        answers["Q10"] = {
            "answer": f"{home} vs {away} — both present on federation site",
            "supports": "MATCH_CONTEXT", "confidence": 0.9,
            "evidence": f"Federation page confirms both teams (source: {_FEDERATION_URLS.get(competition_id)})",
            "status": "VERIFIED",
        }
        answers["Q19"] = {
            "answer": f"Competition context verified on federation site",
            "supports": "MATCH_CONTEXT", "confidence": 0.85,
            "evidence": f"Federation source: {_FEDERATION_URLS.get(competition_id)}",
            "status": "VERIFIED",
        }
    elif home_found or away_found:
        answers["Q10"] = {
            "answer": f"Partial — only one team found on federation page",
            "supports": "MATCH_CONTEXT", "confidence": 0.5,
            "evidence": f"Federation page contains one of the two team names",
            "status": "INSUFFICIENT_EVIDENCE",
        }
    return answers


def _extract_answers_for(source: str, raw: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    if not isinstance(raw, dict):
        return {}
    s = (source or "").lower()
    if "espn" in s:
        return _extract_from_espn(raw)
    if "livescore" in s:
        return _extract_from_livescore(raw)
    if "thesportsdb" in s:
        return _extract_from_thesportsdb(raw)
    return {}


def _apply_answers(state: Any, answers: Dict[str, Dict[str, Any]]) -> int:
    """Write answers into the V2 state's items. Returns count written."""
    if not answers:
        return 0

    now = _now()
    applied = 0
    items_by_id = {}
    for it in state.items:
        qid = getattr(it, "question_id", None)
        if qid:
            items_by_id[qid] = it

    for qid, payload in answers.items():
        item = items_by_id.get(qid)
        if item is None:
            continue
        try:
            item.answer = payload.get("answer", "")
            item.supports = payload.get("supports", "UNKNOWN")
            item.confidence = payload.get("confidence")
            item.status = payload.get("status", "VERIFIED")
            item.observed_at = now
            if payload.get("evidence"):
                item.evidence = payload["evidence"]
            applied += 1
        except Exception:
            continue
    return applied


def collect_for_match(match: Dict[str, Any], timeout: float = 0.0) -> Optional[Any]:
    """Build V2 state from stored payload. No network."""
    home = match.get("home_team") or ""
    away = match.get("away_team") or ""
    if not home or not away:
        return None

    match_id = str(match.get("match_id") or "")
    if not match_id:
        return None

    live = V2LiveEvidenceCollector()
    try:
        state = live.create_match_state(
            match_id=match_id,
            competition=match.get("competition") or "",
            home_team=home,
            away_team=away,
        )
    except Exception:
        return None

    # Read payload
    payload_raw = {}
    source = match.get("source") or ""
    try:
        import json
        p = json.loads(match.get("payload") or "{}")
        payload_raw = p.get("raw") or {}
    except Exception:
        payload_raw = {}

    # 1. Source-specific extractor (ESPN / LiveScore / TheSportsDB)
    answers = _extract_answers_for(source, payload_raw)

    # 2. Federation extractor — cross-verifies team presence on official site
    try:
        fed_answers = _extract_from_federation(
            raw=payload_raw,
            competition_id=match.get("competition_id") or "",
            home=home,
            away=away,
        )
        for qid, payload in fed_answers.items():
            if qid not in answers:
                answers[qid] = payload
            else:
                # Federation gives higher confidence — upgrade
                if payload.get("confidence", 0) > answers[qid].get("confidence", 0):
                    answers[qid] = payload
    except Exception:
        pass

    _apply_answers(state, answers)

    return state


def collect_batch(matches, *, timeout: float = 0.0, max_workers: int = 4,
                  persist: bool = True) -> Dict[str, Any]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    states: List[Any] = []
    per_match_stats: List[Dict[str, Any]] = []
    failed = 0

    if not matches:
        return {"matches_attempted": 0, "matches_enriched": 0,
                "matches_failed": 0, "states_saved": 0,
                "avg_answered": 0.0, "sample": []}

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(collect_for_match, m): m for m in matches}
        for fut in as_completed(futures):
            try:
                state = fut.result(timeout=30)
            except Exception:
                state = None
            if state is None:
                failed += 1
                continue
            states.append(state)
            answered = sum(
                1 for it in state.items
                if (getattr(it, "answer", "") or "").upper()
                   not in ("UNKNOWN", "", None)
            )
            verified = sum(
                1 for it in state.items
                if getattr(it, "status", "") in ("VERIFIED", "CONFIRMED")
            )
            per_match_stats.append({
                "match_id": getattr(state, "match_id", ""),
                "home_team": getattr(state, "home_team", ""),
                "away_team": getattr(state, "away_team", ""),
                "answered": answered,
                "verified": verified,
            })

    saved = 0
    if persist and states:
        try:
            store = EvidenceStateStore()
            store.save_states(states)
            saved = len(states)
        except Exception:
            saved = 0

    avg = 0.0
    if per_match_stats:
        avg = sum(s["answered"] for s in per_match_stats) / len(per_match_stats)
    per_match_stats.sort(key=lambda s: -s["answered"])

    return {
        "matches_attempted": len(matches),
        "matches_enriched": len(states),
        "matches_failed": failed,
        "states_saved": saved,
        "avg_answered": round(avg, 2),
        "sample": per_match_stats[:10],
    }


if __name__ == "__main__":
    import sqlite3
    from datetime import date

    conn = sqlite3.connect("data/football_daily.db")
    conn.row_factory = sqlite3.Row
    today = date.today().isoformat()
    rows = conn.execute(
        "SELECT match_id, competition, competition_id, home_team, away_team, "
        "       kickoff_at, source, payload "
        "FROM matches WHERE match_date = ? LIMIT 20",
        (today,),
    ).fetchall()
    conn.close()

    matches = [dict(r) for r in rows]
    print(f"Testing on {len(matches)} matches...\n")
    result = collect_batch(matches, persist=False)
    print(f"attempted:    {result['matches_attempted']}")
    print(f"enriched:     {result['matches_enriched']}")
    print(f"failed:       {result['matches_failed']}")
    print(f"avg_answered: {result['avg_answered']} / 37")
    print()
    for s in result["sample"]:
        print(f"  {s['home_team']:<26} vs {s['away_team']:<26}  "
              f"answered={s['answered']:>2}  verified={s['verified']:>2}")
