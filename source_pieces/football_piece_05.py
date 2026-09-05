from typing import Dict, Any, List, Optional

class UnderdogOddsAnalyzer:
    """
    Step 24 Engine: Analyzes odds across Pinnacle, Stake, and Bet365 for the underdog.
    Isolates maximum value, minimum line, and bookmaker spread.
    """

    def extract_underdog_odds_range(
        self,
        underdog_name: str,
        bookmaker_odds: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        :param underdog_name: Name of the underdog team
        :param bookmaker_odds: Dict with keys 'pinnacle', 'stake', 'bet365' and float odds
        """
        # Filter for requested sites (case-insensitive key matching)
        target_sites = ["pinnacle", "stake", "bet365"]
        filtered_odds = {
            k.lower(): v for k, v in bookmaker_odds.items() 
            if k.lower() in target_sites and v > 1.0
        }

        if not filtered_odds:
            return {
                "error": "No valid odds found for Pinnacle, Stake, or Bet365",
                "underdog": underdog_name
            }

        # Identify Highest and Lowest Odds
        highest_site = max(filtered_odds, key=filtered_odds.get)
        highest_odds = filtered_odds[highest_site]

        lowest_site = min(filtered_odds, key=filtered_odds.get)
        lowest_odds = filtered_odds[lowest_site]

        spread_pct = round(((highest_odds - lowest_odds) / lowest_odds) * 100, 2)

        return {
            "underdog_team": underdog_name,
            "comparison_sites": list(filtered_odds.keys()),
            "highest_odds": {
                "bookmaker": highest_site.capitalize(),
                "odds": highest_odds
            },
            "lowest_odds": {
                "bookmaker": lowest_site.capitalize(),
                "odds": lowest_odds
            },
            "odds_spread_percentage": f"{spread_pct}%",
            "raw_odds_breakdown": {k.capitalize(): v for k, v in filtered_odds.items()}
        }


class ScheduleContextEngine:
    """
    Step 25 Engine: Assesses fatigue, fixture congestion, and lookahead/hangover risks.
    Determines if a top-tier team is likely to rotate key players due to an upcoming 
    or recent major fixture (e.g., Champions League, Derby, Cup Final).
    """

    def evaluate_favorite_schedule_context(
        self,
        favorite_team: str,
        days_until_next_fixture: Optional[int] = None,
        next_fixture_importance: str = "NORMAL",  # 'HIGH' (e.g. UCL Knockout, Derby), 'NORMAL', 'LOW'
        next_fixture_name: str = "",
        days_since_last_fixture: Optional[int] = None,
        last_fixture_importance: str = "NORMAL",
        league_title_pressure: str = "HIGH"      # 'HIGH' (Must Win for Title/Top 4), 'MODERATE', 'LOW'
    ) -> Dict[str, Any]:
        
        rotation_risk = "LOW"
        lookahead_factor = False
        hangover_factor = False
        reasons = []

        # 1. Lookahead Effect (Upcoming Big Match)
        if days_until_next_fixture is not None and days_until_next_fixture <= 4:
            if next_fixture_importance.upper() == "HIGH":
                lookahead_factor = True
                rotation_risk = "HIGH"
                reasons.append(
                    f"Lookahead Risk: {favorite_team} plays a major fixture ('{next_fixture_name}') in {days_until_next_fixture} days."
                )

        # 2. Hangover Effect (Recent Intense Match)
        if days_since_last_fixture is not None and days_since_last_fixture <= 3:
            if last_fixture_importance.upper() == "HIGH":
                hangover_factor = True
                if rotation_risk != "HIGH":
                    rotation_risk = "MODERATE"
                reasons.append(
                    f"Fatigue/Hangover Risk: Played a high-intensity match {days_since_last_fixture} days ago."
                )

        # 3. Must-Win Assessment vs. Rotation Incentive
        if league_title_pressure.upper() == "HIGH":
            must_win_status = "CRITICAL MUST-WIN (Points non-negotiable for league objectives)"
            if rotation_risk == "HIGH":
                rotation_risk = "MODERATE (Rotation balanced by critical league point necessity)"
        elif league_title_pressure.upper() == "LOW":
            must_win_status = "LOW URGENCY (Safe position; high likelihood of benching key starters)"
            if lookahead_factor:
                rotation_risk = "EXTREME (Heavy squad rotation expected)"
        else:
            must_win_status = "MODERATE URGENCY (Points valuable, but squad management possible)"

        return {
            "favorite_team": favorite_team,
            "step_25_context": {
                "rotation_risk_level": rotation_risk,
                "lookahead_effect_present": lookahead_factor,
                "hangover_effect_present": hangover_factor,
                "must_win_urgency": must_win_status,
                "contextual_notes": reasons if reasons else ["No severe fixture congestion or lookahead risks detected."]
            }
        }


class WeatherDisruptionEngine:
    """
    Step 26 Engine: Checks localized weather conditions around the match venue 
    to evaluate risks of postponement, delays, or pitch deterioration.
    """

    def evaluate_weather_impact(
        self,
        venue_name: str,
        precipitation_mm: float,
        wind_speed_kmh: float,
        temperature_c: float,
        weather_condition: str = "Clear"  # e.g., 'Heavy Rain', 'Snow', 'Thunderstorm', 'Fog'
    ) -> Dict[str, Any]:
        
        postponement_risk = "LOW"
        delay_risk = "LOW"
        tactical_impact = "NORMAL"
        flags = []

        cond = weather_condition.lower()

        # 1. Postponement / Suspension Thresholds
        if "thunderstorm" in cond or "lightning" in cond:
            delay_risk = "HIGH"
            postponement_risk = "MODERATE"
            flags.append("Electrical storm hazard: High probability of match delays or temporary suspension.")

        if precipitation_mm >= 35.0 or "torrential" in cond or "heavy snow" in cond:
            postponement_risk = "HIGH"
            flags.append(f"Excessive precipitation ({precipitation_mm}mm): Pitch waterlogging or unplayable surface risk.")

        if wind_speed_kmh >= 75.0 or "gale" in cond:
            postponement_risk = "MODERATE"
            delay_risk = "HIGH"
            flags.append(f"Extreme wind speeds ({wind_speed_kmh} km/h): Structural/ball movement disruption risk.")

        if temperature_c <= -10.0 or temperature_c >= 40.0:
            flags.append(f"Extreme temperature ({temperature_c}°C): Player safety hazard / mandated cooling/heating breaks.")

        # 2. Style of Play / Tactical Impact
        if precipitation_mm >= 15.0 or "rain" in cond:
            tactical_impact = "SLICK/HEAVY PITCH (Favors direct play, increases errors/slip-ups)"
        elif wind_speed_kmh >= 45.0:
            tactical_impact = "HIGH WIND (Impairs long passing accuracy and high aerial balls)"

        return {
            "venue": venue_name,
            "weather_summary": f"{weather_condition}, {temperature_c}°C, Wind: {wind_speed_kmh} km/h, Rain: {precipitation_mm}mm",
            "step_26_disruption_assessment": {
                "postponement_risk": postponement_risk,
                "delay_risk": delay_risk,
                "tactical_pitch_impact": tactical_impact,
                "alerts": flags if flags else ["No weather-related disruption anticipated."]
            }
        }


# Pipeline Execution
if __name__ == "__main__":
    print("--- STEPS 24, 25 & 26 ANALYTICS PIPELINE ---")

    # Step 24: Underdog Odds Comparison
    odds_analyzer = UnderdogOddsAnalyzer()
    sample_odds = {
        "Pinnacle": 4.60,
        "Stake": 4.85,
        "Bet365": 4.40,
        "Unibet": 4.50  # Ignored by step 24 filter
    }
    step_24_out = odds_analyzer.extract_underdog_odds_range(
        underdog_name="Bournemouth",
        bookmaker_odds=sample_odds
    )
    print(f"\n[Step 24 - Underdog Odds Range]:")
    print(f"  Highest: {step_24_out['highest_odds']['bookmaker']} @ {step_24_out['highest_odds']['odds']}")
    print(f"  Lowest:  {step_24_out['lowest_odds']['bookmaker']} @ {step_24_out['lowest_odds']['odds']}")
    print(f"  Spread:  {step_24_out['odds_spread_percentage']}")

    # Step 25: Schedule & Rotation Context
    schedule_engine = ScheduleContextEngine()
    step_25_out = schedule_engine.evaluate_favorite_schedule_context(
        favorite_team="Arsenal",
        days_until_next_fixture=3,
        next_fixture_importance="HIGH",
        next_fixture_name="UEFA Champions League Quarter-Final vs Real Madrid",
        days_since_last_fixture=4,
        league_title_pressure="HIGH"
    )
    print(f"\n[Step 25 - Favorite Rotation & Schedule Risk]:")
    print(f"  Rotation Risk Level: {step_25_out['step_25_context']['rotation_risk_level']}")
    print(f"  Must-Win Urgency:    {step_25_out['step_25_context']['must_win_urgency']}")
    for note in step_25_out['step_25_context']['contextual_notes']:
        print(f"  * {note}")

    # Step 26: Weather Disruption Assessment
    weather_engine = WeatherDisruptionEngine()
    step_26_out = weather_engine.evaluate_weather_impact(
        venue_name="Emirates Stadium, London",
        precipitation_mm=5.0,
        wind_speed_kmh=22.0,
        temperature_c=14.0,
        weather_condition="Light Rain"
    )
    print(f"\n[Step 26 - Weather Impact]:")
    print(f"  Postponement Risk: {step_26_out['step_26_disruption_assessment']['postponement_risk']}")
    print(f"  Tactical Pitch:    {step_26_out['step_26_disruption_assessment']['tactical_pitch_impact']}")
    for alert in step_26_out['step_26_disruption_assessment']['alerts']:
        print(f"  * {alert}")
        from typing import Dict, Any, List, Optional

class TeamGapFilter:
    """
    Step 27 Engine: Evaluates the structural gap between competing teams across 
    table standings, ELO rating differential, market value ratio, and xG dominance.
    Ensures the matchup falls within a viable analytical window (avoiding unpredictable 
    extreme mismatches or ultra-tight coin flips).
    """

    def __init__(self, min_gap_score: float = 20.0, max_gap_score: float = 80.0):
        """
        :param min_gap_score: Lower bound (below this is an unpredictable coin-flip match)
        :param max_gap_score: Upper bound (above this is an extreme mismatch/blowout risk)
        """
        self.min_gap = min_gap_score
        self.max_gap = max_gap_score

    def evaluate_team_gap(
        self,
        home_team: str,
        away_team: str,
        table_position_gap: Optional[int] = None,
        elo_diff: float = 0.0,            # Positive = Home favorite, Negative = Away favorite
        home_xg_90: float = 1.5,
        away_xg_90: float = 1.2,
        market_value_ratio: float = 1.0   # Home squad value / Away squad value
    ) -> Dict[str, Any]:
        
        # 1. Component Sub-Scores (Normalized 0 to 100)
        # ELO Differential Contribution (150 ELO diff ~ 70% win probability)
        elo_gap_score = min(100.0, abs(elo_diff) / 3.0)

        # Table Position Gap Contribution (assuming 20-team league)
        if table_position_gap is not None:
            table_gap_score = min(100.0, (table_position_gap / 19.0) * 100.0)
        else:
            table_gap_score = elo_gap_score  # Fallback to ELO

        # xG Metric Gap Contribution
        xg_diff = abs(home_xg_90 - away_xg_90)
        xg_gap_score = min(100.0, (xg_diff / 1.5) * 100.0)

        # Market Value Disparity Contribution
        value_ratio_normalized = max(market_value_ratio, 1.0 / max(market_value_ratio, 0.01))
        value_gap_score = min(100.0, (value_ratio_normalized - 1.0) * 25.0)

        # Composite Structural Gap Index (0 = Identical Strength, 100 = Total Mismatch)
        composite_gap_index = round(
            (elo_gap_score * 0.35) +
            (table_gap_score * 0.25) +
            (xg_gap_score * 0.25) +
            (value_gap_score * 0.15),
            2
        )

        # 2. Gap Classification
        if composite_gap_index > self.max_gap:
            gap_classification = "EXTREME GULF (Heavy Blowout Risk / Low Value Odds)"
            filter_status = "REJECTED (Gap Too Wide)"
            eligible = False
        elif composite_gap_index < self.min_gap:
            gap_classification = "BALANCED EQUILIBRIUM (Coin-Flip Match / High Variance)"
            filter_status = "REJECTED (Gap Too Tight)"
            eligible = False
        else:
            gap_classification = "PRIME ANALYTICAL WINDOW (Optimal Disparity for Value)"
            filter_status = "APPROVED"
            eligible = True

        return {
            "match": f"{home_team} vs {away_team}",
            "step_27_composite_gap_index": composite_gap_index,
            "gap_classification": gap_classification,
            "filter_status": filter_status,
            "is_eligible": eligible,
            "metrics_breakdown": {
                "elo_gap_score": round(elo_gap_score, 2),
                "table_gap_score": round(table_gap_score, 2),
                "xg_gap_score": round(xg_gap_score, 2),
                "market_value_gap_score": round(value_gap_score, 2)
            }
        }


class MotivationFilter:
    """
    Step 28 Engine: Evaluates contextual team motivation based on seasonal stakes,
    relegation pressure, title races, derby rivalries, and 'beach mode' (nothing to play for).
    Detects asymmetric motivation traps where a demotivated favorite plays a desperate underdog.
    """

    STAKE_SCORES = {
        "RELEGATION_BATTLE": 10.0,   # Absolute maximum urgency
        "TITLE_RACE": 9.5,
        "TOP_4_UCL_QUALIFICATION": 8.5,
        "EUROPEAN_SPOTS": 7.0,
        "DERBY_RIVALRY": 8.0,
        "CUP_FINAL_PREP": 4.0,        # May rest players in league
        "MID_TABLE_SAFE": 3.0,        # 'Beach mode' / Low urgency
        "DEAD_RUBBER": 1.0            # Mathematically meaningless
    }

    def evaluate_motivation_dynamics(
        self,
        home_team: str,
        home_stake_category: str,
        away_team: str,
        away_stake_category: str,
        is_derby: bool = False,
        remaining_league_games: int = 10
    ) -> Dict[str, Any]:
        """
        :param home_stake_category: One of STAKE_SCORES keys
        :param away_stake_category: One of STAKE_SCORES keys
        :param is_derby: Boolean flag for local derby
        :param remaining_league_games: Games remaining in the season
        """
        home_cat = home_stake_category.upper()
        away_cat = away_stake_category.upper()

        home_base_score = self.STAKE_SCORES.get(home_cat, 5.0)
        away_base_score = self.STAKE_SCORES.get(away_cat, 5.0)

        # Late-season motivation amplifier (Urgency spikes under 6 games remaining)
        season_late_factor = 1.25 if remaining_league_games <= 6 else 1.0

        home_final_score = round(min(10.0, home_base_score * (season_late_factor if home_base_score >= 7.0 else 1.0)), 1)
        away_final_score = round(min(10.0, away_base_score * (season_late_factor if away_base_score >= 7.0 else 1.0)), 1)

        if is_derby:
            home_final_score = max(home_final_score, 8.5)
            away_final_score = max(away_final_score, 8.5)

        motivation_delta = round(home_final_score - away_final_score, 1)

        # Detect Motivation Asymmetry (Trap Match Warning)
        asymmetry_warning = False
        trap_details = "Balanced motivation dynamics."

        if home_final_score >= 8.5 and away_final_score <= 4.0:
            asymmetry_warning = True
            trap_details = f"HIGH ASYMMETRY: {home_team} highly motivated ({home_stake_category}) vs demotivated {away_team} ({away_stake_category})."
        elif away_final_score >= 8.5 and home_final_score <= 4.0:
            asymmetry_warning = True
            trap_details = f"TRAP WARNING: Underdog {away_team} highly motivated ({away_stake_category}) vs demotivated Favorite {home_team} ({home_stake_category})."

        # Motivation Filter Verdict
        if home_final_score <= 3.0 and away_final_score <= 3.0:
            filter_status = "REJECTED (Dead Rubber Match - Both Teams Demotivated)"
            eligible = False
        else:
            filter_status = "APPROVED"
            eligible = True

        return {
            "match": f"{home_team} vs {away_team}",
            "step_28_motivation": {
                "home_motivation_score": f"{home_final_score}/10 ({home_stake_category})",
                "away_motivation_score": f"{away_final_score}/10 ({away_stake_category})",
                "motivation_delta": motivation_delta,
                "is_derby": is_derby,
                "asymmetry_warning": asymmetry_warning,
                "context_analysis": trap_details
            },
            "filter_status": filter_status,
            "is_eligible": eligible
        }


# Example Execution
if __name__ == "__main__":
    print("--- STEPS 27 & 28: TEAM GAP & MOTIVATION FILTERS ---")

    # Step 27 Test: Team Gap Filter
    gap_filter = TeamGapFilter(min_gap_score=20.0, max_gap_score=80.0)
    gap_res = gap_filter.evaluate_team_gap(
        home_team="Arsenal",
        away_team="Bournemouth",
        table_position_gap=10,
        elo_diff=185.0,
        home_xg_90=1.95,
        away_xg_90=1.05,
        market_value_ratio=3.2
    )
    print(f"\n[Step 27 - Team Gap Filter]:")
    print(f"  Gap Index:    {gap_res['step_27_composite_gap_index']}/100")
    print(f"  Category:     {gap_res['gap_classification']}")
    print(f"  Status:       {gap_res['filter_status']}")

    # Step 28 Test: Motivation Filter (Trap Match Scenario)
    mot_filter = MotivationFilter()
    mot_res = mot_filter.evaluate_motivation_dynamics(
        home_team="Chelsea",
        home_stake_category="MID_TABLE_SAFE",
        away_team="Everton",
        away_stake_category="RELEGATION_BATTLE",
        is_derby=False,
        remaining_league_games=4
    )
    print(f"\n[Step 28 - Motivation Filter]:")
    print(f"  Home Score:   {mot_res['step_28_motivation']['home_motivation_score']}")
    print(f"  Away Score:   {mot_res['step_28_motivation']['away_motivation_score']}")
    print(f"  Asymmetry:    {mot_res['step_28_motivation']['asymmetry_warning']}")
    print(f"  Context:      {mot_res['step_28_motivation']['context_analysis']}")
    print(f"  Status:       {mot_res['filter_status']}")
    from typing import Dict, Any, List, Optional
import math

class ResistanceFilter:
    """
    Step 29 Engine: Analyzes market line resistance and defensive tactical resilience.
    Identifies if a selection is hitting a sharp price wall (market resistance) 
    or if the team possesses strong defensive resilience against high-pressure opponents.
    """

    def __init__(self, key_handicap_barriers: Optional[List[float]] = None):
        # Key Asian Handicap / Goal lines where sharp resistance typically occurs
        self.key_barriers = key_handicap_barriers or [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.5]

    def evaluate_market_and_tactical_resistance(
        self,
        team_name: str,
        opening_odds: float,
        current_odds: float,
        current_handicap: float,
        defensive_xga_last5: float,       # Expected Goals Allowed over last 5 matches
        clean_sheet_pct_last10: float,    # Percentage 0.0 to 1.0
        low_block_resilience_rating: float # Rating 0 to 100 (defensive organization)
    ) -> Dict[str, Any]:
        """
        Evaluates both market price movement resistance and tactical defensive resistance.
        """
        # 1. Market Odds Movement & Resistance Analysis
        implied_open_prob = (1.0 / opening_odds) * 100 if opening_odds > 0 else 0
        implied_curr_prob = (1.0 / current_odds) * 100 if current_odds > 0 else 0
        prob_shift = round(implied_curr_prob - implied_open_prob, 2)

        # Detect Market Resistance Barrier (Price movement stopping at key lines)
        near_key_barrier = any(abs(current_handicap - barrier) < 0.05 for barrier in self.key_barriers)
        
        # Line movement direction
        if current_odds < opening_odds:
            movement_type = "STEAM_INFLOW (Odds shortening / Market buying)"
        elif current_odds > opening_odds:
            movement_type = "DRIFTING (Odds lengthening / Market selling)"
        else:
            movement_type = "STATIC (No price movement)"

        # Market Resistance Score (Higher = Stronger price support/wall)
        market_resistance_score = round(min(100.0, max(0.0, 50.0 + (prob_shift * 2.5))), 2)

        # 2. Tactical Defensive Resistance Index
        # Lower xGA and higher clean sheet % = Higher structural resistance against conceding
        xga_factor = max(0.0, 100.0 - (defensive_xga_last5 * 30.0))
        cs_factor = clean_sheet_pct_last10 * 100.0
        
        tactical_resistance_index = round(
            (xga_factor * 0.40) +
            (cs_factor * 0.30) +
            (low_block_resilience_rating * 0.30),
            2
        )

        # 3. Overall Resistance Verdict
        # Strong resistance = Team is hard to beat AND/OR odds have hit a solid sharp floor
        is_tactically_resilient = tactical_resistance_index >= 55.0
        has_market_support = market_resistance_score >= 45.0

        if is_tactically_resilient and has_market_support:
            filter_status = "APPROVED (High Tactical & Market Resistance Support)"
            eligible = True
        elif is_tactically_resilient:
            filter_status = "APPROVED (Solid Defensive Resistance / Market Neutral)"
            eligible = True
        else:
            filter_status = "REJECTED (Fragile Defensive Structure / Low Resistance)"
            eligible = False

        return {
            "team": team_name,
            "step_29_resistance": {
                "market_movement": movement_type,
                "implied_prob_shift_pct": f"{prob_shift}%",
                "market_resistance_score": f"{market_resistance_score}/100",
                "near_key_handicap_barrier": near_key_barrier,
                "tactical_resistance_index": f"{tactical_resistance_index}/100",
                "defensive_breakdown": {
                    "xGA_last_5": defensive_xga_last5,
                    "clean_sheet_pct": f"{round(clean_sheet_pct_last10 * 100, 1)}%",
                    "low_block_rating": low_block_resilience_rating
                }
            },
            "filter_status": filter_status,
            "is_eligible": eligible
        }


class FormFilter:
    """
    Step 30 Engine: Evaluates team momentum using exponentially weighted recency decay,
    Opponent-Strength Adjusted Form (SoS), and Underlying Performance vs Results Delta (xG vs Points).
    """

    def __init__(self, decay_weights: Optional[List[float]] = None):
        # Default recency weights for last 5 games (most recent game = index 0)
        self.weights = decay_weights or [0.35, 0.25, 0.20, 0.12, 0.08]

    def evaluate_recent_form(
        self,
        team_name: str,
        recent_matches: List[Dict[str, Any]]
        # Each dict format: {'points': 3|1|0, 'xg_for': float, 'xg_against': float, 'opp_elo': float}
    ) -> Dict[str, Any]:
        """
        Evaluates weighted form over the provided matches (up to length of weights).
        """
        n_matches = min(len(recent_matches), len(self.weights))
        if n_matches == 0:
            return {
                "error": "No match history provided for Form Filter",
                "filter_status": "REJECTED (Insufficient Data)",
                "is_eligible": False
            }

        # Normalize weights if fewer than 5 matches
        used_weights = self.weights[:n_matches]
        weight_sum = sum(used_weights)
        norm_weights = [w / weight_sum for w in used_weights]

        weighted_points = 0.0
        weighted_xg_diff = 0.0
        sos_total = 0.0
        actual_points_total = 0

        for i in range(n_matches):
            match = recent_matches[i]
            w = norm_weights[i]

            pts = match.get('points', 0)
            actual_points_total += pts

            xg_f = match.get('xg_for', 1.0)
            xg_a = match.get('xg_against', 1.0)
            xg_diff = xg_f - xg_a

            opp_elo = match.get('opp_elo', 1500.0)
            # Strength of Schedule multiplier (1500 ELO = 1.0 baseline)
            sos_multiplier = max(0.7, min(1.3, opp_elo / 1500.0))

            weighted_points += (pts / 3.0) * w * sos_multiplier
            weighted_xg_diff += xg_diff * w
            sos_total += opp_elo * w

        # Form Index (0 to 100)
        weighted_form_score = round(min(100.0, weighted_points * 100.0), 2)
        avg_weighted_xg_diff = round(weighted_xg_diff, 2)
        avg_opp_elo = round(sos_total, 1)

        # Detect Luck / Performance Divergence (Points vs xG)
        # Expected points approximation from weighted xG diff
        expected_pts_equiv = (avg_weighted_xg_diff + 1.5) / 3.0 # rough scaling
        actual_pts_equiv = actual_points_total / (n_matches * 3.0)
        divergence = round(actual_pts_equiv - expected_pts_equiv, 2)

        if divergence > 0.25:
            form_quality = "OVERPERFORMING xG (Results masking poor underlying metrics - Regression Risk)"
        elif divergence < -0.25:
            form_quality = "UNDERPERFORMING xG (Unlucky results despite solid metrics - Bounce Back Candidate)"
        else:
            form_quality = "SUSTAINABLE (Results align accurately with underlying xG performance)"

        # Determine Form Trajectory
        if weighted_form_score >= 65.0:
            form_trend = "SURGING (High Momentum)"
        elif weighted_form_score >= 40.0:
            form_trend = "STABLE (Moderate/Consistent Form)"
        else:
            form_trend = "SLUMPING (Poor Form / Negative Momentum)"

        # Form Filter Threshold (Minimum score required to pass)
        if weighted_form_score >= 35.0 or (weighted_form_score >= 25.0 and divergence < -0.20):
            filter_status = "APPROVED"
            eligible = True
        else:
            filter_status = "REJECTED (Critically Poor Weighted Form)"
            eligible = False

        return {
            "team": team_name,
            "step_30_form": {
                "weighted_form_score": f"{weighted_form_score}/100",
                "form_trend": form_trend,
                "form_quality_sustainability": form_quality,
                "weighted_xg_net_diff": avg_weighted_xg_diff,
                "avg_opponent_elo_faced": avg_opp_elo,
                "raw_points_last_n": f"{actual_points_total}/{n_matches * 3}"
            },
            "filter_status": filter_status,
            "is_eligible": eligible
        }


# Pipeline Execution Example
if __name__ == "__main__":
    print("--- STEPS 29 & 30: RESISTANCE & FORM FILTERS ---")

    # Step 29 Test: Resistance Filter
    resistance_filter = ResistanceFilter()
    res_out = resistance_filter.evaluate_market_and_tactical_resistance(
        team_name="Crystal Palace",
        opening_odds=3.60,
        current_odds=3.30,
        current_handicap=0.5,
        defensive_xga_last5=1.10,
        clean_sheet_pct_last10=0.40,
        low_block_resilience_rating=72.0
    )
    print(f"\n[Step 29 - Resistance Filter]:")
    print(f"  Tactical Index: {res_out['step_29_resistance']['tactical_resistance_index']}")
    print(f"  Market Score:   {res_out['step_29_resistance']['market_resistance_score']}")
    print(f"  Movement:       {res_out['step_29_resistance']['market_movement']}")
    print(f"  Status:         {res_out['filter_status']}")

    # Step 30 Test: Form Filter (Last 5 Matches, Most Recent First)
    sample_recent_matches = [
        {'points': 3, 'xg_for': 2.1, 'xg_against': 0.8, 'opp_elo': 1650}, # Most recent (Win vs strong team)
        {'points': 1, 'xg_for': 1.4, 'xg_against': 1.2, 'opp_elo': 1520},
        {'points': 3, 'xg_for': 1.8, 'xg_against': 0.5, 'opp_elo': 1480},
        {'points': 0, 'xg_for': 0.9, 'xg_against': 1.9, 'opp_elo': 1710},
        {'points': 1, 'xg_for': 1.1, 'xg_against': 1.1, 'opp_elo': 1500}  # 5th most recent
    ]

    form_filter = FormFilter()
    form_out = form_filter.evaluate_recent_form(
        team_name="Crystal Palace",
        recent_matches=sample_recent_matches
    )
    print(f"\n[Step 30 - Form Filter]:")
    print(f"  Weighted Score: {form_out['step_30_form']['weighted_form_score']}")
    print(f"  Trend:          {form_out['step_30_form']['form_trend']}")
    print(f"  Quality/xG:     {form_out['step_30_form']['form_quality_sustainability']}")
    print(f"  Status:         {form_out['filter_status']}")