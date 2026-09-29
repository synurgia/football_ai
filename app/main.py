from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from app.frontend.dashboard_renderer import render_dashboard
from pydantic import BaseModel

from app.config import settings
from app.services.prediction_service import run_prediction
from app.worldwide_daily_manager import WorldwideDailyDataManager
from app.daily_activation import run_daily_activation
from app.v13_ai_intelligence_engine import run as run_v13_ai
from app.data_registry.v13_competition_identity_resolver import V13CompetitionIdentityResolver
from app.data_registry.v1_3_competition_catalogue import V13_COMPETITION_CATALOGUE
from app.data_registry.v1_3_country_competition_index import get_countries, get_competitions_for_country


@asynccontextmanager
async def lifespan(app: FastAPI):
    daily_task = asyncio.create_task(run_daily_activation())
    try:
        yield
    finally:
        daily_task.cancel()
        try:
            await daily_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Football AI analytical backend API",
)


class PredictionRequest(BaseModel):
    competition: str
    home_team: Dict[str, Any]
    away_team: Dict[str, Any]
    environment: Dict[str, Any] = {}
    referee: Dict[str, Any] = {}
    market_odds: Dict[str, Any] = {}
    data_sources: Dict[str, Any] = {}


class V13MatchIntelligenceRequest(BaseModel):
    team_a: str
    team_b: str
    competition: str
    date: str | None = None


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "version": settings.version,
        "status": "online",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "environment": settings.environment,
    }


@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        return run_prediction(request.model_dump())
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction pipeline error: {exc}",
        ) from exc

from app.data_registry.prediction_result_store import PredictionResultStore
from app.data_registry.rolling_match_store import RollingMatchStore

prediction_result_store = PredictionResultStore()
rolling_match_store = RollingMatchStore()


def _v13_dashboard_envelope(item):
    prediction = item.get("prediction") or {}
    if not isinstance(prediction, dict):
        return item

    v13 = prediction.get("v13")
    if not isinstance(v13, dict):
        v13 = {}

    # Preserve any V1.3 metadata already carried by the prediction.
    for key in (
        "competition_id",
        "competition_name_canonical",
        "competition_identity_status",
        "competition_identity_method",
        "source_status",
        "source_ids",
        "evidence_status",
        "readiness_status",
        "evidence_count",
        "resolved_questions",
        "unresolved_questions",
    ):
        if key in item and key not in v13:
            v13[key] = item[key]

    if v13:
        prediction = dict(prediction)
        prediction["v13"] = v13
        item = dict(item)
        item["prediction"] = prediction

    return item


@app.get("/daily/today")
def get_today_predictions():
    from datetime import date

    results = prediction_result_store.list_results(
        match_date=date.today().isoformat()
    )

    results = [_v13_dashboard_envelope(item) for item in results]

    return {
        "date": date.today().isoformat(),
        "count": len(results),
        "predictions": results,
    }


@app.get("/daily/{match_id}")
def get_daily_prediction(match_id: str):
    result = prediction_result_store.get(match_id)

    if result is None:
        return {
            "status": "not_found",
            "match_id": match_id,
        }

    return result


@app.get("/outcomes/today")
def get_today_outcomes():
    import sqlite3
    from datetime import date
    today = date.today().isoformat()
    conn = sqlite3.connect("data/football_daily.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT match_id, competition, home_team, away_team, kickoff_at, "
        "       verdict, asserted, confidence, source "
        "FROM match_outcomes WHERE match_date = ? "
        "ORDER BY kickoff_at",
        (today,),
    ).fetchall()
    conn.close()
    return {
        "date": today,
        "total": len(rows),
        "matches": [dict(r) for r in rows],
        "counts": {
            "HOME": sum(1 for r in rows if r["verdict"] == "HOME"),
            "DRAW": sum(1 for r in rows if r["verdict"] == "DRAW"),
            "AWAY": sum(1 for r in rows if r["verdict"] == "AWAY"),
            "HELD": sum(1 for r in rows if r["verdict"] == "HELD"),
        },
    }


@app.get("/outcomes/{match_id}")


@app.get("/dashboard/matches")
def dashboard_matches(date_str: str = None):
    """Today's scanned worldwide matches. Proves the scanner wrote them."""
    import sqlite3
    from datetime import date
    if not date_str:
        date_str = date.today().isoformat()

    conn = sqlite3.connect("data/football_daily.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT match_id, competition, competition_id, home_team, away_team, "
        "       kickoff_at, source, status "
        "FROM matches WHERE match_date = ? "
        "ORDER BY kickoff_at, competition",
        (date_str,),
    ).fetchall()

    by_source = {}
    by_competition = {}
    matches = []
    for r in rows:
        m = dict(r)
        matches.append(m)
        src = m.get("source") or "unknown"
        by_source[src] = by_source.get(src, 0) + 1
        cid = m.get("competition_id") or m.get("competition") or "unresolved"
        by_competition[cid] = by_competition.get(cid, 0) + 1

    conn.close()
    return {
        "date": date_str,
        "total": len(matches),
        "by_source": by_source,
        "by_competition": dict(sorted(
            by_competition.items(), key=lambda x: -x[1]
        )),
        "matches": matches,
    }


@app.get("/dashboard/sources")
def dashboard_sources():
    """Live source health — proves no source is primary."""
    import asyncio
    from app.sources.worldwide import scan_worldwide
    try:
        result = asyncio.run(asyncio.to_thread(scan_worldwide))
        return {
            "date": result.get("date"),
            "total_unique": result.get("total"),
            "source_status": result.get("source_status", []),
        }
    except Exception as e:
        return {"error": str(e)}


def get_match_outcome(match_id: str):
    import sqlite3, json
    conn = sqlite3.connect("data/football_daily.db")
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM match_outcomes WHERE match_id = ? LIMIT 1",
        (match_id,),
    ).fetchone()
    conn.close()
    if not row:
        return {"error": "not found", "match_id": match_id}
    d = dict(row)
    try:
        d["outcome"] = json.loads(d.get("outcome_json") or "{}")
    except Exception:
        d["outcome"] = {}
    return d


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    date: str = None,
    competition: str = None,
    country: str = None,
    league: str = None,
):
    """Dual-mode dashboard.

    No params  → daily view (today's all matches + verdicts)
    With params → search view (by date, competition, country, league)

    Examples:
      /dashboard
      /dashboard?date=2026-09-30
      /dashboard?competition=eng.1
      /dashboard?country=ke
      /dashboard?league=premier
    """
    from app.frontend.dashboard_renderer import render_dashboard
    return render_dashboard(
        date_str=date,
        filter_competition=competition,
        country=country,
        league=league,
    )



@app.get("/v13/countries")
async def v13_countries():
    return {
        "framework": "V1.3",
        "countries": get_countries(),
    }


@app.get("/v13/countries/{country}/competitions")
async def v13_country_competitions(country: str):
    competitions = get_competitions_for_country(country)

    if not competitions:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "COUNTRY_NOT_FOUND",
                "country": country,
            },
        )

    return {
        "framework": "V1.3",
        "country": country,
        "competitions": competitions,
    }

@app.get("/v13/questions")
async def v13_questions():
    from app.v2_question_registry import get_all_questions

    questions = get_all_questions()

    return {
        "status": "QUESTIONS_AVAILABLE",
        "question_count": len(questions),
        "questions": questions,
    }


@app.post("/v13/match-intelligence")
async def v13_match_intelligence(request: V13MatchIntelligenceRequest):
    # Every request is a completely fresh intelligence session.
    resolver = V13CompetitionIdentityResolver()
    resolved = resolver.resolve(request.competition)

    if not resolved or resolved.get("status") != "RESOLVED":
        raise HTTPException(
            status_code=422,
            detail={
                "status": "UNRESOLVED_COMPETITION",
                "competition": request.competition,
                "message": "Competition could not be verified against the V1.3 191-competition universe.",
            },
        )

    competition_id = resolved["competition_id"]

    try:
        # Match Intelligence must consume the already-discovered daily fixture
        # when available. Held/insufficient matches remain inspectable without
        # being incorrectly inserted into PredictionResultStore.
        stored_matches = rolling_match_store.list_matches()
        result = None

        target_home = str(request.team_a).strip().lower()
        target_away = str(request.team_b).strip().lower()
        target_date = str(request.date)

        for stored in stored_matches:
            if not isinstance(stored, dict):
                continue

            home = str(
                stored.get("home_team") or stored.get("team_a") or ""
            ).strip().lower()
            away = str(
                stored.get("away_team") or stored.get("team_b") or ""
            ).strip().lower()
            match_date = str(
                stored.get("match_date") or stored.get("date") or ""
            )

            if (
                home == target_home
                and away == target_away
                and match_date == target_date
            ):
                result = dict(stored)
                break

        if result is None:
            result = run_v13_ai(
                request.team_a,
                request.team_b,
                competition_id,
                request.date,
            )

        from app.v2_question_registry import get_all_questions
        result["questions"] = get_all_questions()


        # V1.3: expose all existing registered questions AND run
        # the existing AI evidence through the V1.3 reasoning layer.
        from app.v2_question_registry import get_all_questions
        from app.v1_3_reasoning_bridge import V13ReasoningBridge

        # V1.3: the live AI engine returns its actual QuestionAnswer
        # objects under "questions". Preserve them for the dashboard.
        existing_qas = (
            result.get("qas")
            or result.get("questions")
            or []
        )
        existing_by_id = {
            str(item.get("id", "")): item
            for item in existing_qas
            if isinstance(item, dict)
        }

        # Convert the AI's existing question evidence into the V1.3
        # reasoning input. No new questions and no invented evidence.
        reasoning_input = {}

        for item in existing_qas:
            if not isinstance(item, dict):
                continue

            qid = str(item.get("id", ""))
            if not qid:
                continue

            reasoning_input[qid] = [{
                "source_id": (
                    item.get("source")
                    or item.get("source_id")
                    or "EXISTING_AI"
                ),
                "answer": item.get("answer"),
                "status": (
                    item.get("status")
                    or item.get("answer_status")
                    or "UNVERIFIED"
                ),
                "method": (
                    item.get("method")
                    or "EXISTING_AI_EVIDENCE"
                ),
                "confidence": (
                    item.get("confidence")
                    or "NONE"
                ),
                "evidence": (
                    item.get("evidence")
                    or item.get("reasoning")
                    or ""
                ),
                "freshness": item.get("freshness"),
                "source_url": (
                    item.get("source_url")
                    or item.get("url")
                ),
            }]

        reasoning_report = V13ReasoningBridge().reason_match(
            {"questions": reasoning_input}
        )

        result["v1_3_reasoning"] = reasoning_report

        reasoning_questions = reasoning_report.get(
            "questions",
            {}
        )

        all_questions = get_all_questions()
        result["qas"] = []

        for question in all_questions:
            qid = question["id"]

            match = existing_by_id.get(qid)

            if match is None:
                for key, item in existing_by_id.items():
                    if key.startswith(qid + "_"):
                        match = item
                        break

            reasoned = reasoning_questions.get(qid)

            if reasoned is None and match is not None:
                reasoned = reasoning_questions.get(
                    str(match.get("id", ""))
                )

            result["qas"].append({
                "id": qid,
                "question": question["question"],
                "answer": (
                    reasoned.get("answer", "UNKNOWN")
                    if reasoned
                    else (
                        match.get("answer", "UNKNOWN")
                        if match
                        else "UNKNOWN"
                    )
                ),
                "status": (
                    reasoned.get("status", "INSUFFICIENT_EVIDENCE")
                    if reasoned
                    else (
                        match.get("status", "UNVERIFIED")
                        if match
                        else "UNVERIFIED"
                    )
                ),
                "evidence": (
                    reasoned.get("supporting_evidence", [])
                    if reasoned
                    else (
                        match.get("evidence")
                        if match
                        else None
                    )
                ),
                "confidence": (
                    reasoned.get("confidence", "NONE")
                    if reasoned
                    else (
                        match.get("confidence")
                        if match
                        else None
                    )
                ),
                "source": (
                    reasoned.get("method")
                    if reasoned
                    else (
                        match.get("source")
                        if match
                        else None
                    )
                ),
                "reasoning": (
                    reasoned.get("reasoning", "")
                    if reasoned
                    else ""
                ),
                "conflicting_evidence": (
                    reasoned.get("conflicting_evidence", [])
                    if reasoned
                    else []
                ),
                "unresolved_evidence": (
                    reasoned.get("unresolved_evidence", [])
                    if reasoned
                    else []
                ),
                "freshness": (
                    reasoned.get("freshness", [])
                    if reasoned
                    else []
                ),
            })

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "AI_ANALYSIS_FAILED",
                "team_a": request.team_a,
                "team_b": request.team_b,
                "competition_id": competition_id,
                "error": str(exc),
            },
        )

    return {
        "framework": "V1.3",
        "session": "FRESH",
        "competition": resolved,
        "match": {
            "team_a": request.team_a,
            "team_b": request.team_b,
            "date": request.date,
        },
        "intelligence": result,
    }


@app.get("/api/pl/today")
def api_pl_today(date_str: str = None):
    """Premier League — today or next matchday."""
    from app.pl.premier_league import build_report
    try:
        return build_report(for_date=date_str)
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/pl/calendar")
def api_pl_calendar():
    """Premier League matchday calendar."""
    from app.pl.premier_league import find_matchdays
    return find_matchdays()


@app.get("/api/verdicts/today")
def api_verdicts_today(date_str: str = None):
    """All today's verdicts from match_outcomes."""
    import sqlite3, json
    from datetime import date
    if not date_str:
        date_str = date.today().isoformat()

    conn = sqlite3.connect("data/football_daily.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT match_id, competition, home_team, away_team, kickoff_at, "
        "       verdict, asserted, confidence, source, outcome_json "
        "FROM match_outcomes WHERE match_date = ? "
        "ORDER BY kickoff_at",
        (date_str,),
    ).fetchall()
    conn.close()

    matches = []
    counts = {"HOME": 0, "DRAW": 0, "AWAY": 0, "HELD": 0}
    for r in rows:
        m = dict(r)
        try:
            outcome = json.loads(m.pop("outcome_json") or "{}")
        except Exception:
            outcome = {}
        m["reason"] = outcome.get("reason", "")
        m["method"] = outcome.get("method", "")
        m["probabilities"] = outcome.get("probabilities")
        matches.append(m)
        counts[m["verdict"]] = counts.get(m["verdict"], 0) + 1

    return {
        "date": date_str,
        "total": len(matches),
        "counts": counts,
        "matches": matches,
    }


@app.get("/api/verdicts/stats")
def api_verdicts_stats():
    """Verdict counts by date for the last 30 days."""
    import sqlite3
    conn = sqlite3.connect("data/football_daily.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT match_date, verdict, COUNT(*) AS n FROM match_outcomes "
        "GROUP BY match_date, verdict ORDER BY match_date DESC LIMIT 300"
    ).fetchall()
    conn.close()

    by_date = {}
    for r in rows:
        d = r["match_date"]
        if d not in by_date:
            by_date[d] = {"HOME": 0, "DRAW": 0, "AWAY": 0, "HELD": 0, "total": 0}
        by_date[d][r["verdict"]] = r["n"]
        by_date[d]["total"] += r["n"]

    return {"by_date": by_date}


@app.get("/match/{match_id}", response_class=HTMLResponse)
def match_detail(match_id: str):
    """Detailed view of one match — verdict, form, evidence, reasoning."""
    from app.frontend.match_detail_renderer import render_match_detail
    return render_match_detail(match_id)



