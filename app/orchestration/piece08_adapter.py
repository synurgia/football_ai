from typing import Any, Dict, List

from app.models.match_data import PreMatchData, PlayerMatchData

from app.tactical.piece08_engine import (
    RefereeProfile,
    MatchContext,
    RefereeStrictnessEngine,
    PitchProfile,
    KeyPlayerStatus,
    PitchAndRosterMicroEngine,
    PositionGroup,
    PlayerProfile,
    StartingXI,
    StartingXIEvaluationEngine,
)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    return default


def _get_team_id(team) -> str:
    return str(
        team.additional_data.get(
            "team_id",
            team.team_name,
        )
    )


def _build_referee_profile(match: PreMatchData) -> RefereeProfile:
    """
    Convert the central referee contract into Piece 8's RefereeProfile.

    Piece 8 declares var_overturns_per_game but its engine later reads
    var_penalties_per_game. We preserve the original engine and provide
    the expected runtime attribute here.
    """
    referee = match.referee

    if referee is None:
        raise ValueError("Referee data is required for referee analysis.")

    additional = referee.additional_data

    profile = RefereeProfile(
        referee_id=str(additional.get("referee_id", referee.name)),
        referee_name=referee.name,
        matches_officiated=int(
            _safe_float(additional.get("matches_officiated", 0))
        ),
        fouls_per_game=_safe_float(referee.fouls_per_game),
        tackles_per_game=_safe_float(referee.tackles_per_game),
        cards_per_foul=_safe_float(referee.cards_per_foul),
        penalties_per_game=_safe_float(referee.penalties_per_game),
        var_overturns_per_game=_safe_float(
            additional.get("var_overturns_per_game", 0.0)
        ),
    )

    # Piece 8's method currently expects this differently named attribute.
    setattr(
        profile,
        "var_penalties_per_game",
        _safe_float(
            additional.get(
                "var_penalties_per_game",
                additional.get("var_overturns_per_game", 0.0),
            )
        ),
    )

    return profile


def _build_match_context(match: PreMatchData) -> MatchContext:
    home = match.home_team
    away = match.away_team

    favorite_context = home.additional_data.get(
        "favorite_box_touch_share",
        match.data_sources.get("favorite_box_touch_share", 0.0),
    )

    underdog_context = away.additional_data.get(
        "underdog_tackle_intensity",
        match.data_sources.get("underdog_tackle_intensity", 0.0),
    )

    transition_context = home.additional_data.get(
        "favorite_transition_dependency",
        match.data_sources.get("favorite_transition_dependency", 0.0),
    )

    return MatchContext(
        favorite_box_touch_share=_safe_float(favorite_context),
        underdog_tackle_intensity=_safe_float(underdog_context),
        favorite_transition_dependency=_safe_float(transition_context),
    )


def _build_pitch_profile(match: PreMatchData) -> PitchProfile:
    environment = match.environment

    if environment is None:
        raise ValueError(
            "Match environment data is required for pitch analysis."
        )

    missing = []

    if environment.pitch_width_m is None:
        missing.append("pitch_width_m")

    if environment.pitch_length_m is None:
        missing.append("pitch_length_m")

    if environment.grass_length_mm is None:
        missing.append("grass_length_mm")

    if environment.watered_pre_match is None:
        missing.append("watered_pre_match")

    if missing:
        raise ValueError(
            "Incomplete pitch data. Missing: " + ", ".join(missing)
        )

    watered_halftime = environment.additional_data.get(
        "watered_halftime",
        False,
    )

    return PitchProfile(
        pitch_width_meters=float(environment.pitch_width_m),
        pitch_length_meters=float(environment.pitch_length_m),
        grass_length_mm=float(environment.grass_length_mm),
        is_watered_pre_match=bool(environment.watered_pre_match),
        is_watered_halftime=_safe_bool(watered_halftime),
    )


def _build_key_player_status(team) -> KeyPlayerStatus:
    additional = team.additional_data

    return KeyPlayerStatus(
        team_id=_get_team_id(team),
        is_missing_primary_playmaker=_safe_bool(
            additional.get(
                "is_missing_primary_playmaker",
                False,
            )
        ),
        playmaker_progressive_pass_share=_safe_float(
            additional.get(
                "playmaker_progressive_pass_share",
                0.0,
            )
        ),
        playmaker_xg_buildup_share=_safe_float(
            additional.get(
                "playmaker_xg_buildup_share",
                0.0,
            )
        ),
    )


def _map_position_group(position: str) -> PositionGroup:
    value = str(position).upper().strip()

    goalkeeper_values = {
        "GK",
        "GOALKEEPER",
        "KEEPER",
    }

    defender_values = {
        "DEF",
        "DF",
        "CB",
        "LB",
        "RB",
        "LWB",
        "RWB",
        "WB",
        "DEFENDER",
    }

    midfielder_values = {
        "MID",
        "MF",
        "CM",
        "DM",
        "AM",
        "LM",
        "RM",
        "CDM",
        "CAM",
        "MIDFIELDER",
    }

    attacker_values = {
        "ATT",
        "FW",
        "ST",
        "CF",
        "LW",
        "RW",
        "SS",
        "FORWARD",
        "ATTACKER",
    }

    if value in goalkeeper_values:
        return PositionGroup.GOALKEEPER

    if value in defender_values:
        return PositionGroup.DEFENDER

    if value in midfielder_values:
        return PositionGroup.MIDFIELDER

    if value in attacker_values:
        return PositionGroup.ATTACKER

    raise ValueError(
        f"Unsupported player position '{position}'. "
        "Map the player's position to GK, DEF, MID, or ATT."
    )


def _build_player_profile(player: PlayerMatchData) -> PlayerProfile:
    statistics = player.statistics or {}

    weaknesses = statistics.get(
        "known_weaknesses",
        statistics.get("weaknesses", []),
    )

    if weaknesses is None:
        weaknesses = []

    if not isinstance(weaknesses, list):
        weaknesses = list(weaknesses)

    return PlayerProfile(
        player_id=str(player.player_id),
        name=player.name,
        position_group=_map_position_group(player.position),
        overall_form=_safe_float(
            statistics.get("overall_form", player.form)
        ),
        pace=_safe_float(
            statistics.get("pace", player.pace)
        ),
        defensive_solidity=_safe_float(
            statistics.get(
                "defensive_solidity",
                player.defensive_strength,
            )
        ),
        press_resistance=_safe_float(
            statistics.get(
                "press_resistance",
                0.0,
            )
        ),
        aerial_dominance=_safe_float(
            statistics.get(
                "aerial_dominance",
                0.0,
            )
        ),
        progressive_output=_safe_float(
            statistics.get(
                "progressive_output",
                player.attacking_strength,
            )
        ),
        known_weaknesses=weaknesses,
    )


def _build_starting_xi(team) -> StartingXI:
    starting_xi = team.starting_xi

    if starting_xi is None:
        raise ValueError(
            f"No starting XI data supplied for {team.team_name}."
        )

    if len(starting_xi.players) != 11:
        raise ValueError(
            f"{team.team_name} starting XI contains "
            f"{len(starting_xi.players)} players; exactly 11 are required."
        )

    players = [
        _build_player_profile(player)
        for player in starting_xi.players
    ]

    return StartingXI(
        team_id=_get_team_id(team),
        team_name=team.team_name,
        formation=starting_xi.formation,
        players=players,
    )


def _run_referee_analysis(match: PreMatchData) -> Dict[str, Any]:
    if match.referee is None:
        return {
            "available": False,
            "reason": "Referee data was not supplied.",
        }

    engine = RefereeStrictnessEngine()

    referee_profile = _build_referee_profile(match)
    match_context = _build_match_context(match)

    result = engine.analyze_referee_impact(
        referee_profile,
        match_context,
    )

    return {
        "available": True,
        "result": result,
    }


def _run_pitch_analysis(match: PreMatchData) -> Dict[str, Any]:
    try:
        pitch = _build_pitch_profile(match)
    except ValueError as exc:
        return {
            "available": False,
            "reason": str(exc),
        }

    engine = PitchAndRosterMicroEngine()

    favorite_key_player = _build_key_player_status(
        match.home_team
    )

    favorite_possession_share = _safe_float(
        match.home_team.additional_data.get(
            "favorite_possession_share",
            0.65,
        ),
        0.65,
    )

    result = engine.Evaluate_match_micro_factors(
        pitch=pitch,
        favorite_key_player=favorite_key_player,
        favorite_possession_share=favorite_possession_share,
    )

    return {
        "available": True,
        "result": result,
    }


def _run_starting_xi_analysis(match: PreMatchData) -> Dict[str, Any]:
    if match.home_team.starting_xi is None:
        return {
            "available": False,
            "reason": "Home starting XI was not supplied.",
        }

    if match.away_team.starting_xi is None:
        return {
            "available": False,
            "reason": "Away starting XI was not supplied.",
        }

    try:
        home_xi = _build_starting_xi(match.home_team)
        away_xi = _build_starting_xi(match.away_team)
    except ValueError as exc:
        return {
            "available": False,
            "reason": str(exc),
        }

    engine = StartingXIEvaluationEngine()

    result = engine.evaluate_lineup_matchup(
        home_xi,
        away_xi,
    )

    return {
        "available": True,
        "result": result,
    }


def run_piece08(match: PreMatchData) -> Dict[str, Any]:
    """
    Run Piece 8 against the central pre-match data contract.

    Piece 8 remains unchanged. This adapter performs all translation
    between PreMatchData and the original Piece 8 engine interfaces.
    """

    return {
        "piece": "piece08",
        "referee_analysis": _run_referee_analysis(match),
        "pitch_and_roster_micro_factors": _run_pitch_analysis(match),
        "starting_xi_analysis": _run_starting_xi_analysis(match),
    }
