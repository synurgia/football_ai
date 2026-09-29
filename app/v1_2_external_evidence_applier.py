from typing import Any, Dict, List

from app.v1_2_external_evidence_envelope import ExternalEvidenceEnvelope
from app.v1_2_question_capabilities import QUESTION_CAPABILITIES
from app.v2_evidence_manager import V2EvidenceManager
from app.v2_evidence_state import V2EvidenceState


CAPABILITY_REQUIREMENT_ALIASES = {
    "competition_rules": {"competition_rules"},
    "financial_context": {"financial_context"},
    "team_changes": {"squad_changes", "manager_changes", "tactical_changes"},
    "motivation": {"standings", "fixtures", "competition_rules"},
    "results": {"historical_results", "team_statistics", "xg"},
    "geopolitical_context": {"geopolitical_context", "news"},
    "public_context": {"public_signal", "reputation_context"},
    "team_identity": {"team_identity"},
    "competition_context": {"standings", "competition_stage", "competition_rules"},
    "team_strength": {"rankings", "ratings", "team_strength", "xg"},
    "model_analysis": {"model_output", "model_inputs"},
    "team_matrix": {"team_statistics", "performance_metrics"},
    "statistical_models": {"historical_results", "team_statistics", "model_inputs", "statistical_models"},
    "tactical_analysis": {"tactical_data", "formations", "team_statistics"},
    "standings": {"standings", "rankings", "team_statistics"},
    "market_context": {"market_context"},
    "schedule": {"fixtures", "travel", "rest", "rotation", "competition_stage"},
    "weather_venue": {"weather", "venue_condition", "pitch_condition"},
    "defensive_resistance": {"defensive_statistics", "tactical_data"},
    "tactical_metrics": {"formations", "tactical_metrics", "lineups"},
    "transition_analysis": {"transition_metrics", "pace", "finishing", "tactical_data"},
    "favorite_risk": {"finishing", "goalkeeping", "historical_matchups", "team_strength"},
    "opponent_resistance": {"historical_results", "opponent_strength"},
    "bayesian_adjustment": {"model_inputs", "statistical_models", "bayesian_adjustments"},
    "match_status": {"referee_appointment", "referee_statistics", "expected_lineup", "confirmed_lineup", "formations"},
    "pitch_conditions": {"venue", "pitch_dimensions", "surface", "grass", "watering"},
}


class V12ExternalEvidenceApplier:
    """
    Applies external evidence to the existing canonical V2 question state.

    This class:
    - does not create questions;
    - does not replace the V2EvidenceManager;
    - does not answer questions semantically;
    - does not modify Pieces 1-9;
    - preserves the evidence status and provenance supplied by the source.
    """

    def __init__(self) -> None:
        self.manager = V2EvidenceManager()

    def apply(
        self,
        state: V2EvidenceState,
        envelope: ExternalEvidenceEnvelope,
    ) -> List[Dict[str, Any]]:
        envelope.validate()

        results: List[Dict[str, Any]] = []

        for question_id, capability in QUESTION_CAPABILITIES.items():
            if capability != envelope.capability:
                continue

            question = next((item for item in state.items if item.question_id == question_id), None)

            if question is None:
                raise KeyError(
                    f"Canonical question not found: {question_id}"
                )

            allowed_requirements = set(
                CAPABILITY_REQUIREMENT_ALIASES.get(
                    envelope.capability,
                    {envelope.capability},
                )
            )

            question_requirements = set(
                getattr(question, "evidence_requirements", [])
            )

            if question_requirements and not (
                allowed_requirements & question_requirements
            ):
                continue

            piece = int(question.piece)

            result = self.manager.update_question(
                state,
                piece=piece,
                question_id=question_id,
                answer=question.answer,
                evidence=envelope.evidence,
                supports="EXTERNAL_EVIDENCE",
                confidence=None,
                source=envelope.source_id,
                source_ref=envelope.source_ref,
                observed_at=envelope.observed_at,
                status=envelope.status,
                notes=envelope.notes,
            )

            results.append(result)

        return results
