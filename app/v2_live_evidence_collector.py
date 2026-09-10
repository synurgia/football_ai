from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.v2_evidence_manager import V2EvidenceManager
from app.v1_2_external_evidence_applier import V12ExternalEvidenceApplier
from app.v2_evidence_state import V2EvidenceState


class V2LiveEvidenceCollector:
    """
    V2 live-evidence collection framework.

    The collector receives verified/current data from external sources
    and writes it into the match-specific V2 evidence state.

    It does NOT replace Pieces 1-9.
    It does NOT fabricate missing information.
    """

    def __init__(self) -> None:
        self.manager = V2EvidenceManager()
        self.external_applier = V12ExternalEvidenceApplier()

    def create_match_state(
        self,
        match_id: str,
        competition: str,
        home_team: str,
        away_team: str,
    ) -> V2EvidenceState:
        return self.manager.create_state(
            match_id=match_id,
            competition=competition,
            home_team=home_team,
            away_team=away_team,
        )

    def collect_q10_mens_first_team(
        self,
        state: V2EvidenceState,
        home_team_data: Dict[str, Any],
        away_team_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Completed V2 collector for Q10.

        Expected explicit fields:

            {
                "team_type": "men_first_team"
            }

        Accepted explicit values:
            men_first_team
            men's_first_team
            mens_first_team

        Any other value, missing value, or ambiguous information
        remains UNKNOWN.
        """

        valid_values = {
            "men_first_team",
            "men's_first_team",
            "mens_first_team",
        }

        home_type = str(
            home_team_data.get("team_type", "")
        ).strip().lower()

        away_type = str(
            away_team_data.get("team_type", "")
        ).strip().lower()

        home_verified = home_type in valid_values
        away_verified = away_type in valid_values

        observed_at = datetime.now(timezone.utc).isoformat()

        if home_verified and away_verified:
            answer = "YES — both verified as men's first teams"
            evidence = (
                f"{state.home_team}: explicitly identified as a men's "
                f"first team; "
                f"{state.away_team}: explicitly identified as a men's "
                f"first team."
            )
            status = "VERIFIED"
            supports = "MATCH_CONTEXT"
            confidence = 1.0

        elif home_type or away_type:
            answer = "UNKNOWN"
            evidence = (
                "Team-type information is incomplete or does not "
                "explicitly verify both teams as men's first teams."
            )
            status = "INSUFFICIENT_EVIDENCE"
            supports = "UNKNOWN"
            confidence = None

        else:
            answer = "UNKNOWN"
            evidence = (
                "No explicit verified team-type information was supplied "
                "for either team."
            )
            status = "UNVERIFIED"
            supports = "UNKNOWN"
            confidence = None

        return self.manager.update_question(
            state=state,
            piece=2,
            question_id="Q10",
            answer=answer,
            evidence=evidence,
            supports=supports,
            confidence=confidence,
            source="incoming_verified_team_metadata",
            observed_at=observed_at,
            status=status,
        )

    def apply_external_evidence(self, state, envelope):
        """
        Apply externally collected evidence through the canonical
        V1.2 evidence applier.

        This does not answer questions semantically.
        """
        return self.external_applier.apply(state, envelope)

    def collect(
        self,
        state: V2EvidenceState,
        source_data: Optional[Dict[str, Any]] = None,
    ) -> V2EvidenceState:
        """
        Main collection entry point.

        At this stage Q10 is the only implemented live-evidence
        collector. All other questions remain preserved in the state
        until their dedicated collectors are implemented.
        """

        source_data = source_data or {}

        home_team_data = source_data.get("home_team", {})
        away_team_data = source_data.get("away_team", {})

        if isinstance(home_team_data, dict) and isinstance(
            away_team_data, dict
        ):
            self.collect_q10_mens_first_team(
                state,
                home_team_data,
                away_team_data,
            )

        return state

    def collection_status(
        self,
        state: V2EvidenceState,
    ) -> Dict[str, Any]:
        unresolved = self.manager.unresolved_questions(state)

        return {
            "match_id": state.match_id,
            "competition": state.competition,
            "home_team": state.home_team,
            "away_team": state.away_team,
            "total_questions": len(state.items),
            "resolved_questions": len(state.items) - len(unresolved),
            "unresolved_questions": len(unresolved),
        }
