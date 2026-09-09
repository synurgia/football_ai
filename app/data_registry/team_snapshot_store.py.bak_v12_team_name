import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional


class TeamSnapshotStore:
    """
    Persistent store for the latest known football team snapshots.

    A snapshot is keyed by:
        competition + season + team

    Existing snapshots are updated rather than duplicated.
    """

    def __init__(self, db_path: str = "data/football_daily.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS team_snapshots (
                    snapshot_key TEXT PRIMARY KEY,
                    competition TEXT NOT NULL,
                    season TEXT NOT NULL,
                    team_name TEXT NOT NULL,
                    matches_played INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    draws INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    goals_for INTEGER DEFAULT 0,
                    goals_against INTEGER DEFAULT 0,
                    goal_difference INTEGER DEFAULT 0,
                    points INTEGER DEFAULT 0,
                    points_per_game REAL DEFAULT 0.0,
                    league_position INTEGER,
                    recent_form TEXT,
                    source TEXT,
                    payload TEXT NOT NULL,
                    first_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_seen_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    @staticmethod
    def _key(
        competition: str,
        season: str,
        team_name: str,
    ) -> str:
        return f"{competition}|{season}|{team_name.strip().lower()}"

    def upsert(
        self,
        competition: str,
        season: str,
        team_name: str,
        snapshot: Dict[str, Any],
    ) -> str:

        key = self._key(competition, season, team_name)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO team_snapshots (
                    snapshot_key,
                    competition,
                    season,
                    team_name,
                    matches_played,
                    wins,
                    draws,
                    losses,
                    goals_for,
                    goals_against,
                    goal_difference,
                    points,
                    points_per_game,
                    league_position,
                    recent_form,
                    source,
                    payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(snapshot_key) DO UPDATE SET
                    matches_played=excluded.matches_played,
                    wins=excluded.wins,
                    draws=excluded.draws,
                    losses=excluded.losses,
                    goals_for=excluded.goals_for,
                    goals_against=excluded.goals_against,
                    goal_difference=excluded.goal_difference,
                    points=excluded.points,
                    points_per_game=excluded.points_per_game,
                    league_position=excluded.league_position,
                    recent_form=excluded.recent_form,
                    source=excluded.source,
                    payload=excluded.payload,
                    last_seen_at=CURRENT_TIMESTAMP
                """,
                (
                    key,
                    competition,
                    season,
                    team_name,
                    snapshot.get("matches_played", 0),
                    snapshot.get("wins", 0),
                    snapshot.get("draws", 0),
                    snapshot.get("losses", 0),
                    snapshot.get("goals_for", 0),
                    snapshot.get("goals_against", 0),
                    snapshot.get("goal_difference", 0),
                    snapshot.get("points", 0),
                    snapshot.get("points_per_game", 0.0),
                    snapshot.get("league_position"),
                    json.dumps(
                        snapshot.get("recent_form", []),
                        ensure_ascii=False,
                    ),
                    snapshot.get("source", "unknown"),
                    json.dumps(snapshot, ensure_ascii=False),
                ),
            )

        return key

    def get(
        self,
        competition: str,
        season: str,
        team_name: str,
    ) -> Optional[Dict[str, Any]]:

        key = self._key(competition, season, team_name)

        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT payload
                FROM team_snapshots
                WHERE snapshot_key = ?
                """,
                (key,),
            ).fetchone()

        if row is None:
            return None

        return json.loads(row[0])

    def count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM team_snapshots"
            ).fetchone()

        return int(row[0])
