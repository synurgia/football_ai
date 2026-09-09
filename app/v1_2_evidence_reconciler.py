from __future__ import annotations

from typing import Any, Dict, List

from app.v1_2_source_evidence_ledger import (
    SourceEvidence,
    V12SourceEvidenceLedger,
)


class V12EvidenceReconciler:
    """
    Reconcile multiple source-level evidence records for one V1.2
    question without inventing football conclusions.

    This layer only evaluates agreement and availability of supplied
    source answers. It does not modify Pieces 1-9.
    """

    UNUSABLE_STATUSES = {
        "UNKNOWN",
        "UNVERIFIED",
        "INSUFFICIENT_EVIDENCE",
    }

    def reconcile(
        self,
        ledger: V12SourceEvidenceLedger,
        question_id: str,
    ) -> Dict[str, Any]:

        records = ledger.for_question(question_id)

        usable = [
            record
            for record in records
            if self._usable(record)
        ]

        if not usable:
            return {
                "question_id": question_id,
                "status": "INSUFFICIENT_EVIDENCE",
                "answer": None,
                "supports": "UNKNOWN",
                "confidence": None,
                "source_count": 0,
                "sources": [],
                "agreement": "NO_USABLE_EVIDENCE",
                "records": [],
            }

        answers = [
            str(record.answer).strip()
            for record in usable
            if record.answer is not None
        ]

        sources = list(
            dict.fromkeys(
                record.source
                for record in usable
            )
        )

        if not answers:
            return {
                "question_id": question_id,
                "status": "INSUFFICIENT_EVIDENCE",
                "answer": None,
                "supports": "UNKNOWN",
                "confidence": None,
                "source_count": len(sources),
                "sources": sources,
                "agreement": "NO_USABLE_ANSWERS",
                "records": [
                    record.to_dict()
                    for record in usable
                ],
            }

        normalized_answers = {
            answer.upper()
            for answer in answers
        }

        if len(normalized_answers) > 1:
            return {
                "question_id": question_id,
                "status": "INSUFFICIENT_EVIDENCE",
                "answer": None,
                "supports": "UNKNOWN",
                "confidence": None,
                "source_count": len(sources),
                "sources": sources,
                "agreement": "CONFLICT",
                "records": [
                    record.to_dict()
                    for record in usable
                ],
            }

        answer = answers[0]

        supports = [
            str(record.supports).strip()
            for record in usable
            if record.supports
        ]

        normalized_supports = {
            support.upper()
            for support in supports
        }

        if len(normalized_supports) == 1:
            resolved_supports = supports[0]
        else:
            resolved_supports = "UNKNOWN"

        confidence_values = [
            record.confidence
            for record in usable
            if isinstance(record.confidence, (int, float))
        ]

        confidence = (
            min(confidence_values)
            if confidence_values
            else None
        )

        return {
            "question_id": question_id,
            "status": "VERIFIED",
            "answer": answer,
            "supports": resolved_supports,
            "confidence": confidence,
            "source_count": len(sources),
            "sources": sources,
            "agreement": "AGREEMENT",
            "records": [
                record.to_dict()
                for record in usable
            ],
        }

    @classmethod
    def _usable(cls, record: SourceEvidence) -> bool:
        """
        Accept only records that contain an answer and are not explicitly
        marked as unresolved.
        """
        if record.answer is None:
            return False

        status = str(
            getattr(record, "status", "VERIFIED")
        ).upper()

        return status not in cls.UNUSABLE_STATUSES
