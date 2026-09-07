from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from app.frontend.dashboard_renderer import render_dashboard
from pydantic import BaseModel

from app.config import settings
from app.services.prediction_service import run_prediction


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

prediction_result_store = PredictionResultStore()


@app.get("/daily/today")
def get_today_predictions():
    from datetime import date

    results = prediction_result_store.list_results(
        match_date=date.today().isoformat()
    )

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
    return render_dashboard(prediction_result_store)
