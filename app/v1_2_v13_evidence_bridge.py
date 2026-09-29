from __future__ import annotations

from typing import Any, Dict

from app.v1_2_capability_question_mapper import V12CapabilityQuestionMapper
from app.v1_2_multisource_evidence import V12MultiSourceEvidence
from app.v1_2_question_reasoning_engine import V12QuestionReasoningEngine
from app.v2_evidence_state import V2EvidenceState


class V12V13EvidenceBridge:
    """
    V1.3 multi-source evidence -> canonical V1.2 question state.

    Source evidence is routed by explicit capability and the enriched
    V1.2 evidence requirements. No answer is invented here.
    """

    def __init__(self) -> None:
        self.multisource = V12MultiSourceEvidence()
        self.mapper = V12CapabilityQuestionMapper()
        self.reasoning = V12QuestionReasoningEngine()

    def create_state(self, fixture: Dict[str, Any]) -> V2EvidenceState:
        return self.multisource.create_state(
            match_id=str(fixture.get("match_id", "")),
            competition=str(fixture.get("competition", "")),
            home_team=str(fixture.get("home_team", "")),
            away_team=str(fixture.get("away_team", "")),
        )

    def apply_packet(
        self,
        state: V2EvidenceState,
        packet: Dict[str, Any],
    ) -> V2EvidenceState:

        for item in packet.get("evidence", []):
            if not isinstance(item, dict):
                continue

            capability = str(item.get("capability", "")).strip()
            if not capability:
                continue

            mapped = self.mapper.map_evidence(item)

            for question in mapped:
                question_id = question["question_id"]

                evidence_item = {
                    "answer": item.get("answer"),
                    "evidence": item.get("evidence"),
                    "supports": item.get("supports", "UNKNOWN"),
                    "confidence": item.get("confidence"),
                    "source_ref": (
                        item.get("source_ref")
                        or item.get("source_url")
                    ),
                    "observed_at": item.get("observed_at"),
                    "impact": item.get("impact"),
                    "status": item.get("status", "UNKNOWN"),
                    "notes": item.get("notes"),
                }

                self.multisource.add_evidence(
                    state,
                    question_id,
                    **evidence_item,
                    source=item.get("source") or capability,
                )

        return state

    def process(
        self,
        fixture: Dict[str, Any],
        packet: Dict[str, Any],
    ) -> Dict[str, Any]:

        state = self.create_state(fixture)
        self.apply_packet(state, packet)

        return {
            "match_id": fixture.get("match_id"),
            "competition_id": fixture.get("competition_id"),
            "mapped_source_count": packet.get("mapped_source_count", 0),
            "retrieval": packet.get("retrieval", {}),
            "evidence_packet_count": packet.get("total_evidence", 0),
            "question_count": self.multisource.question_count(),
            "evidence_state": state.to_dict(),
            "reasoning": self.reasoning.evaluate_state(state),
            "coverage": packet.get("coverage", {}),
        }
