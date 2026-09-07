import json
import sqlite3
from typing import Any, Dict, List, Optional


class PredictionResultStore:
    """
    Persistent storage for worldwide football prediction results.

    Results are keyed by canonical match_id.
    Existing analytical logic is not modified.
    """

    def __init__(self, db_path: str = "data/football_daily.db"):
        self.db_path = db_path
        self._initialize()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _initialize(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS prediction_results (
                    match_id TEXT PRIMARY KEY,
                    match_date TEXT,
                    competition TEXT,
                    home_team TEXT,
                    away_team TEXT,
                    kickoff_at TEXT,
                    status TEXT NOT NULL,
                    prediction_json TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def upsert(self, match: Dict[str, Any], prediction: Dict[str, Any]) -> None:
        match_id = (
            match.get("match_id")
            or match.get("canonical_match_id")
            or match.get("source_match_id")
        )

        if not match_id:
            raise ValueError("Prediction result requires a match identifier.")

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO prediction_results (
                    match_id,
                    match_date,
                    competition,
                    home_team,
                    away_team,
                    kickoff_at,
                    status,
                    prediction_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(match_id) DO UPDATE SET
                    match_date=excluded.match_date,
                    competition=excluded.competition,
                    home_team=excluded.home_team,
                    away_team=excluded.away_team,
                    kickoff_at=excluded.kickoff_at,
                    status=excluded.status,
                    prediction_json=excluded.prediction_json
                """,
                (
                    match_id,
                    match.get("match_date"),
                    match.get("competition"),
                    match.get("home_team"),
                    match.get("away_team"),
                    match.get("kickoff_at"),
                    "processed",
                    json.dumps(prediction, default=str),
                ),
            )
            conn.commit()

    def get(self, match_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    match_id,
                    match_date,
                    competition,
                    home_team,
                    away_team,
                    kickoff_at,
                    status,
                    prediction_json
                FROM prediction_results
                WHERE match_id = ?
                """,
                (match_id,),
            ).fetchone()

        if row is None:
            return None

        return {
            "match_id": row[0],
            "match_date": row[1],
            "competition": row[2],
            "home_team": row[3],
            "away_team": row[4],
            "kickoff_at": row[5],
            "status": row[6],
            "prediction": json.loads(row[7]),
        }

    def list_results(self, match_date: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT
                match_id,
                match_date,
                competition,
                home_team,
                away_team,
                kickoff_at,
                status,
                prediction_json
            FROM prediction_results
        """
        params = ()

        if match_date:
            query += " WHERE match_date = ?"
            params = (match_date,)

        query += " ORDER BY kickoff_at"

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()

        return [
            {
                "match_id": row[0],
                "match_date": row[1],
                "competition": row[2],
                "home_team": row[3],
                "away_team": row[4],
                "kickoff_at": row[5],
                "status": row[6],
                "prediction": json.loads(row[7]),
            }
            for row in rows
        ]

    def count(self, match_date: Optional[str] = None) -> int:
        if match_date:
            query = "SELECT COUNT(*) FROM prediction_results WHERE match_date = ?"
            params = (match_date,)
        else:
            query = "SELECT COUNT(*) FROM prediction_results"
            params = ()

        with self._connect() as conn:
            return int(conn.execute(query, params).fetchone()[0])
