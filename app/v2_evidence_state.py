from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class V2EvidenceItem:
    piece: int
    question_id: str
    question: str

    answer: Any = None
    evidence: Any = None

    supports: str = "UNKNOWN"
    confidence: Optional[float] = None

    source: Optional[str] = None
    source_ref: Optional[str] = None
    observed_at: Optional[str] = None

    impact: Optional[float] = None
    status: str = "UNVERIFIED"

    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "piece": self.piece,
            "question_id": self.question_id,
            "question": self.question,
            "answer": self.answer,
            "evidence": self.evidence,
            "supports": self.supports,
            "confidence": self.confidence,
            "source": self.source,
            "source_ref": self.source_ref,
            "observed_at": self.observed_at,
            "impact": self.impact,
            "status": self.status,
            "notes": self.notes,
        }


@dataclass
class V2EvidenceState:
    match_id: str
    competition: str
    home_team: str
    away_team: str

    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    items: List[V2EvidenceItem] = field(default_factory=list)

    def add(
        self,
        piece: int,
        question_id: str,
        question: str,
        answer: Any = None,
        evidence: Any = None,
        supports: str = "UNKNOWN",
        confidence: Optional[float] = None,
        source: Optional[str] = None,
        source_ref: Optional[str] = None,
        observed_at: Optional[str] = None,
        impact: Optional[float] = None,
        status: str = "UNVERIFIED",
        notes: Optional[str] = None,
    ) -> V2EvidenceItem:
        item = V2EvidenceItem(
            piece=piece,
            question_id=question_id,
            question=question,
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

        self.items.append(item)
        return item

    def get_piece(self, piece: int) -> List[V2EvidenceItem]:
        return [
            item for item in self.items
            if item.piece == piece
        ]

    def get_question(
        self,
        piece: int,
        question_id: str,
    ) -> List[V2EvidenceItem]:
        return [
            item for item in self.items
            if item.piece == piece
            and item.question_id == question_id
        ]

    def unresolved(self) -> List[V2EvidenceItem]:
        return [
            item
            for item in self.items
            if item.status in {
                "UNVERIFIED",
                "UNKNOWN",
                "INSUFFICIENT_EVIDENCE",
            }
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "match": {
                "match_id": self.match_id,
                "competition": self.competition,
                "home_team": self.home_team,
                "away_team": self.away_team,
            },
            "created_at": self.created_at,
            "evidence_count": len(self.items),
            "evidence": [
                item.to_dict()
                for item in self.items
            ],
        }
