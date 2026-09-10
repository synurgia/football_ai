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
        </style>
    </head>

    <body>
        <header>
            <h1>Football AI</h1>
            <p>Today's Match Predictions • V1.2 Evidence Engine</p>
        </header>

        <main>
            <section class="grid">
                {body}
            </section>
        </main>
    </body>
    </html>
    """
