from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np
import pandas as pd


@dataclass
class MatchupRiskProfile:
    is_fraudulent_favorite: bool
    favorite_xg_waste_ratio: float
    is_underdog_gk_hot: bool
    gk_goals_prevented_p90: float
    is_bogeyman_h2h: bool
    h2h_ppg_delta: float
    upset_flag: bool


class StatisticalMatchFilter:
    """Engine for filtering football matches using advanced metrics:

    1. xG Efficiency vs Packed Defenses (Fraudulent Favorite Detection)
    2. PSxG Goalkeeper Hot-Hand (Bus-Parking Viability)
    3. H2H Historical Volatility (Bogeyman Dynamic)
    """

    def __init__(
        self,
        xg_waste_threshold: float = 0.25,  # Wasteful if missing >=25% of xG vs low blocks
        psxg_prevented_p90_threshold: float = 0.35,  # Saving +0.35 goals/90 above xG
        bogeyman_ppg_delta_threshold: float = 0.40,  # Underdog earns +0.40 PPG over baseline
    ):
        self.xg_waste_threshold = xg_waste_threshold
        self.psxg_prevented_p90_threshold = psxg_prevented_p90_threshold
        self.bogeyman_ppg_delta_threshold = bogeyman_ppg_delta_threshold

    def filter_fraudulent_favorite(
        self,
        favorite_recent_matches: pd.DataFrame,
        packed_defense_only: bool = True,
    ) -> Dict[str, float]:
        """Identifies heavy favorites that generate high xG but struggle to score

        against low-block / deep-defensive-line opponents.
        """
        df = favorite_recent_matches.copy()

        # Isolate matches against low blocks (PPDA > 15 or defensive depth < 40m)
        if packed_defense_only and "opp_ppda" in df.columns:
            df = df[df["opp_ppda"] >= 15.0]

        if df.empty:
            return {"xg_waste_ratio": 0.0, "is_fraud": False}

        total_xg = df["xg"].sum()
        total_goals = df["goals_scored"].sum()

        # Underperformance metric: Max(0, xG - Actual Goals) / xG
        xg_deficit = max(0.0, total_xg - total_goals)
        waste_ratio = xg_deficit / total_xg if total_xg > 0 else 0.0

        # Must have sustained high volume (>= 1.4 xG/game) to be classified as a "fraud"
        is_fraud = (waste_ratio >= self.xg_waste_threshold) and (
            total_xg / len(df) >= 1.4
        )

        return {
            "total_xg": round(total_xg, 2),
            "actual_goals": int(total_goals),
            "xg_waste_ratio": round(waste_ratio, 3),
            "is_fraud": is_fraud,
        }

    def filter_goalkeeper_hot_period(
        self, goalkeeper_recent_matches: pd.DataFrame, rolling_games: int = 5
    ) -> Dict[str, float]:
        """Uses Post-Shot Expected Goals (PSxG) vs actual goals conceded to check

        if the underdog's goalkeeper is in a high-performing hot streak.
        """
        recent = goalkeeper_recent_matches.tail(rolling_games)
        if recent.empty:
            return {"goals_prevented_p90": 0.0, "is_hot": False}

        # Goals Prevented = PSxG - Non-Own-Goal Conceded
        total_psxg = recent["psxg"].sum()
        actual_conceded = recent["goals_conceded"].sum()

        goals_prevented = total_psxg - actual_conceded
        prevented_p90 = goals_prevented / (len(recent) * (90 / 90))

        is_hot = prevented_p90 >= self.psxg_prevented_p90_threshold

        return {
            "psxg_sum": round(total_psxg, 2),
            "goals_conceded_sum": int(actual_conceded),
            "goals_prevented_p90": round(prevented_p90, 3),
            "is_hot": is_hot,
        }

    def filter_h2h_bogeyman_status(
        self,
        h2h_matches: pd.DataFrame,
        underdog_team_id: str,
        underdog_baseline_ppg_vs_top_tier: float,
    ) -> Dict[str, float]:
        """Measures if the underdog consistently outperforms its baseline points

        per game (PPG) expectation specifically against this favorite.
        """
        if h2h_matches.empty:
            return {"h2h_ppg": 0.0, "ppg_delta": 0.0, "is_bogeyman": False}

        points = []
        for _, match in h2h_matches.iterrows():
            if match["winner_id"] == underdog_team_id:
                points.append(3)
            elif match["is_draw"]:
                points.append(1)
            else:
                points.append(0)

        h2h_ppg = float(np.mean(points)) if points else 0.0
        ppg_delta = h2h_ppg - underdog_baseline_ppg_vs_top_tier

        is_bogeyman = ppg_delta >= self.bogeyman_ppg_delta_threshold

        return {
            "h2h_ppg": round(h2h_ppg, 2),
            "baseline_ppg": round(underdog_baseline_ppg_vs_top_tier, 2),
            "ppg_delta": round(ppg_delta, 2),
            "is_bogeyman": is_bogeyman,
        }

    def Evaluate_matchup(
        self,
        favorite_df: pd.DataFrame,
        underdog_gk_df: pd.DataFrame,
        h2h_df: pd.DataFrame,
        underdog_id: str,
        underdog_baseline_ppg: float,
    ) -> MatchupRiskProfile:
        """Combines all three statistical checks into an aggregate assessment."""
        fraud_res = self.filter_fraudulent_favorite(favorite_df)
        gk_res = self.filter_goalkeeper_hot_period(underdog_gk_df)
        h2h_res = self.filter_h2h_bogeyman_status(
            h2h_df, underdog_id, underdog_baseline_ppg
        )

        # Core Upset Logic: Wasteful favorite faces EITHER a hot GK or a historical bogeyman
        upset_flag = fraud_res["is_fraud"] and (
            gk_res["is_hot"] or h2h_res["is_bogeyman"]
        )

        return MatchupRiskProfile(
            is_fraudulent_favorite=fraud_res["is_fraud"],
            favorite_xg_waste_ratio=fraud_res["xg_waste_ratio"],
            is_underdog_gk_hot=gk_res["is_hot"],
            gk_goals_prevented_p90=gk_res["goals_prevented_p90"],
            is_bogeyman_h2h=h2h_res["is_bogeyman"],
            h2h_ppg_delta=h2h_res["ppg_delta"],
            upset_flag=upset_flag,
        )


# --- Example Execution ---
if __name__ == "__main__":
    # Sample mock data: Favorite generates 10.2 xG but scores only 5 goals against deep blocks
    fav_data = pd.DataFrame(
        {
            "xg": [2.1, 1.8, 2.4, 1.9, 2.0],
            "goals_scored": [1, 0, 2, 1, 1],
            "opp_ppda": [16.5, 18.2, 14.0, 17.1, 15.8],
        }
    )

    # Sample mock data: Underdog GK faced 7.8 PSxG over 5 matches, conceded only 4 goals
    gk_data = pd.DataFrame({"psxg": [1.8, 1.2, 2.1, 1.5, 1.2], "goals_conceded": [1, 0, 1, 1, 1]})

    # Sample H2H mock data: Underdog has won 1 and drawn 2 of last 4 meetings
    h2h_data = pd.DataFrame(
        [
            {"winner_id": "UNDERDOG", "is_draw": False},
            {"winner_id": "FAVORITE", "is_draw": False},
            {"winner_id": None, "is_draw": True},
            {"winner_id": None, "is_draw": True},
        ]
    )

    filter_engine = StatisticalMatchFilter()
    profile = filter_engine.Evaluate_matchup(
        favorite_df=fav_data,
        underdog_gk_df=gk_data,
        h2h_df=h2h_data,
        underdog_id="UNDERDOG",
        underdog_baseline_ppg=0.65,  # Underdog usually averages 0.65 PPG vs top 6
    )

    print("--- MATCHUP EVALUATION ---")
    print(f"Fraudulent Favorite: {profile.is_fraudulent_favorite} (Waste Ratio: {profile.favorite_xg_waste_ratio})")
    print(f"Hot Goalkeeper: {profile.is_underdog_gk_hot} (+{profile.gk_goals_prevented_p90} G/90 Saved)")
    print(f"Bogeyman Dynamic: {profile.is_bogeyman_h2h} (+{profile.h2h_ppg_delta} PPG boost)")
    print(f"High-Risk Upset Flag: {profile.upset_flag}")
    from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


class OddsFormat(Enum):
    DECIMAL = "decimal"  # e.g., 2.10
    PROBABILITY_CENTS = "cents"  # e.g., 0.48 ($0.48 on Polymarket/Kalshi)


@dataclass
class MarketQuote:
    selection_id: str  # e.g., "1X", "HOME", "AH_-0.5"
    bid_price: float  # Best buy price (cents or decimal odds)
    ask_price: float  # Best sell price / limit price to hit
    available_liquidity_usd: float  # Orderbook depth at best ask
    odds_format: OddsFormat = OddsFormat.PROBABILITY_CENTS


@dataclass
class ValueOpportunity:
    selection_id: str
    ai_probability: float
    market_implied_prob: float
    value_gap: float  # AI Prob - Implied Market Prob
    ev_percentage: float  # Expected Return on Investment (%)
    adjusted_kelly_stake_usd: float  # Liquidity & Risk-capped stake
    is_tradable: bool
    rejection_reason: Optional[str] = None


class MarketAlignmentEngine:
    """Quantitative engine for identifying value gaps, double chance (1X/X2) synthesis,

    handicap alignment, and liquidity-adjusted execution across prediction markets/sportsbooks.
    """

    def __init__(
        self,
        bankroll_usd: float = 10000.0,
        fractional_kelly: float = 0.25,  # Quarter-Kelly for risk management
        min_ev_threshold: float = 0.03,  # Minimum +3% EV
        min_liquidity_usd: float = 200.0,  # Minimum market depth
        max_spread_pct: float = 0.05,  # Max 5% bid-ask spread friction
    ):
        self.bankroll_usd = bankroll_usd
        self.fractional_kelly = fractional_kelly
        self.min_ev_threshold = min_ev_threshold
        self.min_liquidity_usd = min_liquidity_usd
        self.max_spread_pct = max_spread_pct

    @staticmethod
    def _normalize_to_implied_prob(price: float, fmt: OddsFormat) -> float:
        """Converts decimal odds or prediction market probability cents to true implied prob."""
        if fmt == OddsFormat.DECIMAL:
            return 1.0 / price if price > 1.0 else 0.0
        return max(0.001, min(0.999, price))  # Prediction market cents (0.00 - 1.00)

    @staticmethod
    def remove_vig_proportional(
        home_implied: float, draw_implied: float, away_implied: float
    ) -> Tuple[float, float, float]:
        """Removes bookmaker overround/vig using proportional normalization."""
        overround = home_implied + draw_implied + away_implied
        if overround <= 0:
            return 0.333, 0.333, 0.333
        return (
            home_implied / overround,
            draw_implied / overround,
            away_implied / overround,
        )

    def derive_double_chance_probs(
        self, p_home: float, p_draw: float, p_away: float
    ) -> Dict[str, float]:
        """Synthesizes Double Chance (1X, 12, X2) AI probabilities from 1X2 base model."""
        return {
            "1X": max(0.0, min(1.0, p_home + p_draw)),
            "X2": max(0.0, min(1.0, p_draw + p_away)),
            "12": max(0.0, min(1.0, p_home + p_away)),
        }

    def evaluate_market_quote(
        self,
        quote: MarketQuote,
        ai_prob: float,
    ) -> ValueOpportunity:
        """Calculates value gap, EV, and liquidity-adjusted stake against market limit prices."""

        # 1. Market Mechanics & Friction Checks
        market_implied_prob = self._normalize_to_implied_prob(
            quote.ask_price, quote.odds_format
        )
        bid_implied = self._normalize_to_implied_prob(
            quote.bid_price, quote.odds_format
        )

        # Spread check (Bid-Ask Friction Gap)
        spread = abs(market_implied_prob - bid_implied)
        if spread > self.max_spread_pct:
            return ValueOpportunity(
                selection_id=quote.selection_id,
                ai_probability=ai_prob,
                market_implied_prob=market_implied_prob,
                value_gap=ai_prob - market_implied_prob,
                ev_percentage=0.0,
                adjusted_kelly_stake_usd=0.0,
                is_tradable=False,
                rejection_reason=f"Spread too wide ({round(spread*100, 2)}%)",
            )

        # Liquidity Check
        if quote.available_liquidity_usd < self.min_liquidity_usd:
            return ValueOpportunity(
                selection_id=quote.selection_id,
                ai_probability=ai_prob,
                market_implied_prob=market_implied_prob,
                value_gap=ai_prob - market_implied_prob,
                ev_percentage=0.0,
                adjusted_kelly_stake_usd=0.0,
                is_tradable=False,
                rejection_reason=f"Insufficient liquidity (${quote.available_liquidity_usd})",
            )

        # 2. Value Gap & Expected Value (EV) Calculation
        value_gap = ai_prob - market_implied_prob

        if quote.odds_format == OddsFormat.DECIMAL:
            decimal_odds = quote.ask_price
        else:
            decimal_odds = (
                1.0 / quote.ask_price if quote.ask_price > 0 else 1.0
            )

        # EV = (Probability of Win * Net Payout) - (Probability of Loss * Stake)
        b = decimal_odds - 1.0
        ev_percentage = (ai_prob * b) - (1.0 - ai_prob)

        if ev_percentage < self.min_ev_threshold:
            return ValueOpportunity(
                selection_id=quote.selection_id,
                ai_probability=ai_prob,
                market_implied_prob=market_implied_prob,
                value_gap=round(value_gap, 4),
                ev_percentage=round(ev_percentage, 4),
                adjusted_kelly_stake_usd=0.0,
                is_tradable=False,
                rejection_reason=f"EV below threshold ({round(ev_percentage*100, 2)}%)",
            )

        # 3. Kelly Stake Sizing & Market Depth Capping
        # Full Kelly = (bp - q) / b
        p = ai_prob
        q = 1.0 - p
        full_kelly = (b * p - q) / b if b > 0 else 0.0

        raw_stake_usd = (
            self.bankroll_usd * max(0.0, full_kelly) * self.fractional_kelly
        )

        # Cap stake to 10% of total available market orderbook liquidity (Slippage Guard)
        liquidity_capped_stake = min(
            raw_stake_usd, quote.available_liquidity_usd * 0.10
        )

        return ValueOpportunity(
            selection_id=quote.selection_id,
            ai_probability=round(ai_prob, 4),
            market_implied_prob=round(market_implied_prob, 4),
            value_gap=round(value_gap, 4),
            ev_percentage=round(ev_percentage, 4),
            adjusted_kelly_stake_usd=round(liquidity_capped_stake, 2),
            is_tradable=True,
        )

    def Scan_and_align_match(
        self,
        ai_1x2_probs: Dict[str, float],  # {'HOME': 0.52, 'DRAW': 0.28, 'AWAY': 0.20}
        market_quotes: List[MarketQuote],
    ) -> pd.DataFrame:
        """Scans primary and derivative markets (1X2, Double Chance 1X/X2) to flag tradeable quant gaps."""
        results = []

        # Derive 1X/X2 synthetic probabilities
        dc_probs = self.derive_double_chance_probs(
            ai_1x2_probs.get("HOME", 0.0),
            ai_1x2_probs.get("DRAW", 0.0),
            ai_1x2_probs.get("AWAY", 0.0),
        )

        # Combine all AI model probabilities
        all_ai_probs = {**ai_1x2_probs, **dc_probs}

        for quote in market_quotes:
            if quote.selection_id in all_ai_probs:
                ai_prob = all_ai_probs[quote.selection_id]
                opp = self.evaluate_market_quote(quote, ai_prob)
                results.append(opp.__dict__)

        return pd.DataFrame(results)


# --- Example Execution ---
if __name__ == "__main__":
    # AI Engine Probabilities
    ai_probs = {"HOME": 0.54, "DRAW": 0.26, "AWAY": 0.20}

    # Market Quotes from Polymarket / Bookmaker Limit Orders
    quotes = [
        # Polymarket 1X Limit Price (0.72 = 72 cents limit price)
        MarketQuote(
            selection_id="1X",
            bid_price=0.70,
            ask_price=0.72,
            available_liquidity_usd=1500.0,
            odds_format=OddsFormat.PROBABILITY_CENTS,
        ),
        # Mispriced Away Win decimal odds on traditional sportsbook
        MarketQuote(
            selection_id="AWAY",
            bid_price=6.00,
            ask_price=6.20,
            available_liquidity_usd=800.0,
            odds_format=OddsFormat.DECIMAL,
        ),
        # Low liquidity market example
        MarketQuote(
            selection_id="HOME",
            bid_price=0.51,
            ask_price=0.53,
            available_liquidity_usd=50.0,
            odds_format=OddsFormat.PROBABILITY_CENTS,
        ),
    ]

    aligner = MarketAlignmentEngine(bankroll_usd=5000.0)
    opportunities_df = aligner.Scan_and_align_match(ai_probs, quotes)

    print("--- PREDICTION MARKET ALIGNMENT MATRIX ---")
    print(opportunities_df.to_string(index=False))
    from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


class MatchRole(Enum):
    UNDERDOG = "underdog"
    FAVORITE = "favorite"


@dataclass
class MatchProbabilities:
    p_favorite_win: float
    p_draw: float
    p_underdog_win: float

    @property
    def p_upset(self) -> float:
        """Combined probability of underdog securing points (Win or Draw)."""
        return self.p_underdog_win + self.p_draw


@dataclass
class BayesianAdjustmentResult:
    poisson_base_probs: MatchProbabilities
    adjusted_probs: MatchProbabilities
    top_tier_matches_evaluated: int
    successful_bus_parks: int
    prior_condition_met: bool
    applied_boost_factor: float


class BayesianBusParkAdjuster:
    """Bayesian Prior Adjuster for Poisson Distribution Models.

    Evaluates underdog resilience against top-tier opponents and applies a 15%
    boost to non-loss outcomes (Win/Draw) when low-block sustainability is
    proven.
    """

    def __init__(
        self,
        min_matches_required: int = 5,
        required_successes: int = 3,
        upset_boost_pct: float = 0.15,  # 15% increase over Poisson baseline
    ):
        self.min_matches_required = min_matches_required
        self.required_successes = required_successes
        self.upset_boost_pct = upset_boost_pct

    def evaluate_bus_park_prior(
        self,
        underdog_top_tier_history: pd.DataFrame,
    ) -> Tuple[bool, int, int]:
        """Evaluates whether the underdog successfully 'parked the bus' (secured W or D)

        in at least 3 of their last 5 matches against top-tier opponents.
        """
        # Take the most recent N matches against top-tier opposition
        recent_matches = underdog_top_tier_history.tail(
            self.min_matches_required
        )
        total_eval = len(recent_matches)

        if total_eval < self.min_matches_required:
            return False, total_eval, 0

        # Success condition: Result is either 'W' (Win) or 'D' (Draw)
        successes = recent_matches["result"].isin(["W", "D", "WIN", "DRAW"]).sum()
        condition_met = successes >= self.required_successes

        return condition_met, total_eval, int(successes)

    def adjust_probabilities(
        self,
        poisson_probs: MatchProbabilities,
        underdog_top_tier_history: pd.DataFrame,
    ) -> BayesianAdjustmentResult:
        """Applies Bayesian prior update to baseline Poisson match outcome probabilities."""
        condition_met, match_count, success_count = (
            self.evaluate_bus_park_prior(underdog_top_tier_history)
        )

        if not condition_met:
            # No adjustment if Bayesian prior threshold is not reached
            return BayesianAdjustmentResult(
                poisson_base_probs=poisson_probs,
                adjusted_probs=poisson_probs,
                top_tier_matches_evaluated=match_count,
                successful_bus_parks=success_count,
                prior_condition_met=False,
                applied_boost_factor=1.0,
            )

        # 1. Calculate raw boosted upset probabilities (Underdog Win + Draw boosted by 15%)
        boost_multiplier = 1.0 + self.upset_boost_pct

        raw_u_win = poisson_probs.p_underdog_win * boost_multiplier
        raw_draw = poisson_probs.p_draw * boost_multiplier
        raw_fav_win = poisson_probs.p_favorite_win

        # 2. Bayesian Normalization: Ensure sum of mutually exclusive outcomes equals 1.0
        total_mass = raw_fav_win + raw_draw + raw_u_win

        norm_fav_win = raw_fav_win / total_mass
        norm_draw = raw_draw / total_mass
        norm_u_win = raw_u_win / total_mass

        adjusted = MatchProbabilities(
            p_favorite_win=round(norm_fav_win, 4),
            p_draw=round(norm_draw, 4),
            p_underdog_win=round(norm_u_win, 4),
        )

        return BayesianAdjustmentResult(
            poisson_base_probs=poisson_probs,
            adjusted_probs=adjusted,
            top_tier_matches_evaluated=match_count,
            successful_bus_parks=success_count,
            prior_condition_met=True,
            applied_boost_factor=boost_multiplier,
        )


# --- Example Execution ---
if __name__ == "__main__":
    # Standard Poisson Baseline (e.g., Favorite 65%, Draw 22%, Underdog 13%)
    poisson_base = MatchProbabilities(
        p_favorite_win=0.65, p_draw=0.22, p_underdog_win=0.13
    )

    # Mock Data: Underdog's last 5 matches vs Top Tier Opponents (3 Draws/Wins = Bus Parked)
    underdog_history = pd.DataFrame(
        [
            {"opponent": "Arsenal", "goals_for": 1, "goals_against": 1, "result": "D"},
            {"opponent": "Man City", "goals_for": 0, "goals_against": 2, "result": "L"},
            {"opponent": "Liverpool", "goals_for": 1, "goals_against": 0, "result": "W"},
            {"opponent": "Chelsea", "goals_for": 0, "goals_against": 0, "result": "D"},
            {"opponent": "Real Madrid", "goals_for": 0, "goals_against": 3, "result": "L"},
        ]
    )

    adjuster = BayesianBusParkAdjuster(
        min_matches_required=5,
        required_successes=3,
        upset_boost_pct=0.15,
    )

    result = adjuster.adjust_probabilities(poisson_base, underdog_history)

    print("--- BAYESIAN POISSON ADJUSTMENT MATRIX ---")
    print(f"Base Poisson Probs  : Fav {poisson_base.p_favorite_win} | Draw {poisson_base.p_draw} | Underdog {poisson_base.p_underdog_win}")
    print(f"Top-Tier Bus Parks : {result.successful_bus_parks}/{result.top_tier_matches_evaluated} Matches (Condition Met: {result.prior_condition_met})")
    print(f"Adjusted Probs     : Fav {result.adjusted_probs.p_favorite_win} | Draw {result.adjusted_probs.p_draw} | Underdog {result.adjusted_probs.p_underdog_win}")
    print(f"Base Upset Prob    : {round(poisson_base.p_upset * 100, 2)}%")
    print(f"Adjusted Upset Prob: {round(result.adjusted_probs.p_upset * 100, 2)}%")