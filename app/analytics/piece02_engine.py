from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class GeopoliticalContext:
    is_conflict_zone: bool
    is_displaced_home_venue: bool
    disruption_notes: str


@dataclass
class MarketHypeContext:
    global_fame_level: str       # "GLOBAL_ELITE", "HIGH", "REGIONAL", "LOW"
    public_reputation_bias: bool # True if public blindly wagers on team name
    market_odds_inflated: bool  # True if market odds are artificially compressed due to hype


@dataclass
class TeamProfile:
    name: str
    geopolitical_status: GeopoliticalContext
    hype_status: MarketHypeContext
    scoring_probability: float
    is_must_win: bool = False


class ExtendedAnalyticalEngine:
    def __init__(self, team_a: TeamProfile, team_b: TeamProfile):
        self.team_a = team_a
        self.team_b = team_b

    def _analyze_conflict_impact(self, team: TeamProfile) -> Dict[str, Any]:
        """Rule 7: Evaluates war zone impact and venue displacement logistics."""
        geo = team.geopolitical_status
        
        if not geo.is_conflict_zone and not geo.is_displaced_home_venue:
            return {
                "impact_level": "NEUTRAL",
                "disruption_vector": 0.0,
                "analysis": "No active conflict disruption or venue displacement reported."
            }

        # Calculate performance friction index
        vector = -0.15 if geo.is_displaced_home_venue else -0.10
        if geo.is_conflict_zone:
            vector -= 0.20

        return {
            "impact_level": "HIGH_DISRUPTION",
            "disruption_vector": round(vector, 2),
            "neutral_venue_penalty": geo.is_displaced_home_venue,
            "analysis": f"Geopolitical impact active: {geo.disruption_notes}"
        }

    def _analyze_hype_trap(self, team: TeamProfile) -> Dict[str, Any]:
        """Rule 8: Evaluates brand-name overvaluation and public betting traps."""
        hype = team.hype_status
        
        is_public_trap = (
            hype.global_fame_level in ["GLOBAL_ELITE", "HIGH"] and
            hype.public_reputation_bias and
            hype.market_odds_inflated
        )

        if is_public_trap:
            return {
                "trap_risk": "HIGH_PUBLIC_TRAP",
                "value_rating": "OVERVALUED",
                "analysis": (
                    f"{team.name} carries heavy public reputation bias. Odds are artificially "
                    "compressed by causal market volume rather than true statistical probability."
                )
            }
        elif hype.public_reputation_bias:
            return {
                "trap_risk": "MODERATE_REPUTATION_BIAS",
                "value_rating": "FAIR_TO_SLIGHTLY_OVERVALUED",
                "analysis": f"{team.name} has notable popularity; monitor line movement for public inflation."
            }
        
        return {
            "trap_risk": "LOW",
            "value_rating": "MARKET_ALIGNED",
            "analysis": "Odds reflect true baseline statistical edge with minimal public name inflation."
        }

    def run_full_evaluation(self) -> Dict[str, Any]:
        """Executes full sweep across geopolitical and public market trap variables."""
        return {
            self.team_a.name: {
                "war_conflict_analysis": self._analyze_conflict_impact(self.team_a),
                "public_hype_analysis": self._analyze_hype_trap(self.team_a)
            },
            self.team_b.name: {
                "war_conflict_analysis": self._analyze_conflict_impact(self.team_b),
                "public_hype_analysis": self._analyze_hype_trap(self.team_b)
            }
        }

    def print_report(self) -> None:
        """Outputs structured text analysis across both teams."""
        results = self.run_full_evaluation()

        print("=" * 70)
        print(f"GEOPOLITICAL & MARKET HYPE ANALYSIS: {self.team_a.name} vs {self.team_b.name}")
        print("=" * 70)

        for team_name, data in results.items():
            war_info = data["war_conflict_analysis"]
            hype_info = data["public_hype_analysis"]

            print(f"\n--- {team_name.upper()} ---")
            print("7. GEOPOLITICAL / WAR ZONE ANALYSIS:")
            print(f"  • Disruption Impact : {war_info['impact_level']}")
            print(f"  • Performance Vector: {war_info.get('disruption_vector', 0.0):+.2f}")
            print(f"  • Analytical Detail : {war_info['analysis']}")

            print("\n8. PUBLIC HYPE / REPUTATION TRAP ANALYSIS:")
            print(f"  • Market Trap Risk  : {hype_info['trap_risk']}")
            print(f"  • Valuation Rating  : {hype_info['value_rating']}")
            print(f"  • Analytical Detail : {hype_info['analysis']}")

        print("\n" + "=" * 70)


# --- Execution Example ---
if __name__ == "__main__":
    # Team A: Affected by regional conflict, playing home matches at a neutral venue
    team_a = TeamProfile(
        name="Team A",
        scoring_probability=0.55,
        geopolitical_status=GeopoliticalContext(
            is_conflict_zone=True,
            is_displaced_home_venue=True,
            disruption_notes="Home matches moved to neutral country due to regional conflict; training disrupted."
        ),
        hype_status=MarketHypeContext(
            global_fame_level="REGIONAL",
            public_reputation_bias=False,
            market_odds_inflated=False
        )
    )

    # Team B: Global elite brand name causing severe public betting inflation
    team_b = TeamProfile(
        name="Team B",
        scoring_probability=0.48,
        geopolitical_status=GeopoliticalContext(
            is_conflict_zone=False,
            is_displaced_home_venue=False,
            disruption_notes="None"
        ),
        hype_status=MarketHypeContext(
            global_fame_level="GLOBAL_ELITE",
            public_reputation_bias=True,
            market_odds_inflated=True
        )
    )

    engine = ExtendedAnalyticalEngine(team_a, team_b)
    engine.print_report()
    from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any


class GenderCategory(Enum):
    MENS = "MENS"
    WOMENS = "WOMENS"
    YOUTH = "YOUTH"


@dataclass
class Team:
    name: str
    gender: GenderCategory  # Rule 10: Gender validation
    must_win_score: int     # Rule 9: Urgency scale from 1 (low) to 10 (critical)
    must_win_reason: str


class MatchUrgencyEngine:
    def __init__(self, team_a: Team, team_b: Team):
        self.team_a = team_a
        self.team_b = team_b
        self._validate_mens_teams()

    def _validate_mens_teams(self) -> None:
        """Rule 10: Ensures strict eligibility for Men's teams only."""
        if self.team_a.gender != GenderCategory.MENS or self.team_b.gender != GenderCategory.MENS:
            raise ValueError(
                f"GENDER VALIDATION ERROR: Both teams must be Men's teams. "
                f"Received: {self.team_a.name} ({self.team_a.gender.value}), "
                f"{self.team_b.name} ({self.team_b.gender.value})."
            )

    def evaluate_must_win(self) -> Dict[str, Any]:
        """Rule 9: Evaluates comparative motivation to identify which team must win."""
        score_a = self.team_a.must_win_score
        score_b = self.team_b.must_win_score

        if score_a > score_b:
            priority_team = self.team_a.name
            analysis = (
                f"{self.team_a.name} carries higher competitive urgency "
                f"({score_a}/10 vs {score_b}/10). Context: {self.team_a.must_win_reason}"
            )
        elif score_b > score_a:
            priority_team = self.team_b.name
            analysis = (
                f"{self.team_b.name} carries higher competitive urgency "
                f"({score_b}/10 vs {score_a}/10). Context: {self.team_b.must_win_reason}"
            )
        else:
            priority_team = "EQUAL URGENCY"
            analysis = f"Both teams share identical urgency levels ({score_a}/10)."

        return {
            "gender_verified": "MENS TEAMS CONFIRMED",
            "must_win_priority": priority_team,
            "team_a_urgency": f"{self.team_a.name}: {score_a}/10",
            "team_b_urgency": f"{self.team_b.name}: {score_b}/10",
            "analytical_detail": analysis
        }

    def print_analysis(self) -> None:
        """Outputs pure text analytical report."""
        res = self.evaluate_must_win()
        print("=" * 65)
        print(f"MATCH EVALUATION: {self.team_a.name} vs {self.team_b.name}")
        print("=" * 65)
        print(f"10. Gender Verification : {res['gender_verified']}")
        print(f" 9. Must-Win Priority   : {res['must_win_priority']}")
        print(f"    • {res['team_a_urgency']}")
        print(f"    • {res['team_b_urgency']}")
        print(f"    • Detail: {res['analytical_detail']}")
        print("=" * 65 + "\n")


# --- Testing Executable Example ---
if __name__ == "__main__":
    # Example 1: Valid Men's match evaluation
    team_a = Team(
        name="Team A (Men)",
        gender=GenderCategory.MENS,
        must_win_score=9,
        must_win_reason="Needs 3 points to avoid relegation."
    )

    team_b = Team(
        name="Team B (Men)",
        gender=GenderCategory.MENS,
        must_win_score=3,
        must_win_reason="Mid-table safety, no promotion/relegation pressure."
    )

    engine = MatchUrgencyEngine(team_a, team_b)
    engine.print_analysis()
    from dataclasses import dataclass
from typing import Dict, Any, Tuple


@dataclass
class TeamTierProfile:
    name: str
    squad_rating: float                # Objective rating/ELO/power index (higher = stronger)
    is_win_or_die_for_top: bool        # Rule 11: Must win to secure 1st place/top spot
    win_or_die_context: str            # e.g., "3 points required on final matchday to lift title"


class TierAndMotivationEngine:
    def __init__(self, team_a: TeamTierProfile, team_b: TeamTierProfile):
        self.team_a = team_a
        self.team_b = team_b

    def classify_tier_hierarchy(self) -> Dict[str, Any]:
        """
        Rule 12: Evaluates team ratings to dynamically categorize 
        the Top Tier favorite and the Underdog.
        """
        rating_a = self.team_a.squad_rating
        rating_b = self.team_b.squad_rating

        if rating_a > rating_b:
            top_tier = self.team_a
            underdog = self.team_b
        elif rating_b > rating_a:
            top_tier = self.team_b
            underdog = self.team_a
        else:
            return {
                "is_evenly_matched": True,
                "top_tier": "EQUALLY MATCHED",
                "underdog": "EQUALLY MATCHED",
                "rating_gap": 0.0,
                "analysis": "Both teams operate at the same quality/rating tier."
            }

        rating_gap = abs(rating_a - rating_b)
        return {
            "is_evenly_matched": False,
            "top_tier": top_tier.name,
            "underdog": underdog.name,
            "rating_gap": round(rating_gap, 2),
            "analysis": f"{top_tier.name} is classified as TOP TIER (Rating: {top_tier.squad_rating}), while {underdog.name} is the UNDERDOG (Rating: {underdog.squad_rating})."
        }

    def evaluate_win_or_die_status(self) -> Dict[str, Any]:
        """
        Rule 11: Audits whether a team is in an absolute 'Win or Die' scenario 
        specifically for emerging at the top.
        """
        a_status = self.team_a.is_win_or_die_for_top
        b_status = self.team_b.is_win_or_die_for_top

        if a_status and not b_status:
            critical_team = self.team_a.name
            context = self.team_a.win_or_die_context
            analysis = f"CRITICAL: {self.team_a.name} is in a mandatory 'Win or Die' scenario to take top spot. {self.team_b.name} does not face this pressure."
        elif b_status and not a_status:
            critical_team = self.team_b.name
            context = self.team_b.win_or_die_context
            analysis = f"CRITICAL: {self.team_b.name} is in a mandatory 'Win or Die' scenario to take top spot. {self.team_a.name} does not face this pressure."
        elif a_status and b_status:
            critical_team = "BOTH TEAMS"
            context = f"{self.team_a.name}: {self.team_a.win_or_die_context} | {self.team_b.name}: {self.team_b.win_or_die_context}"
            analysis = "DIRECT HEAD-TO-HEAD: Both teams face a mutual 'Win or Die' scenario for top spot."
        else:
            critical_team = "NONE"
            context = "Neither team is facing a final-threshold 'Win or Die' situation for top position."
            analysis = "NO TOP-SPOT WIN-OR-DIE PRESSURE: Standard points fixture."

        return {
            "win_or_die_active": a_status or b_status,
            "critical_team": critical_team,
            "context_details": context,
            "analysis": analysis
        }

    def run_full_analysis(self) -> Dict[str, Any]:
        """Runs unified audit for Rules 11 and 12."""
        return {
            "tier_classification": self.classify_tier_hierarchy(),
            "win_or_die_audit": self.evaluate_win_or_die_status()
        }

    def print_analysis(self) -> None:
        """Outputs pure text analytical report."""
        audit = self.run_full_analysis()
        tier_data = audit["tier_classification"]
        wod_data = audit["win_or_die_audit"]

        print("=" * 65)
        print(f"MATCH EVALUATION: {self.team_a.name} vs {self.team_b.name}")
        print("=" * 65)

        print("\n11. WIN OR DIE FOR TOP SPOT EMERGENCY AUDIT")
        print(f"  • Win or Die Active : {wod_data['win_or_die_active']}")
        print(f"  • High-Pressure Team: {wod_data['critical_team']}")
        print(f"  • Match Context     : {wod_data['context_details']}")
        print(f"  • Analysis          : {wod_data['analysis']}")

        print("\n12. TOP TIER VS UNDERDOG HIERARCHY")
        print(f"  • Top Tier (Favorite): {tier_data['top_tier']}")
        print(f"  • Underdog           : {tier_data['underdog']}")
        if not tier_data.get("is_evenly_matched"):
            print(f"  • Quality Differential: +{tier_data['rating_gap']} rating edge")
        print(f"  • Hierarchy Analysis  : {tier_data['analysis']}")
        print("=" * 65 + "\n")


# --- Execution Example ---
if __name__ == "__main__":
    # Example Scenario:
    # Team A: Rating 88.5 (Top Tier), needs win on final matchday to win league title (Win or Die)
    team_a = TeamTierProfile(
        name="Team A",
        squad_rating=88.5,
        is_win_or_die_for_top=True,
        win_or_die_context="Trailing 1st place by 2 points on final matchday; 3 points mandatory for title."
    )

    # Team B: Rating 72.0 (Underdog), mid-table safety with no top-spot pressure
    team_b = TeamTierProfile(
        name="Team B",
        squad_rating=72.0,
        is_win_or_die_for_top=False,
        win_or_die_context="Mid-table position secured; no top-tier qualification at stake."
    )

    engine = TierAndMotivationEngine(team_a, team_b)
    engine.print_analysis()
    from typing import Dict, Any

def evaluate_match_tiers_and_outcomes(
    home_team: str,
    away_team: str,
    p_home: float,
    p_draw: float,
    p_away: float
) -> Dict[str, Any]:
    """
    Implements steps 12 and 13 for match evaluation.
    
    :param home_team: Home team name
    :param away_team: Away team name
    :param p_home: Win probability for home team (0.0 to 1.0 or raw probability)
    :param p_draw: Draw probability (0.0 to 1.0 or raw probability)
    :param p_away: Win probability for away team (0.0 to 1.0 or raw probability)
    :return: Formatted evaluation containing tiers, probabilities out of 100, 1X2 outcome, and safe rating.
    """
    # Normalize probabilities to sum to 100%
    total_p = p_home + p_draw + p_away
    pct_home = round((p_home / total_p) * 100, 2)
    pct_draw = round((p_draw / total_p) * 100, 2)
    pct_away = round((p_away / total_p) * 100, 2)

    # Step 12: Determine Top-Tier (Favorite) vs Underdog
    if pct_home > pct_away:
        toptier = f"{home_team} (Home)"
        underdog = f"{away_team} (Away)"
        prob_gap = pct_home - pct_away
    elif pct_away > pct_home:
        toptier = f"{away_team} (Away)"
        underdog = f"{home_team} (Home)"
        prob_gap = pct_away - pct_home
    else:
        toptier = "Even Match (No Clear Favorite)"
        underdog = "Even Match"
        prob_gap = 0.0

    # Step 13: Determine 1X2 Pick and Probabilities out of 100
    max_prob = max(pct_home, pct_draw, pct_away)
    
    if max_prob == pct_home:
        probable_1x2 = "1"
        pick_description = f"{home_team} Win (Home)"
    elif max_prob == pct_away:
        probable_1x2 = "2"
        pick_description = f"{away_team} Win (Away)"
    else:
        probable_1x2 = "X"
        pick_description = "Draw"

    # Step 13: Calculate Safe Rating (1.0 to 10.0 scale)
    # Factoring dominance, win margin gap, and draw exposure
    base_confidence = max_prob / 10.0
    gap_bonus = prob_gap / 20.0
    draw_risk_penalty = (pct_draw / 100.0) * 2.0

    if probable_1x2 == "X":
        # Draws carry inherently higher variance
        raw_safety = min(pct_draw / 10.0, 6.0)
    else:
        raw_safety = base_confidence + gap_bonus - draw_risk_penalty

    safe_rating = round(max(1.0, min(10.0, raw_safety)), 1)

    # Classify Safety Tier
    if safe_rating >= 7.5:
        safety_class = "High Safety (Strong Selection)"
    elif safe_rating >= 5.5:
        safety_class = "Moderate Safety (Controlled Risk)"
    else:
        safety_class = "Low Safety (Volatile / High Risk)"

    return {
        "step_12": {
            "top_tier": toptier,
            "underdog": underdog,
            "margin_gap_pct": round(prob_gap, 2)
        },
        "step_13": {
            "probabilities_out_of_100": {
                "1": pct_home,
                "X": pct_draw,
                "2": pct_away
            },
            "probable_outcome_1x2": probable_1x2,
            "pick_prediction": pick_description,
            "safe_rating": f"{safe_rating}/10",
            "safety_classification": safety_class
        }
    }


# Example Execution
if __name__ == "__main__":
    # Test match: Calculated model probabilities (e.g., from Poisson or Market Devig)
    match_result = evaluate_match_tiers_and_outcomes(
        home_team="Arsenal",
        away_team="Fulham",
        p_home=0.68,
        p_draw=0.20,
        p_away=0.12
    )

    print("Step 12 Tier Breakdown:")
    print(f" Top-Tier (Favorite): {match_result['step_12']['top_tier']}")
    print(f" Underdog:           {match_result['step_12']['underdog']}")
    print("\nStep 13 Outcome Prediction:")
    print(f" Probabilities (%):  {match_result['step_13']['probabilities_out_of_100']}")
    print(f" Probable 1X2:       {match_result['step_13']['probable_outcome_1x2']} ({match_result['step_13']['pick_prediction']})")
    print(f" Safe Rating:        {match_result['step_13']['safe_rating']} [{match_result['step_13']['safety_classification']}]")