"""Universal verdict — works for any match from any source.

Priority order for a verdict:
  1. Odds (moneyline → implied probabilities) — best signal
  2. Recent form (W/L/D strings) — directional lean, low confidence
  3. HELD — honest, no fabrication

The module never invents data. If the source didn't supply odds or form,
the verdict is HELD with a clear reason. That's the honest answer.

Works inline during scan (with raw payload) and on DB rows (raw missing).
When raw is missing, verdict = HELD unless a re-fetch is requested.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional


# ================================================================
# Helpers
# ================================================================

def _team_name(obj: Any) -> str:
    """Extract team name from various source shapes."""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return (
            obj.get("displayName")
            or obj.get("name")
            or obj.get("shortDisplayName")
            or ""
        )
    return ""


def _implied_probability(ml: Any) -> Optional[float]:
    """American moneyline → implied probability (0-1)."""
    try:
        ml = float(ml)
    except (TypeError, ValueError):
        return None
    if ml == 0:
        return None
    if ml > 0:
        return 100.0 / (ml + 100.0)
    return abs(ml) / (abs(ml) + 100.0)


def _verdict_from_probs(p_home: float, p_draw: float, p_away: float) -> Dict[str, Any]:
    """Pick the most likely outcome and grade confidence by spread."""
    ranked = sorted(
        [("HOME", p_home), ("DRAW", p_draw), ("AWAY", p_away)],
        key=lambda x: -x[1],
    )
    winner = ranked[0][0]
    gap = ranked[0][1] - ranked[1][1]
    if gap >= 0.20:
        band = "HIGH"
    elif gap >= 0.10:
        band = "MODERATE"
    else:
        band = "LOW"
    return {
        "verdict": winner,
        "confidence": band,
        "asserted": band in ("HIGH", "MODERATE"),
        "probabilities": {
            "HOME": round(p_home, 3),
            "DRAW": round(p_draw, 3),
            "AWAY": round(p_away, 3),
        },
    }


def _verdict_from_form(home_form: str, away_form: str) -> Dict[str, Any]:
    """Directional lean from W/L/D strings — never asserted."""
    hw, aw = home_form.count("W"), away_form.count("W")
    if hw > aw:
        winner = "HOME"
    elif aw > hw:
        winner = "AWAY"
    else:
        winner = "DRAW"
    return {
        "verdict": winner,
        "confidence": "LOW",
        "asserted": False,
        "reason": f"Form: home {home_form} | away {away_form}",
    }


# ================================================================
# ESPN
# ================================================================

def verdict_from_espn(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """ESPN event → verdict. Odds first, then form."""
    comps = (event.get("competitions") or [{}])
    comp = comps[0] if comps else {}

    # --- Odds ---
    odds_list = comp.get("odds") or []
    if odds_list:
        odds = odds_list[0] if isinstance(odds_list[0], dict) else {}
        p_home = _implied_probability((odds.get("homeTeamOdds") or {}).get("moneyLine"))
        p_away = _implied_probability((odds.get("awayTeamOdds") or {}).get("moneyLine"))
        p_draw = _implied_probability((odds.get("drawOdds") or {}).get("moneyLine"))

        if p_home and p_away:
            if p_draw is None:
                p_draw = max(0.05, 1.0 - (p_home + p_away))
            t = p_home + p_draw + p_away
            p_home, p_draw, p_away = p_home / t, p_draw / t, p_away / t
            v = _verdict_from_probs(p_home, p_draw, p_away)
            v["method"] = "ESPN_ODDS"
            v["reason"] = f"Odds: H {p_home:.2f} / D {p_draw:.2f} / A {p_away:.2f}"
            return v

    # --- Form ---
    forms = {}
    for c in comp.get("competitors") or []:
        side = c.get("homeAway")
        form = c.get("form") or ""
        if side and form:
            forms[side] = form
    if "home" in forms and "away" in forms:
        v = _verdict_from_form(forms["home"], forms["away"])
        v["method"] = "ESPN_FORM"
        return v

    return None


# ================================================================
# LiveScore
# ================================================================

def verdict_from_livescore(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """LiveScore event → verdict. LiveScore carries form in several shapes.

    - T1/T2 may be lists or single dicts
    - Form may be 'Form', 'form', or within 'Ep' (event participants)
    - Sometimes "form" is embedded in the stage, not the event
    """
    home_form = ""
    away_form = ""

    def _extract_form(team_obj):
        if not isinstance(team_obj, dict):
            return ""
        for key in ("Form", "form", "f", "F"):
            v = team_obj.get(key)
            if isinstance(v, str) and v:
                return v
        return ""

    t1 = event.get("T1") or event.get("home_team") or event.get("homeTeam")
    t2 = event.get("T2") or event.get("away_team") or event.get("awayTeam")

    if isinstance(t1, list) and t1:
        home_form = _extract_form(t1[0])
    elif isinstance(t1, dict):
        home_form = _extract_form(t1)

    if isinstance(t2, list) and t2:
        away_form = _extract_form(t2[0])
    elif isinstance(t2, dict):
        away_form = _extract_form(t2)

    # Alternate: 'Ep' array of participants
    if not home_form or not away_form:
        ep = event.get("Ep") or []
        if isinstance(ep, list):
            for p in ep:
                if not isinstance(p, dict):
                    continue
                side = (p.get("H") or p.get("homeAway") or "").upper()
                form = _extract_form(p)
                if not form:
                    continue
                if side in ("H", "HOME", "1"):
                    home_form = form
                elif side in ("A", "AWAY", "2"):
                    away_form = form

    if home_form and away_form:
        v = _verdict_from_form(home_form, away_form)
        v["method"] = "LIVESCORE_FORM"
        return v

    # Odds shape
    odds = event.get("odds") or event.get("Odds") or {}
    if isinstance(odds, dict):
        h = odds.get("home") or odds.get("H") or odds.get("1")
        d = odds.get("draw") or odds.get("D") or odds.get("X")
        a = odds.get("away") or odds.get("A") or odds.get("2")
        try:
            p_home = 1.0 / float(h) if h else None
            p_draw = 1.0 / float(d) if d else None
            p_away = 1.0 / float(a) if a else None
        except (TypeError, ValueError):
            p_home = p_draw = p_away = None
        if p_home and p_away:
            if p_draw is None:
                p_draw = max(0.05, 1.0 - (p_home + p_away))
            t = p_home + p_draw + p_away
            v = _verdict_from_probs(p_home/t, p_draw/t, p_away/t)
            v["method"] = "LIVESCORE_ODDS"
            v["reason"] = f"Odds: H {p_home/t:.2f} / D {p_draw/t:.2f} / A {p_away/t:.2f}"
            return v

    return None


# ================================================================
# TheSportsDB
# ================================================================

def verdict_from_thesportsdb(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """TheSportsDB event → verdict. No odds, no form in the free tier."""
    return None


# ================================================================
# Dispatcher
# ================================================================

_SOURCE_DISPATCH = {
    "espn": verdict_from_espn,
    "livescore": verdict_from_livescore,
    "thesportsdb": verdict_from_thesportsdb,
}


# ================================================================
# Form-from-cache fallback (reads team_form_cache)
# ================================================================

def _load_team_form(team_name):
    """Return (form_string, staleness_label) or (None, None)."""
    if not team_name:
        return None, None
    import sqlite3, json, re
    from datetime import date as _date, datetime as _dt
    key = " ".join(str(team_name).lower().split())
    key = re.sub(r"[^a-z0-9 ]+", " ", key)
    try:
        conn = sqlite3.connect("data/football_daily.db")
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT form_string, matches_json FROM team_form_cache WHERE team_key = ? LIMIT 1",
            (key,),
        ).fetchone()
        conn.close()
    except Exception:
        return None, None
    if not row or not row["form_string"]:
        return None, None

    # Compute staleness label from stored days_ago
    label = "unknown"
    try:
        matches = json.loads(row["matches_json"] or "[]")
        days = [m.get("days_ago") for m in matches if isinstance(m, dict) and m.get("days_ago") is not None]
        if days:
            oldest = max(days)
            if oldest <= 30: label = "fresh"
            elif oldest <= 90: label = "current"
            elif oldest <= 180: label = "aging"
            else: label = "stale"
    except Exception:
        pass
    return row["form_string"], label


def _verdict_from_cached_forms(home_team, away_team):
    """Build a verdict from team_form_cache when source payload has no form."""
    hf, h_label = _load_team_form(home_team)
    af, a_label = _load_team_form(away_team)
    if not hf or not af:
        return None

    hw, aw = hf.count("W"), af.count("W")
    hd, ad = hf.count("D"), af.count("D")
    hl, al = hf.count("L"), af.count("L")

    # Score: wins*2 + draws*1
    h_score = hw * 2 + hd
    a_score = aw * 2 + ad
    diff = h_score - a_score

    if diff >= 3:
        winner = "HOME"
    elif diff <= -3:
        winner = "AWAY"
    elif abs(diff) <= 1:
        winner = "DRAW"
    else:
        winner = "HOME" if diff > 0 else "AWAY"

    # Confidence from staleness
    labels = [h_label, a_label]
    if "stale" in labels:
        band = "LOW"
    elif "aging" in labels:
        band = "LOW"
    elif "current" in labels:
        band = "MODERATE"
    else:
        band = "MODERATE"

    return {
        "verdict": winner,
        "confidence": band,
        "method": "TEAM_FORM_CACHE",
        "asserted": band == "MODERATE",
        "reason": f"Cached form: {home_team} {hf} ({h_label}) vs {away_team} {af} ({a_label})",
    }



def compute_verdict(match: Dict[str, Any], siblings: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Universal verdict for one match.

    Args:
        match: dict with at least home_team, away_team.
               Optionally: source, raw (source-specific payload).

    Returns:
        dict with keys: verdict, confidence, method, asserted, reason,
                        probabilities (when available).
    """
    home = match.get("home_team") or ""
    away = match.get("away_team") or ""
    if not home or not away:
        return {
            "verdict": "HELD",
            "confidence": None,
            "method": "NONE",
            "asserted": False,
            "reason": "Missing team name(s).",
        }

    source = (match.get("source") or "").split(",")[0].strip().lower()
    raw = match.get("raw") or {}

    # Try the source-specific extractor
    fn = _SOURCE_DISPATCH.get(source)
    if fn and isinstance(raw, dict):
        try:
            result = fn(raw)
        except Exception:
            result = None
        if result:
            result.setdefault("reason", "")
            return result

    # Cross-source fallback: if we know the competition, try ESPN
    # (opt-in via match['_try_espn'] to avoid network in Chunk 1)
    if match.get("_try_espn"):
        try:
            from app.pl.premier_league import fetch_matches_for
            # Only supports PL for now
            if match.get("competition_id") == "eng.1":
                date_str = (match.get("kickoff_at") or "")[:10]
                if date_str:
                    for ev in fetch_matches_for(date_str):
                        if (ev["home_team"].lower() == home.lower()
                                and ev["away_team"].lower() == away.lower()):
                            return verdict_from_espn(ev.get("raw") or {}) or {
                                "verdict": "HELD",
                                "confidence": None,
                                "method": "ESPN_MISS",
                                "asserted": False,
                                "reason": "Match found on ESPN but no odds/form.",
                            }
        except Exception:
            pass

    # Team-form cache fallback (LiveScore / unknown sources)
    try:
        cached = _verdict_from_cached_forms(home, away)
        if cached:
            return cached
    except Exception:
        pass

    # Sibling fallback — try other sources for the same team pair
    if siblings:
        for sib in siblings:
            if not isinstance(sib, dict):
                continue
            sib_source = (sib.get("source") or "").split(",")[0].strip().lower()
            if sib_source == source:
                continue
            sib_fn = _SOURCE_DISPATCH.get(sib_source)
            sib_raw = sib.get("raw") or {}
            if sib_fn and isinstance(sib_raw, dict):
                try:
                    result = sib_fn(sib_raw)
                except Exception:
                    result = None
                if result:
                    result["method"] = (
                        f"{result.get('method', '')}_VIA_{sib_source.upper()}"
                    )
                    result["reason"] = (
                        f"{result.get('reason', '')} "
                        f"(cross-source: {source} + {sib_source})"
                    ).strip()
                    return result

    # No data → honest HELD
    return {
        "verdict": "HELD",
        "confidence": None,
        "method": "NONE",
        "asserted": False,
        "reason": f"Source '{source}' provided no odds or form.",
    }


def verdict_batch(matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compute verdicts for many matches. Returns new list with verdicts attached."""
    out = []
    for m in matches:
        v = compute_verdict(m)
        row = dict(m)
        row["verdict"] = v["verdict"]
        row["confidence"] = v.get("confidence")
        row["asserted"] = v.get("asserted", False)
        row["verdict_method"] = v.get("method")
        row["verdict_reason"] = v.get("reason")
        row["probabilities"] = v.get("probabilities")
        out.append(row)
    return out


if __name__ == "__main__":
    import json

    # Smoke test with a synthetic ESPN-shaped event
    espn_test = {
        "source": "espn",
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "raw": {
            "competitions": [{
                "odds": [{
                    "homeTeamOdds": {"moneyLine": -180},
                    "awayTeamOdds": {"moneyLine": 400},
                    "drawOdds": {"moneyLine": 280},
                }],
            }],
        },
    }
    print("ESPN odds test:")
    print(json.dumps(compute_verdict(espn_test), indent=2))

    espn_form_test = {
        "source": "espn",
        "home_team": "A",
        "away_team": "B",
        "raw": {
            "competitions": [{
                "competitors": [
                    {"homeAway": "home", "form": "WWLWD"},
                    {"homeAway": "away", "form": "LLDLW"},
                ],
            }],
        },
    }
    print("\nESPN form test:")
    print(json.dumps(compute_verdict(espn_form_test), indent=2))

    held_test = {"source": "livescore", "home_team": "X", "away_team": "Y"}
    print("\nLiveScore no-data test:")
    print(json.dumps(compute_verdict(held_test), indent=2))
