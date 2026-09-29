"""Federation fixture cache.

The federation HTML sources are slow and fragile. They are scraped ONCE
per day by the daily federation job and cached here. Match pipeline reads
from the cache, never from live HTML.

Table: federation_fixtures
    competition_id TEXT
    scrape_date    TEXT   (YYYY-MM-DD)
    fixtures_json  TEXT   (list of {home, away, kickoff, source_url})
    scraped_at     TEXT   (ISO timestamp)
    status         TEXT   ('OK', 'EMPTY', 'FAILED')
    error          TEXT

Read: load_today(competition_id) -> list of fixtures
Write: store_scrape(competition_id, fixtures, status, error)
"""

from __future__ import annotations
import json
import sqlite3
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

DB = "data/football_daily.db"


def _ensure():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS federation_fixtures (
            competition_id TEXT,
            scrape_date    TEXT,
            fixtures_json  TEXT,
            scraped_at     TEXT,
            status         TEXT,
            error          TEXT,
            PRIMARY KEY (competition_id, scrape_date)
        )
    """)
    conn.commit()
    conn.close()


def store_scrape(
    competition_id: str,
    fixtures: List[Dict[str, Any]],
    status: str = "OK",
    error: Optional[str] = None,
    scrape_date: Optional[str] = None,
) -> None:
    _ensure()
    scrape_date = scrape_date or date.today().isoformat()
    conn = sqlite3.connect(DB)
    try:
        conn.execute(
            "INSERT OR REPLACE INTO federation_fixtures "
            "(competition_id, scrape_date, fixtures_json, scraped_at, status, error) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                str(competition_id),
                scrape_date,
                json.dumps(fixtures or []),
                datetime.now(timezone.utc).isoformat(),
                status,
                error,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def load_today(competition_id: str, scrape_date: Optional[str] = None) -> List[Dict[str, Any]]:
    _ensure()
    scrape_date = scrape_date or date.today().isoformat()
    conn = sqlite3.connect(DB)
    try:
        row = conn.execute(
            "SELECT fixtures_json, status FROM federation_fixtures "
            "WHERE competition_id = ? AND scrape_date = ? LIMIT 1",
            (str(competition_id), scrape_date),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        return []
    fixtures_json, status = row
    if status != "OK":
        return []
    try:
        return json.loads(fixtures_json) or []
    except Exception:
        return []


def load_all_today(scrape_date: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    _ensure()
    scrape_date = scrape_date or date.today().isoformat()
    conn = sqlite3.connect(DB)
    try:
        rows = conn.execute(
            "SELECT competition_id, fixtures_json FROM federation_fixtures "
            "WHERE scrape_date = ? AND status = 'OK'",
            (scrape_date,),
        ).fetchall()
    finally:
        conn.close()

    out: Dict[str, List[Dict[str, Any]]] = {}
    for cid, fj in rows:
        try:
            out[cid] = json.loads(fj) or []
        except Exception:
            out[cid] = []
    return out


def stats(scrape_date: Optional[str] = None) -> Dict[str, int]:
    _ensure()
    scrape_date = scrape_date or date.today().isoformat()
    conn = sqlite3.connect(DB)
    try:
        rows = conn.execute(
            "SELECT status, COUNT(*) FROM federation_fixtures "
            "WHERE scrape_date = ? GROUP BY status",
            (scrape_date,),
        ).fetchall()
    finally:
        conn.close()
    return {s: n for s, n in rows}


if __name__ == "__main__":
    _ensure()
    print("cache table ready")
    print("stats today:", stats())
