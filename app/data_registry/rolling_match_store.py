import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from app.data_registry.match_identity import MatchIdentity


class RollingMatchStore:
    """
    Persistent rolling store for worldwide daily football data.

    Records are keyed by canonical match identity.

    Existing records are updated rather than duplicated.
    Historical records are retained.
    """

    def __init__(self, db_path: str = "data/football_daily.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS matches (
                    match_id TEXT PRIMARY KEY,
                    match_date TEXT NOT NULL,
                    day_role TEXT NOT NULL,
                    competition TEXT,
                    season TEXT,
                    home_team TEXT,
                    away_team TEXT,
                    kickoff_at TEXT,
                    status TEXT,
                    source TEXT,
                    source_match_id TEXT,
                    payload TEXT NOT NULL,
                    first_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_seen_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def upsert(self, match: Dict[str, Any], day_role: str) -> str:
        match_id = MatchIdentity.match_id(match)

        payload = json.dumps(match, ensure_ascii=False)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO matches (
                    match_id, match_date, day_role, competition, season,
                    home_team, away_team, kickoff_at, status, source,
                    source_match_id, payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(match_id) DO UPDATE SET
                    match_date=excluded.match_date,
                    day_role=excluded.day_role,
                    competition=excluded.competition,
                    season=excluded.season,
                    home_team=excluded.home_team,
                    away_team=excluded.away_team,
                    kickoff_at=excluded.kickoff_at,
                    status=excluded.status,
                    source=excluded.source,
                    source_match_id=excluded.source_match_id,
                    payload=excluded.payload,
                    last_seen_at=CURRENT_TIMESTAMP
                """,
                (
                    match_id,
                    match.get("kickoff_at", "")[:10],
                    day_role,
                    match.get("competition"),
                    match.get("season"),
                    match.get("home_team"),
                    match.get("away_team"),
                    match.get("kickoff_at"),
                    match.get("status"),
                    match.get("source"),
                    match.get("source_match_id"),
                    payload,
                ),
            )

        return match_id

    def upsert_many(
        self,
        matches: List[Dict[str, Any]],
        day_role: str,
    ) -> List[str]:
        return [
            self.upsert(match, day_role)
            for match in matches
        ]

    def count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM matches"
            ).fetchone()

        return int(row[0])

    def list_matches(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT match_id, match_date, day_role, competition,
                       season, home_team, away_team, kickoff_at,
                       status, source, source_match_id
                FROM matches
                ORDER BY kickoff_at
                """
            ).fetchall()

        columns = [
            "match_id",
            "match_date",
            "day_role",
            "competition",
            "season",
            "home_team",
            "away_team",
            "kickoff_at",
            "status",
            "source",
            "source_match_id",
        ]

        return [
            dict(zip(columns, row))
            for row in rows
        ]


    def get_latest_team_snapshot(
        self,
        team_name: str,
    ) -> Dict[str, Any]:
        """
        Return the latest stored team-level snapshot if available.

        Team snapshots are stored separately from match identity records
        in later data-layer stages. Until then, return an empty snapshot.
        """
        return {}
