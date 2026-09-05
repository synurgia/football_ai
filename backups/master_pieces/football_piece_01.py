from dataclasses import dataclass, field
from typing import List, Dict, Any


# =====================================================================
# ANSI TERMINAL COLORS FOR TERMUX / PYDROID 3 OUTPUT
# =====================================================================

GREEN_ANSI = "\033[92m"
RED_ANSI = "\033[91m"
YELLOW_ANSI = "\033[93m"
BLUE_ANSI = "\033[94m"
RESET_ANSI = "\033[0m"


# =====================================================================
# 1. COMPETITION / PENALTY RULES
# =====================================================================

@dataclass
class CompetitionRules:
    """
    Defines the competition framework.

    Rule 1:
        Whether a full-time draw goes to penalties.

    Rule 2:
        Whether the competition awards special points
        associated with the penalty shootout.
    """
    goes_to_penalties_on_draw: bool
    penalty_points_awarded: bool
    tournament_name: str


@dataclass
class MatchRulesEvaluator:
    team_a: str
    team_b: str
    goes_to_penalties_on_draw: bool
    penalty_point_rule_applies: bool

    def _get_box_status(self, condition: bool) -> Dict[str, str]:
        """
        Returns visual indicator metadata for CLI, APIs,
        and UI mockups.
        """

        if condition:
            return {
                "status": "YES",
                "color_name": "GREEN",
                "hex_code": "#2ECC71",
                "cli_box": (
                    f"{GREEN_ANSI}"
                    "███ [ GREEN BOX: YES ] ███"
                    f"{RESET_ANSI}"
                )
            }

        return {
            "status": "NO",
            "color_name": "RED",
            "hex_code": "#E74C3C",
            "cli_box": (
                f"{RED_ANSI}"
                "███ [ RED BOX: NO ] ███"
                f"{RESET_ANSI}"
            )
        }

    def evaluate(self) -> Dict[str, Any]:
        """
        Evaluates both competition-rule variables and
        generates a structured data payload.
        """

        rule_1_indicator = self._get_box_status(
            self.goes_to_penalties_on_draw
        )

        rule_2_indicator = self._get_box_status(
            self.penalty_point_rule_applies
        )

        return {
            "fixture": f"{self.team_a} vs {self.team_b}",

            "rule_1_penalties_on_draw": {
                "active": self.goes_to_penalties_on_draw,
                "description": (
                    "Match goes to penalties if tied at full-time."
                ),
                "box": rule_1_indicator
            },

            "rule_2_penalty_points": {
                "active": self.penalty_point_rule_applies,
                "description": (
                    "Special penalty points allocated "
                    "(e.g., point earned for penalty loss/win)."
                ),
                "box": rule_2_indicator
            }
        }

    def print_display(self) -> None:
        """
        Renders colored visual output in the terminal.
        """

        data = self.evaluate()

        print("\n" + "=" * 60)
        print(f" MATCH CONTEXT: {data['fixture']}")
        print("=" * 60)

        r1 = data["rule_1_penalties_on_draw"]

        print("1. Penalties on Full-Time Draw?")
        print(f"   {r1['box']['cli_box']}")
        print(f"   Note: {r1['description']}\n")

        r2 = data["rule_2_penalty_points"]

        print("2. Special Penalty Point Rule Applies?")
        print(f"   {r2['box']['cli_box']}")
        print(f"   Note: {r2['description']}")

        print("=" * 60 + "\n")


# =====================================================================
# 2. TEAM FUNDING + MAJOR CHANGES
# =====================================================================

# FIX: Redefine TeamChange with numeric impact_score instead of impact_level
@dataclass
class TeamChange:
    """
    Represents a major team change.
    impact_score: positive for beneficial, negative for disruptive.
    """
    change_type: str
    description: str
    impact_score: float


@dataclass
class TeamContext:
    name: str
    has_big_funding: bool
    funding_description: str = ""
    changes: List[TeamChange] = field(default_factory=list)


class MatchIntelligenceEvaluator:

    def __init__(
        self,
        team_a: TeamContext,
        team_b: TeamContext
    ):
        self.team_a = team_a
        self.team_b = team_b

    def _evaluate_funding(
        self,
        team: TeamContext
    ) -> Dict[str, Any]:
        """
        Rule 3:
        Evaluates funding disparity / financial injection.
        """

        if team.has_big_funding:

            return {
                "status": "YES",

                "box": (
                    f"{GREEN_ANSI}"
                    "███ [ GREEN BOX: BIG FUNDING ] ███"
                    f"{RESET_ANSI}"
                ),

                "detail": (
                    team.funding_description
                    or
                    "Major financial backing/takeover present."
                )
            }

        return {
            "status": "NO",

            "box": (
                f"{RED_ANSI}"
                "███ [ RED BOX: STANDARD FUNDING ] ███"
                f"{RESET_ANSI}"
            ),

            "detail": "Standard operating budget."
        }

    def _analyze_impact(
        self,
        changes: List[TeamChange]
    ) -> Dict[str, Any]:
        """
        Rule 4:
        Analyzes major changes and generates dynamic advice.
        Uses impact_score to determine positive/negative.
        """

        if not changes:

            return {
                "changes_list": [],
                "advice": (
                    "Stable environment. "
                    "No major changes reported."
                ),
                "morale_index": "STABLE",
                "color": RESET_ANSI
            }

        negative_count = 0
        positive_count = 0
        descriptions = []

        for change in changes:

            descriptions.append(
                f"• [{change.change_type}] "
                f"{change.description}"
            )

            # FIX: use impact_score instead of impact_level string
            if change.impact_score < 0:
                negative_count += 1
            elif change.impact_score > 0:
                positive_count += 1

        if negative_count > positive_count:

            advice = (
                "CAUTION: Disruption likely. "
                "Key losses or tactical instability may "
                "cause short-term friction."
            )

            morale = "HIGH DISRUPTIVE RISK"
            color = RED_ANSI

        elif positive_count > negative_count:

            advice = (
                "ADVANTAGE: Positive momentum expected "
                "(e.g., new manager boost or squad reinforcement)."
            )

            morale = "BOOSTED"
            color = GREEN_ANSI

        else:

            advice = (
                "NEUTRAL: Mixed adjustments; "
                "team stability remains balanced."
            )

            morale = "BALANCED"
            color = YELLOW_ANSI

        return {
            "changes_list": descriptions,
            "advice": advice,
            "morale_index": morale,
            "color": color
        }

    def print_assessment(self) -> None:
        """
        Renders the assessment directly to console.
        """

        print("\n" + "=" * 65)

        print(
            f" MATCH INTELLIGENCE: "
            f"{self.team_a.name} vs {self.team_b.name}"
        )

        print("=" * 65)

        for team in [self.team_a, self.team_b]:

            print(f"\n[{team.name.upper()}]")

            # -------------------------------------------------------
            # RULE 3: FUNDING
            # -------------------------------------------------------

            funding_info = self._evaluate_funding(team)

            print("3. Big Funding/Financial Edge?")
            print(f"   {funding_info['box']}")
            print(f"   Detail: {funding_info['detail']}")

            # -------------------------------------------------------
            # RULE 4: MAJOR CHANGES
            # -------------------------------------------------------

            change_info = self._analyze_impact(team.changes)

            print("4. Major Changes & Advisory Impact:")

            if "changes_list" in change_info:

                for line in change_info["changes_list"]:
                    print(f"   {line}")

            print(
                f"   {change_info['color']}"
                f"ADVICE: {change_info['advice']}"
                f"{RESET_ANSI}"
            )

            print("-" * 65)


# =====================================================================
# 3. MUST-WIN + GOAL-SCORING PROBABILITY
# =====================================================================

@dataclass
class TeamGoalMetrics:
    """
    Rule 5:
        Must-win status.

    Rule 6:
        Goal-scoring probability.
    """

    name: str
    is_must_win: bool
    must_win_reason: str
    scoring_probability: float


class MatchDynamicsEvaluator:

    def __init__(
        self,
        team_a: TeamGoalMetrics,
        team_b: TeamGoalMetrics
    ):
        self.team_a = team_a
        self.team_b = team_b

    def evaluate_must_win(
        self,
        team: TeamGoalMetrics
    ) -> Dict[str, Any]:
        """
        Rule 5:
        Evaluates top-tier must-win status and motivation.
        """

        if team.is_must_win:

            return {
                "must_win": True,
                "status": "MUST WIN",

                "box": (
                    f"{GREEN_ANSI}"
                    "███ [ GREEN BOX: MUST WIN ] ███"
                    f"{RESET_ANSI}"
                ),

                "reason": team.must_win_reason
            }

        return {
            "must_win": False,
            "status": "STANDARD / LOW URGENCY",

            "box": (
                f"{RED_ANSI}"
                "███ [ RED BOX: NOT MUST WIN ] ███"
                f"{RESET_ANSI}"
            ),

            "reason": (
                team.must_win_reason
                or
                "Standard league fixture, low pressure."
            )
        }

    def evaluate_scoring_edge(self) -> Dict[str, Any]:
        """
        Rule 6:
        Identifies which team has the higher
        goal-scoring probability.
        """

        prob_a = self.team_a.scoring_probability
        prob_b = self.team_b.scoring_probability

        if prob_a > prob_b:

            diff = (prob_a - prob_b) * 100

            top_team = self.team_a.name

            msg = (
                f"{top_team} holds the scoring edge "
                f"(+{diff:.1f}% higher probability)."
            )

            color = GREEN_ANSI

        elif prob_b > prob_a:

            diff = (prob_b - prob_a) * 100

            top_team = self.team_b.name

            msg = (
                f"{top_team} holds the scoring edge "
                f"(+{diff:.1f}% higher probability)."
            )

            color = GREEN_ANSI

        else:

            top_team = "EVEN"

            msg = (
                "Both teams have identical "
                "goal scoring probabilities."
            )

            color = YELLOW_ANSI

        return {
            "top_team": top_team,
            "prob_a_pct": round(prob_a * 100, 1),
            "prob_b_pct": round(prob_b * 100, 1),
            "edge_message": msg,
            "color": color
        }

    def print_assessment(self) -> None:
        """
        Renders formatted terminal output.
        """

        print("\n" + "=" * 65)

        print(
            f" MATCH DYNAMICS: "
            f"{self.team_a.name} vs {self.team_b.name}"
        )

        print("=" * 65)

        # -----------------------------------------------------------
        # RULE 5
        # -----------------------------------------------------------

        print("\n5. TOP TIER MUST-WIN EVALUATION:")

        for team in [self.team_a, self.team_b]:

            must_win = self.evaluate_must_win(team)

            print(f"   [{team.name.upper()}]")
            print(f"   {must_win['box']}")
            print(
                f"   Context: {must_win['reason']}\n"
            )

        # -----------------------------------------------------------
        # RULE 6
        # -----------------------------------------------------------

        edge = self.evaluate_scoring_edge()

        print("-" * 65)

        print("6. HIGHEST GOAL SCORING PROBABILITY:")

        print(
            f"   • {self.team_a.name}: "
            f"{edge['prob_a_pct']}%"
        )

        print(
            f"   • {self.team_b.name}: "
            f"{edge['prob_b_pct']}%"
        )

        print(
            f"   {edge['color']}"
            f"★ RESULT: {edge['edge_message']}"
            f"{RESET_ANSI}"
        )

        print("=" * 65 + "\n")


# =====================================================================
# 4. INTEGRATED MATCH ANALYTICAL ENGINE
# =====================================================================

class MatchAnalyticalEngine:

    def __init__(
        self,
        rules: CompetitionRules,
        team_a: "TeamProfile",
        team_b: "TeamProfile"
    ):

        self.rules = rules
        self.team_a = team_a
        self.team_b = team_b

    def _analyze_squad_changes(
        self,
        team: "TeamProfile"
    ) -> Dict[str, Any]:
        """
        Calculates net impact vector from roster
        and tactical changes.
        """

        if not team.changes:

            return {
                "net_impact": 0.0,
                "status": "Stable",
                "details": []
            }

        net_impact = sum(
            change.impact_score
            for change in team.changes
        )

        if net_impact > 0.2:

            status = "Net Positive Alignment"

        elif net_impact < -0.2:

            status = "Net Negative Disruption"

        else:

            status = "Balanced / Neutral Adjustment"

        # FIX: use change_type instead of category
        details = [

            f"[{change.change_type}] "
            f"{change.description} "
            f"(Impact: {change.impact_score:+.2f})"

            for change in team.changes
        ]

        return {
            "net_impact": round(net_impact, 2),
            "status": status,
            "details": details
        }

    def _compute_scoring_edge(self) -> Dict[str, Any]:
        """
        Analyzes scoring probability differential
        across the board.
        """

        prob_a = self.team_a.scoring_probability
        prob_b = self.team_b.scoring_probability

        diff = abs(prob_a - prob_b)

        if prob_a > prob_b:

            leader = self.team_a.name
            lagging = self.team_b.name

        elif prob_b > prob_a:

            leader = self.team_b.name
            lagging = self.team_a.name

        else:

            return {
                "leader": None,
                "differential_pct": 0.0,
                "analysis": (
                    "Equal goal-scoring probabilities "
                    "across both teams."
                )
            }

        return {
            "leader": leader,
            "differential_pct": round(diff * 100, 2),

            "analysis": (
                f"{leader} holds a +"
                f"{diff * 100:.1f}% probability edge "
                f"over {lagging}."
            )
        }

    def run_full_analysis(self) -> Dict[str, Any]:
        """
        Executes full cross-board analytical sweep
        across all 6 variables.
        """

        changes_a = self._analyze_squad_changes(
            self.team_a
        )

        changes_b = self._analyze_squad_changes(
            self.team_b
        )

        scoring_edge = self._compute_scoring_edge()

        return {

            "competition_framework": {

                "tournament":
                    self.rules.tournament_name,

                "penalty_on_draw":
                    self.rules.goes_to_penalties_on_draw,

                "special_point_rules":
                    self.rules.penalty_points_awarded
            },

            "team_a_analysis": {

                "name":
                    self.team_a.name,

                "financial_backing":
                    self.team_a.has_major_funding,

                "funding_context":
                    self.team_a.funding_notes,

                "must_win_status":
                    self.team_a.is_must_win,

                "urgency_context":
                    self.team_a.must_win_context,

                "scoring_probability_pct":
                    round(
                        self.team_a.scoring_probability * 100,
                        2
                    ),

                "squad_changes_analysis":
                    changes_a
            },

            "team_b_analysis": {

                "name":
                    self.team_b.name,

                "financial_backing":
                    self.team_b.has_major_funding,

                "funding_context":
                    self.team_b.funding_notes,

                "must_win_status":
                    self.team_b.is_must_win,

                "urgency_context":
                    self.team_b.must_win_context,

                "scoring_probability_pct":
                    round(
                        self.team_b.scoring_probability * 100,
                        2
                    ),

                "squad_changes_analysis":
                    changes_b
            },

            "cross_board_synthesis": {

                "scoring_edge":
                    scoring_edge,

                "urgency_asymmetry":
                    self.team_a.is_must_win
                    !=
                    self.team_b.is_must_win,

                "funding_disparity":
                    self.team_a.has_major_funding
                    !=
                    self.team_b.has_major_funding
            }
        }

    def print_report(self) -> None:
        """
        Outputs the complete analytical report.
        """

        data = self.run_full_analysis()

        comp = data["competition_framework"]
        team_a = data["team_a_analysis"]
        team_b = data["team_b_analysis"]
        synthesis = data["cross_board_synthesis"]

        print("\n" + "=" * 75)

        print(
            f"SYSTEM MATCH ANALYSIS: "
            f"{team_a['name']} vs {team_b['name']}"
        )

        print(
            f"Competition: {comp['tournament']}"
        )

        print("=" * 75)

        # -----------------------------------------------------------
        # RULES 1 & 2
        # -----------------------------------------------------------

        print("\n[1 & 2] COMPETITION & PENALTY STRUCTURE")

        print(
            f"  • Full-Time Draw Penalties : "
            f"{comp['penalty_on_draw']}"
        )

        print(
            f"  • Shootout Point Rule      : "
            f"{comp['special_point_rules']}"
        )

        # -----------------------------------------------------------
        # RULES 3, 4, 5 & 6
        # -----------------------------------------------------------

        print("\n[3, 4, 5 & 6] TEAM METRICS BARS")

        for team in [team_a, team_b]:

            print(
                f"\n--- {team['name'].upper()} ---"
            )

            # RULE 3

            print(
                "  • Financial Funding Level : "
                f"{'Major Backing' if team['financial_backing'] else 'Standard Budget'}"
            )

            print(
                f"    Notes                   : "
                f"{team['funding_context']}"
            )

            # RULE 5

            print(
                "  • Urgency / Must-Win      : "
                f"{team['must_win_status']}"
            )

            print(
                f"    Context                 : "
                f"{team['urgency_context']}"
            )

            # RULE 6

            print(
                "  • Scoring Probability     : "
                f"{team['scoring_probability_pct']}%"
            )

            # RULE 4

            squad_analysis = team[
                "squad_changes_analysis"
            ]

            print(
                "  • Internal Adjustments    : "
                f"{squad_analysis['status']} "
                f"(Net Vector: "
                f"{squad_analysis['net_impact']:+.2f})"
            )

            for item in squad_analysis["details"]:

                print(
                    f"      {item}"
                )

        # -----------------------------------------------------------
        # CROSS-BOARD SYNTHESIS
        # -----------------------------------------------------------

        print("\n" + "=" * 75)

        print(
            "CROSS-BOARD SYSTEM SYNTHESIS"
        )

        print("=" * 75)

        print(
            "  • Scoring Probability Edge : "
            f"{synthesis['scoring_edge']['analysis']}"
        )

        print(
            "  • Urgency Asymmetry       : "
            f"{synthesis['urgency_asymmetry']} "
            "(One-sided high motivation pressure)"
        )

        print(
            "  • Financial Disparity     : "
            f"{synthesis['funding_disparity']}"
        )

        print("=" * 75 + "\n")


# =====================================================================
# 5. TEAM PROFILE
# =====================================================================

@dataclass
class TeamProfile:
    name: str

    has_major_funding: bool

    funding_notes: str

    is_must_win: bool

    must_win_context: str

    scoring_probability: float

    changes: List[TeamChange] = field(
        default_factory=list
    )


# =====================================================================
# 6. EXECUTION PIPELINE
# =====================================================================

if __name__ == "__main__":

    # ================================================================
    # COMPETITION RULES
    # ================================================================

    rules = CompetitionRules(

        tournament_name="CONCACAF Leagues Cup",

        goes_to_penalties_on_draw=True,

        penalty_points_awarded=True
    )

    # ================================================================
    # TEAM A
    # ================================================================

    # FIX: use change_type and impact_score (not category/impact_level)
    team_a = TeamProfile(

        name="Team A",

        has_major_funding=True,

        funding_notes=(
            "Acquired new ownership with "
            "high transfer spend."
        ),

        is_must_win=True,

        must_win_context=(
            "Requires 3 points to secure "
            "top seed advance."
        ),

        scoring_probability=0.68,

        changes=[

            TeamChange(
                change_type="Managerial",
                description=(
                    "New head coach appointed "
                    "5 days prior."
                ),
                impact_score=-0.30
            ),

            TeamChange(
                change_type="Roster",
                description=(
                    "Starting center-back "
                    "return from suspension."
                ),
                impact_score=+0.15
            )
        ]
    )

    # ================================================================
    # TEAM B
    # ================================================================

    team_b = TeamProfile(

        name="Team B",

        has_major_funding=False,

        funding_notes=(
            "Operating under mid-table "
            "payroll constraints."
        ),

        is_must_win=False,

        must_win_context=(
            "Already mathematically eliminated "
            "from next round."
        ),

        scoring_probability=0.42,

        changes=[

            TeamChange(
                change_type="Tactical",
                description=(
                    "Transitioned to defensive "
                    "5-3-2 setup."
                ),
                impact_score=+0.10
            )
        ]
    )

    # ================================================================
    # RUN RULES 1 & 2
    # ================================================================

    match_rules = MatchRulesEvaluator(

        team_a=team_a.name,

        team_b=team_b.name,

        goes_to_penalties_on_draw=
            rules.goes_to_penalties_on_draw,

        penalty_point_rule_applies=
            rules.penalty_points_awarded
    )

    match_rules.print_display()

    # ================================================================
    # RUN RULES 3 & 4
    # ================================================================

    # FIX: pass changes directly (no conversion needed)
    intelligence = MatchIntelligenceEvaluator(

        team_a=TeamContext(

            name=team_a.name,

            has_big_funding=
                team_a.has_major_funding,

            funding_description=
                team_a.funding_notes,

            changes=team_a.changes
        ),

        team_b=TeamContext(

            name=team_b.name,

            has_big_funding=
                team_b.has_major_funding,

            funding_description=
                team_b.funding_notes,

            changes=team_b.changes
        )
    )

    intelligence.print_assessment()

    # ================================================================
    # RUN RULES 5 & 6
    # ================================================================

    dynamics = MatchDynamicsEvaluator(

        team_a=TeamGoalMetrics(

            name=team_a.name,

            is_must_win=
                team_a.is_must_win,

            must_win_reason=
                team_a.must_win_context,

            scoring_probability=
                team_a.scoring_probability
        ),

        team_b=TeamGoalMetrics(

            name=team_b.name,

            is_must_win=
                team_b.is_must_win,

            must_win_reason=
                team_b.must_win_context,

            scoring_probability=
                team_b.scoring_probability
        )
    )

    dynamics.print_assessment()

    # ================================================================
    # RUN COMPLETE 6-VARIABLE ANALYTICAL ENGINE
    # ================================================================

    engine = MatchAnalyticalEngine(
        rules,
        team_a,
        team_b
    )

    engine.print_report()