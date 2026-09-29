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

                # V1.3 DAILY SOURCE EVIDENCE HANDOFF:
                # Preserve all verified source evidence for the existing
                # V1.2 question/evidence resolver before prediction.
                if isinstance(payload, dict):
                    data_sources = payload.setdefault("data_sources", {})
                    if not isinstance(data_sources, dict):
                        data_sources = {}
                        payload["data_sources"] = data_sources

                    for key in (
                        "v13_mapped_sources",
                        "unified_sources",
                        "external_evidence",
                        "source_results",
                        "evidence",
                    ):
                        if key in item:
                            data_sources[key] = item.get(key)

                    if isinstance(match, dict):
                        for key in (
                            "v13_mapped_sources",
                            "unified_sources",
                            "external_evidence",
                            "source_results",
                            "evidence",
                        ):
                            if key in match and key not in data_sources:
                                data_sources[key] = match.get(key)


                from app.services.prediction_service import run_prediction

                prediction = run_prediction(payload)

                # V1.3 metadata travels with the existing prediction object.
                prediction["v13"] = {
                    "competition_id": item.get("competition_id"),
                    "competition_name_canonical": item.get("competition_name_canonical"),
                    "competition_identity_status": item.get("competition_identity_status"),
                    "competition_identity_method": item.get("competition_identity_method"),
                    "source_status": item.get("source_status"),
                    "source_ids": item.get("source_ids"),
                    "evidence_status": item.get("evidence_status"),
                    "readiness_status": item.get("readiness_status"),
                    "evidence_count": item.get("evidence_count"),
                    "resolved_questions": item.get("resolved_questions"),
                    "unresolved_questions": item.get("unresolved_questions"),
                }

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
    def process_all_matches(self, readiness_result):
        """Run the full daily pipeline for every scanned match.

        Prediction-capable matches receive a full V1.4/V1.5 prediction.
        Every other reasoning-eligible match receives an intelligence card
        with prediction explicitly HELD. Nothing that the scanner saw is
        dropped.
        """
        # 1. Prediction track for READY matches
        try:
            prediction_result = self.process_ready_matches(readiness_result)
        except Exception as exc:
            prediction_result = {
                "status": "FAILED",
                "processed": 0,
                "predictions": [],
                "error": str(exc),
            }

        predictions_by_id = {}
        for pred in prediction_result.get("predictions", []):
            mid = str(pred.get("match_id") or "")
            if mid:
                predictions_by_id[mid] = pred

        reasoning_entries = []

        for item in readiness_result.get("today_reasoning", []):
            match = item.get("match", {}) or {}
            readiness = item.get("readiness", {}) or {}
            mid = str(match.get("match_id") or "")

            # Already predicted -> attach reasoning reference, keep prediction.
            if mid and mid in predictions_by_id:
                pred = predictions_by_id[mid]
                reasoning_entries.append({
                    "match_id": mid,
                    "prediction_status": "PROCESSED",
                    "readiness": readiness,
                    "reasoning": pred.get(
                        "broad_reasoning",
                        pred.get("reasoning"),
                    ),
                    "final_outcome": pred.get("final_outcome"),
                    "outcome": pred.get("outcome"),
                    "verdict": pred.get("verdict") or pred.get("final_outcome"),
                    "outcome_asserted": True,
                    "outcome_source": pred.get("outcome_source") or "V1_5_SYNTHESIS",
                })
                continue

            # Otherwise emit a HELD intelligence card for this match.
            card = {
                "match_id": mid,
                "competition": match.get("competition"),
                "home_team": match.get("home_team"),
                "away_team": match.get("away_team"),
                "kickoff_at": match.get("kickoff_at"),
                "readiness": readiness,
                "prediction_status": "HELD",
                "final_outcome": None,
                "confidence": readiness.get("status", "UNKNOWN"),
                "notes": readiness.get("reasons", []),
                "warnings": readiness.get("warnings", []),
                "competition_type": readiness.get("competition_type"),
            }

            try:
                from app.v1_5_broad_reasoning import run_broad
                augmented = run_broad(
                    card["home_team"],
                    card["away_team"],
                    card.get("competition_id")
                    or readiness.get("competition_id")
                    or card["competition"],
                )
                card["broad_reasoning"] = (
                    augmented.get("broad_reasoning")
                    if isinstance(augmented, dict)
                    else None
                )
                if isinstance(augmented, dict):
                    br = augmented.get("broad_reasoning") or {}
                    card["decisive_factors"] = br.get("decisive_factors")
                    card["advantages"] = br.get("advantages")
                    card["counter_advantages"] = br.get("counter_advantages")
                    card["missing_evidence"] = br.get("missing_evidence")
                    card["self_challenge"] = br.get("self_challenge")
            except Exception as exc:
                card["broad_reasoning"] = None
                card["broad_reasoning_error"] = str(exc)

            # --- Resolve HOME / DRAW / AWAY / HELD ---
            try:
                from app.v1_5_outcome_resolver import resolve_outcome
                snapshots = None
                try:
                    from app.data_registry.team_snapshot_store import TeamSnapshotStore
                    store = TeamSnapshotStore()
                    season = match.get("season") or ""
                    cid = (card.get("competition_id")
                           or readiness.get("competition_id")
                           or match.get("openfoot_competition_id")
                           or match.get("competition"))
                    if season and cid:
                        snapshots = {
                            "home": store.get(cid, season, card.get("home_team")),
                            "away": store.get(cid, season, card.get("away_team")),
                        }
                except Exception:
                    snapshots = None

                outcome = resolve_outcome(
                    card.get("home_team"),
                    card.get("away_team"),
                    card.get("competition_id") or readiness.get("competition_id") or card.get("competition"),
                    readiness=readiness,
                    v15_result=card.get("broad_reasoning") or None,
                    matrix=None,
                    snapshots=snapshots,
                )
                card["outcome"] = outcome
                card["verdict"] = outcome.get("verdict")
                card["outcome_asserted"] = outcome.get("asserted")
                card["outcome_confidence"] = outcome.get("confidence")
                card["outcome_source"] = outcome.get("source")
                card["final_outcome"] = (
                    outcome.get("verdict") if outcome.get("asserted") else None
                )
            except Exception as exc:
                card["outcome"] = {
                    "verdict": "HELD",
                    "asserted": False,
                    "source": "ERROR",
                    "reasoning": str(exc),
                }
                card["verdict"] = "HELD"
                card["outcome_asserted"] = False
                card["outcome_source"] = "ERROR"

            reasoning_entries.append(card)


        # 2. Matches that were held pre-identity also reported, never dropped.
        for item in readiness_result.get("today_held", []):
            match = item.get("match", {}) or {}
            readiness = item.get("readiness", {}) or {}
            reasoning_entries.append({
                "match_id": str(match.get("match_id") or ""),
                "competition": match.get("competition"),
                "home_team": match.get("home_team"),
                "away_team": match.get("away_team"),
                "kickoff_at": match.get("kickoff_at"),
                "readiness": readiness,
                "prediction_status": "HELD",
                "final_outcome": None,
                "confidence": readiness.get("status", "UNKNOWN"),
                "notes": readiness.get("reasons", []),
                "warnings": readiness.get("warnings", []),
                "competition_type": readiness.get("competition_type"),
                "broad_reasoning": None,
                "broad_reasoning_error": "identity or context incomplete",
            })

        return {
            "status": "COMPLETED",
            "processed": prediction_result.get("processed", 0),
            "predictions": prediction_result.get("predictions", []),
            "reasoning_cards": reasoning_entries,
            "reasoning_total": len(reasoning_entries),
            "reasoning_held": sum(
                1 for c in reasoning_entries
                if c.get("prediction_status") == "HELD"
            ),
            "reasoning_processed": sum(
                1 for c in reasoning_entries
                if c.get("prediction_status") == "PROCESSED"
            ),
        }

