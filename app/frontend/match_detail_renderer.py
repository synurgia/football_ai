"""Match detail page — click a card, see the full intelligence.

Loads:
  matches         — fixture info (teams, kickoff, venue, competition)
  match_outcomes  — verdict + confidence + reason
  evidence_states — 37Q answers

Renders:
  Header       — teams, competition, venue, kickoff
  Verdict      — HOME/DRAW/AWAY/HELD with confidence + score
  Form         — home / away recent form strings
  Evidence     — all 37 questions with status + answer
  Reasoning    — the trace of how the verdict was produced
"""

from datetime import datetime, timedelta, timezone
from html import escape
import json
import sqlite3

EAT = timezone(timedelta(hours=3))
DB = "data/football_daily.db"


def _load(match_id):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    match = conn.execute(
        "SELECT match_id, match_date, competition, competition_id, home_team, "
        "       away_team, kickoff_at, source, venue, payload "
        "FROM matches WHERE match_id = ? LIMIT 1",
        (match_id,),
    ).fetchone()

    outcome = conn.execute(
        "SELECT verdict, asserted, confidence, source, outcome_json "
        "FROM match_outcomes WHERE match_id = ? LIMIT 1",
        (match_id,),
    ).fetchone()

    evidence = conn.execute(
        "SELECT state_json FROM evidence_states WHERE match_id = ? LIMIT 1",
        (match_id,),
    ).fetchone()

    conn.close()
    return match, outcome, evidence


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


def _predict_score(probs):
    if probs and probs.get("HOME") is not None:
        ph = probs["HOME"]
        pa = probs.get("AWAY", 0.3)
        return max(0, round(1.3 + 1.2 * (ph - pa))), max(0, round(1.1 + 1.2 * (pa - ph)))
    return None, None


def _form_from_reason(reason):
    """Extract 'home WWLDL | away WDLLW' from a reason string."""
    import re
    m = re.search(r"home\s+([WDL]+)\s*\|\s*away\s+([WDL]+)", str(reason or ""))
    if m:
        return m.group(1), m.group(2)
    return "", ""


def _render_question_rows(items):
    rows = []
    for it in items:
        qid = it.get("question_id") or "?"
        piece = it.get("piece") or "?"
        qtext = (it.get("question") or "")[:110]
        status = (it.get("status") or "UNKNOWN").upper()
        answer = it.get("answer") or ""
        if answer.upper() == "UNKNOWN":
            answer = ""

        status_class = {
            "VERIFIED": "q-ok",
            "CONFIRMED": "q-ok",
            "INSUFFICIENT_EVIDENCE": "q-warn",
            "CONFLICT": "q-err",
        }.get(status, "q-none")

        answer_html = (
            f'<div class="q-answer">{escape(answer[:200])}</div>'
            if answer else
            f'<div class="q-answer empty">— no answer —</div>'
        )

        rows.append(
            f'<div class="q-row">'
            f'<div class="q-id">{escape(qid)} <span class="q-piece">P{escape(str(piece))}</span></div>'
            f'<div class="q-body">'
            f'<div class="q-text">{escape(qtext)}</div>'
            f'{answer_html}'
            f'</div>'
            f'<div class="q-status {status_class}">{escape(status)}</div>'
            f'</div>'
        )
    return "".join(rows)


def render_match_detail(match_id):
    match, outcome, evidence = _load(match_id)

    if not match:
        return _missing(match_id)

    home = match["home_team"] or ""
    away = match["away_team"] or ""
    comp = match["competition"] or match["competition_id"] or ""
    venue = match["venue"] or ""
    source = match["source"] or ""

    kickoff = _parse_kickoff_eat(match["kickoff_at"])
    if kickoff:
        kickoff_str = kickoff.strftime("%a %d %b · %H:%M EAT")
    else:
        kickoff_str = "time TBD"

    # Verdict
    v_dict = {}
    if outcome:
        try:
            v_dict = json.loads(outcome["outcome_json"] or "{}")
        except Exception:
            v_dict = {}
    verdict = (outcome["verdict"] if outcome else "PENDING")
    confidence = (outcome["confidence"] if outcome else "") or ""
    method = (outcome["source"] if outcome else "") or ""
    reason = v_dict.get("reason") or ""
    probs = v_dict.get("probabilities") or {}

    hg, ag = _predict_score(probs)
    score_str = f"{hg} – {ag}" if hg is not None else "—"

    # Winner label
    if verdict == "HOME":
        winner_label = home
    elif verdict == "AWAY":
        winner_label = away
    elif verdict == "DRAW":
        winner_label = "Draw"
    else:
        winner_label = "Held"

    # Form
    home_form, away_form = _form_from_reason(reason)

    # Questions
    questions_html = "<div class='empty-note'>No evidence collected for this match yet.</div>"
    answered = 0
    verified = 0
    total = 0
    if evidence:
        try:
            state = json.loads(evidence["state_json"] or "{}")
        except Exception:
            state = {}
        items = state.get("items") or []
        total = len(items)
        for it in items:
            a = (it.get("answer") or "").upper()
            if a and a not in ("UNKNOWN", ""):
                answered += 1
            if (it.get("status") or "").upper() in ("VERIFIED", "CONFIRMED"):
                verified += 1
        questions_html = _render_question_rows(items)

    # Prob line
    prob_line = ""
    if probs:
        prob_line = (
            f"H {int(probs.get('HOME', 0) * 100)}% &nbsp;·&nbsp; "
            f"D {int(probs.get('DRAW', 0) * 100)}% &nbsp;·&nbsp; "
            f"A {int(probs.get('AWAY', 0) * 100)}%"
        )

    # Raw payload preview (collapsed)
    try:
        payload_pretty = json.dumps(json.loads(match["payload"] or "{}"), indent=2, default=str)
    except Exception:
        payload_pretty = ""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(home)} vs {escape(away)} · Football AI</title>
<style>
    * {{ box-sizing: border-box; }}
    body {{
        margin: 0; padding: 16px;
        font-family: -apple-system, system-ui, sans-serif;
        background: #0b0e14; color: #d8dee9;
        max-width: 900px; margin: 0 auto;
    }}
    a.back {{
        display: inline-block; color: #88c0d0; text-decoration: none;
        font-size: 12px; margin-bottom: 12px;
    }}
    a.back:hover {{ text-decoration: underline; }}
    .hdr {{
        background: #151a23; border: 1px solid #232a36;
        border-radius: 12px; padding: 16px; margin-bottom: 12px;
    }}
    .teams {{
        display: grid; grid-template-columns: 1fr auto 1fr;
        gap: 8px; align-items: center; margin: 8px 0;
    }}
    .team-home {{ font-size: 15px; font-weight: 600; text-align: left; }}
    .team-vs   {{ color: #4c566a; font-size: 12px; }}
    .team-away {{ font-size: 15px; font-weight: 600; text-align: right; }}
    .meta {{
        font-size: 11px; color: #7b8794;
        display: flex; gap: 10px; flex-wrap: wrap;
        margin-top: 10px; padding-top: 10px;
        border-top: 1px dashed #232a36;
    }}
    .meta span {{ display: inline-block; }}

    .verdict-card {{
        background: linear-gradient(135deg, #1c2430 0%, #151a23 100%);
        border: 1px solid #2d3a4d;
        border-left: 4px solid #5e81ac;
        border-radius: 12px; padding: 16px; margin-bottom: 12px;
    }}
    .verdict-status {{
        font-size: 11px; font-weight: 700; letter-spacing: 1px;
        margin-bottom: 6px;
    }}
    .verdict-status.PROCESSED {{
        color: #a3be8c; background: rgba(163,190,140,0.15);
        padding: 4px 10px; border-radius: 5px;
        display: inline-block; border: 1px solid rgba(163,190,140,0.3);
    }}
    .verdict-status.HELD {{
        color: #d08770; background: rgba(208,135,112,0.15);
        padding: 4px 10px; border-radius: 5px;
        display: inline-block; border: 1px solid rgba(208,135,112,0.3);
    }}
    .verdict-status.PENDING {{
        color: #7b8794; background: rgba(123,135,148,0.10);
        padding: 4px 10px; border-radius: 5px;
        display: inline-block; border: 1px solid rgba(123,135,148,0.2);
    }}
    .verdict-main {{
        font-size: 24px; font-weight: 800; color: #ebcb8b;
        margin: 8px 0 6px 0; letter-spacing: -0.5px;
    }}
    .verdict-score {{
        font-size: 18px; color: #88c0d0; font-weight: 700;
        margin-bottom: 8px; letter-spacing: 0.5px;
        font-family: ui-monospace, monospace;
    }}
    .verdict-line {{
        font-size: 12px; color: #a0a8b4; line-height: 1.5;
    }}
    .verdict-line strong {{ color: #d8dee9; }}
    .prob-row {{
        margin-top: 10px; padding-top: 10px;
        border-top: 1px dashed #2d3a4d;
        font-size: 12px; color: #88c0d0;
    }}

    .section {{
        background: #151a23; border: 1px solid #232a36;
        border-radius: 12px; padding: 16px; margin-bottom: 12px;
    }}
    .section h2 {{
        font-size: 12px; font-weight: 700; letter-spacing: 1px;
        color: #88c0d0; margin: 0 0 12px 0;
        text-transform: uppercase;
    }}
    .form-grid {{
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 12px;
    }}
    .form-cell {{
        background: #1c2430; border: 1px solid #2d3a4d;
        border-radius: 8px; padding: 10px;
    }}
    .form-cell-label {{
        font-size: 10px; color: #7b8794;
        text-transform: uppercase; letter-spacing: 0.5px;
        margin-bottom: 4px;
    }}
    .form-cell-value {{
        font-family: ui-monospace, monospace;
        font-size: 15px; color: #ebcb8b; font-weight: 700;
        letter-spacing: 2px;
    }}

    .q-row {{
        display: grid;
        grid-template-columns: 80px 1fr auto;
        gap: 10px; padding: 8px 0;
        border-bottom: 1px dashed #232a36;
        align-items: start;
    }}
    .q-row:last-child {{ border-bottom: none; }}
    .q-id {{
        font-family: ui-monospace, monospace;
        font-size: 11px; color: #d8dee9; font-weight: 700;
    }}
    .q-piece {{
        color: #4c566a; font-weight: 400;
        font-size: 9px; margin-left: 3px;
    }}
    .q-text {{
        font-size: 11px; color: #a0a8b4;
        line-height: 1.4; margin-bottom: 3px;
    }}
    .q-answer {{
        font-size: 12px; color: #a3be8c;
    }}
    .q-answer.empty {{ color: #4c566a; font-style: italic; }}
    .q-status {{
        font-size: 9px; font-weight: 700;
        letter-spacing: 0.5px; padding: 2px 6px;
        border-radius: 4px; align-self: start;
    }}
    .q-ok   {{ background: rgba(163,190,140,0.15); color: #a3be8c; border: 1px solid rgba(163,190,140,0.3); }}
    .q-warn {{ background: rgba(235,203,139,0.15); color: #ebcb8b; border: 1px solid rgba(235,203,139,0.3); }}
    .q-err  {{ background: rgba(208,135,112,0.15); color: #d08770; border: 1px solid rgba(208,135,112,0.3); }}
    .q-none {{ background: #232a36; color: #6a7684; border: 1px solid #2d3a4d; }}

    details {{
        margin-top: 8px;
        background: #0b0e14; border: 1px solid #232a36;
        border-radius: 6px; padding: 8px;
    }}
    details summary {{
        cursor: pointer; color: #88c0d0;
        font-size: 11px; font-weight: 600;
    }}
    details pre {{
        background: #0b0e14; color: #a0a8b4;
        font-size: 10px; padding: 10px;
        overflow-x: auto; margin: 8px 0 0 0;
        border-radius: 4px;
    }}

    .placeholder {{
        color: #4c566a; font-style: italic;
        font-size: 12px; text-align: center;
        padding: 20px 10px;
    }}
    .stats {{
        font-size: 11px; color: #7b8794; margin-bottom: 10px;
    }}
    .empty-note {{
        color: #4c566a; font-style: italic;
        font-size: 12px; text-align: center; padding: 10px;
    }}
</style>
</head>
<body>

<a href="/dashboard" class="back">← back to dashboard</a>

<div class="hdr">
    <div class="teams">
        <div class="team-home">{escape(home)}</div>
        <div class="team-vs">vs</div>
        <div class="team-away">{escape(away)}</div>
    </div>
    <div class="meta">
        <span>🕐 {escape(kickoff_str)}</span>
        <span>🏆 {escape(comp)}</span>
        {f'<span>📍 {escape(venue)}</span>' if venue else ''}
        <span>source: {escape(source)}</span>
    </div>
</div>

<div class="verdict-card">
    <div class="verdict-status {verdict}">{escape(verdict)}</div>
    <div class="verdict-main">{escape(winner_label)}</div>
    {f'<div class="verdict-score">Predicted score: {score_str}</div>' if hg is not None else ''}
    <div class="verdict-line">
        <strong>Method:</strong> {escape(method or '—')} &nbsp;·&nbsp;
        <strong>Confidence:</strong> {escape(confidence or '—')}
    </div>
    {f'<div class="verdict-line"><strong>Reason:</strong> {escape(reason)}</div>' if reason else ''}
    {f'<div class="prob-row">{prob_line}</div>' if prob_line else ''}
</div>

<div class="section">
    <h2>Recent form</h2>
    <div class="form-grid">
        <div class="form-cell">
            <div class="form-cell-label">{escape(home)}</div>
            <div class="form-cell-value">{escape(home_form or '—')}</div>
        </div>
        <div class="form-cell">
            <div class="form-cell-label">{escape(away)}</div>
            <div class="form-cell-value">{escape(away_form or '—')}</div>
        </div>
    </div>
</div>

<div class="section">
    <h2>Evidence · 37 questions</h2>
    <div class="stats">
        {answered} answered &nbsp;·&nbsp; {verified} verified &nbsp;·&nbsp; {total} total
    </div>
    {questions_html}
</div>

<div class="section">
    <h2>Broad reasoning · V1.5</h2>
    <div class="placeholder">
        V1.5 broad reasoning will appear here after Phase 2 wiring.<br>
        Advantages · counter-advantages · self-challenge · conflict detection
    </div>
</div>

<div class="section">
    <h2>Five-dimensional matrix · V1.4</h2>
    <div class="placeholder">
        V1.4 matrix (momentum, attack, defence, volatility, composite) will appear here.
    </div>
</div>

<div class="section">
    <h2>Reasoning trace · the demo</h2>
    <details>
        <summary>Show raw source payload</summary>
        <pre>{escape(payload_pretty[:4000])}</pre>
    </details>
</div>

</body>
</html>"""


def _missing(match_id):
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Not found</title>
<style>body{{background:#0b0e14;color:#d8dee9;font-family:system-ui;padding:40px;text-align:center;}}</style>
</head><body>
<h1>Match not found</h1>
<p style="color:#7b8794;">match_id: {escape(match_id)}</p>
<a href="/dashboard" style="color:#88c0d0;">← back to dashboard</a>
</body></html>"""
