from typing import Dict, List, Any

class TacticalResearchEngine:
    """
    Step 18 Engine: Conducts deep tactical research on both competing teams.
    Extracts core strengths, structural weaknesses, and critical match dynamics 
    across offensive, defensive, set-piece, and transition metrics.
    """

    def __init__(self, high_threshold: float = 1.25, low_threshold: float = 0.75):
        """
        :param high_threshold: Metric multiplier benchmark for identifying a 'Strength' (> 125% of league avg)
        :param low_threshold: Metric multiplier benchmark for identifying a 'Weakness' (< 75% of league avg)
        """
        self.high_thresh = high_threshold
        self.low_thresh = low_threshold

    def _evaluate_team_metrics(self, team_name: str, metrics: Dict[str, float]) -> Dict[str, List[str]]:
        """
        Internal evaluator mapping raw metric ratios against league benchmarks 
        to isolate tactical attributes.
        """
        strengths = []
        weaknesses = []

        # 1. Offensive Threat & Conversion
        if metrics.get("open_play_xg_ratio", 1.0) >= self.high_thresh:
            strengths.append("High Open-Play xG Creation (Dominant Chance Generation)")
        elif metrics.get("open_play_xg_ratio", 1.0) <= self.low_thresh:
            weaknesses.append("Low Open-Play Penetration (Struggles vs Set Defensive Blocks)")

        if metrics.get("shot_conversion_rate_pct", 10.0) >= 15.0:
            strengths.append("Elite Clinical Finishing (High xG Overperformance)")
        elif metrics.get("shot_conversion_rate_pct", 10.0) <= 7.5:
            weaknesses.append("Wasteful in Front of Goal (Low Shot Conversion Rate)")

        # 2. Defensive Solidity & Transition Risk
        if metrics.get("defensive_duels_win_pct", 50.0) >= 60.0:
            strengths.append("Robust 1v1 Defensive Ground Dominance")
        elif metrics.get("defensive_duels_win_pct", 50.0) <= 42.0:
            weaknesses.append("Vulnerable in Individual 1v1 Defensive Ground Duels")

        if metrics.get("ppda", 10.0) <= 8.5:  # Passes Per Defensive Action (Lower = Higher Pressing)
            strengths.append("Aggressive High-Press System (Forces High Turnover Rates)")
        elif metrics.get("ppda", 10.0) >= 14.0:
            weaknesses.append("Passive Pressing Intensity (Allows Opponent Uncontested Build-up)")

        if metrics.get("counter_attack_goals_conceded_per_90", 0.3) >= 0.5:
            weaknesses.append("High Vulnerability to Rapid Counter-Attacks on Defensive Transitions")
        else:
            strengths.append("Effective Rest-Defense (Limits Transition Threats)")

        # 3. Set Pieces & Aerial Metrics
        if metrics.get("set_piece_xg_per_90", 0.25) >= 0.45:
            strengths.append("High Set-Piece Threat (Dangerous Free Kicks and Corners)")
        if metrics.get("aerial_duels_win_pct", 50.0) <= 44.0:
            weaknesses.append("Aerial Susceptibility (Weak Against Crosses and Long Balls)")

        # 4. Discipline & Fatigue Dynamics
        if metrics.get("late_goals_conceded_pct_75_90", 20.0) >= 35.0:
            weaknesses.append("Late-Game Concentration Drop (High Goal Concession in Min 75-90)")

        return {
            "strengths": strengths if strengths else ["Balanced / Baseline Performance"],
            "weaknesses": weaknesses if weaknesses else ["No Severe Structural Faults Isolated"]
        }

    def generate_tactical_research_report(
        self,
        home_team: str,
        home_metrics: Dict[str, float],
        away_team: str,
        away_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Step 18: Synthesizes strength/weakness evaluations and isolates 
        direct tactical head-to-head exploits.
        """
        home_eval = self._evaluate_team_metrics(home_team, home_metrics)
        away_eval = self._evaluate_team_metrics(away_team, away_metrics)

        # Tactical Exploits Engine (H2H Structural Clashes)
        tactical_exploits = []

        # Check Home High Press vs Away Build-Up
        if home_metrics.get("ppda", 10.0) <= 9.0 and away_metrics.get("defensive_duels_win_pct", 50.0) <= 45.0:
            tactical_exploits.append(
                f"EXPLOIT: {home_team}'s high press is positioned to exploit {away_team}'s weak build-up efficiency."
            )

        # Check Away Counter-Attack vs Home Transition Vulnerability
        if away_metrics.get("counter_attack_goals_conceded_per_90", 0.0) < 0.2 and home_metrics.get("counter_attack_goals_conceded_per_90", 0.0) >= 0.5:
            tactical_exploits.append(
                f"EXPLOIT: {away_team} can leverage fast transitions against {home_team}'s vulnerable rest-defense."
            )

        # Check Aerial Mismatch
        if home_metrics.get("set_piece_xg_per_90", 0.0) >= 0.4 and away_metrics.get("aerial_duels_win_pct", 50.0) <= 44.0:
            tactical_exploits.append(
                f"EXPLOIT: {home_team} holds a significant set-piece aerial mismatch over {away_team}."
            )

        return {
            "match": f"{home_team} vs {away_team}",
            "home_team_analysis": {
                "team": home_team,
                "strengths": home_eval["strengths"],
                "weaknesses": home_eval["weaknesses"]
            },
            "away_team_analysis": {
                "team": away_team,
                "strengths": away_eval["strengths"],
                "weaknesses": away_eval["weaknesses"]
            },
            "step_18_tactical_exploits": tactical_exploits if tactical_exploits else ["Standard Game Flow Expected (No Critical Mismatch)"]
        }


# Example Execution
if __name__ == "__main__":
    # Sample underlying metrics pulled from football API / data parser
    home_stats = {
        "open_play_xg_ratio": 1.35,
        "shot_conversion_rate_pct": 16.2,
        "defensive_duels_win_pct": 58.5,
        "ppda": 7.8,  # Aggressive press
        "counter_attack_goals_conceded_per_90": 0.52,  # Vulnerable on transition
        "set_piece_xg_per_90": 0.48,
        "aerial_duels_win_pct": 52.0,
        "late_goals_conceded_pct_75_90": 18.0
    }

    away_stats = {
        "open_play_xg_ratio": 0.68,
        "shot_conversion_rate_pct": 8.1,
        "defensive_duels_win_pct": 41.2,
        "ppda": 15.2,  # Low block / Passive
        "counter_attack_goals_conceded_per_90": 0.15,
        "set_piece_xg_per_90": 0.20,
        "aerial_duels_win_pct": 42.1,  # Poor aerial defense
        "late_goals_conceded_pct_75_90": 38.5  # Drops late in games
    }

    research_engine = TacticalResearchEngine()
    report = research_engine.generate_tactical_research_report(
        home_team="Arsenal",
        home_metrics=home_stats,
        away_team="Leicester City",
        away_metrics=away_stats
    )

    print("--- STEP 18: DEEP TACTICAL STRENGTHS & WEAKNESSES REPORT ---")
    print(f"\n[{report['home_team_analysis']['team']} Strengths]:")
    for s in report['home_team_analysis']['strengths']:
        print(f"  + {s}")
    print(f"\n[{report['home_team_analysis']['team']} Weaknesses]:")
    for w in report['home_team_analysis']['weaknesses']:
        print(f"  - {w}")

    print(f"\n[{report['away_team_analysis']['team']} Strengths]:")
    for s in report['away_team_analysis']['strengths']:
        print(f"  + {s}")
    print(f"\n[{report['away_team_analysis']['team']} Weaknesses]:")
    for w in report['away_team_analysis']['weaknesses']:
        print(f"  - {w}")

    print("\n[Direct H2H Tactical Exploits]:")
    for exploit in report['step_18_tactical_exploits']:
        print(f"  * {exploit}")
        from typing import List, Dict, Any, Optional

class RankingEngine:
    """
    Step 19 Engine: Processes and parses league table standings or FIFA world rankings.
    Extracts positional standings, calculates table gaps between competing teams,
    and categorizes league performance zones (e.g., Title Race, European Spots, Relegation).
    """

    def __init__(self):
        pass

    @staticmethod
    def _classify_league_zone(position: int, total_teams: int) -> str:
        """Classifies a team's position into domestic competition zones."""
        if position <= 4:
            return "UEFA Champions League Zone / Title Contender"
        elif position in [5, 6]:
            return "UEFA Europa League / Conference League Zone"
        elif position > (total_teams - 3):
            return "Relegation Danger Zone"
        elif position <= (total_teams // 2):
            return "Upper Mid-Table"
        else:
            return "Lower Mid-Table"

    @staticmethod
    def _classify_fifa_tier(position: int) -> str:
        """Classifies national teams by FIFA World Ranking tiers."""
        if position <= 10:
            return "Tier 1: Global Elite (Top 10)"
        elif position <= 30:
            return "Tier 2: Upper International Tier (Top 30)"
        elif position <= 70:
            return "Tier 3: Competitive Mid-Tier (Top 70)"
        else:
            return "Tier 4: Developing National Federation"

    def process_rankings(
        self,
        competition_name: str,
        standings_data: List[Dict[str, Any]],
        home_team: str,
        away_team: str,
        ranking_type: str = "LEAGUE"  # Options: "LEAGUE" or "FIFA"
    ) -> Dict[str, Any]:
        """
        Step 19: Formats competition standings and isolates competing team ranks.
        
        :param competition_name: e.g., 'English Premier League' or 'FIFA World Rankings'
        :param standings_data: List of team dicts ordered by position
        :param home_team: Name of Home team
        :param away_team: Name of Away team
        :param ranking_type: 'LEAGUE' or 'FIFA'
        :return: Comprehensive structured ranking report
        """
        total_teams = len(standings_data)
        formatted_table = []
        home_info = None
        away_info = None

        for entry in standings_data:
            pos = entry.get("position")
            team = entry.get("team")
            
            if ranking_type.upper() == "FIFA":
                pts = entry.get("points", 0.0)
                confed = entry.get("confederation", "N/A")
                zone = self._classify_fifa_tier(pos)
                row_str = f"Rank {pos:03d} | {team:<22} | Points: {pts:<7.2f} | Confed: {confed}"
            else:
                p = entry.get("played", 0)
                w = entry.get("won", 0)
                d = entry.get("drawn", 0)
                l = entry.get("lost", 0)
                gd = entry.get("gd", 0)
                pts = entry.get("points", 0)
                zone = self._classify_league_zone(pos, total_teams)
                row_str = f"#{pos:02d} {team:<20} | P: {p:<2} | W-D-L: {w}-{d}-{l} | GD: {gd:<+3} | Pts: {pts}"

            record = {
                "position": pos,
                "team": team,
                "zone_classification": zone,
                "display_row": row_str,
                "raw": entry
            }
            formatted_table.append(record)

            # Match lookup (supports partial string matching)
            if team.lower() in home_team.lower() or home_team.lower() in team.lower():
                home_info = record
            if team.lower() in away_team.lower() or away_team.lower() in team.lower():
                away_info = record

        # Calculate Positional Gap & Market Superiority
        home_pos = home_info["position"] if home_info else None
        away_pos = away_info["position"] if away_info else None

        if home_pos and away_pos:
            table_gap = abs(home_pos - away_pos)
            higher_ranked = home_team if home_pos < away_pos else away_team
        else:
            table_gap = None
            higher_ranked = None

        return {
            "competition": competition_name,
            "type": ranking_type.upper(),
            "total_teams_in_table": total_teams,
            "competing_matchup_analysis": {
                "home_team": {
                    "name": home_team,
                    "position": home_pos if home_pos else "Not Found",
                    "zone": home_info["zone_classification"] if home_info else "N/A",
                    "details": home_info["raw"] if home_info else {}
                },
                "away_team": {
                    "name": away_team,
                    "position": away_pos if away_pos else "Not Found",
                    "zone": away_info["zone_classification"] if away_info else "N/A",
                    "details": away_info["raw"] if away_info else {}
                },
                "table_position_gap": table_gap,
                "higher_ranked_team": higher_ranked
            },
            "standings_table": formatted_table
        }


# Example Execution
if __name__ == "__main__":
    ranking_engine = RankingEngine()

    # Scenario A: Domestic League Table (Premier League mock dataset)
    league_standings_data = [
        {"position": 1, "team": "Liverpool", "played": 26, "won": 18, "drawn": 6, "lost": 2, "gd": 34, "points": 60},
        {"position": 2, "team": "Arsenal", "played": 26, "won": 17, "drawn": 6, "lost": 3, "gd": 31, "points": 57},
        {"position": 3, "team": "Manchester City", "played": 26, "won": 16, "drawn": 6, "lost": 4, "gd": 28, "points": 54},
        {"position": 4, "team": "Aston Villa", "played": 26, "won": 15, "drawn": 4, "lost": 7, "gd": 16, "points": 49},
        {"position": 5, "team": "Tottenham Hotspur", "played": 26, "won": 14, "drawn": 5, "lost": 7, "gd": 14, "points": 47},
        {"position": 6, "team": "Manchester United", "played": 26, "won": 14, "drawn": 2, "lost": 10, "gd": 1, "points": 44},
        {"position": 7, "team": "Brighton", "played": 26, "won": 10, "drawn": 9, "lost": 7, "gd": 8, "points": 39},
        {"position": 8, "team": "West Ham", "played": 26, "won": 10, "drawn": 6, "lost": 10, "gd": -4, "points": 36},
        {"position": 9, "team": "Chelsea", "played": 26, "won": 10, "drawn": 5, "lost": 11, "gd": 1, "points": 35},
        {"position": 10, "team": "Newcastle United", "played": 26, "won": 10, "drawn": 3, "lost": 13, "gd": 3, "points": 33},
        {"position": 11, "team": "Wolves", "played": 26, "won": 10, "drawn": 5, "lost": 11, "gd": -1, "points": 35},
        {"position": 12, "team": "Bournemouth", "played": 26, "won": 8, "drawn": 7, "lost": 11, "gd": -9, "points": 31},
        {"position": 13, "team": "Fulham", "played": 26, "won": 8, "drawn": 5, "lost": 13, "gd": -11, "points": 29},
        {"position": 14, "team": "Crystal Palace", "played": 26, "won": 7, "drawn": 7, "lost": 12, "gd": -13, "points": 28},
        {"position": 15, "team": "Brentford", "played": 26, "won": 7, "drawn": 4, "lost": 15, "gd": -11, "points": 25},
        {"position": 16, "team": "Everton", "played": 26, "won": 8, "drawn": 5, "lost": 13, "gd": -10, "points": 23},
        {"position": 17, "team": "Nottingham Forest", "played": 26, "won": 6, "drawn": 6, "lost": 14, "gd": -14, "points": 24},
        {"position": 18, "team": "Luton Town", "played": 26, "won": 5, "drawn": 5, "lost": 16, "gd": -18, "points": 20},
        {"position": 19, "team": "Burnley", "played": 26, "won": 3, "drawn": 4, "lost": 19, "gd": -33, "points": 13},
        {"position": 20, "team": "Sheffield United", "played": 26, "won": 3, "drawn": 4, "lost": 19, "gd": -44, "points": 13}
    ]

    report = ranking_engine.process_rankings(
        competition_name="Premier League 2025/26",
        standings_data=league_standings_data,
        home_team="Arsenal",
        away_team="Bournemouth",
        ranking_type="LEAGUE"
    )

    print("--- STEP 19: UPDATED STANDINGS & RANKINGS ANALYSIS ---")
    print(f"Competition: {report['competition']}")
    print(f"Home ({report['competing_matchup_analysis']['home_team']['name']}): Rank #{report['competing_matchup_analysis']['home_team']['position']} [{report['competing_matchup_analysis']['home_team']['zone']}]")
    print(f"Away ({report['competing_matchup_analysis']['away_team']['name']}): Rank #{report['competing_matchup_analysis']['away_team']['position']} [{report['competing_matchup_analysis']['away_team']['zone']}]")
    print(f"Table Gap: {report['competing_matchup_analysis']['table_position_gap']} positions advantage to {report['competing_matchup_analysis']['higher_ranked_team']}\n")

    print("--- FULL STANDINGS TABLE ---")
    for row in report['standings_table']:
        highlight = " <-- MATCHUP" if row['team'] in ["Arsenal", "Bournemouth"] else ""
        print(f"{row['display_row']}{highlight}")
        import re
from typing import Dict, Any, List

class SeniorMenMatchFilter:
    """
    Step 20 Engine: Validates match eligibility to ensure fixtures are strictly 
    Senior Men's competitive matches, filtering out Youth/Age-restricted teams 
    (e.g., U19, U21, U23, Reserves) and Women's teams.
    """

    def __init__(self):
        # Youth and Age-Restricted patterns (case-insensitive)
        self.youth_patterns = [
            r'\bu-?1[4-9]\b',     # U14 through U19
            r'\bu-?2[0-3]\b',     # U20 through U23
            r'\bunder\s*1[4-9]\b',# Under 14 through Under 19
            r'\bunder\s*2[0-3]\b',# Under 20 through Under 23
            r'\bsub-?1[7-9]\b',   # Sub-17, Sub-19 (South American naming)
            r'\bsub-?2[0-3]\b',   # Sub-20, Sub-23
            r'\byouth\b',
            r'\breserves?\b',
            r'\bacademy\b',
            r'\bjuniors?\b',
            r'\bii\b',            # Reserve "II" teams (e.g., Dortmund II)
            r'\bb\b'              # B-teams where applicable (e.g., Barca B)
        ]

        # Women's football patterns (case-insensitive)
        self.women_patterns = [
            r'\bwomen\b',
            r'\bwomen\'s\b',
            r'\bladies\b',
            r'\bwfc\b',
            r'\bfeminine\b',
            r'\bfeminil\b',
            r'\bfeminino\b',
            r'\bfrauen\b',
            r'\bkvinner\b',
            r'\bdamer\b',
            r'\(w\)',
            r'\bw\b'
        ]

    def _check_string(self, text: str, patterns: List[str]) -> bool:
        """Helper to match regex patterns against string."""
        combined_pattern = "|".join(patterns)
        return bool(re.search(combined_pattern, text, re.IGNORECASE))

    def validate_match_eligibility(
        self,
        home_team: str,
        away_team: str,
        league_name: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluates home team, away team, and league names against exclusion rules.
        
        :param home_team: Name of Home team
        :param away_team: Name of Away team
        :param league_name: Optional competition or league title
        :return: Eligibility status and detailed flags
        """
        reasons = []

        # 1. Check Youth / Age-Restricted Filters
        is_home_youth = self._check_string(home_team, self.youth_patterns)
        is_away_youth = self._check_string(away_team, self.youth_patterns)
        is_league_youth = self._check_string(league_name, self.youth_patterns)

        if is_home_youth:
            reasons.append(f"Home team '{home_team}' identified as Youth/Under-age team.")
        if is_away_youth:
            reasons.append(f"Away team '{away_team}' identified as Youth/Under-age team.")
        if is_league_youth:
            reasons.append(f"League '{league_name}' identified as Youth/Under-age competition.")

        # 2. Check Women's Football Filters
        is_home_women = self._check_string(home_team, self.women_patterns)
        is_away_women = self._check_string(away_team, self.women_patterns)
        is_league_women = self._check_string(league_name, self.women_patterns)

        if is_home_women:
            reasons.append(f"Home team '{home_team}' identified as Women's team.")
        if is_away_women:
            reasons.append(f"Away team '{away_team}' identified as Women's team.")
        if is_league_women:
            reasons.append(f"League '{league_name}' identified as Women's competition.")

        # 3. Final Eligibility Determination
        is_eligible = len(reasons) == 0

        return {
            "match": f"{home_team} vs {away_team}",
            "league": league_name if league_name else "Unspecified",
            "step_20_eligible": is_eligible,
            "category": "Senior Men's Professional" if is_eligible else "REJECTED",
            "rejection_reasons": reasons if not is_eligible else ["None (Passed All Senior Men Filters)"]
        }


# Example Execution
if __name__ == "__main__":
    filter_engine = SeniorMenMatchFilter()

    # Test Fixtures
    test_matches = [
        {"home": "Arsenal", "away": "Chelsea", "league": "Premier League"},
        {"home": "Liverpool U21", "away": "Everton U21", "league": "Premier League 2"},
        {"home": "Barcelona W", "away": "Real Madrid Femenino", "league": "Liga F"},
        {"home": "Bayern Munich II", "away": "Unterhaching", "league": "3. Liga"},
        {"home": "France U19", "away": "Spain U19", "league": "UEFA European U19 Championship"}
    ]

    print("--- STEP 20: SENIOR MEN'S MATCH ELIGIBILITY FILTER ---")
    for match in test_matches:
        result = filter_engine.validate_match_eligibility(
            home_team=match["home"],
            away_team=match["away"],
            league_name=match["league"]
        )
        status_icon = "🟢 APPROVED" if result["step_20_eligible"] else "🔴 REJECTED"
        print(f"\nMatch: {result['match']} ({result['league']})")
        print(f"Status: {status_icon} | Category: {result['category']}")
        if not result["step_20_eligible"]:
            for r in result["rejection_reasons"]:
                print(f"  - Reason: {r}")
                import re
from typing import Dict, Any, List, Optional

class CompetitiveFirstXIFilter:
    """
    Step 21 & Step 22 Engine:
    Step 21: Filters out non-competitive fixtures (Friendlies, Pre-season, Exhibitions).
    Step 22: Ensures teams are strictly Primary Senior First XI squads, excluding 
            reserve/side/B-teams and validating starting lineup integrity.
    """

    def __init__(self):
        # Step 21: Non-Competitive / Friendly Indicators
        self.friendly_patterns = [
            r'\bfriendly\b',
            r'\bfriendlies\b',
            r'\bclub\s*friendly\b',
            r'\bint\.\s*friendly\b',
            r'\binternational\s*friendly\b',
            r'\bpre-?season\b',
            r'\bexhibition\b',
            r'\bcharity\s*match\b',
            r'\bshowcase\b',
            r'\btest\s*match\b',
            r'\bcupa\s*de\s*vara\b',  # Summer friendly cups
            r'\bflorida\s*cup\b',
            r'\baudi\s*cup\b'
        ]

        # Step 22: Reserve / Side / Secondary Squad Indicators
        self.secondary_squad_patterns = [
            r'\breserves?\b',
            r'\bres\.?\b',
            r'\bii\b',            # e.g. Bayern II
            r'\biii\b',           # e.g. Breidablik III
            r'\biv\b',
            r'\bb\b',             # e.g. Dortmund B
            r'\bc\b',
            r'\balt\.?\b',
            r'\bside\s*team\b',
            r'\breference\s*team\b',
            r'\bsquad\s*b\b',
            r'\bolympic\b',        # Olympic squads often restricted/side squads
            r'\bunder-?\d+\b',     # Catch-all age restrictions
            r'\bu-?\d+\b'
        ]

    def _matches_any(self, text: str, patterns: List[str]) -> bool:
        """Helper regex matcher for string validation."""
        combined = "|".join(patterns)
        return bool(re.search(combined, text, re.IGNORECASE))

    def evaluate_competitive_and_first_xi_status(
        self,
        home_team: str,
        away_team: str,
        league_or_tournament: str,
        is_official_competitive_fixture: Optional[bool] = None,
        starting_lineup_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Step 21 & 22 Filter Pipeline.
        
        :param home_team: Name of Home team
        :param away_team: Name of Away team
        :param league_or_tournament: Name of competition/league
        :param is_official_competitive_fixture: Direct API flag if match is friendly (optional)
        :param starting_lineup_metadata: Optional dict containing starting 11 roster flags
        """
        rejection_reasons = []

        # --- STEP 21: COMPETITIVE MATCH CHECK ---
        is_friendly_name = (
            self._matches_any(league_or_tournament, self.friendly_patterns) or
            self._matches_any(home_team, self.friendly_patterns) or
            self._matches_any(away_team, self.friendly_patterns)
        )

        if is_official_competitive_fixture is False or is_friendly_name:
            rejection_reasons.append(
                f"Step 21 Violation: Match '{league_or_tournament}' flagged as Non-Competitive / Friendly fixture."
            )

        # --- STEP 22: MAIN FIRST XI & PRIMARY TEAM CHECK ---
        # 1. Team Name Secondary Marker Inspection
        home_is_secondary = self._matches_any(home_team, self.secondary_squad_patterns)
        away_is_secondary = self._matches_any(away_team, self.secondary_squad_patterns)

        if home_is_secondary:
            rejection_reasons.append(f"Step 22 Violation: Home team '{home_team}' identified as Reserve/Side/B-team.")
        if away_is_secondary:
            rejection_reasons.append(f"Step 22 Violation: Away team '{away_team}' identified as Reserve/Side/B-team.")

        # 2. Lineup Verification (If Lineup Metadata Available)
        lineup_verified = True
        if starting_lineup_metadata:
            home_starters_count = starting_lineup_metadata.get("home_first_team_starters", 11)
            away_starters_count = starting_lineup_metadata.get("away_first_team_starters", 11)

            # Minimum 9 established primary first-team players required to prevent heavy squad rotation/reserve fill
            if home_starters_count < 9:
                lineup_verified = False
                rejection_reasons.append(
                    f"Step 22 Violation: {home_team} fielded only {home_starters_count}/11 main senior starters (Heavy Rotation)."
                )
            if away_starters_count < 9:
                lineup_verified = False
                rejection_reasons.append(
                    f"Step 22 Violation: {away_team} fielded only {away_starters_count}/11 main senior starters (Heavy Rotation)."
                )

        # Final Approval Determination
        step_21_passed = not is_friendly_name and (is_official_competitive_fixture is not False)
        step_22_passed = not home_is_secondary and not away_is_secondary and lineup_verified
        overall_eligible = step_21_passed and step_22_passed

        return {
            "match": f"{home_team} vs {away_team}",
            "competition": league_or_tournament,
            "step_21_competitive_check": {
                "passed": step_21_passed,
                "is_official_points_match": step_21_passed
            },
            "step_22_first_xi_check": {
                "passed": step_22_passed,
                "is_primary_senior_squad": not (home_is_secondary or away_is_secondary),
                "lineup_integrity_verified": lineup_verified
            },
            "overall_status": "APPROVED (Official Senior First XI Match)" if overall_eligible else "REJECTED",
            "rejection_reasons": rejection_reasons if rejection_reasons else ["None (Passed Steps 21 & 22)"]
        }


# Example Execution
if __name__ == "__main__":
    filter_engine = CompetitiveFirstXIFilter()

    # Test Cases
    test_fixtures = [
        {
            "home": "Real Madrid",
            "away": "FC Barcelona",
            "league": "La Liga",
            "lineup": {"home_first_team_starters": 11, "away_first_team_starters": 10}
        },
        {
            "home": "Manchester United",
            "away": "Liverpool",
            "league": "Club Friendly - Pre Season Tour",
            "lineup": {"home_first_team_starters": 6, "away_first_team_starters": 5}
        },
        {
            "home": "Benfica B",
            "away": "Porto B",
            "league": "Liga Portugal 2",
            "lineup": {"home_first_team_starters": 11, "away_first_team_starters": 11}
        }
    ]

    print("--- STEPS 21 & 22: COMPETITIVE FIXTURE & FIRST XI GUARDRAIL ---")
    for fix in test_fixtures:
        res = filter_engine.evaluate_competitive_and_first_xi_status(
            home_team=fix["home"],
            away_team=fix["away"],
            league_or_tournament=fix["league"],
            starting_lineup_metadata=fix["lineup"]
        )
        print(f"\nMatch: {res['match']} ({res['competition']})")
        print(f"Status: {res['overall_status']}")
        print(f"  * Step 21 (Competitive): {res['step_21_competitive_check']['passed']}")
        print(f"  * Step 22 (First XI):     {res['step_22_first_xi_check']['passed']}")
        if res["rejection_reasons"][0] != "None (Passed Steps 21 & 22)":
            for reason in res["rejection_reasons"]:
                print(f"  ! {reason}")