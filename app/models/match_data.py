from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PlayerMatchData:
    player_id: str
    name: str
    position: str

    # Pre-match player information
    form: float = 0.0
    pace: float = 0.0
    defensive_strength: float = 0.0
    attacking_strength: float = 0.0
    stamina: float = 0.0

    # Additional information supplied by the data source
    statistics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StartingXIData:
    team_name: str
    formation: str
    players: List[PlayerMatchData] = field(default_factory=list)


@dataclass
class TeamMatchData:
    team_name: str
    is_home: bool

    # Current team-level information
    league_position: Optional[int] = None
    recent_form: Dict[str, Any] = field(default_factory=dict)
    team_statistics: Dict[str, Any] = field(default_factory=dict)

    # The actual XI expected/confirmed for the match
    starting_xi: Optional[StartingXIData] = None

    # Absences and squad information
    injuries: List[str] = field(default_factory=list)
    suspensions: List[str] = field(default_factory=list)

    # Additional pre-match information
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RefereeMatchData:
    name: str
    fouls_per_game: float = 0.0
    tackles_per_game: float = 0.0
    cards_per_foul: float = 0.0
    penalties_per_game: float = 0.0
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MatchEnvironmentData:
    venue: str = ""
    pitch_width_m: Optional[float] = None
    pitch_length_m: Optional[float] = None
    grass_length_mm: Optional[float] = None
    watered_pre_match: Optional[bool] = None
    weather: str = ""
    temperature_c: Optional[float] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PreMatchData:
    competition: str
    home_team: TeamMatchData
    away_team: TeamMatchData
    referee: Optional[RefereeMatchData] = None
    environment: Optional[MatchEnvironmentData] = None

    # Market information is kept separate from analytical inputs
    market_odds: Dict[str, Any] = field(default_factory=dict)

    # Source/provenance information
    data_sources: Dict[str, Any] = field(default_factory=dict)
