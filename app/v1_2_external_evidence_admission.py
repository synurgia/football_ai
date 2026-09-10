"""
V1.2 External Evidence Admission

Purpose:
    Provide the controlled entry point from the external-source
    federation into the existing canonical V2 evidence state.

Rules:
    - Uses the existing V12ExternalEvidenceApplier.
    - Does not create a second question registry.
    - Does not create a second evidence writer.
    - Does not infer answers.
    - Does not compare home and away teams.
    - Does not modify Pieces 1-9.
"""

from typing import Any, Dict

from app.v1_2_external_evidence_applier import (
    V12ExternalEvidenceApplier,
)
from app.v1_2_external_evidence_envelope import (
    ExternalEvidenceEnvelope,
)
from app.v2_evidence_state import V2EvidenceState


class V12ExternalEvidenceAdmission:
    """Controlled admission point for verified external evidence."""

    def __init__(self) -> None:
        self.applier = V12ExternalEvidenceApplier()

    def admit(
        self,
        state: V2EvidenceState,
        envelope: ExternalEvidenceEnvelope,
    ) -> Dict[str, Any]:
        if state is None:
            raise ValueError("Evidence state is required.")

        if envelope is None:
            raise ValueError("External evidence envelope is required.")

        envelope.validate()

        applied = self.applier.apply(
            state,
            envelope,
        )

        return {
            "status": "ADMITTED",
            "capability": envelope.capability,
            "source_id": envelope.source_id,
            "source_type": envelope.source_type,
            "question_count": len(applied),
            "applied_questions": [
                result.get("question_id")
                for result in applied
            ],
            "results": applied,
        }


__all__ = ["V12ExternalEvidenceAdmission"]
