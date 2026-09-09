from __future__ import annotations

from typing import Any, Dict


class V12AdvantageSynthesis:
    """
    V1.2 advantage synthesis layer.

    Converts resolved question evidence into a controlled matchup
    advantage assessment.

    Rules:
    - VERIFIED evidence may contribute.
    - UNKNOWN / UNVERIFIED / INSUFFICIENT evidence contributes nothing.
    - Evidence supporting HOME increases home score.
    - Evidence supporting AWAY increases away score.
    - Evidence supporting BOTH/NEUTRAL does not create team advantage.
    - This layer does not modify Piece 9 probabilities.
    """

    VALID_STATUSES = {
        "VERIFIED",
    }

    HOME_VALUES = {"HOME", "HOME_ADVANTAGE", "HOME_TEAM"}
    AWAY_VALUES = {"AWAY", "AWAY_ADVANTAGE", "AWAY_TEAM"}
    NEUTRAL_VALUES = {
        "BOTH",
        "BALANCED",
        "NEUTRAL",
        "NONE",
        "NEITHER",
        "DRAW",
        "UNKNOWN",
    }

    def synthesize(self, state) -> Dict[str, Any]:
        home_score = 0
        away_score = 0
        neutral_count = 0
        usable_count = 0

        contributions = []

        for item in state.items:
            status = str(item.status).upper()

            if status not in self.VALID_STATUSES:
                continue

            support = self._classify_support(item)

            if support == "HOME":
                home_score += 1
                usable_count += 1
            elif support == "AWAY":
                away_score += 1
                usable_count += 1
            elif support == "NEUTRAL":
                neutral_count += 1

            if support != "UNUSABLE":
                contributions.append({
                    "question_id": item.question_id,
                    "support": support,
                    "confidence": item.confidence,
                    "impact": item.impact,
                })

        total_directional = home_score + away_score

        if usable_count == 0:
            decision = "INSUFFICIENT_EVIDENCE"
        elif home_score > away_score:
            decision = "HOME_ADVANTAGE"
        elif away_score > home_score:
            decision = "AWAY_ADVANTAGE"
        else:
            decision = "BALANCED"

        return {
            "decision": decision,
            "home_score": home_score,
            "away_score": away_score,
            "neutral_count": neutral_count,
            "usable_directional_evidence": total_directional,
            "resolved_questions": len(state.items),
            "contributions": contributions,
        }

    def _classify_support(self, item) -> str:
        """
        Determine whether the resolved answer explicitly supports
        the home team, away team, or neither.

        No inference is made from arbitrary evidence text.
        """
        answer = str(item.answer).upper().strip()

        if answer in self.HOME_VALUES:
            return "HOME"

        if answer in self.AWAY_VALUES:
            return "AWAY"

        if answer in self.NEUTRAL_VALUES:
            return "NEUTRAL"

        supports = str(item.supports).upper().strip()

        if supports in self.HOME_VALUES:
            return "HOME"

        if supports in self.AWAY_VALUES:
            return "AWAY"

        if supports in self.NEUTRAL_VALUES:
            return "NEUTRAL"

        return "UNUSABLE"
