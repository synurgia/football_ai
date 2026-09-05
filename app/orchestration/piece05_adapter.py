from typing import Any, Dict

from app.analytics.piece05_engine import (
    UnderdogOddsAnalyzer,
    ScheduleContextEngine,
    WeatherDisruptionEngine,
    TeamGapFilter,
    MotivationFilter,
    ResistanceFilter,
    FormFilter,
)
from app.models.match_data import PreMatchData


def run_piece05(match: PreMatchData) -> Dict[str, Any]:
    home = match.home_team
    away = match.away_team

    # ---------------------------------------------------------------
    # 1. Underdog odds
    # ---------------------------------------------------------------
    odds_engine = UnderdogOddsAnalyzer()

    numeric_odds = {
        key: float(value)
        for key, value in match.market_odds.items()
        if isinstance(value, (int, float))
    }

    underdog_is_home = bool(
        home.additional_data.get("is_underdog", False)
    )

    underdog_name = (
        home.team_name
        if underdog_is_home
        else away.team_name
    )

    underdog_odds = odds_engine.extract_underdog_odds_range(
        underdog_name=underdog_name,
        bookmaker_odds=numeric_odds,
    )

    # ---------------------------------------------------------------
    # 2. Favorite schedule context
    # ---------------------------------------------------------------
    favorite_is_home = bool(
        home.additional_data.get("is_favorite", False)
    )

    favorite_name = (
        home.team_name
        if favorite_is_home
        else away.team_name
    )

    favorite_data = home if favorite_is_home else away

    schedule_engine = ScheduleContextEngine()

    schedule_context = schedule_engine.evaluate_favorite_schedule_context(
        favorite_team=favorite_name,
        days_until_next_fixture=favorite_data.additional_data.get(
            "days_until_next_fixture"
        ),
        next_fixture_importance=str(
            favorite_data.additional_data.get(
                "next_fixture_importance",
                "NORMAL",
            )
        ),
        next_fixture_name=str(
            favorite_data.additional_data.get(
                "next_fixture_name",
                "",
            )
        ),
        days_since_last_fixture=favorite_data.additional_data.get(
            "days_since_last_fixture"
        ),
        last_fixture_importance=str(
            favorite_data.additional_data.get(
                "last_fixture_importance",
                "NORMAL",
            )
        ),
        league_title_pressure=str(
            favorite_data.additional_data.get(
                "league_title_pressure",
                "HIGH",
            )
        ),
    )

    # ---------------------------------------------------------------
    # 3. Weather disruption
    # ---------------------------------------------------------------
    weather_engine = WeatherDisruptionEngine()

    environment = match.environment

    weather_result = weather_engine.evaluate_weather_impact(
        venue_name=(
            environment.venue
            if environment is not None
            else ""
        ),
        precipitation_mm=float(
            environment.additional_data.get(
                "precipitation_mm",
                0.0,
            )
            if environment is not None
            else 0.0
        ),
        wind_speed_kmh=float(
            environment.additional_data.get(
                "wind_speed_kmh",
                0.0,
            )
            if environment is not None
            else 0.0
        ),
        temperature_c=float(
            environment.temperature_c
            if environment is not None
            and environment.temperature_c is not None
            else 20.0
        ),
        weather_condition=(
            environment.weather
            if environment is not None and environment.weather
            else "Clear"
        ),
    )

    # ---------------------------------------------------------------
    # 4. Team gap
    # ---------------------------------------------------------------
    gap_engine = TeamGapFilter()

    table_gap = None

    if (
        home.league_position is not None
        and away.league_position is not None
    ):
        table_gap = abs(
            home.league_position - away.league_position
        )

    home_stats = home.team_statistics
    away_stats = away.team_statistics

    team_gap = gap_engine.evaluate_team_gap(
        home_team=home.team_name,
        away_team=away.team_name,
        table_position_gap=table_gap,
        elo_diff=float(
            home_stats.get("elo", 0.0)
        ) - float(
            away_stats.get("elo", 0.0)
        ),
        home_xg_90=float(
            home_stats.get("xg_avg", 1.5)
        ),
        away_xg_90=float(
            away_stats.get("xg_avg", 1.2)
        ),
        market_value_ratio=float(
            home_stats.get("market_value_ratio", 1.0)
        ),
    )

    # ---------------------------------------------------------------
    # 5. Motivation dynamics
    # ---------------------------------------------------------------
    motivation_engine = MotivationFilter()

    motivation = motivation_engine.evaluate_motivation_dynamics(
        home_team=home.team_name,
        home_stake_category=str(
            home.additional_data.get(
                "stake_category",
                "NORMAL",
            )
        ),
        away_team=away.team_name,
        away_stake_category=str(
            away.additional_data.get(
                "stake_category",
                "NORMAL",
            )
        ),
        is_derby=bool(
            match.data_sources.get(
                "is_derby",
                False,
            )
        ),
        remaining_league_games=int(
            match.data_sources.get(
                "remaining_league_games",
                10,
            )
        ),
    )

    # ---------------------------------------------------------------
    # 6. Market + tactical resistance
    # ---------------------------------------------------------------
    resistance_engine = ResistanceFilter()

    home_opening_odds = float(
        home.additional_data.get(
            "opening_odds",
            0.0,
        )
    )

    home_current_odds = float(
        home.additional_data.get(
            "current_odds",
            home_opening_odds,
        )
    )

    resistance = resistance_engine.evaluate_market_and_tactical_resistance(
        team_name=home.team_name,
        opening_odds=home_opening_odds,
        current_odds=home_current_odds,
        current_handicap=float(
            home.additional_data.get(
                "current_handicap",
                0.0,
            )
        ),
        defensive_xga_last5=float(
            home_stats.get(
                "defensive_xga_last5",
                1.2,
            )
        ),
        clean_sheet_pct_last10=float(
            home_stats.get(
                "clean_sheet_pct_last10",
                0.30,
            )
        ),
        low_block_resilience_rating=float(
            home_stats.get(
                "low_block_resilience_rating",
                0.50,
            )
        ),
    )

    # ---------------------------------------------------------------
    # 7. Recent form
    # ---------------------------------------------------------------
    form_engine = FormFilter()

    home_matches = home.team_statistics.get(
        "matches",
        []
    )

    away_matches = away.team_statistics.get(
        "matches",
        []
    )

    home_form = form_engine.evaluate_recent_form(
        team_name=home.team_name,
        recent_matches=home_matches,
    )

    away_form = form_engine.evaluate_recent_form(
        team_name=away.team_name,
        recent_matches=away_matches,
    )

    return {
        "underdog_odds": underdog_odds,
        "favorite_schedule": schedule_context,
        "weather_disruption": weather_result,
        "team_gap": team_gap,
        "motivation": motivation,
        "market_tactical_resistance": resistance,
        "recent_form": {
            "home": home_form,
            "away": away_form,
        },
    }
