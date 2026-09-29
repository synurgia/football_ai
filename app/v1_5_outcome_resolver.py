"""Outcome resolver — produces HOME / DRAW / AWAY / HELD for every match.

Four-level fallback so every match with any signal gets a verdict:
  1. V1.5 synthesis (asserted when readiness allows)
  2. V1.4 five-dimensional matrix lean (provisional)
  3. 37-question bundle heuristic (provisional)
  4. Snapshot heuristic (provisional)

Only returns HELD when there is genuinely no signal on any of the four.
"""

from __future__ import annotations
from typing import Any, Dict, Optional

VERDICTS = {"HOME", "DRAW", "AWAY"}


def _normalise_verdict(raw):
    if not raw:
        return None
    s = str(raw).strip().upper().replace(" ", "_")
    if s in VERDICTS:
        return s
    if s in ("H", "HOMEWIN", "HOME_WIN", "1", "HOME_TEAM"):
        return "HOME"
    if s in ("A", "AWAYWIN", "AWAY_WIN", "2", "AWAY_TEAM"):
        return "AWAY"
    if s in ("D", "X", "TIE", "DRAW_"):
        return "DRAW"
    return None


# ------------------------------------------------------------------ 1. V1.5

def _call_v15(home, away, competition_id):
    try:
        from app import v1_5_broad_reasoning as v15
    except Exception:
        return None
    fn = getattr(v15, "run_broad", None)
    if callable(fn):
        try:
            r = fn(home, away, competition_id)
            if isinstance(r, dict):
                return r
        except Exception:
            pass
    return None


def _extract_v15_outcome(v15_result):
    if not isinstance(v15_result, dict):
        return None
    candidates = [v15_result]
    for k in ("broad_reasoning", "augmented", "report"):
        n = v15_result.get(k)
        if isinstance(n, dict):
            candidates.append(n)
            if isinstance(n.get("broad_reasoning"), dict):
                candidates.append(n["broad_reasoning"])
    for src in candidates:
        for key in ("final_outcome", "broad_outcome", "outcome", "verdict"):
            norm = _normalise_verdict(src.get(key))
            if norm:
                status = str(src.get("prediction_status") or "").upper()
                return {
                    "verdict": norm,
                    "asserted": status == "PROCESSED",
                    "confidence": src.get("confidence"),
                    "source": "V1_5_SYNTHESIS",
                    "reasoning": src.get("overall_synthesis") or src.get("reasoning"),
                }
    return None


# ------------------------------------------------------------------ 2. V1.4 matrix

def _extract_matrix_from_card(card):
    """Try hard to find a V1.4 matrix anywhere on the card."""
    for k in ("statistical_assessment", "matrix", "five_dimensional_matrix", "v13_ai"):
        v = card.get(k)
        if isinstance(v, dict):
            return v
    br = card.get("broad_reasoning")
    if isinstance(br, dict):
        for k in ("statistical_assessment", "matrix"):
            v = br.get(k)
            if isinstance(v, dict):
                return v
    return None


def _derive_from_matrix(matrix):
    if not isinstance(matrix, dict):
        return None

    def num(*keys):
        for k in keys:
            v = matrix.get(k)
            if isinstance(v, (int, float)):
                return float(v)
        return 0.0

    home_att = num("home_offensive_threat", "offensive_threat_home",
                   "home_attack", "dim_2_home", "attacking_threat_home")
    away_att = num("away_offensive_threat", "offensive_threat_away",
                   "away_attack", "dim_2_away", "attacking_threat_away")
    home_def = num("home_defensive_stability", "defensive_stability_home",
                   "home_defence", "dim_3_home")
    away_def = num("away_defensive_stability", "defensive_stability_away",
                   "away_defence", "dim_3_away")
    momentum = num("dim_1_momentum_delta", "momentum_delta", "home_momentum")

    if not any([home_att, away_att, home_def, away_def, momentum]):
        return None

    eff_home = home_att - away_def + momentum + 0.20
    eff_away = away_att - home_def - momentum
    diff = eff_home - eff_away
    verdict = "DRAW" if abs(diff) < 0.25 else ("HOME" if diff > 0 else "AWAY")
    return {
        "verdict": verdict,
        "asserted": False,
        "confidence": "LOW",
        "source": "V1_4_MATRIX_LEAN",
        "difference": round(diff, 3),
        "effective_home": round(eff_home, 3),
        "effective_away": round(eff_away, 3),
    }


# ------------------------------------------------------------------ 3. 37Q heuristic

_HOME_FAVOUR_PATTERNS = (
    "home", "yes_home", "stronger_home", "higher", "favourite_home",
)
_AWAY_FAVOUR_PATTERNS = (
    "away", "yes_away", "stronger_away", "favourite_away",
)


def _derive_from_37q(bundle):
    """Very light lean: count verified answers that carry home/away support."""
    if not isinstance(bundle, dict):
        return None
    items = bundle.get("per_question") or []
    if not items:
        return None

    home_signal = 0.0
    away_signal = 0.0
    verified = 0

    for e in items:
        status = str(e.get("status") or "").upper()
        if status not in ("VERIFIED", "CONFIRMED"):
            continue
        verified += 1
        supports = str(e.get("supports") or "").lower()
        ans = str(e.get("answer") or "").lower()
        q = str(e.get("question_id") or "")
        qlow = q.lower()
        if any(p in supports for p in _HOME_FAVOUR_PATTERNS):
            home_signal += 1
        if any(p in supports for p in _AWAY_FAVOUR_PATTERNS):
            away_signal += 1

    if verified < 2:
        return None

    diff = home_signal - away_signal
    if abs(diff) < 1:
        verdict = "DRAW"
    else:
        verdict = "HOME" if diff > 0 else "AWAY"
    return {
        "verdict": verdict,
        "asserted": False,
        "confidence": "LOW",
        "source": "THIRTY7Q_LEAN",
        "difference": round(diff, 3),
        "verified_answers": verified,
    }


# ------------------------------------------------------------------ 4. Snapshots

def _derive_from_snapshots(home_snap, away_snap):
    if not home_snap or not away_snap:
        return None

    def num(d, *keys):
        for k in keys:
            v = d.get(k)
            if isinstance(v, (int, float)):
                return float(v)
        return 0.0

    home_ppg = num(home_snap, "points_per_game", "ppg")
    away_ppg = num(away_snap, "points_per_game", "ppg")
    if home_ppg == 0 and away_ppg == 0:
        return None

    home_gd = num(home_snap, "goal_difference", "gd")
    away_gd = num(away_snap, "goal_difference", "gd")

    home_s = home_ppg + (home_gd / 10.0) + 0.20
    away_s = away_ppg + (away_gd / 10.0)
    diff = home_s - away_s
    verdict = "DRAW" if abs(diff) < 0.25 else ("HOME" if diff > 0 else "AWAY")
    return {
        "verdict": verdict,
        "asserted": False,
        "confidence": "LOW",
        "source": "SNAPSHOT_LEAN",
        "difference": round(diff, 3),
        "home_strength": round(home_s, 3),
        "away_strength": round(away_s, 3),
    }


def _fetch_snapshots_smart(conn, match):
    """Try every plausible key: (competition, team), (openfoot_competition_id, team),
    (competition_id, team), and season-agnostic fallback."""
    team = match.get("home_team") or match.get("team")
    if not team:
        return None
    keys = [
        match.get("competition"),
        match.get("openfoot_competition_id"),
        match.get("competition_id"),
    ]
    keys = [str(k) for k in keys if k]
    if not keys:
        return None

    for key in keys:
        row = conn.execute(
            "SELECT points_per_game, goal_difference, matches_played, "
            "       league_position, recent_form "
            "FROM team_snapshots WHERE competition = ? AND team_name = ? "
            "ORDER BY last_seen_at DESC LIMIT 1",
            (key, team),
        ).fetchone()
        if row:
            return {
                "points_per_game": row[0],
                "goal_difference": row[1],
                "matches_played": row[2],
                "league_position": row[3],
                "recent_form": row[4],
            }
    return None


# ------------------------------------------------------------------ entry point

def resolve_outcome(
    home_team,
    away_team,
    competition_id,
    *,
    match_id=None,
    readiness=None,
    v15_result=None,
    matrix=None,
    snapshots=None,
    bundle=None,
    db_path="data/football_daily.db",
):
    import sqlite3
    readiness = readiness or {}
    is_ready = bool(readiness.get("process"))

    # 1. V1.5
    if v15_result is None:
        v15_result = _call_v15(home_team, away_team, competition_id)
    extracted = _extract_v15_outcome(v15_result)
    if extracted:
        if not is_ready and extracted.get("source") == "V1_5_SYNTHESIS":
            extracted["asserted"] = False
            extracted["source"] = "V1_5_SYNTHESIS_HELD"
        return extracted

    # 2. Matrix
    derived = _derive_from_matrix(matrix)
    if derived:
        return derived

    # 3. 37Q bundle
    derived = _derive_from_37q(bundle)
    if derived:
        return derived

    # 4. Snapshots (or fetch them)
    if snapshots is None and db_path:
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            home_snap = _fetch_snapshots_smart(conn, {
                "home_team": home_team,
                "competition": competition_id,
                "competition_id": competition_id,
            })
            away_snap = _fetch_snapshots_smart(conn, {
                "home_team": away_team,
                "competition": competition_id,
                "competition_id": competition_id,
            })
            conn.close()
            if home_snap or away_snap:
                snapshots = {"home": home_snap, "away": away_snap}
        except Exception:
            pass

    if snapshots:
        derived = _derive_from_snapshots(
            snapshots.get("home") if isinstance(snapshots, dict) else None,
            snapshots.get("away") if isinstance(snapshots, dict) else None,
        )
        if derived:
            return derived

    return {
        "verdict": "HELD",
        "asserted": False,
        "confidence": None,
        "source": "NONE",
        "reasoning": "No evidence path produced an outcome.",
    }
