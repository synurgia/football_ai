from datetime import date, datetime, timedelta, timezone
from html import escape


EAT = timezone(timedelta(hours=3))


def render_dashboard(prediction_store, match_store):
    today = date.today().isoformat()

    predictions = prediction_store.list_results(
        match_date=today
    )

    prediction_map = {
        item.get("match_id"): item
        for item in predictions
        if item.get("match_id")
    }

    fixtures = [
        item
        for item in match_store.list_matches()
        if item.get("match_date") == today
        and item.get("day_role") == "today"
    ]

    def parse_kickoff(value):
        raw = str(value or "").strip()
        if not raw:
            return None

        try:
            return datetime.fromisoformat(
                raw.replace("Z", "+00:00")
            ).astimezone(EAT)
        except ValueError:
            return None

    fixtures.sort(
        key=lambda item: (
            parse_kickoff(item.get("kickoff_at"))
            or datetime.max.replace(tzinfo=EAT)
        )
    )

    cards = []
    current_hour = None

    for i, fixture in enumerate(fixtures, 1):
        kickoff = parse_kickoff(
            fixture.get("kickoff_at")
        )

        if kickoff:
            hour_key = kickoff.strftime("%Y-%m-%d %H")

            if hour_key != current_hour:
                current_hour = hour_key

                cards.append(
                    '<div class="time-group">'
                    + escape(kickoff.strftime("%H:00 EAT"))
                    + '</div>'
                )

            date_display = kickoff.strftime("%d %B %Y")
            time_display = kickoff.strftime("%H:%M EAT")
        else:
            date_display = today
            time_display = "Time unavailable"

        match_id = fixture.get("match_id")
        prediction_item = prediction_map.get(match_id)

        home = escape(
            str(fixture.get("home_team", "Home"))
        )
        away = escape(
            str(fixture.get("away_team", "Away"))
        )
        competition = escape(
            str(
                fixture.get(
                    "competition",
                    "Unknown Competition"
                )
            )
        )

        if prediction_item:
            prediction = (
                prediction_item.get("prediction")
                or {}
            )
            final_output = (
                prediction.get("final_output")
                or {}
            )

            outcome = escape(
                str(
                    final_output.get(
                        "outcome",
                        prediction.get(
                            "outcome",
                            "N/A"
                        )
                    )
                )
            )

            score = escape(
                str(
                    final_output.get(
                        "predicted_score",
                        prediction.get(
                            "predicted_score",
                            "N/A"
                        )
                    )
                )
            )

            v12 = prediction.get("v1_2") or {}
            synthesis = (
                v12.get(
                    "advantage_synthesis"
                )
                or {}
            )
            evidence = (
                v12.get("evidence_state")
                or {}
            )

            decision = escape(
                str(
                    synthesis.get(
                        "decision",
                        "INSUFFICIENT_EVIDENCE"
                    )
                )
            )

            evidence_count = escape(
                str(
                    evidence.get(
                        "evidence_count",
                        0
                    )
                )
            )

            status_html = "PROCESSED"

            result_html = (
                '<div class="result">'
                f'<span>{outcome}</span>'
                f'<strong>{score}</strong>'
                '</div>'
                '<div class="meta">'
                f'<span>V1.2: {decision}</span>'
                f'<span>{evidence_count}/37 evidence</span>'
                '</div>'
            )
        else:
            status_html = "INSUFFICIENT"

            result_html = (
                '<div class="result pending">'
                '<span>No prediction processed</span>'
                '</div>'
                '<div class="meta">'
                '<span>Held by readiness gate</span>'
                '<span>Evidence incomplete</span>'
                '</div>'
            )

        cards.append(
            '<article class="card">'
            f'<div class="number">{i:02d}</div>'
            '<div class="time">'
            f'<strong>{escape(time_display)}</strong>'
            f'<span>{escape(date_display)}</span>'
            '</div>'
            '<div class="teams">'
            f'<div>{home}</div>'
            '<span>vs</span>'
            f'<div>{away}</div>'
            '</div>'
            f'<div class="competition">{competition}</div>'
            f'<div class="status">{status_html}</div>'
            f'{result_html}'
            '</article>'
        )

    body = "".join(cards)

    if not body:
        body = (
            '<div class="empty">'
            'No matches discovered for today.'
            '</div>'
        )


    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport"
              content="width=device-width, initial-scale=1">
        <title>Football AI</title>

        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                background: #f4f6f8;
                color: #17202a;
                font-family: Arial, Helvetica, sans-serif;
                font-size: 12px;
            }}

            header {{
                background: #111827;
                color: white;
                padding: 12px 16px;
                position: sticky;
                top: 0;
                z-index: 10;
                box-shadow: 0 2px 10px rgba(0,0,0,.12);
            }}

            header h1 {{
                margin: 0;
                font-size: 18px;
                font-weight: 700;
                letter-spacing: .2px;
            }}

            header p {{
                margin: 3px 0 0;
                font-size: 10px;
                opacity: .72;
            }}

            main {{
                width: min(1200px, 100%);
                margin: 0 auto;
                padding: 10px;
            }}

            .grid {{
                display: grid;
                grid-template-columns:
                    repeat(auto-fill, minmax(260px, 1fr));
                gap: 8px;
            }}

            .card {{
                position: relative;
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 9px;
                padding: 9px 10px 8px 34px;
                min-height: 82px;
                box-shadow: 0 1px 3px rgba(0,0,0,.06);
            }}

            .number {{
                position: absolute;
                left: 9px;
                top: 10px;
                font-size: 10px;
                font-weight: 700;
                color: #9ca3af;
            }}

            .teams {{
                display: grid;
                grid-template-columns: 1fr auto 1fr;
                gap: 6px;
                align-items: center;
                font-size: 11px;
                font-weight: 700;
                line-height: 1.2;
            }}

            .teams div:last-child {{
                text-align: right;
            }}

            .teams span {{
                color: #9ca3af;
                font-size: 9px;
                font-weight: 400;
            }}

            .result {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 7px;
                padding-top: 6px;
                border-top: 1px solid #f0f1f3;
            }}

            .result span {{
                font-size: 10px;
                color: #4b5563;
                font-weight: 600;
            }}

            .result strong {{
                font-size: 12px;
                color: #111827;
            }}

            .meta {{
                display: flex;
                justify-content: space-between;
                gap: 8px;
                margin-top: 5px;
                color: #9ca3af;
                font-size: 8px;
                white-space: nowrap;
            }}

            .empty {{
                background: white;
                border-radius: 10px;
                padding: 30px;
                text-align: center;
                color: #6b7280;
            }}

            @media (max-width: 600px) {{
                main {{
                    padding: 7px;
                }}

                .grid {{
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                    gap: 6px;
                }}

                .card {{
                    min-height: 78px;
                    padding: 8px 7px 7px 27px;
                }}

                .number {{
                    left: 7px;
                    top: 9px;
                }}

                .teams {{
                    font-size: 9px;
                    gap: 3px;
                }}

                .result span {{
                    font-size: 8px;
                }}

                .result strong {{
                    font-size: 10px;
                }}

                .meta {{
                    font-size: 7px;
                    gap: 3px;
                }}

                header {{
                    padding: 10px 12px;
                }}

                header h1 {{
                    font-size: 16px;
                }}
            }}
        
        .header-row {{
            display:flex;
            align-items:center;
            justify-content:space-between;
        }}

        .menu-button {{
            border:0;
            background:transparent;
            color:white;
            font-size:26px;
            cursor:pointer;
            padding:2px 8px;
        }}

        .menu {{
            display:none;
            position:absolute;
            right:12px;
            top:52px;
            background:white;
            border:1px solid #e5e7eb;
            border-radius:8px;
            box-shadow:0 4px 14px rgba(0,0,0,.16);
            min-width:190px;
            overflow:hidden;
        }}

        .menu.open {{ display:block; }}

        .menu button {{
            width:100%;
            border:0;
            background:white;
            text-align:left;
            padding:11px 13px;
            font-size:11px;
            cursor:pointer;
        }}

        .menu button:hover {{ background:#f3f4f6; }}

        .intelligence-page {{ display:none; }}

        .intelligence-card {{
            background:white;
            border:1px solid #e5e7eb;
            border-radius:10px;
            padding:14px;
        }}

        .intelligence-card h2 {{
            margin:0;
            font-size:17px;
        }}

        .search-grid {{
            display:grid;
            grid-template-columns:repeat(4,1fr);
            gap:7px;
            margin:12px 0 8px;
        }}

        .search-grid input {{
            width:100%;
            padding:9px;
            border:1px solid #d1d5db;
            border-radius:6px;
            font-size:11px;
        }}

        #analyzeMatch {{
            border:0;
            border-radius:6px;
            padding:9px 14px;
            background:#111827;
            color:white;
            cursor:pointer;
            font-size:11px;
            font-weight:700;
        }}

        #intelligenceStatus {{ margin-top:9px; }}

        .question-card {{
            display:flex;
            gap:9px;
            margin-top:7px;
            padding:9px;
            border:1px solid #e5e7eb;
            border-radius:7px;
        }}

        .question-number {{
            min-width:25px;
            font-weight:700;
            color:#6b7280;
        }}

        .question-content {{ flex:1; }}

        .question-content h4 {{
            margin:0 0 3px;
            font-size:10px;
        }}

        .question-content p {{
            margin:0 0 7px;
            font-size:10px;
        }}

        .question-meta {{
            display:flex;
            flex-wrap:wrap;
            gap:6px;
            font-size:8px;
            color:#6b7280;
        }}

        .answer {{
            margin-top:6px;
            font-size:10px;
        }}

        .detail {{
            margin-top:5px;
            font-size:9px;
            color:#4b5563;
        }}

        @media (max-width:600px) {{
            .search-grid {{
                grid-template-columns:1fr 1fr;
            }}
        }}

        </style>
    </head>

    <body>
        <header>
            <div class="header-row">
                <div>
                    <h1>Football AI</h1>
                    <p>Today's Match Predictions • V1.3 Intelligence Engine</p>
                </div>
                <button class="menu-button" onclick="toggleMenu()">⋮</button>
            </div>

            <div id="menu" class="menu">
                <button onclick="showPage('today')">Today's Matches</button>
                <button onclick="showPage('intelligence')">Match Intelligence</button>
            </div>
        </header>

        <main>
            <section id="today-page">
                <section class="grid">
                    {{body}}
                </section>
            </section>

            <section id="intelligence-page" class="intelligence-page">
                <div class="intelligence-card">
                    <h2>Match Intelligence</h2>

                    <div class="search-grid">
                        <input id="teamA" placeholder="Team A">
                        <input id="teamB" placeholder="Team B">
                        <select id="country" onchange="loadCompetitions()">
                            <option value="">Select Country</option>
                        </select>
                        <select id="competition">
                            <option value="">Select Competition</option>
                        </select>
                        <input id="matchDate" type="date">
                    </div>

                    <button id="analyzeMatch" onclick="analyzeMatch()">
                        Analyze Match
                    </button>

                    <div id="intelligenceStatus"></div>
                    <div id="intelligenceResult"></div>
                </div>
            </section>
        </main>

        <script>
        function toggleMenu() {{
            document.getElementById("menu").classList.toggle("open");
        }}

        function showPage(page) {{
            document.getElementById("today-page").style.display =
                page === "today" ? "block" : "none";

            document.getElementById("intelligence-page").style.display =
                page === "intelligence" ? "block" : "none";

            document.getElementById("menu").classList.remove("open");
        }}

        async function loadCountries() {{
            const response = await fetch("/v13/countries");
            if (!response.ok) return;

            const data = await response.json();
            const country = document.getElementById("country");

            country.innerHTML = '<option value="">Select Country</option>';

            for (const name of data.countries || []) {{
                const option = document.createElement("option");
                option.value = name;
                option.textContent = name;
                country.appendChild(option);
            }}
        }}

        async function loadCompetitions() {{
            const country = document.getElementById("country").value;
            const competition = document.getElementById("competition");

            competition.innerHTML = '<option value="">Select Competition</option>';

            if (!country) return;

            const response = await fetch(
                "/v13/countries/" + encodeURIComponent(country) + "/competitions"
            );

            if (!response.ok) return;

            const data = await response.json();

            for (const item of data.competitions || []) {{
                const option = document.createElement("option");
                option.value = item.name;
                option.textContent = item.name;
                competition.appendChild(option);
            }}
        }}

        loadCountries();

        async function analyzeMatch() {{
            const teamA = document.getElementById("teamA").value.trim();
            const teamB = document.getElementById("teamB").value.trim();
            const competition = document.getElementById("competition").value.trim();
            const date = document.getElementById("matchDate").value || null;
            const status = document.getElementById("intelligenceStatus");
            const result = document.getElementById("intelligenceResult");

            if (!teamA || !teamB || !competition) {{
                status.innerHTML = "Team A, Team B and Competition are required.";
                return;
            }}

            status.innerHTML = "Analyzing fresh V1.3 session...";
            result.innerHTML = "";

            try {{
                const r = await fetch("/v13/match-intelligence", {{
                    method:"POST",
                    headers:{{"Content-Type":"application/json"}},
                    body:JSON.stringify({{
                        team_a:teamA,
                        team_b:teamB,
                        competition:competition,
                        date:date
                    }})
                }});

                const data = await r.json();

                if (!r.ok) {{
                    status.innerHTML = "Analysis failed.";
                    result.innerHTML = "<pre>" +
                        escapeHtml(JSON.stringify(data,null,2)) +
                        "</pre>";
                    return;
                }}

                status.innerHTML = "Fresh V1.3 session completed.";

                const intelligence = data.intelligence || {{}};
                const questions = intelligence.questions || [];

                let html =
                    "<h3>Question-by-Question Intelligence</h3>";

                for (const q of questions) {{
                    html +=
                        '<article class="question-card">' +
                        '<div class="question-number">' +
                        escapeHtml(q.question_id || "") +
                        '</div>' +
                        '<div class="question-content">' +
                        '<h4>' +
                        escapeHtml(q.question || "") +
                        '</h4>' +
                        '<div class="answer"><b>Answer:</b> ' +
                        escapeHtml(String(q.answer ?? "UNKNOWN")) +
                        '</div>' +
                        '<div class="question-meta">' +
                        'Status: ' +
                        escapeHtml(q.answer_status || "UNKNOWN") +
                        ' | Method: ' +
                        escapeHtml(q.resolution_type || q.method || "UNKNOWN") +
                        ' | Confidence: ' +
                        escapeHtml(String(q.confidence ?? "UNKNOWN")) +
                        '</div>' +
                        '</div></article>';
                }}

                result.innerHTML = html;

            }} catch (e) {{
                status.innerHTML =
                    "Could not connect to V1.3 intelligence API.";
                result.innerHTML =
                    "<pre>" + escapeHtml(String(e)) + "</pre>";
            }}
        }}

        function escapeHtml(value) {{
            return String(value)
                .replace(/&/g,"&amp;")
                .replace(/</g,"&lt;")
                .replace(/>/g,"&gt;")
                .replace(/"/g,"&quot;")
                .replace(/'/g,"&#039;");
        }}

        showPage("today");
        </script>
    </body>
    </html>
    """
