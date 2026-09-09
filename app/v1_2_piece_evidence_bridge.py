from __future__ import annotations

from typing import Any, Dict

from app.v2_evidence_manager import V2EvidenceManager
from app.v2_evidence_state import V2EvidenceState
from app.v2_question_registry import get_all_questions


class V12PieceEvidenceBridge:
    """
    Controlled bridge from existing Pieces 1-8 analytical results
    into the existing V1.2 37-question evidence state.

    This component:
    - uses the existing question registry;
    - does not create a second question system;
    - does not modify Pieces 1-9;
    - does not fabricate missing evidence;
    - preserves unresolved questions as unresolved;
    - stores Piece output as evidence with provenance.
    """

    PIECE_SOURCE = {
        "1": "piece01",
        "2": "piece02",
        "3": "piece03",
        "4": "piece04",
        "5": "piece05",
        "6": "piece06",
        "7": "piece07",
        "8": "piece08",
    }

    def __init__(self) -> None:
        self.manager = V2EvidenceManager()

    def create_state(self, analytical_state) -> V2EvidenceState:
        match = analytical_state.match

        return self.manager.create_state(
            match_id=getattr(match, "match_id", "UNKNOWN"),
            competition=getattr(match, "competition", "UNKNOWN"),
            home_team=self._team_name(match, "home_team"),
            away_team=self._team_name(match, "away_team"),
        )

    def build_evidence_state(self, analytical_state) -> V2EvidenceState:
        """
        Map all 37 registered questions against existing Piece 1-8 output.

        Questions are never invented here. If the relevant Piece did not
        produce usable output, the question remains in its original
        unresolved state.
        """
        state = self.create_state(analytical_state)

        for question in get_all_questions():
            piece = str(question["piece"])
            question_id = question["id"]

            piece_name = self.PIECE_SOURCE.get(piece)
            if piece_name is None:
                continue

            result = analytical_state.results.get(piece_name)

            if result is None or not result.success:
                continue

            output = result.output

            if output is None:
                continue

            self._record_piece_evidence(
                state=state,
                piece=piece,
                question_id=question_id,
                output=output,
                source=piece_name,
            )

        return state

    def _record_piece_evidence(
        self,
        state: V2EvidenceState,
        piece: str,
        question_id: str,
        output: Any,
        source: str,
    ) -> None:
        """
        Record existing analytical output against the registered question.

        The bridge deliberately does not manufacture a semantic answer
        from arbitrary output. Structured output is preserved as evidence.
        """
        self.manager.update_question(
            state=state,
            piece=int(piece),
            question_id=question_id,
            answer="EVIDENCE_AVAILABLE",
            evidence=output,
            supports="UNKNOWN",
            confidence=None,
            source=source,
            source_ref=f"{source}:{question_id}",
            observed_at=None,
            impact=None,
            status="VERIFIED",
            notes=(
                "Existing Piece output preserved as analytical evidence. "
                "Semantic advantage interpretation is handled separately."
            ),
        )

    @staticmethod
    def _team_name(match: Any, field_name: str) -> str:
        team = getattr(match, field_name, None)

        if team is None:
            return "UNKNOWN"

        name = getattr(team, "team_name", None)

        if name:
            return str(name)

        return str(team)
