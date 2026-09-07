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
        outcome = escape(str(final_output.get("outcome", prediction.get("outcome", "N/A"))))
        score = escape(str(final_output.get("predicted_score", prediction.get("predicted_score", "N/A"))))

        cards.append(
            f"""
            <div class="card">
                <div class="game">GAME {i}</div>
                <h2>{home} vs {away}</h2>
                <p><strong>Outcome:</strong> {outcome}</p>
                <p><strong>Predicted Score:</strong> {score}</p>
            </div>
            """
        )

    body = "".join(cards)

    if not body:
        body = '<div class="card"><p>No predictions available for today.</p></div>'

    return f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Football AI Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                background: #eef1f5;
                color: #17202a;
            }}
            header {{
                background: #111827;
                color: white;
                padding: 20px;
            }}
            main {{
                max-width: 800px;
                margin: 20px auto;
                padding: 10px;
            }}
            .card {{
                background: white;
                margin: 20px 0;
                padding: 20px;
                border-radius: 12px;
            }}
            .game {{
                font-weight: bold;
                color: #555;
            }}
        </style>
    </head>
    <body>
        <header>
            <h1>Football AI</h1>
            <p>Daily Match Prediction Dashboard</p>
        </header>
        <main>
            {body}
        </main>
    </body>
    </html>
    """
