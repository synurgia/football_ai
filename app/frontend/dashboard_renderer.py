"""Unified dashboard renderer.

Supports two views via parameters:
  - Daily view (no filters): every match today + verdicts + evidence
  - Search view (with filters): matches by date / competition / country / league

Reads from three tables:
  matches         — every fixture (base)
  match_outcomes  — verdict if computed
  evidence_states — 37Q answer count
"""

from datetime import date, datetime, timedelta, timezone
from html import escape
import json
import sqlite3

EAT = timezone(timedelta(hours=3))
DB = "data/football_daily.db"


# ================================================================
# Loaders
# ================================================================

def _load_all(today, filter_competition=None, date_str=None,
              country=None, league=None):
    """Return list of fixtures with joined verdict + evidence data."""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    query_date = date_str or today

    query = (
        "SELECT match_id, competition, competition_id, home_team, away_team, "
        "       kickoff_at, source, venue FROM matches WHERE match_date = ? "
    )
    params = [query_date]

    if filter_competition:
        query += " AND (LOWER(competition_id) = ? OR LOWER(competition) LIKE ?)"
        params.append(filter_competition.lower())
        params.append(f"%{filter_competition.lower()}%")

    if country:
        query += " AND (LOWER(competition_id) LIKE ? OR LOWER(competition) LIKE ?)"
        params.append(f"{country.lower()}.%")
        params.append(f"%{country.lower()}%")

    if league:
        query += " AND LOWER(competition) LIKE ?"
        params.append(f"%{league.lower()}%")

    query += " ORDER BY kickoff_at"
    matches = conn.execute(query, params).fetchall()

    # Verdicts
    verdicts = {}
    try:
        for r in conn.execute(
            "SELECT match_id, verdict, asserted, confidence, source, outcome_json "
            "FROM match_outcomes WHERE match_date = ?",
            (query_date,),
        ):
            try:
                outcome = json.loads(r["outcome_json"] or "{}")
            except Exception:
                outcome = {}
            verdicts[r["match_id"]] = {
                "verdict": r["verdict"],
                "asserted": bool(r["asserted"]),
                "confidence": r["confidence"],
                "method": r["source"],
                "reason": outcome.get("reason") or "",
                "probabilities": outcome.get("probabilities"),
            }
    except Exception:
        pass

    # Evidence
    evidence = {}
    try:
        for r in conn.execute(
            "SELECT match_id, state_json FROM evidence_states WHERE match_date = ?",
            (query_date,),
        ):
            try:
                state = json.loads(r["state_json"])
            except Exception:
                state = {}
            items = state.get("items") or []
            answered = sum(
                1 for it in items
                if (it.get("answer") or "").upper() not in ("UNKNOWN", "")
            )
            verified = sum(
                1 for it in items
                if (it.get("status") or "").upper() in ("VERIFIED", "CONFIRMED")
            )
            evidence[r["match_id"]] = {
                "answered": answered,
                "verified": verified,
                "total": len(items),
            }
    except Exception:
        pass

    conn.close()

    out = []
    for m in matches:
        row = dict(m)
        row["_verdict"] = verdicts.get(row["match_id"])
        row["_evidence"] = evidence.get(row["match_id"])
        out.append(row)
    return out


# ================================================================
# Score helper
# ================================================================

def _predict_score(probs):
    if probs and probs.get("HOME") is not None:
        ph = probs["HOME"]
        pa = probs.get("AWAY", 0.3)
        hg = max(0, round(1.3 + 1.2 * (ph - pa)))
        ag = max(0, round(1.1 + 1.2 * (pa - ph)))
        return hg, ag
    return None, None


def _parse_kickoff_eat(raw):
    raw = str(raw or "").strip()
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(EAT)
    except Exception:
        try:
            return datetime.fromtimestamp(float(raw), tz=timezone.utc).astimezone(EAT)
        except Exception:
            return None


# ================================================================
# Card
# ================================================================

def _card(i, m):
    home = m.get("home_team") or ""
    away = m.get("away_team") or ""
    comp = m.get("competition") or m.get("competition_id") or ""

    kickoff = _parse_kickoff_eat(m.get("kickoff_at"))
    if kickoff:
        time_display = kickoff.strftime("%H:%M EAT")
        date_display = kickoff.strftime("%d %B %Y")
    else:
        time_display = "TBD"
        date_display = ""

    v = m.get("_verdict")
    ev = m.get("_evidence")

    if v and v["verdict"] in ("HOME", "AWAY", "DRAW"):
        if v["verdict"] == "HOME":
            winner = home or "Home"
        elif v["verdict"] == "AWAY":
            winner = away or "Away"
        else:
            winner = "Draw"

        probs = v.get("probabilities") or {}
        hg, ag = _predict_score(probs)
        score_line = f"Predicted: {hg}–{ag}" if hg is not None else ""

        prob_line = ""
        if probs:
            prob_line = (
                f" &nbsp; H {int(probs.get('HOME', 0) * 100)}%"
                f" · D {int(probs.get('DRAW', 0) * 100)}%"
                f" · A {int(probs.get('AWAY', 0) * 100)}%"
            )

        status_html = "PROCESSED"
        result_html = (
            f'<div class="result"><strong>{escape(winner)}</strong></div>'
            f'<div class="meta">'
            f'<span>{escape(score_line)}{prob_line}</span>'
            f'<span>{escape((v.get("reason") or "")[:110])}</span>'
            f'</div>'
        )
    elif v:
        status_html = "HELD"
        result_html = (
            f'<div class="result pending"><span>Held — insufficient data</span></div>'
            f'<div class="meta">'
            f'<span>{escape((v.get("reason") or "no odds or form")[:110])}</span>'
            f'</div>'
        )
    else:
        status_html = "PENDING"
        result_html = (
            f'<div class="result pending"><span>Awaiting verdict</span></div>'
        )

    ev_line = ""
    if ev:
        ev_line = (
            f'<div class="evidence">'
            f'Q answered: {ev["answered"]}/{ev["total"]} · '
            f'verified: {ev["verified"]}'
            f'</div>'
        )

    return (
        f'<a class="match-link" href="/match/{escape(m.get("match_id") or "")}">'
        f'<article class="card">'
        f'<div class="number">{i:02d}</div>'
        f'<div class="time">'
        f'<strong>{escape(time_display)}</strong>'
        f'<span>{escape(date_display)}</span>'
        f'</div>'
        f'<div class="teams">'
        f'<div>{escape(home)}</div>'
        f'<span>vs</span>'
        f'<div>{escape(away)}</div>'
        f'</div>'
        f'<div class="status {status_html.lower()}">{status_html}</div>'
                f'<div class="competition">{escape(comp)}'
        + (f' &nbsp;·&nbsp; 📍 {escape(m.get("venue"))}' if m.get("venue") else '')
        + f'</div>'
        f'{result_html}'
        f'{ev_line}'         f'</article>'
        f'</a>'
    )


# ================================================================
# Main
# ================================================================

def render_dashboard(prediction_store=None, match_store=None,
                     filter_competition=None, date_str=None,
                     country=None, league=None):
    """Dual-mode renderer.

    Daily (no filters): every match today + verdict + evidence.
    Search (with filters): matches by date / competition / country / league.
    """
    today = date.today().isoformat()
    fixtures = _load_all(
        today,
        filter_competition=filter_competition,
        date_str=date_str,
        country=country,
        league=league,
    )

    counts = {"PROCESSED": 0, "HELD": 0, "PENDING": 0}
    cards = []
    for i, m in enumerate(fixtures, 1):
        v = m.get("_verdict")
        if v and v["verdict"] in ("HOME", "AWAY", "DRAW"):
            counts["PROCESSED"] += 1
        elif v:
            counts["HELD"] += 1
        else:
            counts["PENDING"] += 1
        cards.append(_card(i, m))

    body = "".join(cards) if cards else '<div class="empty">No matches found.</div>'

    title = "Football AI"
    mode = "Daily"
    if date_str or filter_competition or country or league:
        mode = "Search"
        parts = []
        if date_str:
            parts.append(date_str)
        if filter_competition:
            parts.append(filter_competition)
        if country:
            parts.append(country)
        if league:
            parts.append(league)
        if parts:
            title += " — " + " · ".join(parts)

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0; padding: 16px;
            font-family: -apple-system, system-ui, sans-serif;
            background: #0b0e14; color: #d8dee9;
        }}
        h1 {{ font-size: 18px; margin: 0 0 4px; color: #88c0d0; }}
        .summary {{ font-size: 12px; color: #7b8794; margin-bottom: 16px; }}
        .grid {{ display: grid; grid-template-columns: 1fr; gap: 10px; }}
        a.match-link,
        a.match-link:link,
        a.match-link:visited,
        a.match-link:hover,
        a.match-link:active,
        a.match-link *,
        a.match-link *:link,
        a.match-link *:visited,
        a.match-link *:hover,
        a.match-link *:active {{
            text-decoration: none !important;
            color: inherit !important;
            border-bottom: none !important;
            background-image: none !important;
        }}
        a.match-link {{
            display: block;
        }}
        a.match-link:hover .card {{
            border-color: #3d4a5c !important;
            background: #1a2029 !important;
        }}
        .card {{
            background: #151a23; border: 1px solid #232a36;
            border-radius: 10px; padding: 12px;
            display: grid; grid-template-columns: 32px 68px 1fr auto;
            gap: 10px; align-items: start;
        }}
        .number {{ color: #4c566a; font-size: 12px; font-weight: 700; }}
        .time {{ font-size: 11px; }}
        .time strong {{ display: block; font-size: 12px; color: #e5e9f0; }}
        .time span {{ display: block; color: #6a7684; margin-top: 2px; }}
        .teams {{ font-size: 13px; color: #e5e9f0; }}
        .teams div {{ margin: 1px 0; }}
        .teams span {{ color: #4c566a; font-size: 10px; margin: 0 4px; }}
        .status {{
            font-size: 10px; font-weight: 700;
            letter-spacing: 0.5px; text-align: right; align-self: start;
        }}
        .status.processed {{
            color: #a3be8c; background: rgba(163,190,140,0.12);
            padding: 3px 7px; border-radius: 5px; border: 1px solid rgba(163,190,140,0.25);
        }}
        .status.held {{
            color: #d08770; background: rgba(208,135,112,0.12);
            padding: 3px 7px; border-radius: 5px; border: 1px solid rgba(208,135,112,0.25);
        }}
        .status.pending {{
            color: #7b8794; background: rgba(123,135,148,0.10);
            padding: 3px 7px; border-radius: 5px; border: 1px solid rgba(123,135,148,0.20);
        }}
        .competition {{
            grid-column: 1 / -1; font-size: 11px; color: #7b8794;
            margin-top: 6px; padding-top: 6px;
            border-top: 1px dashed #232a36;
        }}
        .result {{
            grid-column: 1 / -1; margin-top: 10px;
            padding: 8px 10px; border-radius: 8px;
            background: rgba(163,190,140,0.08);
            border-left: 3px solid #a3be8c;
            font-size: 13px; color: #d8dee9;
        }}
        .result.pending {{
            background: rgba(208,135,112,0.08);
            border-left: 3px solid #d08770;
            color: #d08770;
        }}
        .result strong {{
            font-size: 15px; color: #ebcb8b; font-weight: 700;
            display: inline-block; margin-bottom: 2px;
        }}
        .result .score {{
            color: #88c0d0; font-weight: 700; font-size: 14px;
        }}
        .result .prob {{
            color: #7b8794; font-size: 11px; margin-top: 3px;
        }}
        .meta {{
            grid-column: 1 / -1; margin-top: 4px;
            font-size: 11px; color: #6a7684; line-height: 1.4;
            font-style: italic;
        }}
        .meta span {{ display: block; }}
        .evidence {{
            grid-column: 1 / -1; margin-top: 4px;
            font-size: 10px; color: #5e81ac;
            letter-spacing: 0.3px;
        }}
        .empty {{
            text-align: center; color: #4c566a;
            padding: 40px 0; font-size: 13px;
        }}
    </style>
</head>
<body>
    <h1>{escape(title)}</h1>
    <div class="summary">
        {mode} view &nbsp;·&nbsp; {date_str or today} &nbsp;·&nbsp;
        {counts['PROCESSED']} processed &nbsp;·&nbsp;
        {counts['HELD']} held &nbsp;·&nbsp;
        {counts['PENDING']} pending &nbsp;·&nbsp;
        {len(fixtures)} total
    </div>
    <div class="grid">{body}</div>
</body>
</html>"""
