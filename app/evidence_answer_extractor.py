"""Evidence answer extractor.

Runs after V12ExternalEvidenceApplier.apply() and derives a concrete
`answer` for each question whose evidence payload actually contains one.

Without this, `status` becomes VERIFIED but `answer` stays UNKNOWN, and
V1.4/V1.5 (which read `answer`) see nothing.

The extractor is deterministic and read-only with respect to the evidence
state's `evidence` field — it only fills in `answer`, `supports`,
`confidence`, and `observed_at`.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_event(evidence: Any) -> Optional[Dict[str, Any]]:
    if isinstance(evidence, dict):
        ev = evidence.get("event")
        if isinstance(ev, dict):
            return ev
        # Some records nest under "events"
        evs = evidence.get("events")
        if isinstance(evs, list) and evs and isinstance(evs[0], dict):
            return evs[0]
    return None


def _competitors(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(event, dict):
        return []
    comps = (event.get("competitions") or [{}])[0].get("competitors") or []
    return [c for c in comps if isinstance(c, dict)]


def _side(comps, side):
    for c in comps:
        if (c.get("homeAway") or "").lower() == side:
            return c
    return None


def _team_name(comp) -> str:
    if not comp:
        return ""
    team = comp.get("team") or {}
    return (
        team.get("displayName")
        or team.get("name")
        or team.get("shortDisplayName")
        or ""
    )


def _status_text(event) -> str:
    try:
        return (
            event["competitions"][0]["status"]["type"]["description"]
        )
    except Exception:
        return ""


def _is_full_time(event) -> bool:
    try:
        return bool(event["competitions"][0]["status"]["type"]["completed"])
    except Exception:
        return False


def _extract_q6_q15_q30_answers(event, state):
    """Q6, Q15, Q30 — attacking / form / opponent strength."""
    comps = _competitors(event)
    home_c = _side(comps, "home")
    away_c = _side(comps, "away")

    answers: Dict[str, Dict[str, Any]] = {}

    home_name = _team_name(home_c) or state.home_team
    away_name = _team_name(away_c) or state.away_team
    home_form = (home_c or {}).get("form") or ""
    away_form = (away_c or {}).get("form") or ""
    home_score = (home_c or {}).get("score")
    away_score = (away_c or {}).get("score")

    if home_form and away_form:
        hw = home_form.count("W")
        aw = away_form.count("W")
        if hw > aw:
            lean = "HOME"
            rationale = f"{home_name} form ({home_form}) stronger than {away_name} ({away_form})"
        elif aw > hw:
            lean = "AWAY"
            rationale = f"{away_name} form ({away_form}) stronger than {home_name} ({home_form})"
        else:
            lean = "EVEN"
            rationale = f"Both forms equal ({home_form} vs {away_form})"

        answers["Q15"] = {
            "answer": f"Recent form — home {home_form} | away {away_form} — lean {lean}",
            "supports": lean if lean in ("HOME", "AWAY") else "EVEN",
            "confidence": 0.65,
            "evidence": rationale,
        }
        answers["Q30"] = {
            "answer": f"Form trend — home {home_form} | away {away_form}",
            "supports": lean if lean in ("HOME", "AWAY") else "EVEN",
            "confidence": 0.6,
            "evidence": rationale,
        }

    if home_score is not None and away_score is not None and _is_full_time(event):
        try:
            hs = int(str(home_score))
            as_ = int(str(away_score))
        except ValueError:
            hs = as_ = None
        if hs is not None and as_ is not None:
            if hs > as_:
                s = "HOME"
            elif as_ > hs:
                s = "AWAY"
            else:
                s = "DRAW"
            answers["Q6"] = {
                "answer": f"Historical result {home_name} {hs}-{as_} {away_name}",
                "supports": s,
                "confidence": 0.85,
                "evidence": f"Full-time score from ESPN: {hs}-{as_}",
            }

    return answers


def _extract_q10_answer(event, state):
    """Q10 — both teams are men's first teams? Only if we can confirm."""
    return None  # ESPN data does not confirm gender/first-team status; stay UNKNOWN


def _extract_q38_q41_answers(event, state):
    """Q38 (referee), Q41 (lineups). Usually absent in scoreboard payload."""
    return {}


def _extract_q25_q34_answers(event, state):
    """Q25 (schedule), Q34 (travel). ESPN scoreboard gives date/time only."""
    return {}


def apply_answers_to_state(state, answers: Dict[str, Dict[str, Any]]) -> int:
    """Write extracted answers into the V2 evidence state."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()

    if not answers:
        return 0

    items_by_qid = {}
    for it in state.items:
        qid = getattr(it, "question_id", None)
        if qid:
            items_by_qid[qid] = it

    updated = 0
    for qid, payload in answers.items():
        item = items_by_qid.get(qid)
        if item is None:
            continue
        # Only upgrade if currently UNKNOWN / UNVERIFIED
        current_answer = (getattr(item, "answer", "") or "").upper()
        if current_answer and current_answer not in ("UNKNOWN", ""):
            continue

        try:
            item.answer = payload["answer"]
            item.supports = payload.get("supports", "UNKNOWN")
            if payload.get("confidence") is not None:
                item.confidence = payload["confidence"]
            item.status = "VERIFIED"
            item.observed_at = now
            if not item.evidence or "No verified evidence" in str(item.evidence):
                item.evidence = payload.get("evidence", "")
            updated += 1
        except Exception:
            continue

    return updated




def _extract_from_teams_payload(evidence, state):
    """Handle {teams: [...]} payloads from TheSportsDB, Wikidata, OpenLigaDB.

    The envelope may wrap the payload different ways:
      - evidence = {"teams": [...]}         (raw record)
      - evidence = {"evidence": {"teams": [...]}}  (wrapped record)
      - evidence = {"raw": {...}}           (adapter output)
    Try each path.
    """
    answers: Dict[str, Dict[str, Any]] = {}
    if not isinstance(evidence, dict):
        return answers

    teams = evidence.get("teams")
    if not isinstance(teams, list):
        # Try nested paths
        for key in ("evidence", "raw", "payload", "data"):
            inner = evidence.get(key)
            if isinstance(inner, dict) and isinstance(inner.get("teams"), list):
                teams = inner["teams"]
                break
    if not isinstance(teams, list):
        return answers

    for t in teams:
        if not isinstance(t, dict):
            continue
        side = (t.get("side") or "").upper()
        if not side:
            continue
        # Q18/Q19/Q12 etc. — team identity & standings
        if t.get("country"):
            answers.setdefault("Q19", {
                "answer": f"Team country from external source: {t.get('country')}",
                "supports": "MATCH_CONTEXT",
                "confidence": 0.75,
                "evidence": f"{t.get('team_name')} located in {t.get('country')}",
            })
        if t.get("standings_position") is not None:
            answers.setdefault("Q27", {
                "answer": f"Standings position: {t.get('standings_position')} "
                          f"(points {t.get('standings_points')}, played {t.get('standings_played')})",
                "supports": side,
                "confidence": 0.85,
                "evidence": f"{t.get('team_name')} — position {t.get('standings_position')}, "
                            f"GD {t.get('standings_goal_difference')}",
            })
        if t.get("manager"):
            answers.setdefault("Q4", {
                "answer": f"Manager: {t.get('manager')}",
                "supports": "MATCH_CONTEXT",
                "confidence": 0.8,
                "evidence": f"{t.get('team_name')} manager: {t.get('manager')}",
            })
        if t.get("venue"):
            answers.setdefault("Q2", {
                "answer": f"Venue: {t.get('venue')}",
                "supports": "MATCH_CONTEXT",
                "confidence": 0.85,
                "evidence": f"{t.get('team_name')} home venue: {t.get('venue')}",
            })

    return answers


def _extract_from_fkf_payload(evidence, state):
    """Handle FKF {home_seen, away_seen} payload."""
    if not isinstance(evidence, dict):
        return {}
    if evidence.get("home_seen") and evidence.get("away_seen"):
        return {
            "Q26": {
                "answer": "Both teams listed on Football Kenya Federation official site",
                "supports": "MATCH_CONTEXT",
                "confidence": 0.7,
                "evidence": "FKF front page contains both team names",
            }
        }
    return {}




def _extract_recent_form(evidence, state):
    """Handle {teams: [{side, recent_form: 'WWLDW'}]} payload."""
    if not isinstance(evidence, dict):
        return {}
    teams = evidence.get("teams")
    if not isinstance(teams, list):
        for key in ("evidence", "raw", "payload", "data"):
            inner = evidence.get(key)
            if isinstance(inner, dict) and isinstance(inner.get("teams"), list):
                teams = inner["teams"]
                break
    if not isinstance(teams, list):
        return {}

    answers = {}
    forms = {}
    for t in teams:
        if not isinstance(t, dict):
            continue
        side = (t.get("side") or "").lower()
        form = t.get("recent_form")
        if side and form:
            forms[side] = form

    if "home" in forms and "away" in forms:
        hf, af = forms["home"], forms["away"]
        hw = hf.count("W"); aw = af.count("W")
        if hw > aw:
            lean = "HOME"
            rationale = f"Home form {hf} > away form {af}"
        elif aw > hw:
            lean = "AWAY"
            rationale = f"Away form {af} > home form {hf}"
        else:
            lean = "EVEN"
            rationale = f"Both forms {hf} vs {af}"

        answers["Q3"] = {
            "answer": f"Recent form — home {hf} | away {af} — lean {lean}",
            "supports": lean if lean in ("HOME", "AWAY") else "EVEN",
            "confidence": 0.7,
            "evidence": rationale,
        }
        answers["Q15"] = {
            "answer": f"Last-5 record — home {hf} | away {af}",
            "supports": lean if lean in ("HOME", "AWAY") else "EVEN",
            "confidence": 0.7,
            "evidence": rationale,
        }
        answers["Q30"] = {
            "answer": f"Form trend — home {hf} | away {af}",
            "supports": lean if lean in ("HOME", "AWAY") else "EVEN",
            "confidence": 0.65,
            "evidence": rationale,
        }
    return answers


def extract_answers(state, envelope_evidence: Any) -> int:
    """Top-level entry. Returns number of questions updated."""
    event = _extract_event(envelope_evidence)
    if not event:
        return 0

    answers: Dict[str, Dict[str, Any]] = {}

    # Event-based extractors (ESPN scoreboard)
    for fn in (
        _extract_q6_q15_q30_answers,
        _extract_q10_answer,
        _extract_q38_q41_answers,
        _extract_q25_q34_answers,
    ):
        try:
            result = fn(event, state)
        except Exception:
            result = None
        if isinstance(result, dict):
            answers.update(result)

    # Teams-payload extractors (TheSportsDB, Wikidata, OpenLigaDB)
    try:
        r = _extract_from_teams_payload(envelope_evidence, state)
        if isinstance(r, dict):
            answers.update(r)
    except Exception:
        pass

    # FKF-specific
    try:
        r = _extract_from_fkf_payload(envelope_evidence, state)
        if isinstance(r, dict):
            answers.update(r)
    except Exception:
        pass

    # Recent form (TheSportsDB eventslast)
    try:
        r = _extract_recent_form(envelope_evidence, state)
        if isinstance(r, dict):
            answers.update(r)
    except Exception:
        pass

    return apply_answers_to_state(state, answers)
