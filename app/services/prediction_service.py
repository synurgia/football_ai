from typing import Any, Dict, List

from app.models.match_data import (
    PlayerMatchData,
    PreMatchData,
    TeamMatchData,
)
from app.orchestration.analytical_pipeline import PreMatchAnalyticalPipeline
from app.orchestration.master_orchestrator import (
    MasterMatchOrchestrator,
    MatchEnvironment,
    PlayerProfile,
    PositionGroup,
    RefereeProfile,
    StartingXI,
    TeamMatchInput,
    WeatherCondition,
)


def _position_group(position: str) -> PositionGroup:
    """Convert the API position string into Piece 9's PositionGroup."""
    value = position.strip().upper()

    mapping = {
        "GK": PositionGroup.GK,
        "DEF": PositionGroup.DEFENDER,
        "DEFENDER": PositionGroup.DEFENDER,
        "MID": PositionGroup.MIDFIELDER,
        "MIDFIELDER": PositionGroup.MIDFIELDER,
        "ATT": PositionGroup.ATTACKER,
        "ATTACKER": PositionGroup.ATTACKER,
    }

    if value not in mapping:
        raise ValueError(
            f"Unsupported player position '{position}'. "
            "Use GK, DEF, MID, or ATT."
        )

    return mapping[value]


def _build_starting_xi(team: Dict[str, Any]) -> StartingXI:
    players: List[PlayerProfile] = []

    for player in team.get("starting_xi", {}).get("players", []):
        players.append(
            PlayerProfile(
                player_id=str(player["player_id"]),
                name=player["name"],
                position_group=_position_group(player["position"]),
                overall_form=float(player.get("form", 0.0)),
                pace=float(player.get("pace", 0.0)),
                defensive_solidity=float(
                    player.get("defensive_strength", 0.0)
                ),
                press_resistance=float(
                    player.get("press_resistance", 0.0)
                ),
                aerial_dominance=float(
                    player.get("aerial_dominance", 0.0)
                ),
                stamina=float(player.get("stamina", 0.0)),
                known_weaknesses=list(
                    player.get("known_weaknesses", [])
                ),
            )
        )

    return StartingXI(
        team_name=team["team_name"],
        formation=team.get("starting_xi", {}).get(
            "formation", "Unknown"
        ),
        players=players,
    )


def _build_piece9_team(team: Dict[str, Any]) -> TeamMatchInput:
    return TeamMatchInput(
        team_name=team["team_name"],
        starting_xi=_build_starting_xi(team),
        is_favorite=bool(team.get("is_favorite", False)),
        recent_xg_waste_ratio=float(
            team.get("recent_xg_waste_ratio", 0.0)
        ),
        gk_goals_prevented_p90=float(
            team.get("gk_goals_prevented_p90", 0.0)
        ),
        bus_park_success_count=int(
            team.get("bus_park_success_count", 0)
        ),
        is_missing_spof_playmaker=bool(
            team.get("is_missing_spof_playmaker", False)
        ),
        spof_progressive_share=float(
            team.get("spof_progressive_share", 0.0)
        ),
    )


def _build_central_team(
    team: Dict[str, Any],
    is_home: bool,
) -> TeamMatchData:
    players = []

    for player in team.get("starting_xi", {}).get("players", []):
        players.append(
            PlayerMatchData(
                player_id=str(player["player_id"]),
                name=player["name"],
                position=player["position"],
                form=float(player.get("form", 0.0)),
                pace=float(player.get("pace", 0.0)),
                defensive_strength=float(
                    player.get("defensive_strength", 0.0)
                ),
                attacking_strength=float(
                    player.get("attacking_strength", 0.0)
                ),
                stamina=float(player.get("stamina", 0.0)),
                statistics=dict(player.get("statistics", {})),
            )
        )

    from app.models.match_data import StartingXIData

    starting_xi = StartingXIData(
        team_name=team["team_name"],
        formation=team.get("starting_xi", {}).get(
            "formation", "Unknown"
        ),
        players=players,
    )

    return TeamMatchData(
        team_name=team["team_name"],
        is_home=is_home,
        league_position=team.get("league_position"),
        recent_form=dict(team.get("recent_form", {})),
        team_statistics=dict(team.get("team_statistics", {})),
        starting_xi=starting_xi,
        injuries=list(team.get("injuries", [])),
        suspensions=list(team.get("suspensions", [])),
        additional_data=dict(team.get("additional_data", {})),
    )


def run_prediction(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run the existing Pieces 1-8 pipeline and Piece 9 orchestrator."""

    home = payload["home_team"]
    away = payload["away_team"]

    central_match = PreMatchData(
        competition=payload["competition"],
        home_team=_build_central_team(home, True),
        away_team=_build_central_team(away, False),
        market_odds=dict(payload.get("market_odds", {})),
        data_sources=dict(payload.get("data_sources", {})),
    )

    analytical_pipeline = PreMatchAnalyticalPipeline(central_match)
    analytical_state = analytical_pipeline.run()

    environment_data = payload.get("environment", {})
    referee_data = payload.get("referee", {})

    weather_value = environment_data.get("weather", "CLEAR").upper()

    if weather_value not in WeatherCondition.__members__:
        raise ValueError(
            f"Unsupported weather '{weather_value}'. "
            f"Use one of: {', '.join(WeatherCondition.__members__.keys())}"
        )

    orchestrator = MasterMatchOrchestrator(
        home_input=_build_piece9_team(home),
        away_input=_build_piece9_team(away),
        environment=MatchEnvironment(
            pitch_width_m=float(
                environment_data.get("pitch_width_m", 68.0)
            ),
            pitch_length_m=float(
                environment_data.get("pitch_length_m", 105.0)
            ),
            grass_length_mm=float(
                environment_data.get("grass_length_mm", 25.0)
            ),
            is_watered_pre_match=bool(
                environment_data.get(
                    "is_watered_pre_match", False
                )
            ),
            weather=WeatherCondition[weather_value],
        ),
        referee=RefereeProfile(
            name=referee_data.get("name", "Unknown"),
            fouls_per_game=float(
                referee_data.get("fouls_per_game", 0.0)
            ),
            tackles_per_game=float(
                referee_data.get("tackles_per_game", 0.0)
            ),
            cards_per_foul=float(
                referee_data.get("cards_per_foul", 0.0)
            ),
            penalties_per_game=float(
                referee_data.get("penalties_per_game", 0.0)
            ),
        ),
    )

    orchestrator.attach_analytical_state(analytical_state)

    evidence_map = orchestrator.build_evidence_map()
    final_output = orchestrator.run_master_orchestration()

    return {
        "competition": payload["competition"],
        "home_team": home["team_name"],
        "away_team": away["team_name"],
        "analytical_summary": analytical_state.summary(),
        "analytical_evidence_sections": len(
            [value for value in evidence_map.values() if value is not None]
        ),
        "final_output": final_output,
    }
