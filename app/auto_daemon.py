"""Auto daemon — refreshes fixture data every N hours."""

from __future__ import annotations
import os
import signal
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("FOOTBALL_AI_BATCH_MODE", "1")

DB = "data/football_daily.db"
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "auto_daemon.log"


def log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def _ensure_cycle_runs():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cycle_runs (
            run_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at       TEXT,
            finished_at      TEXT,
            matches_scanned  INTEGER,
            matches_saved    INTEGER,
            status           TEXT,
            error            TEXT
        )
    """)
    conn.commit()
    conn.close()


def one_cycle() -> None:
    started = datetime.now(timezone.utc).isoformat()
    log("CYCLE START")

    try:
        from app.sources.scanner import scan_today
        result = scan_today(write_to_db=True)
    except Exception as exc:
        log(f"  SCAN FAILED: {exc}")
        conn = sqlite3.connect(DB)
        conn.execute(
            "INSERT INTO cycle_runs (started_at, finished_at, status, error) "
            "VALUES (?, ?, ?, ?)",
            (started, datetime.now(timezone.utc).isoformat(), "FAILED", str(exc)),
        )
        conn.commit()
        conn.close()
        return

    scanned = result.get("total_unique", 0)
    saved = result.get("written_to_db", 0)
    sources = result.get("source_status", [])

    log(f"  scanned={scanned}  saved={saved}")
    for s in sources:
        err = f"  err={s.get('error')[:60]}" if s.get("error") else ""
        log(f"    {s['source']:<14} {s['status']:<8} {s['count']:>4}{err}")

    # --- Evidence collection (Phase 1 of Path B) ---
    try:
        import sqlite3 as _sq
        from datetime import date as _date
        from app.pipeline.evidence import collect_batch

        _conn = _sq.connect(DB)
        _conn.row_factory = _sq.Row
        _rows = _conn.execute(
            "SELECT match_id, competition, competition_id, home_team, away_team, "
            "       kickoff_at, source, payload "
            "FROM matches WHERE match_date = ?",
            (_date.today().isoformat(),),
        ).fetchall()
        _conn.close()

        matches = [dict(r) for r in _rows]
        log(f"  running evidence collection on {len(matches)} matches")

        ev = collect_batch(matches, persist=True)
        log(f"    enriched:     {ev['matches_enriched']}")
        log(f"    failed:       {ev['matches_failed']}")
        log(f"    states_saved: {ev['states_saved']}")
        log(f"    avg_answered: {ev['avg_answered']} / 37")
    except Exception as exc:
        log(f"  evidence collection FAILED: {exc}")

    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT INTO cycle_runs (started_at, finished_at, matches_scanned, "
        " matches_saved, status) VALUES (?, ?, ?, ?, ?)",
        (started, datetime.now(timezone.utc).isoformat(),
         scanned, saved, "OK"),
    )
    conn.commit()
    conn.close()
    log("CYCLE END")


def daemon_loop(hours: float) -> None:
    interval = int(hours * 3600)
    log(f"DAEMON START — interval={hours}h ({interval}s)")

    stop = {"flag": False}

    def _stop(signum, frame):
        log("SIGNAL received — will exit after current cycle")
        stop["flag"] = True

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    _ensure_cycle_runs()
    while not stop["flag"]:
        one_cycle()
        if stop["flag"]:
            break
        log(f"  sleeping {interval}s")
        for _ in range(int(interval / 60)):
            if stop["flag"]:
                break
            time.sleep(60)
    log("DAEMON STOP")


def main():
    args = sys.argv[1:]
    _ensure_cycle_runs()
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
