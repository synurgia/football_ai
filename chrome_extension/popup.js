const API_URL = "http://127.0.0.1:8000/daily/today";

async function loadPredictions() {
  const container = document.getElementById("predictions");

  try {
    const response = await fetch(API_URL);

    if (!response.ok) {
      throw new Error(`Backend returned HTTP ${response.status}`);
    }

    const data = await response.json();
    const predictions = data.predictions || [];

    if (!predictions.length) {
      container.innerHTML =
        '<div class="empty">No predictions available for today.</div>';
      return;
    }

    container.innerHTML = predictions.map((item) => {
      const prediction = item.prediction || {};
      const finalOutput = prediction.final_output || {};
      const home = escapeHtml(item.home_team || "Home");
      const away = escapeHtml(item.away_team || "Away");
      const outcome = escapeHtml(
        finalOutput.outcome || prediction.outcome || "N/A"
      );
      const score = escapeHtml(
        finalOutput.predicted_score ||
        prediction.predicted_score ||
        "N/A"
      );

      return `
        <article class="card">
          <div class="teams">
            <div>${home}</div>
            <div class="vs">vs</div>
            <div>${away}</div>
          </div>
          <div class="outcome">${outcome}</div>
          <div class="score">${score}</div>
        </article>
      `;
    }).join("");

  } catch (error) {
    container.innerHTML = `
      <div class="error">
        Unable to connect to Football AI backend.<br>
        ${escapeHtml(error.message)}
      </div>
    `;
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

loadPredictions();
