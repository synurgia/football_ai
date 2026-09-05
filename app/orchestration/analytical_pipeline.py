from dataclasses import dataclass, field
from typing import Any, Dict

from app.models.match_data import PreMatchData


@dataclass
class AnalyticalResult:
    """
    Standard container for one analytical engine's result.
    The original engine implementations remain untouched.
    """
    piece: str
    success: bool
    output: Any = None
    error: str | None = None


@dataclass
class CombinedAnalyticalState:
    """
    Combined pre-match analytical state passed toward
    the Master Match Orchestrator.
    """
    match: PreMatchData
    results: Dict[str, AnalyticalResult] = field(default_factory=dict)

    def add_result(
        self,
        piece: str,
        output: Any,
    ) -> None:
        self.results[piece] = AnalyticalResult(
            piece=piece,
            success=True,
            output=output,
        )

    def add_error(
        self,
        piece: str,
        error: Exception,
    ) -> None:
        self.results[piece] = AnalyticalResult(
            piece=piece,
            success=False,
            error=f"{type(error).__name__}: {error}",
        )

    def successful_pieces(self) -> list[str]:
        return [
            name
            for name, result in self.results.items()
            if result.success
        ]

    def failed_pieces(self) -> list[str]:
        return [
            name
            for name, result in self.results.items()
            if not result.success
        ]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "match": self.match,
            "results": {
                name: {
                    "success": result.success,
                    "output": result.output,
                    "error": result.error,
                }
                for name, result in self.results.items()
            },
        }


class PreMatchAnalyticalPipeline:
    """
    Central integration layer for Pieces 1–8.

    IMPORTANT:
    This class does not replace or modify the original engines.
    Each existing engine will be connected through a dedicated
    adapter as its real input/output contract is confirmed.
    """

    def __init__(self, match: PreMatchData):
        self.match = match
        self.state = CombinedAnalyticalState(match=match)

    def validate_match(self) -> None:
        """
        Validate the minimum information required to begin
        pre-match analysis.
        """
        if not self.match.competition:
            raise ValueError("Competition is required.")

        if not self.match.home_team.team_name:
            raise ValueError("Home team name is required.")

        if not self.match.away_team.team_name:
            raise ValueError("Away team name is required.")

        if self.match.home_team.is_home is not True:
            raise ValueError(
                "Home team must have is_home=True."
            )

        if self.match.away_team.is_home is not False:
            raise ValueError(
                "Away team must have is_home=False."
            )

    def run(self) -> CombinedAnalyticalState:
        """
        Entry point for the complete pre-match analytical pipeline.

        Existing Pieces 1–8 are connected through adapters.
        The original source engines remain untouched.
        """
        self.validate_match()

        from app.orchestration.piece01_adapter import run_piece01

        try:
            result = run_piece01(self.match)
            self.state.add_result("piece01", result)
        except Exception as exc:
            self.state.add_error("piece01", exc)

        from app.orchestration.piece02_adapter import run_piece02

        try:
            result = run_piece02(self.match)
            self.state.add_result("piece02", result)
        except Exception as exc:
            self.state.add_error("piece02", exc)

        return self.state

    def summary(self) -> Dict[str, Any]:
        """
        Compact status summary for testing and diagnostics.
        """
        return {
            "match": (
                f"{self.match.home_team.team_name} vs "
                f"{self.match.away_team.team_name}"
            ),
            "competition": self.match.competition,
            "successful_pieces": self.state.successful_pieces(),
            "failed_pieces": self.state.failed_pieces(),
            "pieces_received": len(self.state.results),
        }
