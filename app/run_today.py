"""Today-only runner — processes only today's matches, on a loop.

Usage:
    python -m app.run_today              # one pass
    python -m app.run_today --watch      # loop every 5 minutes
    python -m app.run_today --watch 60   # loop every 60 seconds
"""

from __future__ import annotations
import asyncio
import json
import sqlite3
import sys
import time
from datetime import date, datetime, timezone

DB = "data/football_daily.db"


def _ensure_table():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS match_outcomes (
            match_id TEXT PRIMARY KEY,
            match_date TEXT,
            competition TEXT,
            home_team TEXT,
            away_team TEXT,
            kickoff_at TEXT,
            verdict TEXT,
            asserted INTEGER,
            confidence TEXT,
            source TEXT,
            outcome_json TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def _purge_non_today():
    today = date.today().isoformat()
    conn = sqlite3.connect(DB)
    n = conn.execute(
        "DELETE FROM match_outcomes WHERE match_date != ?", (today,)
    ).rowcount
    conn.commit()
    conn.close()
    return n


def _counts():
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT verdict, COUNT(*) FROM match_outcomes GROUP BY verdict"
    ).fetchall()
    conn.close()
    return {v or "HELD": n for v, n in rows}


def _run_daily():
    from app.worldwide_daily_manager import WorldwideDailyDataManager
    manager = WorldwideDailyDataManager()
    return asyncio.run(manager.run_once())


def _print_result(result):
    today = date.today().isoformat()
    pred = result.get("prediction", {}) or {}
    cards = pred.get("reasoning_cards", []) or []
    persisted = result.get("outcome_persistence", {}) or {}

    print(f"\n=== RUN {datetime.now(timezone.utc).isoformat()} ===")
    print(f"  date           : {today}")
    print(f"  scanned today  : {result.get('today_count')}")
    print(f"  tomorrow       : {result.get('tomorrow_count')}")
    print(f"  cards emitted  : {len(cards)}")
    print(f"  outcomes saved : {persisted.get('saved', 0)}  status={persisted.get('status')}")

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT home_team, away_team, verdict, asserted, source "
        "FROM match_outcomes WHERE match_date = ? "
        "ORDER BY kickoff_at LIMIT 10",
        (today,),
    ).fetchall()
    total = conn.execute(
        "SELECT COUNT(*) FROM match_outcomes WHERE match_date = ?", (today,)
    ).fetchone()[0]
    conn.close()

    print(f"  today rows in DB: {total}")
    print(f"  counts          : {_counts()}")
    if rows:
        print("  sample:")
        for r in rows:
            flag = "ASSERTED" if r["asserted"] else "prov"
            print(f"    [{flag:<8}] {r['verdict']:<5} {r['home_team']} vs {r['away_team']}  ({r['source']})")


def main():
    args = sys.argv[1:]
    watch = "--watch" in args
    interval = 300
    if watch:
        idx = args.index("--watch")
        rest = args[idx + 1:]
        if rest and rest[0].isdigit():
            interval = int(rest[0])

    _ensure_table()

    if not watch:
        purged = _purge_non_today()
        print(f"Purged non-today rows: {purged}")
        result = _run_daily()
        _print_result(result)
        return

    print(f"Watch mode: every {interval}s. Ctrl+C to stop.")
    while True:
        try:
            purged = _purge_non_today()
            if purged:
                print(f"Purged non-today: {purged}")
            result = _run_daily()
            _print_result(result)
        except KeyboardInterrupt:
            print("\nStopped.")
            break
        except Exception as exc:
            print(f"RUN FAILED: {exc}")
        time.sleep(interval)


if __name__ == "__main__":
    main()
