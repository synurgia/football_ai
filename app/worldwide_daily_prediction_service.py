from typing import Any, Dict, List

from app.worldwide_prediction_runner import WorldwidePredictionRunner
from app.data_registry.prediction_result_store import PredictionResultStore


class WorldwideDailyPredictionService:
    """
    Processes every daily match that has passed the readiness gate.

    Every READY match is processed independently through the
    existing Pieces 1-9 analytical pipeline.

    Successful predictions are persisted in the prediction-results store.
    """

    def __init__(
        self,
        prediction_runner: WorldwidePredictionRunner | None = None,
        result_store: PredictionResultStore | None = None,
    ):
        self.prediction_runner = (
            prediction_runner or WorldwidePredictionRunner()
        )
        self.result_store = (
            result_store or PredictionResultStore()
        )

    def process_ready_matches(
        self,
        readiness_result: Dict[str, Any],
    ) -> Dict[str, Any]:

        ready_matches = readiness_result.get("today_ready", [])

        predictions: List[Dict[str, Any]] = []
        failures: List[Dict[str, Any]] = []

        for item in ready_matches:
            match = item.get("match", {})

            try:
                payload = self.prediction_runner.build_prediction_payload(item)

                from app.services.prediction_service import run_prediction

                prediction = run_prediction(payload)

                self.result_store.upsert(
                    match=match,
                    prediction=prediction,
                )

                predictions.append({
                    "match": match,
                    "prediction": prediction,
                    "status": "processed",
                })

            except Exception as exc:
                failures.append({
                    "match": match,
                    "status": "failed",
                    "error": str(exc),
                })

        return {
            "requested": len(ready_matches),
            "processed": len(predictions),
            "failed": len(failures),
            "predictions": predictions,
            "failures": failures,
            "persisted": len(predictions),
        }
