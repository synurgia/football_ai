import json
import sqlite3
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from app.v2_evidence_state import V2EvidenceState


class EvidenceStateStore:
    """
    Persistent SQLite storage for canonical V2 evidence states.

    This stores the existing V2EvidenceState produced by the live
    evidence pipeline. It does not answer questions, perform synthesis,
    or modify Pieces 1-9.
    """

    def __init__(self, db_path: str = "data/football_daily.db"):
        self.db_path = db_path
        self._ensure_table()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _ensure_table(self) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evidence_states (
                    match_id TEXT PRIMARY KEY,
                    match_date TEXT,
                    competition TEXT NOT NULL,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    first_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_seen_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def save_state(self, state: V2EvidenceState) -> None:
        state_dict = asdict(state)

        # match_date: derive from match_id prefix (authoritative,
        # matches the `matches` table format). Fallback to created_at.
        match_date = None
        import re as _re
        _mid = str(state.match_id or "")
        _m = _re.match(r"^(\d{4}-\d{2}-\d{2})", _mid)
        if _m:
            match_date = _m.group(1)
        if not match_date:
            kickoff_at = state_dict.get("created_at")
            if kickoff_at:
                match_date = str(kickoff_at)[:10]

        conn = self._connect()
        try:
            conn.execute(
                """
                INSERT INTO evidence_states (
                    match_id,
                    match_date,
                    competition,
                    home_team,
                    away_team,
                    created_at,
                    state_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(match_id) DO UPDATE SET
                    match_date = excluded.match_date,
                    competition = excluded.competition,
                    home_team = excluded.home_team,
                    away_team = excluded.away_team,
                    created_at = excluded.created_at,
                    state_json = excluded.state_json,
                    last_seen_at = CURRENT_TIMESTAMP
                """,
                (
                    state.match_id,
                    match_date,
                    state.competition,
                    state.home_team,
                    state.away_team,
                    state.created_at,
                    json.dumps(state_dict, ensure_ascii=False, default=str),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def save_states(self, states: List[V2EvidenceState]) -> int:
        for state in states:
            self.save_state(state)
        return len(states)

    def get_state(self, match_id: str) -> Optional[Dict[str, Any]]:
        conn = self._connect()
        try:
            row = conn.execute(
                """
                SELECT state_json
                FROM evidence_states
                WHERE match_id = ?
                """,
                (match_id,),
            ).fetchone()
        finally:
            conn.close()

        if row is None:
            return None

        return json.loads(row[0])

    def count(self) -> int:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT COUNT(*) FROM evidence_states"
            ).fetchone()
            return int(row[0])
        finally:
            conn.close()
