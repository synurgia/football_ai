"""12-hour cycle runner — scans new matches and processes outcomes.

Usage:
    python -m app.cycle_runner                # one pass, then exit
    python -m app.cycle_runner --daemon       # loop every 12 hours
    python -m app.cycle_runner --daemon 6     # loop every 6 hours
    python -m app.cycle_runner --daemon 0.5   # loop every 30 minutes

In daemon mode, output goes to logs/cycle_runner.log and the process
detaches from the terminal so Termux can be closed.
"""

from __future__ import annotations
import asyncio
import os
import signal
import sqlite3
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

# Set batch mode BEFORE importing the engine so V1.4 stays quiet
os.environ.setdefault("FOOTBALL_AI_BATCH_MODE", "1")

DB = "data/football_daily.db"
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "cycle_runner.log"


def log(msg):
    ts = datetime.now(timezone.utc).isoformat()
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def ensure_tables():
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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cycle_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT,
            finished_at TEXT,
            matches_scanned INTEGER,
            outcomes_saved INTEGER,
            home_count INTEGER,
            draw_count INTEGER,
            away_count INTEGER,
            held_count INTEGER,
            status TEXT,
            error TEXT
        )
    """)
    conn.commit()
    conn.close()


def purge_non_today():
    today = date.today().isoformat()
    conn = sqlite3.connect(DB)
    n = conn.execute(
        "DELETE FROM match_outcomes WHERE match_date != ?", (today,)
    ).rowcount
    conn.commit()
    conn.close()
    return n


def outcome_counts():
    today = date.today().isoformat()
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT verdict, COUNT(*) FROM match_outcomes WHERE match_date = ? "
        "GROUP BY verdict", (today,)
    ).fetchall()
    conn.close()
    counts = {"HOME": 0, "DRAW": 0, "AWAY": 0, "HELD": 0}
    for v, n in rows:
        counts[v or "HELD"] = n
    return counts


def run_pipeline():
    from app.worldwide_daily_manager import WorldwideDailyDataManager
    manager = WorldwideDailyDataManager()
    return asyncio.run(manager.run_once())


def one_cycle():
    started = datetime.now(timezone.utc).isoformat()
    log("CYCLE START")

    purged = purge_non_today()
    if purged:
        log(f"  purged non-today: {purged}")

    try:
        result = run_pipeline()
    except Exception as exc:
        log(f"  PIPELINE FAILED: {exc}")
        conn = sqlite3.connect(DB)
        conn.execute(
            "INSERT INTO cycle_runs (started_at, finished_at, status, error) "
            "VALUES (?, ?, ?, ?)",
            (started, datetime.now(timezone.utc).isoformat(), "FAILED", str(exc)),
        )
        conn.commit()
        conn.close()
        return

    today = date.today().isoformat()
    scanned = result.get("today_count", 0)
    pred = result.get("prediction", {}) or {}
    cards = pred.get("reasoning_cards", []) or []
    persisted = result.get("outcome_persistence", {}) or {}
    saved = persisted.get("saved", 0)

    counts = outcome_counts()
    log(f"  scanned={scanned}  cards={len(cards)}  saved={saved}")
    log(f"  HOME={counts['HOME']}  DRAW={counts['DRAW']}  "
        f"AWAY={counts['AWAY']}  HELD={counts['HELD']}")

    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT INTO cycle_runs "
        "(started_at, finished_at, matches_scanned, outcomes_saved, "
        " home_count, draw_count, away_count, held_count, status) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            started,
            datetime.now(timezone.utc).isoformat(),
            scanned, saved,
            counts["HOME"], counts["DRAW"], counts["AWAY"], counts["HELD"],
            "OK",
        ),
    )
    conn.commit()
    conn.close()
    log("CYCLE END")


def daemon_loop(hours):
    interval = int(hours * 3600)
    log(f"DAEMON START — interval={hours}h ({interval}s)")
    stop = {"flag": False}

    def _stop(signum, frame):
        log("SIGNAL received — finishing current cycle")
        stop["flag"] = True

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    while not stop["flag"]:
        one_cycle()
        if stop["flag"]:
            break
        log(f"  sleeping {interval}s until next cycle")
        # sleep in 60s chunks so Ctrl+C stays responsive
        for _ in range(int(interval / 60)):
            if stop["flag"]:
                break
            time.sleep(60)

    log("DAEMON STOP")


def main():
    args = sys.argv[1:]
    ensure_tables()

    if "--daemon" not in args:
        one_cycle()
        return

    idx = args.index("--daemon")
    rest = args[idx + 1:]
    hours = 12.0
    if rest:
        try:
            hours = float(rest[0])
        except ValueError:
            pass

    daemon_loop(hours)


if __name__ == "__main__":
    main()
