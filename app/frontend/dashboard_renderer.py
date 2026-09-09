from datetime import date
from html import escape


def render_dashboard(store):
    results = store.list_results(match_date=date.today().isoformat())

    cards = []

    for i, item in enumerate(results, 1):
        prediction = item.get("prediction") or {}
        final_output = prediction.get("final_output") or {}

        home = escape(str(item.get("home_team", "Home")))
        away = escape(str(item.get("away_team", "Away")))

        outcome = escape(
            str(final_output.get(
                "outcome",
                prediction.get("outcome", "N/A")
            ))
        )

        score = escape(
            str(final_output.get(
                "predicted_score",
                prediction.get("predicted_score", "N/A")
            ))
        )

        v12 = prediction.get("v1_2") or {}
        synthesis = v12.get("advantage_synthesis") or {}
        evidence = v12.get("evidence_state") or {}

        decision = escape(
            str(synthesis.get("decision", "INSUFFICIENT_EVIDENCE"))
        )

        evidence_count = escape(
            str(evidence.get("evidence_count", 0))
        )

        cards.append(
            f"""
            <article class="card">
                <div class="number">{i:02d}</div>
                <div class="teams">
                    <div>{home}</div>
                    <span>vs</span>
                    <div>{away}</div>
                </div>
                <div class="result">
                    <span>{outcome}</span>
                    <strong>{score}</strong>
                </div>
                <div class="meta">
                    <span>V1.2: {decision}</span>
                    <span>{evidence_count}/37 evidence</span>
                </div>
            </article>
            """
        )

    body = "".join(cards)

    if not body:
        body = """
        <div class="empty">
            No predictions available for today.
        </div>
        """

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
