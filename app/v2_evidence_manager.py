from typing import Any, Dict, List, Optional

from app.v2_evidence_state import V2EvidenceState
from app.v2_question_registry import get_all_questions


class V2EvidenceManager:
    """
    Match-specific manager for the V2 question-by-question evidence state.

    This component does not collect Internet data by itself.
    It provides the controlled state into which verified evidence
    will be inserted later.
    """

    def create_state(
        self,
        match_id: str,
        competition: str,
        home_team: str,
        away_team: str,
    ) -> V2EvidenceState:
        state = V2EvidenceState(
            match_id=match_id,
            competition=competition,
            home_team=home_team,
            away_team=away_team,
        )

        for question in get_all_questions():
            state.add(
                piece=int(question["piece"]),
                question_id=question["id"],
                question=question["question"],
                answer="UNKNOWN",
                evidence="No verified evidence collected yet.",
                supports="UNKNOWN",
                status="UNVERIFIED",
            )

        return state

    def update_question(
        self,
        state: V2EvidenceState,
        piece: int,
        question_id: str,
        answer: Any,
        evidence: Any,
        supports: str = "UNKNOWN",
        confidence: Optional[float] = None,
        source: Optional[str] = None,
        source_ref: Optional[str] = None,
        observed_at: Optional[str] = None,
        impact: Optional[float] = None,
        status: str = "VERIFIED",
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        matches = state.get_question(piece, question_id)

        if not matches:
            raise KeyError(
                f"Question not registered: Piece {piece}, {question_id}"
            )

        item = matches[0]

        item.answer = answer
        item.evidence = evidence
        item.supports = supports
        item.confidence = confidence
        item.source = source
        item.source_ref = source_ref
        item.observed_at = observed_at
        item.impact = impact
        item.status = status
        item.notes = notes

        return item.to_dict()

    def piece_summary(
        self,
        state: V2EvidenceState,
        piece: int,
    ) -> Dict[str, Any]:
        items = state.get_piece(piece)

        return {
            "piece": piece,
            "question_count": len(items),
            "verified": sum(
                1 for item in items
                if item.status == "VERIFIED"
            ),
            "unverified": sum(
                1 for item in items
                if item.status == "UNVERIFIED"
            ),
            "unknown": sum(
                1 for item in items
                if item.status in {
                    "UNKNOWN",
                    "INSUFFICIENT_EVIDENCE",
                }
            ),
            "questions": [
                item.to_dict()
                for item in items
            ],
        }

    def full_summary(
        self,
        state: V2EvidenceState,
    ) -> Dict[str, Any]:
        return state.to_dict()

    def unresolved_questions(
        self,
        state: V2EvidenceState,
    ) -> List[Dict[str, Any]]:
        return [
            item.to_dict()
            for item in state.unresolved()
        ]
