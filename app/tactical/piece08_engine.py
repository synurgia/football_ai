from dataclasses import field
from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np
import pandas as pd


@dataclass
class RefereeProfile:
    referee_id: str
    referee_name: str
    matches_officiated: int
    fouls_per_game: float
    tackles_per_game: float
    cards_per_foul: float  # (Yellows + Reds) / Total Fouls
    penalties_per_game: float
    var_overturns_per_game: float


@dataclass
class MatchContext:
    favorite_box_touch_share: float  # e.g., 0.82 = 82% of total box touches
    underdog_tackle_intensity: float  # Tackles attempted per 90 in transition
    favorite_transition_dependency: float  # Share of xG generated from fast breaks


@dataclass
class RefereeImpactProfile:
    referee_name: str
    allows_physical_disruption: bool  # Favors physical underdog breaking up transition
    underdog_disruption_index: float  # 0.0 to 1.0 scale
    penalty_risk_high: bool  # Ref awards high penalties/game
    favorite_penalty_boost: float  # Probability boost for favorite penalty event
    expected_card_suppression: float  # Delta on expected cards for tactical fouls
    summary: Dict[str, float]


class RefereeStrictnessEngine:
    """Quantitative engine analyzing referee profiling, card rates, and penalty tendencies:

    1. Disruption Filter: Referees with high fouls-per-tackle thresholds and low cards/foul
       allow physical underdogs to break up fast transitions without early discipline.
    2. Box Dominance Penalty Filter: Referees with high penalty/VAR averages heavily favor
       top-tier favorites dominating penalty area volume (>= 80% box touch share).
    """

    def __init__(
        self,
        high_penalty_threshold: float = 0.35,  # >= 0.35 penalties per game is high
        high_tackle_foul_threshold: float = 2.2,  # > 2.2 tackles per foul called = lenient ref
        low_card_foul_threshold: float = 0.14,  # < 14% of fouls result in yellow/red card
        box_dominance_threshold: float = 0.80,  # 80%+ box touch dominance
    ):
        self.high_penalty_threshold = high_penalty_threshold
        self.high_tackle_foul_threshold = high_tackle_foul_threshold
        self.low_card_foul_threshold = low_card_foul_threshold
        self.box_dominance_threshold = box_dominance_threshold

    def analyze_referee_impact(
        self,
        referee: RefereeProfile,
        match_context: MatchContext,
    ) -> RefereeImpactProfile:
        """Evaluates how a specific referee's strictness metrics impact tactical execution

        and expected event distributions (cards, penalties, transition disruption).
        """
        # 1. Calculate Officiating Threshold Ratios
        tackles_per_foul = (
            referee.tackles_per_game / referee.fouls_per_game
            if referee.fouls_per_game > 0
            else 1.0
        )

        # High tackles/foul + low cards/foul = Ref lets physical play flow
        is_lenient_foul_threshold = tackles_per_foul >= self.high_tackle_foul_threshold
        is_card_averse = referee.cards_per_foul <= self.low_card_foul_threshold

        # Underdog Disruption Advantage Index
        # Higher score means underdog can break up transition play with lower card risk
        disruption_index = min(
            1.0,
            (tackles_per_foul / self.high_tackle_foul_threshold) * 0.5
            + (1.0 - (referee.cards_per_foul / 0.25)) * 0.5,
        )

        favors_physical_underdog = (
            is_lenient_foul_threshold
            and is_card_averse
            and match_context.favorite_transition_dependency >= 0.35
        )

        # 2. Penalty & VAR Frequency vs Box Dominance
        total_penalty_frequency = (
            referee.penalties_per_game + referee.var_penalties_per_game
        )
        is_high_penalty_ref = total_penalty_frequency >= self.high_penalty_threshold

        favorite_penalty_boost = 1.0
        if is_high_penalty_ref:
            if match_context.favorite_box_touch_share >= self.box_dominance_threshold:
                # 80%+ box touch dominance + high penalty ref = heavy penalty probability skew
                excess_touch_share = (
                    match_context.favorite_box_touch_share - self.box_dominance_threshold
                )
                favorite_penalty_boost = 1.25 + (excess_touch_share * 1.5)  # Scale up from +25%

        # 3. Card Line Adjustment Factor (-1.0 to +1.0 card delta)
        card_delta = (referee.cards_per_foul - 0.18) * referee.fouls_per_game

        summary = {
            "tackles_per_foul": round(tackles_per_foul, 2),
            "total_penalty_freq": round(total_penalty_frequency, 2),
            "disruption_index": round(disruption_index, 3),
            "favorite_penalty_boost": round(favorite_penalty_boost, 3),
            "card_delta_per_game": round(card_delta, 2),
        }

        return RefereeImpactProfile(
            referee_name=referee.referee_name,
            allows_physical_disruption=favors_physical_underdog,
            underdog_disruption_index=round(disruption_index, 3),
            penalty_risk_high=is_high_penalty_ref,
            favorite_penalty_boost=round(favorite_penalty_boost, 3),
            expected_card_suppression=round(-card_delta, 2) if card_delta < 0 else 0.0,
            summary=summary,
        )


# --- Example Execution ---
if __name__ == "__main__":
    # Sample Referee: Low cards/foul, high penalty/VAR rate
    ref_lenient_strict_pen = RefereeProfile(
        referee_id="REF_001",
        referee_name="Anthony Taylor",
        matches_officiated=28,
        fouls_per_game=21.4,
        tackles_per_game=38.5,
        cards_per_foul=0.11,  # Only 11% of fouls get booked (card averse)
        penalties_per_game=0.38,  # High penalty referee
        var_overturns_per_game=0.12,
    )

    # Sample Match: Favorite heavily dominates box touches and relies on transition
    match_ctx = MatchContext(
        favorite_box_touch_share=0.84,  # 84% box touch volume
        underdog_tackle_intensity=22.5,
        favorite_transition_dependency=0.42,  # High fast-break dependence
    )

    engine = RefereeStrictnessEngine()
    impact = engine.analyze_referee_impact(ref_lenient_strict_pen, match_ctx)

    print("--- REFEREE IMPACT ASSESSMENT ---")
    print(f"Referee Name             : {impact.referee_name}")
    print(f"Favors Physical Underdog : {impact.allows_physical_disruption} (Index: {impact.underdog_disruption_index})")
    print(f"High Penalty Profile     : {impact.penalty_risk_high}")
    print(f"Favorite Penalty Multiplier: {impact.favorite_penalty_boost}x")
    print(f"Summary Metrics          : {impact.summary}")
    from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd


@dataclass
class PitchProfile:
    pitch_width_meters: float  # Standard width is 68.0m (UEFA standard)
    pitch_length_meters: float  # Standard length is 105.0m
    grass_length_mm: float  # Standard optimal cut: 24.0mm - 26.0mm
    is_watered_pre_match: bool  # Pre-match watering speeds up ball friction
    is_watered_halftime: bool  # Halftime watering maintains ball roll speed


@dataclass
class KeyPlayerStatus:
    team_id: str
    is_missing_primary_playmaker: bool  # Missing solo progressive passer / pivot
    playmaker_progressive_pass_share: float  # Share of team's progressive passes (e.g. 0.22 = 22%)
    playmaker_xg_buildup_share: float  # xG involvement share in build-up phase


@dataclass
class MicroFactorImpactProfile:
    pitch_width_meters: float
    lateral_space_restriction_pct: float  # Area reduction penalizing wing overloads
    ball_roll_speed_friction_pct: float  # Ball movement slowdown penalty
    low_block_defensive_multiplier: float  # Defensive efficiency boost for 5-4-1/5-3-2
    favorite_possession_xg_penalty: float  # Total xG reduction on favorite's attack
    key_player_spof_penalty: float  # Single Point of Failure penalty on build-up
    summary: Dict[str, float]


class PitchAndRosterMicroEngine:
    """Quantitative engine analyzing pitch geometry, surface friction, and single-point-of-failure

    roster dependencies:

    1. Pitch Geometry: Narrow pitches (<66m) reduce lateral width, compacting the pitch
       and making a 5-4-1 low-block exponentially easier to hold.
    2. Turf Friction: Unwatered or long grass (>28mm) slows ball velocity, hurting
       possession-heavy teams relying on quick double-touch combinations.
    3. Single Point of Failure (SPOF): Missing a primary deep-lying midfielder (e.g., Rodri/De Jong archetype)
       severely degrades central progression and transition protection.
    """

    STANDARD_WIDTH_M: float = 68.0
    STANDARD_LENGTH_M: float = 105.0
    STANDARD_AREA_M2: float = 68.0 * 105.0  # 7,140 m²

    def __init__(
        self,
        narrow_pitch_threshold: float = 65.5,  # Pitches <= 65.5m width classified as narrow
        optimal_grass_max_mm: float = 27.0,  # Grass > 27mm causes drag
        spof_pass_share_threshold: float = 0.18,  # Player controlling >= 18% of progressive passes
    ):
        self.narrow_pitch_threshold = narrow_pitch_threshold
        self.optimal_grass_max_mm = optimal_grass_max_mm
        self.spof_pass_share_threshold = spof_pass_share_threshold

    def calculate_pitch_geometry_impact(
        self, pitch: PitchProfile
    ) -> Tuple[float, float]:
        """Calculates lateral width reduction percentage and corresponding low-block defensive boost."""
        width_delta = max(0.0, self.STANDARD_WIDTH_M - pitch.pitch_width_meters)
        lateral_restriction_pct = (width_delta / self.STANDARD_WIDTH_M) * 100.0

        # Narrower pitch reduces lateral space for wing overloads and half-space pockets
        # Boosts 5-4-1 defensive stability by making compact horizontal shifting easier
        low_block_boost = 1.0 + (width_delta * 0.035)  # +3.5% defensive efficacy per meter narrower

        return round(lateral_restriction_pct, 2), round(low_block_boost, 3)

    def calculate_surface_friction_penalty(self, pitch: PitchProfile) -> float:
        """Calculates ball movement speed reduction from grass height and watering conditions."""
        friction_penalty = 0.0

        # Grass length penalty
        if pitch.grass_length_mm > self.optimal_grass_max_mm:
            excess_grass = pitch.grass_length_mm - self.optimal_grass_max_mm
            friction_penalty += excess_grass * 0.025  # 2.5% drag per extra mm

        # Pitch watering friction (dry pitch slows down ball speed significantly)
        if not pitch.is_watered_pre_match:
            friction_penalty += 0.06  # 6% speed drag
        if not pitch.is_watered_halftime:
            friction_penalty += 0.04  # 4% second-half speed drag

        return round(min(0.25, friction_penalty), 3)  # Capped at 25% max drag

    def evaluate_spof_roster_impact(self, player_status: KeyPlayerStatus) -> float:
        """Evaluates Single Point of Failure (SPOF) build-up degradation if primary pivot is missing."""
        if not player_status.is_missing_primary_playmaker:
            return 0.0

        if player_status.playmaker_progressive_pass_share >= self.spof_pass_share_threshold:
            # Significant build-up penalty proportional to missing player's share of progression
            base_penalty = player_status.playmaker_progressive_pass_share * 0.85
            xg_penalty = player_status.playmaker_xg_buildup_share * 0.40
            return round(base_penalty + xg_penalty, 3)

        return 0.05  # Default minor key player absence penalty

    def Evaluate_match_micro_factors(
        self,
        pitch: PitchProfile,
        favorite_key_player: KeyPlayerStatus,
        favorite_possession_share: float = 0.65,  # 65% possession team
    ) -> MicroFactorImpactProfile:
        """Synthesizes pitch dimensions, surface friction, and SPOF roster availability into

        an aggregate offensive xG penalty factor for the possession favorite.
        """
        lateral_restriction_pct, low_block_boost = self.calculate_pitch_geometry_impact(pitch)
        friction_penalty = self.calculate_surface_friction_penalty(pitch)
        spof_penalty = self.evaluate_spof_roster_impact(favorite_key_player)

        # Possession-heavy teams are doubly punished by pitch friction and narrow geometry
        geometry_possession_drag = (lateral_restriction_pct / 100.0) * favorite_possession_share
        turf_possession_drag = friction_penalty * favorite_possession_share

        # Total combined xG reduction penalty multiplier for favorite
        total_xg_penalty = round(geometry_possession_drag + turf_possession_drag + spof_penalty, 3)

        summary = {
            "pitch_width_m": pitch.pitch_width_meters,
            "lateral_space_loss_pct": lateral_restriction_pct,
            "low_block_boost_factor": low_block_boost,
            "surface_friction_drag_pct": round(friction_penalty * 100, 2),
            "spof_buildup_penalty_pct": round(spof_penalty * 100, 2),
            "favorite_total_xg_penalty_pct": round(total_xg_penalty * 100, 2),
        }

        return MicroFactorImpactProfile(
            pitch_width_meters=pitch.pitch_width_meters,
            lateral_space_restriction_pct=lateral_restriction_pct,
            ball_roll_speed_friction_pct=round(friction_penalty * 100, 2),
            low_block_defensive_multiplier=low_block_boost,
            favorite_possession_xg_penalty=total_xg_penalty,
            key_player_spof_penalty=spof_penalty,
            summary=summary,
        )


# --- Example Execution ---
if __name__ == "__main__":
    # Sample Scenario: Narrow, unwatered pitch (e.g. 64m wide, long grass, no pre-match watering)
    narrow_unwatered_pitch = PitchProfile(
        pitch_width_meters=64.0,  # 4m narrower than standard 68m
        pitch_length_meters=101.0,
        grass_length_mm=29.5,  # Long grass (29.5mm)
        is_watered_pre_match=False,  # Unwatered pitch
        is_watered_halftime=False,
    )

    # Sample Scenario: Heavy possession favorite missing their primary progressive midfielder (Rodri archetype)
    favorite_spof_status = KeyPlayerStatus(
        team_id="FAVORITE_FC",
        is_missing_primary_playmaker=True,
        playmaker_progressive_pass_share=0.24,  # Controls 24% of team's progressive passes
        playmaker_xg_buildup_share=0.31,  # Involved in 31% of build-up xG
    )

    engine = PitchAndRosterMicroEngine()
    micro_impact = engine.Evaluate_match_micro_factors(
        pitch=narrow_unwatered_pitch,
        favorite_key_player=favorite_spof_status,
        favorite_possession_share=0.68,  # High-possession team (68%)
    )

    print("--- PITCH GEOMETRY & MICRO-FACTOR EVALUATION ---")
    print(f"Pitch Dimensions         : {micro_impact.pitch_width_meters}m width")
    print(f"Lateral Space Loss       : -{micro_impact.lateral_space_restriction_pct}%")
    print(f"Low-Block Defensive Boost: {micro_impact.low_block_defensive_multiplier}x")
    print(f"Surface Friction Drag    : -{micro_impact.ball_roll_speed_friction_pct}% ball speed")
    print(f"Key Player SPOF Penalty  : -{round(micro_impact.key_player_spof_penalty * 100, 2)}% build-up efficiency")
    print(f"Favorite Total xG Penalty: -{round(micro_impact.favorite_possession_xg_penalty * 100, 2)}%")
    print(f"\nFull Summary Output      : {micro_impact.summary}")
    from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


class PositionGroup(Enum):
    GOALKEEPER = "GK"
    DEFENDER = "DEF"
    MIDFIELDER = "MID"
    ATTACKER = "ATT"


@dataclass
class PlayerProfile:
    player_id: str
    name: str
    position_group: PositionGroup
    overall_form: float  # 0.0 to 100.0 scale
    pace: float  # Sprint speed & acceleration (0-100)
    defensive_solidity: float  # Tackling, positioning, duel win % (0-100)
    press_resistance: float  # Ability to retain ball under heavy pressure (0-100)
    aerial_dominance: float  # Heading & aerial duel success rate (0-100)
    progressive_output: float  # Passing range & ball-carrying progression (0-100)
    known_weaknesses: List[str] = field(default_factory=list)
    # Common weakness tags: "slow_recovery_pace", "poor_aerial_defense",
    # "turnover_prone_under_press", "weak_defensive_workrate"


@dataclass
class StartingXI:
    team_id: str
    team_name: str
    formation: str  # e.g., "4-3-3", "5-4-1"
    players: List[PlayerProfile]  # Must contain exactly 11 players

    def __post_init__(self):
        if len(self.players) != 11:
            raise ValueError(
                f"Starting XI for {self.team_name} must contain exactly 11 players, got {len(self.players)}."
            )

    def get_unit_players(
        self, pos_group: PositionGroup
    ) -> List[PlayerProfile]:
        return [p for p in self.players if p.position_group == pos_group]


@dataclass
class MatchupExploit:
    attacking_team: str
    defending_team: str
    exploit_type: str
    severity_score: float  # 0.0 to 1.0 (Impact on match outcome)
    description: str


@dataclass
class LineupEvaluationReport:
    team_a_overall_xi_rating: float
    team_b_overall_xi_rating: float
    net_xi_rating_delta: float  # Team A - Team B
    unit_matchup_scores: Dict[str, float]  # Unit-vs-Unit control scores
    identified_exploits: List[MatchupExploit]
    team_a_lambda_modifier: float  # xG multiplier based on XI matchup
    team_b_lambda_modifier: float  # xG multiplier based on XI matchup


class StartingXIEvaluationEngine:
    """Quantitative engine for evaluating starting 11 player strengths, weaknesses,

    and real-life tactical mismatches (Pace gaps, Press Traps, Aerial mismatches).
    """

    def __init__(
        self,
        pace_exploit_threshold: float = 20.0,  # +20 pace gap creates isolation exploit
        press_trap_gap_threshold: float = 22.0,  # High press vs low press resistance gap
        aerial_mismatch_threshold: float = 25.0,  # Aerial dominance mismatch
    ):
        self.pace_exploit_threshold = pace_exploit_threshold
        self.press_trap_gap_threshold = press_trap_gap_threshold
        self.aerial_mismatch_threshold = aerial_mismatch_threshold

    @staticmethod
    def _calculate_unit_aggregate(
        players: List[PlayerProfile], attribute: str
    ) -> float:
        """Computes weighted average rating for a positional unit."""
        if not players:
            return 50.0
        return float(np.mean([getattr(p, attribute) for p in players]))

    def evaluate_unit_matchups(
        self, team_a: StartingXI, team_b: StartingXI
    ) -> Dict[str, float]:
        """Calculates tactical unit control differentials (Midfield battle, Attack vs Defense)."""
        # Team A Units
        a_att = self._calculate_unit_aggregate(
            team_a.get_unit_players(PositionGroup.ATTACKER), "overall_form"
        )
        a_mid = self._calculate_unit_aggregate(
            team_a.get_unit_players(PositionGroup.MIDFIELDER), "overall_form"
        )
        a_def = self._calculate_unit_aggregate(
            team_a.get_unit_players(PositionGroup.DEFENDER), "overall_form"
        )

        # Team B Units
        b_att = self._calculate_unit_aggregate(
            team_b.get_unit_players(PositionGroup.ATTACKER), "overall_form"
        )
        b_mid = self._calculate_unit_aggregate(
            team_b.get_unit_players(PositionGroup.MIDFIELDER), "overall_form"
        )
        b_def = self._calculate_unit_aggregate(
            team_b.get_unit_players(PositionGroup.DEFENDER), "overall_form"
        )

        return {
            "midfield_battle_delta": round(a_mid - b_mid, 2),
            "team_a_attack_vs_b_defense": round(a_att - b_def, 2),
            "team_b_attack_vs_a_defense": round(b_att - a_def, 2),
        }

    def detect_tactical_exploits(
        self, attacker_xi: StartingXI, defender_xi: StartingXI
    ) -> List[MatchupExploit]:
        """Scans individual player profiles for real-life weakness exploits."""
        exploits = []

        att_wingers = [
            p
            for p in attacker_xi.get_unit_players(PositionGroup.ATTACKER)
            if p.pace >= 82.0
        ]
        def_backs = [
            p
            for p in defender_xi.get_unit_players(PositionGroup.DEFENDER)
            if "slow_recovery_pace" in p.known_weaknesses or p.pace <= 65.0
        ]

        # 1. Pace Mismatch (Fast Winger vs Slow Fullback/CB)
        if att_wingers and def_backs:
            avg_winger_pace = np.mean([w.pace for w in att_wingers])
            avg_back_pace = np.mean([b.pace for b in def_backs])
            pace_gap = avg_winger_pace - avg_back_pace

            if pace_gap >= self.pace_exploit_threshold:
                exploits.append(
                    MatchupExploit(
                        attacking_team=attacker_xi.team_name,
                        defending_team=defender_xi.team_name,
                        exploit_type="PACE_ISOLATION",
                        severity_score=round(min(0.9, pace_gap / 40.0), 2),
                        description=f"Fast attackers ({[w.name for w in att_wingers]}) exploit slow defensive recovery line ({[b.name for b in def_backs]}). Pace gap: +{round(pace_gap, 1)}.",
                    )
                )

        # 2. Press Trap Exploit (Aggressive Midfield Pressing vs Turnover-Prone Pivot)
        def_vulnerable_midfielders = [
            p
            for p in defender_xi.get_unit_players(PositionGroup.MIDFIELDER)
            if "turnover_prone_under_press" in p.known_weaknesses
            or p.press_resistance <= 62.0
        ]
        att_pressing_mids = [
            p
            for p in attacker_xi.get_unit_players(PositionGroup.MIDFIELDER)
            if p.defensive_solidity >= 75.0
        ]

        if def_vulnerable_midfielders and att_pressing_mids:
            exploits.append(
                MatchupExploit(
                    attacking_team=attacker_xi.team_name,
                    defending_team=defender_xi.team_name,
                    exploit_type="HIGH_PRESS_TURNOVER_TRAP",
                    severity_score=0.75,
                    description=f"Pressing unit triggers turnovers against press-vulnerable midfielder(s): {[m.name for m in def_vulnerable_midfielders]}.",
                )
            )

        # 3. Aerial Target Man vs Aerially Weak Defense
        att_target_men = [
            p
            for p in attacker_xi.get_unit_players(PositionGroup.ATTACKER)
            if p.aerial_dominance >= 82.0
        ]
        def_aerial_vulnerable = [
            p
            for p in defender_xi.get_unit_players(PositionGroup.DEFENDER)
            if "poor_aerial_defense" in p.known_weaknesses
            or p.aerial_dominance <= 60.0
        ]

        if att_target_men and def_aerial_vulnerable:
            exploits.append(
                MatchupExploit(
                    attacking_team=attacker_xi.team_name,
                    defending_team=defender_xi.team_name,
                    exploit_type="AERIAL_BOMBARDMENT",
                    severity_score=0.65,
                    description=f"Aerial dominance threat ({[tm.name for tm in att_target_men]}) targets weak aerial defenders ({[d.name for d in def_aerial_vulnerable]}).",
                )
            )

        return exploits

    def evaluate_lineup_matchup(
        self, team_a: StartingXI, team_b: StartingXI
    ) -> LineupEvaluationReport:
        """Evaluates overall 11 vs 11 lineup strengths, weaknesses, and calculates xG lambda modifiers."""
        # Calculate overall weighted XI ratings
        team_a_rating = np.mean([p.overall_form for p in team_a.players])
        team_b_rating = np.mean([p.overall_form for p in team_b.players])

        unit_matchups = self.evaluate_unit_matchups(team_a, team_b)

        # Detect bi-directional exploits
        exploits_a_on_b = self.detect_tactical_exploits(team_a, team_b)
        exploits_b_on_a = self.detect_tactical_exploits(team_b, team_a)
        all_exploits = exploits_a_on_b + exploits_b_on_a

        # Calculate xG Lambda Modifiers based on exploits & unit control
        # Base modifier starts at 1.0
        lambda_mod_a = 1.0 + (unit_matchups["team_a_attack_vs_b_defense"] * 0.004)
        lambda_mod_b = 1.0 + (unit_matchups["team_b_attack_vs_a_defense"] * 0.004)

        for exp in exploits_a_on_b:
            lambda_mod_a += exp.severity_score * 0.12  # Up to +12% xG boost per major exploit
        for exp in exploits_b_on_a:
            lambda_mod_b += exp.severity_score * 0.12

        return LineupEvaluationReport(
            team_a_overall_xi_rating=round(float(team_a_rating), 2),
            team_b_overall_xi_rating=round(float(team_b_rating), 2),
            net_xi_rating_delta=round(float(team_a_rating - team_b_rating), 2),
            unit_matchup_scores=unit_matchups,
            identified_exploits=all_exploits,
            team_a_lambda_modifier=round(max(0.70, lambda_mod_a), 3),
            team_b_lambda_modifier=round(max(0.70, lambda_mod_b), 3),
        )


# --- Example Execution ---
if __name__ == "__main__":
    # Create Sample XI for Team A (High-Pressing, Pace-Heavy Favorite)
    team_a_xi = StartingXI(
        team_id="TEAM_A",
        team_name="Real Madrid",
        formation="4-3-3",
        players=[
            PlayerProfile("P1", "Courtois", PositionGroup.GOALKEEPER, 88, 50, 85, 70, 85, 60),
            PlayerProfile("P2", "Carvajal", PositionGroup.DEFENDER, 82, 78, 83, 80, 72, 78),
            PlayerProfile("P3", "Rüdiger", PositionGroup.DEFENDER, 86, 82, 88, 75, 86, 70),
            PlayerProfile("P4", "Alaba", PositionGroup.DEFENDER, 80, 74, 80, 85, 75, 84),
            PlayerProfile("P5", "Mendy", PositionGroup.DEFENDER, 79, 83, 82, 72, 76, 68),
            PlayerProfile("P6", "Tchouaméni", PositionGroup.MIDFIELDER, 84, 75, 86, 82, 80, 78),
            PlayerProfile("P7", "Valverde", PositionGroup.MIDFIELDER, 87, 89, 84, 85, 74, 82),
            PlayerProfile("P8", "Bellingham", PositionGroup.MIDFIELDER, 90, 82, 82, 88, 85, 86),
            PlayerProfile("P9", "Rodrygo", PositionGroup.ATTACKER, 85, 88, 45, 84, 62, 81),
            PlayerProfile("P10", "Mbappé", PositionGroup.ATTACKER, 92, 96, 40, 82, 78, 85),  # High Pace
            PlayerProfile("P11", "Vinícius Jr", PositionGroup.ATTACKER, 91, 95, 42, 86, 60, 88),  # High Pace
        ],
    )

    # Create Sample XI for Team B (Underdog with clear weak points in defense/midfield)
    team_b_xi = StartingXI(
        team_id="TEAM_B",
        team_name="Getafe",
        formation="5-4-1",
        players=[
            PlayerProfile("P12", "Soria", PositionGroup.GOALKEEPER, 76, 45, 75, 60, 80, 50),
            PlayerProfile("P13", "Djené", PositionGroup.DEFENDER, 74, 64, 78, 68, 68, 55, weaknesses=["slow_recovery_pace"]),
            PlayerProfile("P14", "Duarte", PositionGroup.DEFENDER, 73, 60, 75, 62, 78, 52, weaknesses=["slow_recovery_pace"]),
            PlayerProfile("P15", "Alderete", PositionGroup.DEFENDER, 75, 62, 76, 65, 81, 58),
            PlayerProfile("P16", "Iglesias", PositionGroup.DEFENDER, 71, 65, 70, 60, 62, 60, weaknesses=["poor_aerial_defense"]),
            PlayerProfile("P17", "Rico", PositionGroup.DEFENDER, 72, 68, 71, 62, 64, 62),
            PlayerProfile("P18", "Arambarri", PositionGroup.MIDFIELDER, 75, 70, 76, 70, 72, 65),
            PlayerProfile("P19", "Milla", PositionGroup.MIDFIELDER, 74, 65, 68, 58, 62, 72, weaknesses=["turnover_prone_under_press"]),
            PlayerProfile("P20", "Maksimović", PositionGroup.MIDFIELDER, 73, 68, 74, 65, 70, 60),
            PlayerProfile("P21", "Greenwood", PositionGroup.ATTACKER, 78, 82, 40, 76, 58, 75),
            PlayerProfile("P22", "Mayoral", PositionGroup.ATTACKER, 76, 72, 38, 70, 75, 62),
        ],
    )

    eval_engine = StartingXIEvaluationEngine()
    report = eval_engine.evaluate_lineup_matchup(team_a_xi, team_b_xi)

    print("--- STARTING XI STRENGTH & TACTICAL EXPLOIT REPORT ---")
    print(f"Overall Ratings     : {team_a_xi.team_name} ({report.team_a_overall_xi_rating}) vs {team_b_xi.team_name} ({report.team_b_overall_xi_rating})")
    print(f"Net Rating Delta    : {report.net_xi_rating_delta}")
    print(f"Unit Matchup Scores : {report.unit_matchup_scores}")
    print(f"Lambda Multipliers  : {team_a_xi.team_name} ({report.team_a_lambda_modifier}x) | {team_b_xi.team_name} ({report.team_b_lambda_modifier}x)")
    print("\nIdentified Real-Life Exploits:")
    for exp in report.identified_exploits:
        print(f"- [{exp.exploit_type}] {exp.description} (Severity: {exp.severity_score})")