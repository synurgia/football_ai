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


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return render_dashboard(prediction_result_store, rolling_match_store)



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
        result = run_v13_ai(
            request.team_a,
            request.team_b,
            competition_id,
            request.date,
        )

        from app.v2_question_registry import get_all_questions
        result["questions"] = get_all_questions()


        # V1.3: expose all existing registered questions.
        # Existing AI answers are preserved; unanswered questions remain UNKNOWN.
        from app.v2_question_registry import get_all_questions

        existing_qas = result.get("qas", [])
        existing_by_id = {
            str(item.get("id", "")): item
            for item in existing_qas
            if isinstance(item, dict)
        }

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

            result["qas"].append({
                "id": qid,
                "question": question["question"],
                "answer": (
                    match.get("answer", "UNKNOWN")
                    if match else "UNKNOWN"
                ),
                "status": (
                    match.get("status", "UNVERIFIED")
                    if match else "UNVERIFIED"
                ),
                "evidence": (
                    match.get("evidence")
                    if match else None
                ),
                "confidence": (
                    match.get("confidence")
                    if match else None
                ),
                "source": (
                    match.get("source")
                    if match else None
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
