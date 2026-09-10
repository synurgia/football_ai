"""
V1.2 Capability Evidence Finder

Purpose:
    Find bounded source-content passages relevant to an explicitly
    requested capability.

Rules:
    - Works only on content from a verified source.
    - Does not answer the 37 questions.
    - Does not infer missing facts.
    - Does not select Home or Away.
    - Does not modify Pieces 1-9.
    - No match conclusion is generated.
"""

from typing import Any, Dict, List


class V12CapabilityEvidenceFinder:
    """Find candidate passages using explicit capability markers."""

    CAPABILITY_MARKERS = {
        "competition_context": (
            "competition",
            "tournament",
            "championship",
            "league",
        ),
        "competition_rules": (
            "rules",
            "regulations",
            "penalty",
            "extra time",
            "tie",
        ),
        "financial_context": (
            "financial",
            "funding",
            "budget",
            "investment",
        ),
        "geopolitical_context": (
            "conflict",
            "war",
            "sanctions",
            "security",
        ),
        "market_context": (
            "market",
            "price",
            "odds",
        ),
        "match_status": (
            "scheduled",
            "postponed",
            "cancelled",
            "live",
            "final",
        ),
        "motivation": (
            "must win",
            "qualification",
            "relegation",
            "promotion",
        ),
        "pitch_conditions": (
            "pitch",
            "surface",
            "grass",
            "artificial",
        ),
        "public_context": (
            "fans",
            "supporters",
            "attendance",
            "expectations",
        ),
        "results": (
            "result",
            "score",
            "won",
            "lost",
            "draw",
        ),
        "schedule": (
            "schedule",
            "fixture",
            "kickoff",
            "match",
        ),
        "standings": (
            "standings",
            "table",
            "position",
            "points",
        ),
        "team_changes": (
            "manager",
            "coach",
            "transfer",
            "signed",
            "departure",
        ),
        "team_identity": (
            "team",
            "club",
            "squad",
            "men",
            "women",
        ),
        "weather_venue": (
            "weather",
            "temperature",
            "rain",
            "stadium",
            "venue",
        ),
    }

    def find(
        self,
        source_content: Dict[str, Any],
        *,
        capability: str,
        context_window: int = 180,
        max_passages: int = 5,
    ) -> Dict[str, Any]:
        if capability not in self.CAPABILITY_MARKERS:
            raise ValueError(
                f"Unsupported external capability: {capability}"
            )

        content = str(source_content.get("content") or "")

        if not content.strip():
            return {
                "capability": capability,
                "status": "INSUFFICIENT_EVIDENCE",
                "passages": [],
            }

        lowered = content.lower()
        passages: List[Dict[str, Any]] = []
        seen = set()

        for marker in self.CAPABILITY_MARKERS[capability]:
            start = 0

            while len(passages) < max_passages:
                index = lowered.find(marker, start)

                if index < 0:
                    break

                left = max(0, index - context_window)
                right = min(
                    len(content),
                    index + len(marker) + context_window,
                )

                passage = content[left:right].strip()
                key = passage.lower()

                if passage and key not in seen:
                    passages.append(
                        {
                            "marker": marker,
                            "text": passage,
                        }
                    )
                    seen.add(key)

                start = index + len(marker)

        status = (
            "CANDIDATE_EVIDENCE_FOUND"
            if passages
            else "INSUFFICIENT_EVIDENCE"
        )

        return {
            "capability": capability,
            "status": status,
            "passage_count": len(passages),
            "passages": passages,
        }


__all__ = ["V12CapabilityEvidenceFinder"]
