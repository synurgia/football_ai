from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SourceEvidence:
    """
    One factual contribution from one source for one V1.2 question.

    This is deliberately separate from V2EvidenceState because the
    canonical V1.2 state keeps one resolved record per question.
    """

    question_id: str
    source: str
    answer: Any = None
    evidence: Any = None
    supports: str = "UNKNOWN"
    confidence: Optional[float] = None
    source_ref: Optional[str] = None
    observed_at: Optional[str] = None
    status: str = "VERIFIED"
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "source": self.source,
            "answer": self.answer,
            "evidence": self.evidence,
            "supports": self.supports,
            "confidence": self.confidence,
            "source_ref": self.source_ref,
            "observed_at": self.observed_at,
            "status": self.status,
            "notes": self.notes,
        }


@dataclass
class V12SourceEvidenceLedger:
    """
    Temporary multi-source evidence store.

    It preserves source-level evidence without resolving or inferring
    the final answer to a V1.2 question.
    """

    records: List[SourceEvidence] = field(default_factory=list)

    def add(
        self,
        question_id: str,
        source: str,
        *,
        answer: Any = None,
        evidence: Any = None,
        supports: str = "UNKNOWN",
        confidence: Optional[float] = None,
        source_ref: Optional[str] = None,
        observed_at: Optional[str] = None,
        status: str = "VERIFIED",
        notes: Optional[str] = None,
    ) -> SourceEvidence:

        if not question_id:
            raise ValueError("question_id is required.")

        if not source:
            raise ValueError("source is required.")

        record = SourceEvidence(
            question_id=question_id,
            source=source,
            answer=answer,
            evidence=evidence,
            supports=supports,
            confidence=confidence,
            source_ref=source_ref,
            observed_at=observed_at,
            status=status,
            notes=notes,
        )

        self.records.append(record)
        return record

    def for_question(
        self,
        question_id: str,
    ) -> List[SourceEvidence]:
        return [
            record
            for record in self.records
            if record.question_id == question_id
        ]

    def sources_for_question(
        self,
        question_id: str,
    ) -> List[str]:
        return list(
            dict.fromkeys(
                record.source
                for record in self.for_question(question_id)
            )
        )

    def count(self) -> int:
        return len(self.records)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_count": len(self.records),
            "evidence": [
                record.to_dict()
                for record in self.records
            ],
        }
