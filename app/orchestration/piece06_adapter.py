from typing import Any, Dict

from app.tactical.piece06_engine import (
    ResistanceFilter,
    FormFilter,
    CompositeTeamEvaluator,
    TeamTacticalMetrics,
    TacticalDefensiveAnalyzer,
    TransitionMatchupMetrics,
    OffensiveTransitionAnalyzer,
    LeagueScheduleMetrics,
    LeagueScheduleContextAnalyzer,
)
from app.models.match_data import PreMatchData


def _team_value(team, key: str, default: float = 0.0) -> float:
    value = team.team_statistics.get(key, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def run_piece06(match: PreMatchData) -> Dict[str, Any]:
    home = match.home_team
    away = match.away_team

    home_stats = home.team_statistics
    away_stats = away.team_statistics

    resistance_engine = ResistanceFilter()

    home_resistance = resistance_engine.evaluate(
        home_stats.get("matches", [])
    )
    away_resistance = resistance_engine.evaluate(
        away_stats.get("matches", [])
    )

    form_engine = FormFilter()

    home_form = form_engine.evaluate(
        home_stats.get("matches", [])
    )
    away_form = form_engine.evaluate(
        away_stats.get("matches", [])
    )

    composite_engine = CompositeTeamEvaluator()

    home_composite = composite_engine.evaluate(
        home_stats.get("matches", []),
        is_away=False,
    )

    away_composite = composite_engine.evaluate(
        away_stats.get("matches", []),
        is_away=True,
    )

    home_defensive_metrics = TeamTacticalMetrics(
        formation=str(
            home_stats.get("formation", "4-3-3")
        ),
        avg_defensive_line_height_m=_team_value(
            home, "avg_defensive_line_height_m", 35.0
        ),
        inter_line_distance_m=_team_value(
            home, "inter_line_distance_m", 10.0
        ),
        width_compactness_m=_team_value(
            home, "width_compactness_m", 35.0
        ),
        open_play_xg_share=_team_value(
            home, "open_play_xg_share", 0.75
        ),
        set_piece_xg_share=_team_value(
            home, "set_piece_xg_share", 0.25
        ),
        set_piece_conversion_rate=_team_value(
            home, "set_piece_conversion_rate", 0.10
        ),
        avg_wing_sprint_speed_kmh=_team_value(
            home, "avg_wing_sprint_speed_kmh", 30.0
        ),
        directness_ratio=_team_value(
            home, "directness_ratio", 0.50
        ),
        vertical_passes_per_possession=_team_value(
            home, "vertical_passes_per_possession", 0.20
        ),
    )

    away_defensive_metrics = TeamTacticalMetrics(
        formation=str(
            away_stats.get("formation", "4-3-3")
        ),
        avg_defensive_line_height_m=_team_value(
            away, "avg_defensive_line_height_m", 35.0
        ),
        inter_line_distance_m=_team_value(
            away, "inter_line_distance_m", 10.0
        ),
        width_compactness_m=_team_value(
            away, "width_compactness_m", 35.0
        ),
        open_play_xg_share=_team_value(
            away, "open_play_xg_share", 0.75
        ),
        set_piece_xg_share=_team_value(
            away, "set_piece_xg_share", 0.25
        ),
        set_piece_conversion_rate=_team_value(
            away, "set_piece_conversion_rate", 0.10
        ),
        avg_wing_sprint_speed_kmh=_team_value(
            away, "avg_wing_sprint_speed_kmh", 30.0
        ),
        directness_ratio=_team_value(
            away, "directness_ratio", 0.50
        ),
        vertical_passes_per_possession=_team_value(
            away, "vertical_passes_per_possession", 0.20
        ),
    )

    defensive_analyzer = TacticalDefensiveAnalyzer()

    home_defensive_analysis = defensive_analyzer.analyze(
        home_defensive_metrics
    )

    away_defensive_analysis = defensive_analyzer.analyze(
        away_defensive_metrics
    )

    underdog_is_home = bool(
        home.additional_data.get("is_underdog", False)
    )

    underdog = home if underdog_is_home else away
    favorite = away if underdog_is_home else home

    transition_metrics = TransitionMatchupMetrics(
        underdog_breakaway_speed_kmh=_team_value(
            underdog,
            "breakaway_speed_kmh",
            30.0,
        ),
        favorite_defensive_recovery_speed_kmh=_team_value(
            favorite,
            "defensive_recovery_speed_kmh",
            29.0,
        ),
        underdog_shots_per_game=_team_value(
            underdog,
            "shots_avg",
            11.0,
        ),
        underdog_shot_conversion_rate=_team_value(
            underdog,
            "shot_conversion_rate",
            0.10,
        ),
        underdog_xg_per_shot=_team_value(
            underdog,
            "xg_per_shot",
            0.10,
        ),
        underdog_multi_goal_burst_rate=_team_value(
            underdog,
            "multi_goal_burst_rate",
            0.20,
        ),
        favorite_post_concession_fragility=_team_value(
            favorite,
            "post_concession_fragility",
            0.30,
        ),
    )

    transition_analyzer = OffensiveTransitionAnalyzer()

    transition_analysis = transition_analyzer.analyze(
        transition_metrics
    )

    favorite_rest_days = int(
        favorite.additional_data.get("rest_days", 0)
    )

    underdog_rest_days = int(
        underdog.additional_data.get("rest_days", 0)
    )

    schedule_metrics = LeagueScheduleMetrics(
        season_type=str(
            match.data_sources.get(
                "season_type",
                "LEAGUE",
            )
        ),
        season_stage_progress=float(
            match.data_sources.get(
                "season_stage_progress",
                0.50,
            )
        ),
        favorite_rotation_index=_team_value(
            favorite,
            "rotation_index",
            0.0,
        ),
        favorite_has_continental_cup_in_3days=bool(
            favorite.additional_data.get(
                "continental_cup_in_3days",
                False,
            )
        ),
        favorite_match_importance=float(
            favorite.additional_data.get(
                "match_importance",
                0.50,
            )
        ),
        favorite_travel_distance_km=float(
            favorite.additional_data.get(
                "travel_distance_km",
                0.0,
            )
        ),
        favorite_rest_days=favorite_rest_days,
        underdog_rest_days=underdog_rest_days,
        pitch_condition_degrader=float(
            match.data_sources.get(
                "pitch_condition_degrader",
                0.0,
            )
        ),
    )

    schedule_analyzer = LeagueScheduleContextAnalyzer()

    schedule_analysis = schedule_analyzer.analyze(
        schedule_metrics
    )

    return {
        "resistance": {
            "home": home_resistance,
            "away": away_resistance,
        },
        "form": {
            "home": home_form,
            "away": away_form,
        },
        "composite_team_evaluation": {
            "home": home_composite,
            "away": away_composite,
        },
        "tactical_defensive": {
            "home": home_defensive_analysis,
            "away": away_defensive_analysis,
        },
        "offensive_transition": transition_analysis,
        "league_schedule_context": schedule_analysis,
    }
