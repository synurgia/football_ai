from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.v2_evidence_manager import V2EvidenceManager
from app.v2_evidence_state import V2EvidenceState
from app.v2_question_registry import get_all_questions


class V12MultiSourceEvidence:
    """
    V1.2 multi-source evidence layer.

    This layer connects verified factual evidence from multiple
    external/internal sources to the existing canonical 37-question
    evidence state.

    It does NOT:
    - create another question registry,
    - modify Pieces 1-9,
    - invent answers,
    - treat OpenFoot as the sole source,
    - mark missing evidence as VERIFIED,
    - perform football inference.

    It only records evidence provenance and preserves unresolved
    questions when usable evidence is not supplied.
    """

    def __init__(self) -> None:
        self.manager = V2EvidenceManager()

        registry = get_all_questions()

        self.questions: Dict[str, Dict[str, Any]] = {
            str(question["id"]): question
            for question in registry
        }

    def create_state(
        self,
        match_id: str,
        competition: str,
        home_team: str,
        away_team: str,
    ) -> V2EvidenceState:
        """
        Create the canonical V1.2 evidence state containing all 37
        registered questions.
        """
        return self.manager.create_state(
            match_id=match_id,
            competition=competition,
            home_team=home_team,
            away_team=away_team,
        )

    def add_evidence(
        self,
        state: V2EvidenceState,
        question_id: str,
        *,
        answer: Any = None,
        evidence: Any = None,
        supports: str = "UNKNOWN",
        confidence: Optional[float] = None,
        source: Optional[str] = None,
        source_ref: Optional[str] = None,
        observed_at: Optional[str] = None,
        impact: Optional[float] = None,
        status: str = "UNKNOWN",
        notes: Optional[str] = None,
    ) -> V2EvidenceState:
        """
        Add one evidence contribution to an existing V1.2 question.

        Multiple providers may contribute evidence to the same question.

        Evidence without a usable answer is not automatically promoted
        to VERIFIED.
        """
        question = self.questions.get(question_id)

        if question is None:
            raise ValueError(
                f"Unknown V1.2 question ID: {question_id}"
            )

        if status.upper() == "VERIFIED" and answer is None:
            raise ValueError(
                f"{question_id} cannot be VERIFIED without an answer."
            )

        self.manager.update_question(
            state=state,
            piece=int(question["piece"]),
            question_id=question_id,
            answer=answer,
            evidence=evidence,
            supports=supports,
            confidence=confidence,
            source=source,
            source_ref=source_ref,
            observed_at=observed_at,
            impact=impact,
            status=status,
            notes=notes,
        )

        return state

    def add_source_bundle(
        self,
        state: V2EvidenceState,
        source: str,
        evidence_items: List[Dict[str, Any]],
    ) -> V2EvidenceState:
        """
        Add evidence from one provider/source.

        Each item must identify an existing canonical question_id.
        """
        for item in evidence_items:
            question_id = item.get("question_id")

            if not question_id:
                raise ValueError(
                    "Every evidence item requires question_id."
                )

            self.add_evidence(
                state,
                question_id,
                answer=item.get("answer"),
                evidence=item.get("evidence"),
                supports=item.get("supports", "UNKNOWN"),
                confidence=item.get("confidence"),
                source=source,
                source_ref=item.get("source_ref"),
                observed_at=item.get("observed_at"),
                impact=item.get("impact"),
                status=item.get("status", "UNKNOWN"),
                notes=item.get("notes"),
            )

        return state

    def question_count(self) -> int:
        return len(self.questions)

    def question_ids(self) -> List[str]:
        return list(self.questions.keys())

    def unresolved_count(self, state: V2EvidenceState) -> int:
        return len(state.unresolved())
