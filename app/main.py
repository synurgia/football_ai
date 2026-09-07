from typing import Any, Dict

from fastapi import FastAPI, HTTPException
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
