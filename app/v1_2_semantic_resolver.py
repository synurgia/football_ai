from __future__ import annotations

from typing import Any, Dict, Optional

from app.v1_2_question_resolver import V12QuestionResolver


class V12SemanticResolver:
    """
    V1.2 semantic resolver for the existing 37-question framework.

    Responsibilities:
    - read existing Pieces 1-8 analytical output;
    - derive question-specific answers only from available evidence;
    - preserve UNKNOWN / INSUFFICIENT_EVIDENCE when evidence is inadequate;
    - use the existing V12QuestionResolver to write state;
    - never create a second question registry;
    - never modify Piece 9 simulation logic.
    """

    def __init__(self) -> None:
        self.resolver = V12QuestionResolver()

    def resolve_all(
        self,
        state,
        analytical_state,
    ):
        """
        Resolve the registered questions from existing analytical evidence.
        """
        pieces = analytical_state.results

        self._q1_q6(state, pieces)
        self._q7_q13(state, pieces)
        self._q14_q19(state, pieces)
        self._q24_q30(state, pieces)
        self._q31_q34(state, pieces)
        self._q35_q37(state, pieces)
        self._q38_q41(state, pieces)

        return state

    def _q1_q6(self, state, pieces):
        output = self._output(pieces, "piece01")

        if output is None:
            for q in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6"):
                self._unknown(state, q, "Piece 1 evidence is unavailable.")
            return

        framework = output.get("competition_framework", {})
        home = output.get("team_a_analysis", {})
        away = output.get("team_b_analysis", {})
        synthesis = output.get("cross_board_synthesis", {})

        self._answer(
            state, "Q1",
            framework.get("penalty_on_draw"),
            framework.get("penalty_on_draw"),
            "piece01",
        )

        self._answer(
            state, "Q2",
            framework.get("special_point_rules"),
            framework.get("special_point_rules"),
            "piece01",
        )

        self._answer(
            state, "Q3",
            self._compare_bool(home, away, "financial_backing"),
            {
                "home": home.get("financial_backing"),
                "away": away.get("financial_backing"),
                "home_context": home.get("funding_context"),
                "away_context": away.get("funding_context"),
            },
            "piece01",
        )

        self._answer(
            state, "Q4",
            "AVAILABLE",
            {
                "home": home.get("squad_changes_analysis"),
                "away": away.get("squad_changes_analysis"),
            },
            "piece01",
        )

        self._answer(
            state, "Q5",
            self._compare_bool(home, away, "must_win_status"),
            {
                "home": home.get("must_win_status"),
                "away": away.get("must_win_status"),
                "urgency_asymmetry": synthesis.get("urgency_asymmetry"),
            },
            "piece01",
        )

        scoring = synthesis.get("scoring_edge", {})
        self._answer(
            state, "Q6",
            scoring.get("leader"),
            scoring,
            "piece01",
        )

    def _q7_q13(self, state, pieces):
        p2 = self._output(pieces, "piece02")
        p3 = self._output(pieces, "piece03")

        if p2 is None:
            for q in ("Q7", "Q8"):
                self._unknown(state, q, "Piece 2 evidence is unavailable.")
        else:
            teams = list(p2.values())

            self._answer(
                state,
                "Q7",
                self._collect_values(
                    teams, "war_conflict_analysis", "impact_level"
                ),
                p2,
                "piece02",
            )

            self._answer(
                state,
                "Q8",
                self._collect_values(
                    teams, "public_hype_analysis", "trap_risk"
                ),
                p2,
                "piece02",
            )

        if p3 is not None:
            must_win = p3.get("must_win", {})
            step17 = must_win.get("step_17_choice", {})
            verification = p3.get("verification", {})

            self._answer(
                state,
                "Q9",
                step17.get("selected_outcome_1x2"),
                must_win,
                "piece03",
            )

            self._answer(
                state,
                "Q13",
                {
                    "poisson": p3.get("poisson"),
                    "hybrid_consensus": p3.get("hybrid_consensus"),
                },
                {
                    "poisson": p3.get("poisson"),
                    "hybrid_consensus": p3.get("hybrid_consensus"),
                    "verification": verification,
                },
                "piece03",
            )
        else:
            self._unknown(state, "Q9", "Model evidence is unavailable.")
            self._unknown(state, "Q13", "Model evidence is unavailable.")

        self._unknown(
            state,
            "Q10",
            "Q10 remains owned by the existing live evidence collector.",
        )

        if p3 is not None:
            matrix = p3.get("five_dimensional", {}).get(
                "prediction_matrix", {}
            )

            self._answer(
                state,
                "Q11",
                p3.get("must_win", {}).get("win_or_die_evaluation"),
                p3.get("must_win"),
                "piece03",
            )

            self._answer(
                state,
                "Q12",
                p3.get("five_dimensional", {}).get("5d_predictive_state"),
                matrix,
                "piece03",
            )

    def _q14_q19(self, state, pieces):
        p3 = self._output(pieces, "piece03")
        p4 = self._output(pieces, "piece04")

        if p3 is not None:
            self._answer(
                state,
                "Q14",
                p3.get("five_dimensional", {}).get("5d_predictive_state"),
                p3.get("five_dimensional"),
                "piece03",
            )

            self._answer(
                state,
                "Q15",
                {
                    "home": p3.get("five_dimensional", {}).get("home_history"),
                    "away": p3.get("five_dimensional", {}).get("away_history"),
                },
                p3.get("five_dimensional"),
                "piece03",
            )

            self._answer(
                state,
                "Q16",
                {
                    "poisson": p3.get("poisson"),
                    "hybrid_consensus": p3.get("hybrid_consensus"),
                },
                {
                    "poisson": p3.get("poisson"),
                    "hybrid_consensus": p3.get("hybrid_consensus"),
                    "verification": p3.get("verification"),
                },
                "piece03",
            )

            self._answer(
                state,
                "Q17",
                p3.get("must_win", {}).get("step_17_choice"),
                p3.get("must_win"),
                "piece03",
            )
        else:
            for q in ("Q14", "Q15", "Q16", "Q17"):
                self._unknown(state, q, "Piece 3 evidence is unavailable.")

        if p4 is not None:
            tactical = p4.get("tactical_research", {})
            rankings = p4.get("rankings", {})

            self._answer(
                state,
                "Q18",
                {
                    "home": tactical.get("home_team_analysis"),
                    "away": tactical.get("away_team_analysis"),
                    "exploits": tactical.get("step_18_tactical_exploits"),
                },
                tactical,
                "piece04",
            )

            self._answer(
                state,
                "Q19",
                rankings.get("competing_matchup_analysis"),
                rankings,
                "piece04",
            )
        else:
            self._unknown(state, "Q18", "Piece 4 evidence is unavailable.")
            self._unknown(state, "Q19", "Piece 4 evidence is unavailable.")

    def _q24_q30(self, state, pieces):
        p5 = self._output(pieces, "piece05")

        if p5 is None:
            for q in ("Q24", "Q25", "Q26", "Q27", "Q28", "Q29", "Q30"):
                self._unknown(state, q, "Piece 5 evidence is unavailable.")
            return

        self._answer(
            state, "Q24",
            p5.get("underdog_odds"),
            p5.get("underdog_odds"),
            "piece05",
        )

        self._answer(
            state, "Q25",
            p5.get("favorite_schedule", {}).get("step_25_context"),
            p5.get("favorite_schedule"),
            "piece05",
        )

        self._answer(
            state, "Q26",
            p5.get("weather_disruption", {}).get(
                "step_26_disruption_assessment"
            ),
            p5.get("weather_disruption"),
            "piece05",
        )

        self._answer(
            state, "Q27",
            p5.get("team_gap", {}).get("gap_classification"),
            p5.get("team_gap"),
            "piece05",
        )

        self._answer(
            state, "Q28",
            p5.get("motivation", {}).get("step_28_motivation"),
            p5.get("motivation"),
            "piece05",
        )

        self._answer(
            state, "Q29",
            p5.get("market_tactical_resistance", {}).get(
                "step_29_resistance"
            ),
            p5.get("market_tactical_resistance"),
            "piece05",
        )

        self._answer(
            state, "Q30",
            p5.get("recent_form"),
            p5.get("recent_form"),
            "piece05",
        )

    def _q31_q34(self, state, pieces):
        p6 = self._output(pieces, "piece06")

        if p6 is None:
            for q in ("Q31", "Q32", "Q33", "Q34"):
                self._unknown(state, q, "Piece 6 evidence is unavailable.")
            return

        self._answer(
            state,
            "Q31",
            p6.get("tactical_defensive"),
            {
                "resistance": p6.get("resistance"),
                "tactical_defensive": p6.get("tactical_defensive"),
            },
            "piece06",
        )

        self._answer(
            state,
            "Q32",
            p6.get("tactical_defensive"),
            p6.get("tactical_defensive"),
            "piece06",
        )

        self._answer(
            state,
            "Q33",
            p6.get("offensive_transition"),
            p6.get("offensive_transition"),
            "piece06",
        )

        self._answer(
            state,
            "Q34",
            p6.get("league_schedule_context"),
            p6.get("league_schedule_context"),
            "piece06",
        )

    def _q35_q37(self, state, pieces):
        p7 = self._output(pieces, "piece07")

        if p7 is None:
            for q in ("Q35", "Q36", "Q37"):
                self._unknown(state, q, "Piece 7 evidence is unavailable.")
            return

        self._answer(
            state,
            "Q35",
            p7.get("statistical_filter", {}).get("matchup_profile"),
            p7.get("statistical_filter"),
            "piece07",
        )

        self._answer(
            state,
            "Q36",
            {
                "h2h": p7.get("statistical_filter", {}).get("h2h"),
                "upset_flag": p7.get("statistical_filter", {})
                .get("matchup_profile", {})
                .get("upset_flag"),
            },
            p7.get("statistical_filter"),
            "piece07",
        )

        self._answer(
            state,
            "Q37",
            p7.get("bayesian_adjustment"),
            p7.get("bayesian_adjustment"),
            "piece07",
        )

    def _q38_q41(self, state, pieces):
        p8 = self._output(pieces, "piece08")

        if p8 is None:
            for q in ("Q38", "Q39", "Q40", "Q41"):
                self._unknown(state, q, "Piece 8 evidence is unavailable.")
            return

        self._answer(
            state,
            "Q38",
            p8.get("referee_analysis"),
            p8.get("referee_analysis"),
            "piece08",
        )

        self._answer(
            state,
            "Q39",
            p8.get("pitch_and_roster_micro_factors"),
            p8.get("pitch_and_roster_micro_factors"),
            "piece08",
        )

        self._answer(
            state,
            "Q40",
            p8.get("pitch_and_roster_micro_factors"),
            p8.get("pitch_and_roster_micro_factors"),
            "piece08",
        )

        self._answer(
            state,
            "Q41",
            p8.get("starting_xi_analysis"),
            p8.get("starting_xi_analysis"),
            "piece08",
        )

    @staticmethod
    def _output(pieces, name: str) -> Optional[Dict[str, Any]]:
        result = pieces.get(name)

        if result is None or not result.success:
            return None

        output = result.output

        return output if isinstance(output, dict) else None

    def _answer(self, state, question_id, answer, evidence, source):
        if answer is None:
            self._unknown(
                state,
                question_id,
                f"No usable answer was exposed by {source}.",
            )
            return

        if self._evidence_is_insufficient(answer, evidence):
            self._unknown(
                state,
                question_id,
                f"{source} output explicitly indicates that required evidence is unavailable or insufficient.",
            )
            return

        self.resolver.resolve(
            state,
            question_id,
            answer=str(answer),
            evidence=evidence,
            supports="ANALYTICAL_EVIDENCE",
            source=source,
            source_reference=f"{source}:{question_id}",
            status="VERIFIED",
        )

    @staticmethod
    def _evidence_is_insufficient(answer, evidence) -> bool:
        """
        Detect explicit absence/insufficiency signals in existing Piece output.

        This does not infer football meaning. It only prevents an output
        that explicitly reports missing data from being labelled VERIFIED.
        """
        text = f"{answer} {evidence}".upper()


        if str(answer).strip().upper() in {"UNKNOWN", "NONE", "NULL"}:
            return True
        explicit_signals = (
            "INSUFFICIENT DEPTH",
            "INSUFFICIENT DATA",
            "NO MATCH HISTORY",
            "NO VALID ODDS",
            "NOT FOUND",
            "NOT SUPPLIED",
            "UNAVAILABLE",
            "AVAILABLE': FALSE",
            '"AVAILABLE": FALSE',
            "REQUIRED.",
            "IS REQUIRED",
        )

        return any(signal in text for signal in explicit_signals)

    def _unknown(self, state, question_id, reason):
        self.resolver.resolve(
            state,
            question_id,
            answer="UNKNOWN",
            evidence=reason,
            supports="UNKNOWN",
            source=None,
            source_reference=None,
            status="INSUFFICIENT_EVIDENCE",
            notes=reason,
        )

    @staticmethod
    def _compare_bool(
        left: Dict[str, Any],
        right: Dict[str, Any],
        field: str,
    ) -> str:
        home = left.get(field)
        away = right.get(field)

        if home is True and away is True:
            return "BOTH"

        if home is True:
            return "HOME"

        if away is True:
            return "AWAY"

        if home is False and away is False:
            return "NEITHER"

        return "UNKNOWN"

    @staticmethod
    def _collect_values(
        teams,
        section: str,
        field: str,
    ):
        values = []

        for team in teams:
            section_data = team.get(section, {})
            if field in section_data:
                values.append(section_data[field])

        if not values:
            return None

        return values
