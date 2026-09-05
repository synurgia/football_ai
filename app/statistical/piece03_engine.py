import math
from typing import List, Dict, Any, Tuple

class FiveDimensionalAnalyticsEngine:
    """
    Step 14 & Step 15 Engine:
    Executes 10-match historical form extraction and synthesizes a 5-Dimensional 
    predictive state across momentum, xG efficiency, defensive stability, 
    recency-weighted performance, and variance control.
    """

    def __init__(self, recency_decay: float = 0.85):
        # Recency decay factor (0.85 weights match N higher than match N-1)
        self.decay = recency_decay

    def analyze_10_game_history(self, team_name: str, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Step 15: Evaluates the last 10 games for a team.
        Expects matches list ordered chronologically [oldest ... newest].
        """
        recent_10 = matches[-10:] if len(matches) >= 10 else matches
        
        wins, draws, losses = 0, 0, 0
        goals_for, goals_against = 0, 0
        clean_sheets, failed_to_score = 0, 0
        
        weighted_points = 0.0
        max_possible_weight = 0.0

        game_logs = []

        for idx, match in enumerate(recent_10):
            # Recency weight index (1 to len)
            weight = math.pow(1 / self.decay, idx)
            max_possible_weight += weight * 3.0

            gf = match.get("gf", 0)
            ga = match.get("ga", 0)
            goals_for += gf
            goals_against += ga

            if gf > ga:
                wins += 1
                pts = 3
                outcome = "W"
            elif gf == ga:
                draws += 1
                pts = 1
                outcome = "D"
            else:
                losses += 1
                pts = 0
                outcome = "L"

            if ga == 0:
                clean_sheets += 1
            if gf == 0:
                failed_to_score += 1

            weighted_points += pts * weight
            game_logs.append(f"{outcome}({gf}-{ga})")

        total_games = len(recent_10) or 1
        raw_points = (wins * 3) + draws
        ppg = round(raw_points / total_games, 2)
        goal_diff = goals_for - goals_against
        
        # Weighted Form Score normalized (0.0 to 100.0)
        weighted_form_score = round((weighted_points / max_possible_weight) * 100, 2) if max_possible_weight > 0 else 0.0

        # Form Trajectory Trend (comparing last 5 vs prior 5)
        if total_games >= 10:
            first_5_pts = sum([3 if m['gf']>m['ga'] else 1 if m['gf']==m['ga'] else 0 for m in recent_10[:5]])
            last_5_pts = sum([3 if m['gf']>m['ga'] else 1 if m['gf']==m['ga'] else 0 for m in recent_10[5:]])
            trend_diff = last_5_pts - first_5_pts
            
            if trend_diff >= 3:
                trend = "Surging (+ Uptrend)"
            elif trend_diff <= -3:
                trend = "Declining (- Downtrend)"
            else:
                trend = "Stable / Steady"
        else:
            trend = "Insufficient Depth"

        return {
            "team": team_name,
            "sample_size": total_games,
            "record": f"{wins}W-{draws}D-{losses}L",
            "sequence": "".join([x[0] for x in game_logs]),
            "ppg": ppg,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "goal_difference": goal_diff,
            "clean_sheets": clean_sheets,
            "failed_to_score": failed_to_score,
            "weighted_form_score": weighted_form_score,
            "trend": trend
        }

    def generate_5d_prediction_matrix(
        self, 
        home_form: Dict[str, Any], 
        away_form: Dict[str, Any],
        home_xg_avg: float = 1.6,
        away_xg_avg: float = 1.1
    ) -> Dict[str, Any]:
        """
        Step 14: Synthesizes 5 High-Dimensional Vectors:
        1. Momentum Vector (Recency & Form Score)
        2. xG Efficiency Index (Expected vs Actual Goal conversion)
        3. Defensive Resistance Matrix (Clean Sheet & Suppress Ratio)
        4. Volatility / Variance Risk Factor
        5. Predictive Alignment Core (Dimensional Edge)
        """
        # Vector 1: Momentum Differential
        momentum_delta = home_form["weighted_form_score"] - away_form["weighted_form_score"]

        # Vector 2: Offensive Threat Ratio
        home_offense_index = (home_form["goals_for"] / max(home_form["sample_size"], 1)) * home_xg_avg
        away_offense_index = (away_form["goals_for"] / max(away_form["sample_size"], 1)) * away_xg_avg

        # Vector 3: Defensive Stability Score
        home_defense = (home_form["clean_sheets"] * 2) - (home_form["goals_against"] / max(home_form["sample_size"], 1))
        away_defense = (away_form["clean_sheets"] * 2) - (away_form["goals_against"] / max(away_form["sample_size"], 1))

        # Vector 4: Volatility Index (variance in outcomes)
        volatility_score = abs(home_form["goal_difference"] - away_form["goal_difference"]) / 10.0

        # Vector 5: Dimensional Composite Prediction Index (-100.0 Away Dominated to +100.0 Home Dominated)
        dimensional_index = (momentum_delta * 0.40) + ((home_offense_index - away_offense_index) * 20.0) + ((home_defense - away_defense) * 10.0)
        dimensional_index = max(-100.0, min(100.0, round(dimensional_index, 2)))

        if dimensional_index > 25.0:
            predicted_state = f"High-Confidence Dominance: {home_form['team']}"
        elif dimensional_index < -25.0:
            predicted_state = f"High-Confidence Dominance: {away_form['team']}"
        elif abs(dimensional_index) <= 10.0:
            predicted_state = "Neutral Equilibrium (High Draw Probability)"
        else:
            dominant = home_form['team'] if dimensional_index > 0 else away_form['team']
            predicted_state = f"Slight Edge: {dominant} (Volatile Margin)"

        return {
            "dim_1_momentum_delta": round(momentum_delta, 2),
            "dim_2_offensive_threat": {"home": round(home_offense_index, 2), "away": round(away_offense_index, 2)},
            "dim_3_defensive_stability": {"home": round(home_defense, 2), "away": round(away_defense, 2)},
            "dim_4_volatility_score": round(volatility_score, 2),
            "dim_5_composite_index": dimensional_index,
            "5d_predictive_state": predicted_state
        }


# Example Pipeline Integration
if __name__ == "__main__":
    # Mock last 10 games for Home and Away teams [oldest ... newest]
    home_matches_10 = [
        {"gf": 1, "ga": 0}, {"gf": 2, "ga": 1}, {"gf": 0, "ga": 0}, {"gf": 3, "ga": 1}, {"gf": 1, "ga": 2},
        {"gf": 2, "ga": 0}, {"gf": 4, "ga": 1}, {"gf": 1, "ga": 1}, {"gf": 2, "ga": 0}, {"gf": 3, "ga": 0}
    ]

    away_matches_10 = [
        {"gf": 0, "ga": 2}, {"gf": 1, "ga": 1}, {"gf": 1, "ga": 0}, {"gf": 0, "ga": 1}, {"gf": 2, "ga": 2},
        {"gf": 0, "ga": 3}, {"gf": 1, "ga": 0}, {"gf": 0, "ga": 0}, {"gf": 1, "ga": 2}, {"gf": 0, "ga": 1}
    ]

    engine = FiveDimensionalAnalyticsEngine(recency_decay=0.85)

    # Step 15 Analysis
    home_form = engine.analyze_10_game_history("Home FC", home_matches_10)
    away_form = engine.analyze_10_game_history("Away City", away_matches_10)

    # Step 14 Analysis
    matrix_5d = engine.generate_5d_prediction_matrix(home_form, away_form, home_xg_avg=1.85, away_xg_avg=0.95)

    print("--- STEP 15: 10-GAME HISTORICAL FORM ---")
    print(f"Home ({home_form['team']}): {home_form['record']} | Sequence: {home_form['sequence']} | PPG: {home_form['ppg']} | Weighted Form: {home_form['weighted_form_score']}% | Trend: {home_form['trend']}")
    print(f"Away ({away_form['team']}): {away_form['record']} | Sequence: {away_form['sequence']} | PPG: {away_form['ppg']} | Weighted Form: {away_form['weighted_form_score']}% | Trend: {away_form['trend']}")

    print("\n--- STEP 14: 5D PREDICTIVE MATRIX ---")
    print(f"Composite 5D Index: {matrix_5d['dim_5_composite_index']} / 100")
    print(f"Predicted State:   {matrix_5d['5d_predictive_state']}")
    import math
from typing import Dict, Any, Tuple

class PoissonModelEngine:
    """
    Sub-System 1: Mathematical distribution model based on goal expectations.
    Calculates exact score probabilities and 1X2 market probabilities.
    """
    @staticmethod
    def _poisson_pmf(k: int, lambd: float) -> float:
        return (math.pow(lambd, k) * math.exp(-lambd)) / math.factorial(k)

    def calculate_1x2_probabilities(
        self, home_xg: float, away_xg: float, max_goals: int = 7
    ) -> Dict[str, float]:
        home_win_p = 0.0
        draw_p = 0.0
        away_win_p = 0.0

        for h in range(max_goals):
            p_h = self._poisson_pmf(h, home_xg)
            for a in range(max_goals):
                p_a = self._poisson_pmf(a, away_xg)
                prob = p_h * p_a

                if h > a:
                    home_win_p += prob
                elif h == a:
                    draw_p += prob
                else:
                    away_win_p += prob

        total = home_win_p + draw_p + away_win_p
        return {
            "1": round(home_win_p / total, 4),
            "X": round(draw_p / total, 4),
            "2": round(away_win_p / total, 4)
        }


class ValueBettingEngine:
    """
    Sub-System 2: Identifies positive Expected Value (+EV) and Kelly Criterion stake sizing.
    """
    @staticmethod
    def evaluate_market_edge(
        model_prob: float, bookmaker_odds: float, fractional_kelly: float = 0.25
    ) -> Dict[str, Any]:
        implied_prob = 1.0 / bookmaker_odds if bookmaker_odds > 0 else 0.0
        ev = (model_prob * bookmaker_odds) - 1.0  # Expected Value
        edge_pct = (model_prob - implied_prob) * 100

        # Fractional Kelly Criterion calculation
        b = bookmaker_odds - 1.0
        p = model_prob
        q = 1.0 - p
        kelly_full = (b * p - q) / b if b > 0 else 0.0
        recommended_stake_pct = max(0.0, round(kelly_full * fractional_kelly * 100, 2))

        has_value = ev > 0.03  # Minimum 3% expected value threshold

        return {
            "implied_prob_pct": round(implied_prob * 100, 2),
            "model_prob_pct": round(model_prob * 100, 2),
            "expected_value_ev": round(ev, 4),
            "edge_percentage": round(edge_pct, 2),
            "has_positive_value": has_value,
            "recommended_stake_pct": recommended_stake_pct if has_value else 0.0
        }


class AgentAIHybridEngine:
    """
    Sub-System 3: Agent AI Hybrid consensus layer.
    Blends Poisson mathematical priors with 5D multi-vector analytical signals.
    """
    def synthesize_consensus(
        self,
        poisson_probs: Dict[str, float],
        dim_5_index: float,
        weight_poisson: float = 0.60,
        weight_5d: float = 0.40
    ) -> Dict[str, float]:
        # Convert 5D index (-100 to +100) into probability shifts
        # Normalizing index to shift Home/Away probabilities
        shift = (dim_5_index / 100.0) * 0.20  # Max 20% shift boost

        adjusted_home = max(0.05, poisson_probs["1"] + shift)
        adjusted_away = max(0.05, poisson_probs["2"] - shift)
        adjusted_draw = max(0.05, poisson_probs["X"] - (abs(shift) * 0.5))

        total = adjusted_home + adjusted_draw + adjusted_away

        # Hybrid Weighted Blend
        final_home = round((adjusted_home / total) * weight_5d + poisson_probs["1"] * weight_poisson, 4)
        final_draw = round((adjusted_draw / total) * weight_5d + poisson_probs["X"] * weight_poisson, 4)
        final_away = round((adjusted_away / total) * weight_5d + poisson_probs["2"] * weight_poisson, 4)

        norm_total = final_home + final_draw + final_away
        return {
            "1": round(final_home / norm_total, 4),
            "X": round(final_draw / norm_total, 4),
            "2": round(final_away / norm_total, 4)
        }


class Step16MultiSystemVerifier:
    """
    Step 16 Pipeline: Cross-validates predictions across Poisson, Agent AI Hybrid, 
    and Value Betting engines before final verification approval.
    """
    def __init__(self):
        self.poisson_engine = PoissonModelEngine()
        self.value_engine = ValueBettingEngine()
        self.ai_hybrid_engine = AgentAIHybridEngine()

    def execute_multi_system_verification(
        self,
        home_team: str,
        away_team: str,
        home_xg: float,
        away_xg: float,
        dim_5_composite_index: float,
        bookmaker_odds: Dict[str, float]
    ) -> Dict[str, Any]:
        # System 1: Poisson Model Output
        poisson_probs = self.poisson_engine.calculate_1x2_probabilities(home_xg, away_xg)

        # System 2: Agent AI Hybrid Consensus
        hybrid_probs = self.ai_hybrid_engine.synthesize_consensus(
            poisson_probs=poisson_probs,
            dim_5_index=dim_5_composite_index
        )

        # Identify Primary Outcome Pick
        best_pick = max(hybrid_probs, key=hybrid_probs.get)
        best_pick_prob = hybrid_probs[best_pick]
        best_odds = bookmaker_odds.get(best_pick, 1.0)

        # System 3: Value Betting Verification
        value_analysis = self.value_engine.evaluate_market_edge(
            model_prob=best_pick_prob,
            bookmaker_odds=best_odds
        )

        # Verification Consensus Logic: Requires positive EV + model probability > 40%
        is_poisson_aligned = poisson_probs[best_pick] >= 0.35
        is_value_approved = value_analysis["has_positive_value"]
        has_sufficient_probability = best_pick_prob >= 0.42

        passed_all_systems = is_poisson_aligned and is_value_approved and has_sufficient_probability

        if passed_all_systems:
            verification_status = "VERIFIED (Passed All 3 Systems)"
            risk_level = "LOW / HIGH CONFIDENCE"
        elif is_value_approved and not is_poisson_aligned:
            verification_status = "PARTIAL APPROVAL (Value Edge Found, Mathematical Divergence)"
            risk_level = "MODERATE"
        else:
            verification_status = "REJECTED (Failed EV Threshold or Low Probability Density)"
            risk_level = "HIGH RISK / NO BET"

        return {
            "match": f"{home_team} vs {away_team}",
            "system_1_poisson_probs": poisson_probs,
            "system_2_agent_ai_hybrid_probs": hybrid_probs,
            "system_3_value_betting": {
                "selected_pick": best_pick,
                "market_odds": best_odds,
                "analysis": value_analysis
            },
            "step_16_verification": {
                "passed_all_systems": passed_all_systems,
                "poisson_aligned": is_poisson_aligned,
                "value_approved": is_value_approved,
                "status": verification_status,
                "risk_assessment": risk_level
            }
        }


# Example Execution
if __name__ == "__main__":
    verifier = Step16MultiSystemVerifier()

    # Inputs from prior steps (14, 15) and market odds
    output = verifier.execute_multi_system_verification(
        home_team="Arsenal",
        away_team="Chelsea",
        home_xg=1.95,
        away_xg=0.85,
        dim_5_composite_index=34.5,  # From Step 14
        bookmaker_odds={"1": 1.75, "X": 3.80, "2": 4.50}
    )

    print("--- STEP 16: MULTI-SYSTEM VERIFICATION ENGINE ---")
    print(f"Match: {output['match']}")
    print(f"1. Poisson Probabilities:      {output['system_1_poisson_probs']}")
    print(f"2. Agent AI Hybrid Probs:      {output['system_2_agent_ai_hybrid_probs']}")
    print(f"3. Value Edge Analysis (+EV):  {output['system_3_value_betting']['analysis']}")
    print(f"\nFinal Verification Status:      {output['step_16_verification']['status']}")
    print(f"Risk Rating:                  {output['step_16_verification']['risk_assessment']}")
    from typing import Dict, Any

class MustWinEvaluator:
    """
    Step 17 Engine: Isolates and evaluates the single highest probability 1X2 outcome.
    Applies strict thresholding to verify if a selection qualifies as an absolute
    'Must Win / Win or Die' high-conviction pick.
    """

    def __init__(self, prob_threshold_pct: float = 60.0, dominance_gap_pct: float = 25.0):
        """
        :param prob_threshold_pct: Minimum win probability required for 'Win or Die' status (e.g., 60.0%).
        :param dominance_gap_pct: Minimum percentage gap over the 2nd most likely outcome (e.g., 25.0%).
        """
        self.prob_threshold = prob_threshold_pct
        self.dominance_gap = dominance_gap_pct

    def isolate_must_win_selection(
        self,
        home_team: str,
        away_team: str,
        probabilities: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Evaluates 1X2 probabilities (from Poisson or AI Hybrid Consensus) 
        and calculates Win-or-Die eligibility.
        """
        # Normalize to percentage scale (0 - 100%)
        pct_probs = {
            k: round(v * 100 if v <= 1.0 else v, 2) 
            for k, v in probabilities.items()
        }

        # Rank outcomes by probability descending
        ranked_outcomes = sorted(pct_probs.items(), key=lambda item: item[1], reverse=True)
        primary_pick, primary_prob = ranked_outcomes[0]
        secondary_pick, secondary_prob = ranked_outcomes[1]

        prob_gap = primary_prob - secondary_prob

        # Map outcome code to readable choice
        pick_descriptions = {
            "1": f"{home_team} Win (Home)",
            "X": "Draw",
            "2": f"{away_team} Win (Away)"
        }
        selection_label = pick_descriptions.get(primary_pick, primary_pick)

        # Rule evaluation: Must-Win choice requires a straight win (1 or 2) and high probability gap
        is_straight_win = primary_pick in ["1", "2"]
        meets_prob_cutoff = primary_prob >= self.prob_threshold
        meets_gap_cutoff = prob_gap >= self.dominance_gap

        is_win_or_die_choice = is_straight_win and (meets_prob_cutoff or (primary_prob >= 55.0 and meets_gap_cutoff))

        # Classification and conviction metrics
        if is_win_or_die_choice:
            status = "QUALIFIED MUST WIN / WIN OR DIE CHOICE"
            conviction_rating = "ULTRA HIGH CONVICTION"
            conviction_score = min(100.0, round(primary_prob + (prob_gap * 0.25), 1))
        elif primary_prob >= 50.0:
            status = "STRONG FAVORITE (Fails Strict Win-Or-Die Threshold)"
            conviction_rating = "MODERATE HIGH CONVICTION"
            conviction_score = round(primary_prob, 1)
        else:
            status = "NO MUST-WIN CHOICE (Market Too Dispersed / High Risk)"
            conviction_rating = "LOW CONVICTION / VOLATILE"
            conviction_score = round(primary_prob, 1)

        return {
            "match": f"{home_team} vs {away_team}",
            "step_17_choice": {
                "selected_outcome_1x2": primary_pick,
                "selection_name": selection_label,
                "must_win_probability_pct": primary_prob,
                "runner_up_outcome": f"{secondary_pick} ({secondary_prob}%)",
                "dominance_gap_pct": round(prob_gap, 2)
            },
            "win_or_die_evaluation": {
                "is_win_or_die_qualified": is_win_or_die_choice,
                "status": status,
                "conviction_rating": conviction_rating,
                "conviction_score": f"{conviction_score}/100",
                "threshold_rules": f"Requires >= {self.prob_threshold}% Prob OR >= {self.dominance_gap}% Gap over 2nd pick"
            },
            "1x2_probabilities": pct_probs
        }


# Example Execution
if __name__ == "__main__":
    evaluator = MustWinEvaluator(prob_threshold_pct=60.0, dominance_gap_pct=25.0)

    # Test Probabilities derived from Step 16 verification engine
    consensus_probs = {
        "1": 0.6720,  # 67.20% Home Win
        "X": 0.2010,  # 20.10% Draw
        "2": 0.1270   # 12.70% Away Win
    }

    result = evaluator.isolate_must_win_selection(
        home_team="Arsenal",
        away_team="Bournemouth",
        probabilities=consensus_probs
    )

    print("--- STEP 17: MUST WIN / WIN OR DIE EVALUATION ---")
    print(f"Match:                   {result['match']}")
    print(f"Primary Pick (1X2):      {result['step_17_choice']['selected_outcome_1x2']} -> {result['step_17_choice']['selection_name']}")
    print(f"Must Win Probability:   {result['step_17_choice']['must_win_probability_pct']}%")
    print(f"Dominance Gap:           +{result['step_17_choice']['dominance_gap_pct']}% over second pick")
    print(f"Win or Die Qualified:    {result['win_or_die_evaluation']['is_win_or_die_qualified']}")
    print(f"Status:                  {result['win_or_die_evaluation']['status']}")
    print(f"Conviction Score:        {result['win_or_die_evaluation']['conviction_score']}")