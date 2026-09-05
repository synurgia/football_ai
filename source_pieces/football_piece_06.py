import numpy as np
from typing import List, Dict, Union

class ResistanceFilter:
    """Evaluates defensive resistance and opposition barrier strength."""
    def __init__(self, xga_weight: float = 0.6, clean_sheet_bonus: float = 0.15):
        self.xga_weight = xga_weight
        self.clean_sheet_bonus = clean_sheet_bonus

    def evaluate(self, matches: List[Dict[str, Union[int, float]]]) -> float:
        if not matches:
            return 0.50
        scores = []
        for match in matches:
            actual = match.get('goals_conceded', 0)
            xga = match.get('xga', float(actual))
            shots = match.get('shots_faced', 10)
            
            expected_suppression = 1.0 - (self.xga_weight * xga + (1 - self.xga_weight) * actual) / (shots * 0.18 + 1e-5)
            score = max(0.0, min(1.0, expected_suppression))
            
            if actual == 0:
                score = min(1.0, score + self.clean_sheet_bonus)
            scores.append(score)
            
        return float(np.mean(scores))


class FormFilter:
    """Calculates exponentially decayed performance form over recent fixtures."""
    def __init__(self, decay_factor: float = 0.85, window_size: int = 5):
        self.decay_factor = decay_factor
        self.window_size = window_size

    def evaluate(self, match_history: List[Dict[str, Union[str, int, float]]]) -> float:
        if not match_history:
            return 0.50
        window = match_history[-self.window_size:]
        weights = [self.decay_factor ** i for i in range(len(window))][::-1]
        
        point_map = {'W': 3.0, 'D': 1.0, 'L': 0.0}
        performance_scores = []

        for match in window:
            pts = point_map.get(str(match.get('result', 'D')), 1.0)
            gd = float(match.get('goals_scored', 0)) - float(match.get('goals_conceded', 0))
            gd_score = (max(-3.0, min(3.0, gd)) + 3.0) / 6.0
            rating = (pts / 3.0) * 0.70 + gd_score * 0.30
            performance_scores.append(rating)

        weighted_form = sum(w * s for w, s in zip(weights, performance_scores)) / sum(weights)
        return float(weighted_form)


class CompositeTeamEvaluator:
    """
    Combines Resistance and Form filters into a single normalized composite metric.
    Allows contextual re-weighting based on venue (home/away) or opposition tier.
    """
    def __init__(
        self,
        resistance_weight: float = 0.45,
        form_weight: float = 0.55,
        rf_kwargs: Dict = None,
        ff_kwargs: Dict = None
    ):
        self.rf = ResistanceFilter(**(rf_kwargs or {}))
        self.ff = FormFilter(**(ff_kwargs or {}))
        self.set_weights(resistance_weight, form_weight)

    def set_weights(self, resistance_weight: float, form_weight: float) -> None:
        """Normalizes dynamic weights to sum to 1.0."""
        total = resistance_weight + form_weight
        self.w_res = resistance_weight / total
        self.w_form = form_weight / total

    def evaluate(
        self, 
        match_history: List[Dict[str, Union[str, int, float]]],
        is_away: bool = False
    ) -> Dict[str, float]:
        """
        Evaluates sub-filters and calculates composite index.
        Adjusts resistance weighting automatically for away fixtures.
        """
        # Dynamic contextual shift: weight resistance 10% higher for away fixtures
        w_res = min(0.80, self.w_res + 0.10) if is_away else self.w_res
        w_form = 1.0 - w_res

        resistance_index = self.rf.evaluate(match_history)
        form_index = self.ff.evaluate(match_history)
        
        composite_score = (resistance_index * w_res) + (form_index * w_form)

        return {
            'resistance_index': round(resistance_index, 4),
            'form_index': round(form_index, 4),
            'composite_rating': round(composite_score, 4),
            'weights_used': {'resistance': round(w_res, 2), 'form': round(w_form, 2)}
        }


# --- Execution Pipeline ---
if __name__ == "__main__":
    fixtures = [
        {'result': 'L', 'goals_scored': 0, 'goals_conceded': 2, 'xga': 2.1, 'shots_faced': 18},
        {'result': 'D', 'goals_scored': 1, 'goals_conceded': 1, 'xga': 1.1, 'shots_faced': 12},
        {'result': 'W', 'goals_scored': 2, 'goals_conceded': 0, 'xga': 0.5, 'shots_faced': 15},
        {'result': 'W', 'goals_scored': 3, 'goals_conceded': 1, 'xga': 0.9, 'shots_faced': 10},
    ]

    engine = CompositeTeamEvaluator(resistance_weight=0.40, form_weight=0.60)
    
    home_eval = engine.evaluate(fixtures, is_away=False)
    away_eval = engine.evaluate(fixtures, is_away=True)

    print("Home Context:", home_eval)
    print("Away Context:", away_eval)
    from dataclasses import dataclass
from typing import Dict, Any, Tuple

@dataclass
class TeamTacticalMetrics:
    # Defensive Metrics
    formation: str                     # e.g., '5-4-1', '4-5-1', '5-3-2'
    avg_defensive_line_height_m: float # Distance in meters from own goal line
    inter_line_distance_m: float       # Vertical compactness between lines (meters)
    width_compactness_m: float         # Width of defensive block (meters)
    open_play_xg_share: float          # Proportion of xG from open play (0.0 to 1.0)
    set_piece_xg_share: float          # Proportion of xG from set pieces (0.0 to 1.0)
    set_piece_conversion_rate: float   # Goal conversion rate from corners/free-kicks (0.0 to 1.0)
    
    # Counter-Attack Transition Metrics
    avg_wing_sprint_speed_kmh: float   # Avg top sprint speed of wide players/wingers (km/h)
    directness_ratio: float            # Ratio of forward pitch distance gained vs total passing distance (0.0 to 1.0)
    vertical_passes_per_possession: float # Avg number of direct forward penetrating passes per possession sequence


class TacticalDefensiveAnalyzer:
    """
    Evaluates underdog tactical defensive structures & transition threat:
    a. Low Block / Parking the Bus detection
    b. Defensive Compactness & space restriction for top-tier opponents
    c. Set Piece Reliance & low-scoring opportunism (1-0 profile)
    d. Counter-Attack Transition Metrics (Wing Pace, Directness, Verticality)
    """

    LOW_BLOCK_FORMATIONS = {"5-4-1", "4-5-1", "5-3-2"}

    def evaluate_low_block(self, formation: str, def_line_height: float) -> Tuple[float, str]:
        is_deep_structure = formation in self.LOW_BLOCK_FORMATIONS
        
        if def_line_height <= 25.0:
            height_score = 1.0
        elif def_line_height <= 35.0:
            height_score = (35.0 - def_line_height) / 10.0
        else:
            height_score = 0.0

        structure_weight = 1.0 if is_deep_structure else 0.7
        low_block_score = round(height_score * structure_weight, 2)

        description = (
            f"Extreme Low Block ({formation} at {def_line_height}m)"
            if low_block_score > 0.75
            else f"Moderate Low Block ({formation} at {def_line_height}m)"
            if low_block_score > 0.40
            else f"Standard/High Defensive Line ({formation} at {def_line_height}m)"
        )
        return low_block_score, description

    def evaluate_compactness(self, inter_line_m: float, width_m: float) -> Tuple[float, float]:
        if inter_line_m <= 10.0:
            vert_score = 1.0
        elif inter_line_m <= 18.0:
            vert_score = (18.0 - inter_line_m) / 8.0
        else:
            vert_score = 0.0

        space_allowed_multiplier = round(max(0.40, 1.0 - (vert_score * 0.45)), 2)
        return round(vert_score, 2), space_allowed_multiplier

    def evaluate_set_piece_reliance(self, sp_xg_share: float, sp_conversion: float) -> Dict[str, Any]:
        reliance_score = min(1.0, (sp_xg_share * 1.5) + (sp_conversion * 1.2))
        is_1_0_threat = sp_xg_share >= 0.35 and reliance_score >= 0.60

        return {
            "set_piece_reliance_score": round(reliance_score, 2),
            "is_single_chance_exploiter": is_1_0_threat,
            "xg_boost_dead_ball": round(1.0 + (reliance_score * 0.20), 2)
        }

    def evaluate_counter_attack_transition(
        self, wing_speed: float, directness: float, vert_passes: float
    ) -> Dict[str, Any]:
        """
        Evaluates speed and directness during turnover-to-shot transitions.
        a. Pace on wings: >33 km/h is elite counter break speed.
        b. Directness ratio: >0.65 indicates heavy vertical progression over lateral passing.
        c. Vertical passes per possession: >2.5 indicates aggressive box-penetrating passes.
        """
        # Wing pace rating (scaled from 28.0 km/h baseline to 35.0 km/h top end)
        pace_score = max(0.0, min(1.0, (wing_speed - 28.0) / 7.0))
        
        # Directness rating (scaled from 0.30 passive passing to 0.75 high directness)
        directness_score = max(0.0, min(1.0, (directness - 0.30) / 0.45))
        
        # Verticality rating (scaled from 0.5 to 3.5 passes per sequence)
        verticality_score = max(0.0, min(1.0, (vert_passes - 0.5) / 3.0))

        # Composite Counter-Attack Lethality Index
        counter_lethality_score = round(
            (pace_score * 0.40) + (directness_score * 0.35) + (verticality_score * 0.25), 
            2
        )

        return {
            "wing_pace_kmh": wing_speed,
            "pace_rating": round(pace_score, 2),
            "directness_ratio": directness,
            "directness_rating": round(directness_score, 2),
            "vertical_passes_per_possession": vert_passes,
            "verticality_rating": round(verticality_score, 2),
            "counter_lethality_score": counter_lethality_score,
            "threat_profile": (
                "Lethal Fast-Break Threat" if counter_lethality_score >= 0.75 else
                "Moderate Transition Threat" if counter_lethality_score >= 0.45 else
                "Low Transition Threat (Slow Build-up)"
            )
        }

    def analyze(self, metrics: TeamTacticalMetrics) -> Dict[str, Any]:
        low_block_score, block_desc = self.evaluate_low_block(
            metrics.formation, metrics.avg_defensive_line_height_m
        )
        compactness_score, space_mult = self.evaluate_compactness(
            metrics.inter_line_distance_m, metrics.width_compactness_m
        )
        sp_data = self.evaluate_set_piece_reliance(
            metrics.set_piece_xg_share, metrics.set_piece_conversion_rate
        )
        transition_data = self.evaluate_counter_attack_transition(
            metrics.avg_wing_sprint_speed_kmh,
            metrics.directness_ratio,
            metrics.vertical_passes_per_possession
        )

        # Composite Underdog Modifier
        underdog_frustration_factor = round(
            (low_block_score * 0.35) + (compactness_score * 0.35) + (sp_data["set_piece_reliance_score"] * 0.15) + (transition_data["counter_lethality_score"] * 0.15),
            2
        )

        return {
            "tactical_setup": {
                "formation": metrics.formation,
                "low_block_score": low_block_score,
                "description": block_desc
            },
            "compactness": {
                "meters_between_lines": metrics.inter_line_distance_m,
                "compactness_score": compactness_score,
                "opp_open_play_space_multiplier": space_mult
            },
            "set_piece_threat": sp_data,
            "counter_attack_transition": transition_data,
            "frustration_index": underdog_frustration_factor
        }


# Example Usage
if __name__ == "__main__":
    underdog = TeamTacticalMetrics(
        formation="5-4-1",
        avg_defensive_line_height_m=22.5,
        inter_line_distance_m=11.2,
        width_compactness_m=34.0,
        open_play_xg_share=0.40,
        set_piece_xg_share=0.60,
        set_piece_conversion_rate=0.20,
        avg_wing_sprint_speed_kmh=34.2,        # Elite pace on wings
        directness_ratio=0.68,                 # High vertical progression
        vertical_passes_per_possession=2.8     # Quick penetrating passes
    )

    analyzer = TacticalDefensiveAnalyzer()
    report = analyzer.analyze(underdog)
    
    import json
    print(json.dumps(report, indent=4))
    from dataclasses import dataclass
from typing import Dict, Any, Tuple

@dataclass
class TransitionMatchupMetrics:
    # Counter-Attack Speed & Defensive Recovery
    underdog_breakaway_speed_kmh: float          # Avg top sprint speed of underdog attacking transition units (km/h)
    favorite_defensive_recovery_speed_kmh: float # Avg top sprint speed of favorite's tracking-back defenders (km/h)
    
    # Clinical Finishing Profile
    underdog_shots_per_game: float                # Avg total shots per match (low volume = < 10)
    underdog_shot_conversion_rate: float          # Goals per shot ratio (0.0 to 1.0; > 0.15 is clinical)
    underdog_xg_per_shot: float                   # Shot quality metric (higher indicates high-value chances)

    # "Double-Tap" Burst Potential
    underdog_multi_goal_burst_rate: float        # % of matches where underdog scored 2+ goals in a 5-10 min window
    favorite_post_concession_fragility: float     # 0.0 to 1.0 rating measuring favorite's tendency to panic after conceding


class OffensiveTransitionAnalyzer:
    """
    Evaluates Offensive Transition Efficiency for underdogs against top-tier favorites:
    a. Counter-Attack Speed (Breakaway pace vs Top-tier defensive recovery speed)
    b. Clinical Finishing (Low volume + High conversion/shot quality profile)
    c. Double-Tap Potential (Likelihood of quick multi-goal burst to shock favorite)
    """

    def evaluate_counter_speed_mismatch(
        self, breakaway_speed: float, recovery_speed: float
    ) -> Dict[str, Any]:
        """
        Calculates pace differential between underdog counter-attackers and favorite's recovery runners.
        Positive delta indicates underdog outpaces defensive recovery line.
        """
        speed_delta = breakaway_speed - recovery_speed
        
        # Mismatch score normalized (0.0 = total recovery coverage, 1.0 = total pace dominance)
        # Baseline zero at -3.0 km/h deficit, max at +5.0 km/h advantage
        mismatch_score = max(0.0, min(1.0, (speed_delta + 3.0) / 8.0))

        return {
            "underdog_breakaway_speed_kmh": breakaway_speed,
            "favorite_recovery_speed_kmh": recovery_speed,
            "pace_differential_kmh": round(speed_delta, 2),
            "pace_mismatch_score": round(mismatch_score, 2),
            "breakaway_threat": (
                "Extreme Over-The-Top Vulnerability" if speed_delta >= 2.0 else
                "Moderate Counter Threat" if speed_delta >= -1.0 else
                "Favorite Has Full Recovery Control"
            )
        }

    def evaluate_clinical_finishing(
        self, shots_per_game: float, conversion_rate: float, xg_per_shot: float
    ) -> Dict[str, Any]:
        """
        Identifies low-volume, high-efficiency underdog finishing profiles.
        Classic underdog pattern: Low shots (< 10/game), High conversion (> 14%).
        """
        # Low volume weight (higher score for lower shot requirements per goal)
        volume_score = max(0.0, min(1.0, (14.0 - shots_per_game) / 8.0))
        
        # Conversion weight (scaled from 8% baseline to 22% top tier)
        conversion_score = max(0.0, min(1.0, (conversion_rate - 0.08) / 0.14))
        
        # Shot quality weight (scaled from 0.07 xG/shot to 0.18 xG/shot)
        quality_score = max(0.0, min(1.0, (xg_per_shot - 0.07) / 0.11))

        clinical_efficiency_index = round(
            (volume_score * 0.30) + (conversion_score * 0.45) + (quality_score * 0.25),
            2
        )

        is_classic_underdog_profile = shots_per_game <= 10.0 and conversion_rate >= 0.14

        return {
            "shots_per_game": shots_per_game,
            "conversion_rate": conversion_rate,
            "xg_per_shot": xg_per_shot,
            "clinical_efficiency_index": clinical_efficiency_index,
            "is_classic_opportunist": is_classic_underdog_profile,
            "efficiency_profile": (
                "Hyper-Clinical Opportunist" if clinical_efficiency_index >= 0.70 else
                "Balanced Efficiency" if clinical_efficiency_index >= 0.40 else
                "Low-Yield/Wasteful Finisher"
            )
        }

    def evaluate_double_tap_potential(
        self, burst_rate: float, fragility_index: float
    ) -> Dict[str, Any]:
        """
        Assesses likelihood of a quick multi-goal burst (e.g., 2 goals within 5 minutes)
        leveraging underdog burst frequency and favorite post-concession psychological fragility.
        """
        # Scaled from 0% to 25% historical multi-goal burst rate
        burst_score = max(0.0, min(1.0, burst_rate / 0.25))
        
        # Combined double-tap shock index
        double_tap_score = round((burst_score * 0.50) + (fragility_index * 0.50), 2)
        
        return {
            "underdog_burst_rate": burst_rate,
            "favorite_fragility_index": fragility_index,
            "double_tap_score": double_tap_score,
            "shock_factor_rating": (
                "High Danger (Prone to Rapid Collapse)" if double_tap_score >= 0.65 else
                "Moderate Burst Risk" if double_tap_score >= 0.35 else
                "Low Shock Potential"
            )
        }

    def analyze(self, metrics: TransitionMatchupMetrics) -> Dict[str, Any]:
        pace_data = self.evaluate_counter_speed_mismatch(
            metrics.underdog_breakaway_speed_kmh,
            metrics.favorite_defensive_recovery_speed_kmh
        )
        finishing_data = self.evaluate_clinical_finishing(
            metrics.underdog_shots_per_game,
            metrics.underdog_shot_conversion_rate,
            metrics.underdog_xg_per_shot
        )
        burst_data = self.evaluate_double_tap_potential(
            metrics.underdog_multi_goal_burst_rate,
            metrics.favorite_post_concession_fragility
        )

        # Composite Offensive Transition Score
        offensive_transition_score = round(
            (pace_data["pace_mismatch_score"] * 0.40) +
            (finishing_data["clinical_efficiency_index"] * 0.40) +
            (burst_data["double_tap_score"] * 0.20),
            2
        )

        return {
            "counter_attack_speed": pace_data,
            "clinical_finishing": finishing_data,
            "double_tap_burst": burst_data,
            "offensive_transition_score": offensive_transition_score
        }


# Example Usage
if __name__ == "__main__":
    matchup = TransitionMatchupMetrics(
        underdog_breakaway_speed_kmh=34.8,          # High-speed wingers/forwards
        favorite_defensive_recovery_speed_kmh=31.2,  # Slow defensive line recovery
        underdog_shots_per_game=7.2,                 # Low shot volume
        underdog_shot_conversion_rate=0.18,          # High conversion rate (18%)
        underdog_xg_per_shot=0.15,                   # High-value chances generated
        underdog_multi_goal_burst_rate=0.16,         # 16% historical multi-goal burst rate
        favorite_post_concession_fragility=0.65      # Favorite shows post-concession panic
    )

    analyzer = OffensiveTransitionAnalyzer()
    report = analyzer.analyze(matchup)

    import json
    print(json.dumps(report, indent=4))
    from dataclasses import dataclass
from typing import Dict, Any, Tuple

@dataclass
class LeagueScheduleMetrics:
    # Season Format
    season_type: str                         # 'sprint' (Apertura/Clausura, state league) or 'marathon' (European 38-game format)
    season_stage_progress: float            # Progression through season/stage (0.0 = start, 1.0 = final round)
    
    # Motivation & Squad Management
    favorite_rotation_index: float           # 0.0 (Full XI) to 1.0 (Heavy reserve rotation)
    favorite_has_continental_cup_in_3days: bool # True if UCL/Copa Libertadores knockout fixture is adjacent
    favorite_match_importance: float         # 0.0 (Dead rubber / Title secured) to 1.0 (Must-win title decider)
    
    # Home & Logistical Advantage
    favorite_travel_distance_km: float      # Distance traveled by favorite (e.g., long-haul flights in Brazil/MLS)
    favorite_rest_days: int                 # Days rest since last match for favorite
    underdog_rest_days: int                 # Days rest since last match for underdog
    pitch_condition_degrader: float          # 0.0 (Immaculate hybrid turf) to 1.0 (Extreme altitude / damaged pitch)


class LeagueScheduleContextAnalyzer:
    """
    Evaluates contextual external factors influencing middle-tier upset probability:
    a. Season Format (Sprint formats with high variance vs. Marathon formats)
    b. Motivation Gap & Squad Rotation (Continental distractions, squad depth deployment)
    c. Home & Logistical Disadvantage (Travel fatigue, rest asymmetry, pitch surface degradation)
    """

    def evaluate_season_format(self, season_type: str, progress: float) -> Tuple[float, str]:
        """
        Sprint formats (Apertura/Clausura, regional state leagues) amplify single-match variance,
        significantly lowering the threshold for middle-tier upsets compared to long marathon leagues.
        """
        is_sprint = season_type.lower() == "sprint"
        
        # Sprint formats provide an inherently higher baseline for volatility
        format_upset_factor = 0.35 if is_sprint else 0.10
        
        # Late-stage sprint matches (playoff push) amplify tension and variance
        if is_sprint and progress >= 0.70:
            format_upset_factor += 0.15
        elif not is_sprint and progress >= 0.85:
            # End of marathon season can yield unpredictable results depending on stakes
            format_upset_factor += 0.10

        desc = (
            f"High-Variance Sprint Format ({'Late Stage' if progress >= 0.70 else 'Early/Mid Stage'})"
            if is_sprint else
            f"Low-Variance Marathon Format ({round(progress * 100)}% Completed)"
        )
        return round(format_upset_factor, 2), desc

    def evaluate_motivation_gap(
        self, rotation_idx: float, continental_distraction: bool, match_importance: float
    ) -> Dict[str, Any]:
        """
        Measures the likelihood of favorite underperformance due to squad rotation,
        impending continental cup fixtures, or low domestic table motivation.
        """
        # Rotation impact
        rotation_score = round(rotation_idx * 0.45, 2)
        
        # Continental cup distraction penalty
        distraction_score = 0.30 if continental_distraction else 0.0
        
        # Inverse importance (low importance = higher complacency/upset risk)
        complacency_score = round((1.0 - match_importance) * 0.25, 2)
        
        motivation_gap_index = min(1.0, round(rotation_score + distraction_score + complacency_score, 2))

        return {
            "squad_rotation_index": rotation_idx,
            "continental_fixture_distraction": continental_distraction,
            "match_importance_rating": match_importance,
            "motivation_gap_index": motivation_gap_index,
            "vulnerability_profile": (
                "Extreme Distraction/Rotation Vulnerability" if motivation_gap_index >= 0.65 else
                "Moderate Motivation Dip" if motivation_gap_index >= 0.35 else
                "Fully Focused / Peak XI Expected"
            )
        }

    def evaluate_logistical_advantage(
        self, travel_km: float, fav_rest: int, und_rest: int, pitch_degrader: float
    ) -> Dict[str, Any]:
        """
        Factors in travel fatigue (e.g., Brazilian Serie A long distance), rest day asymmetry,
        and pitch/environmental conditions that equalize technical skill gaps.
        """
        # Travel fatigue penalty (> 1,000 km begins degrading performance)
        travel_score = min(1.0, max(0.0, (travel_km - 500.0) / 2500.0))
        
        # Rest asymmetry (positive value favors underdog)
        rest_delta = und_rest - fav_rest
        rest_advantage_score = max(0.0, min(1.0, (rest_delta * 0.20)))
        
        # Pitch equalizer: poor pitches or altitude neutralize top-team technical passing mechanics
        technical_equalizer_mult = round(1.0 - (pitch_degrader * 0.35), 2)

        logistical_friction_index = round(
            (travel_score * 0.35) + (rest_advantage_score * 0.35) + (pitch_degrader * 0.30),
            2
        )

        return {
            "travel_distance_km": travel_km,
            "rest_days_differential": rest_delta,
            "pitch_degradation_factor": pitch_degrader,
            "technical_skill_equalizer_multiplier": technical_equalizer_mult,
            "logistical_friction_index": logistical_friction_index,
            "environment_impact": (
                "Heavy Logistical & Environmental Equalizer" if logistical_friction_index >= 0.60 else
                "Moderate Travel/Rest Disadvantage" if logistical_friction_index >= 0.30 else
                "Neutral Logistical Conditions"
            )
        }

    def analyze(self, metrics: LeagueScheduleMetrics) -> Dict[str, Any]:
        format_score, format_desc = self.evaluate_season_format(
            metrics.season_type, metrics.season_stage_progress
        )
        motivation_data = self.evaluate_motivation_gap(
            metrics.favorite_rotation_index,
            metrics.favorite_has_continental_cup_in_3days,
            metrics.favorite_match_importance
        )
        logistics_data = self.evaluate_logistical_advantage(
            metrics.favorite_travel_distance_km,
            metrics.favorite_rest_days,
            metrics.underdog_rest_days,
            metrics.pitch_condition_degrader
        )

        # Composite Contextual Upset Probability Index
        composite_upset_index = round(
            (format_score * 0.25) +
            (motivation_data["motivation_gap_index"] * 0.45) +
            (logistics_data["logistical_friction_index"] * 0.30),
            2
        )

        return {
            "season_format": {
                "type": metrics.season_type,
                "progress": metrics.season_stage_progress,
                "upset_variance_factor": format_score,
                "description": format_desc
            },
            "motivation_gap": motivation_data,
            "logistics_and_environment": logistics_data,
            "composite_contextual_upset_index": composite_upset_index
        }


# Example Usage
if __name__ == "__main__":
    context_data = LeagueScheduleMetrics(
        season_type="sprint",                         # State league or Apertura playoff stage
        season_stage_progress=0.80,                  # Late-stage sprint match
        favorite_rotation_index=0.65,                # Resting 6 primary starters
        favorite_has_continental_cup_in_3days=True,  # Crucial Libertadores knockout game mid-week
        favorite_match_importance=0.40,             # League position locked/secondary priority
        favorite_travel_distance_km=2100.0,          # Cross-country travel fatigue (e.g., Brazil/MLS)
        favorite_rest_days=3,                        # Compressed schedule
        underdog_rest_days=7,                        # Full week of home prep
        pitch_condition_degrader=0.70                # Poor/bumpy pitch surface neutralizing technical dominance
    )

    analyzer = LeagueScheduleContextAnalyzer()
    report = analyzer.analyze(context_data)

    import json
    print(json.dumps(report, indent=4))
    