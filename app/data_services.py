from typing import Any, Dict, List


class TeamStatisticsBuilder:
    """
    Builds transparent team statistics from completed match results.

    No statistics are invented. Only supplied completed match scores
    are used.
    """

    @staticmethod
    def build(
        matches: List[Dict[str, Any]],
        team_name: str,
    ) -> Dict[str, Any]:

        completed = [
            m for m in matches
            if m.get("status") == "completed"
            and isinstance(m.get("score"), dict)
            and m.get("score", {}).get("home") is not None
            and m.get("score", {}).get("away") is not None
        ]

        relevant = [
            m for m in completed
            if m.get("home_team") == team_name
            or m.get("away_team") == team_name
        ]

        wins = draws = losses = goals_for = goals_against = 0

        for match in relevant:
            home = match["home_team"] == team_name
            gf = match["score"]["home"] if home else match["score"]["away"]
            ga = match["score"]["away"] if home else match["score"]["home"]

            goals_for += gf
            goals_against += ga

            if gf > ga:
                wins += 1
            elif gf == ga:
                draws += 1
            else:
                losses += 1

        played = len(relevant)

        return {
            "matches_played": played,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "goal_difference": goals_for - goals_against,
            "points": wins * 3 + draws,
            "points_per_game": (
                round((wins * 3 + draws) / played, 3)
                if played else None
            ),
            "source": "openfoot",
            "derived_from_completed_matches": played,
        }

class OpenFootTeamSnapshot:
    """Build prediction-input team snapshots from real OpenFoot data."""

    @staticmethod
    def build(
        normalized_matches,
        standings_response,
        team_name,
    ):
        stats = TeamStatisticsBuilder.build(
            normalized_matches,
            team_name,
        )

        position = None
        form = []

        for table in standings_response:
            for row in table.get("table", []):
                team = row.get("team") or {}

                if team.get("name") == team_name:
                    position = row.get("position")
                    form = row.get("form") or []
                    break

            if position is not None:
                break

        stats["league_position"] = position
        stats["recent_form"] = form
        stats["source"] = "openfoot"

        return stats
