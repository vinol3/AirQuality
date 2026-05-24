const API = "/api/v1";

async function loadDashboard() {
  try {
    const [rankingsRes] = await Promise.all([
      fetch(`${API}/rankings/?limit=10`),
    ]);

    if (!rankingsRes.ok) throw new Error("Failed to fetch rankings");
    const rankings = await rankingsRes.json();

    renderStats(rankings);
    renderQuickRankings(rankings);

    if (typeof renderCityMarkers === "function") {
      renderCityMarkers(rankings);
    }
  } catch (err) {
    document.getElementById("quick-rankings").innerHTML =
      `<div class="error">Could not load data: ${err.message}</div>`;
  }
}

function renderStats(rankings) {
  const withData = rankings.filter((r) => r.latest_aqi !== null);
  if (!withData.length) return;

  const best  = withData[0];
  const worst = withData[withData.length - 1];
  const avg   = Math.round(withData.reduce((s, r) => s + r.latest_aqi, 0) / withData.length);

  document.getElementById("stat-cities").textContent  = rankings.length;
  document.getElementById("stat-best").textContent    = `${best.city.name} (${best.latest_aqi})`;
  document.getElementById("stat-worst").textContent   = `${worst.city.name} (${worst.latest_aqi})`;
  document.getElementById("stat-avg").textContent     = avg;
  document.getElementById("stat-updated").textContent = new Date().toLocaleTimeString();
}

function renderQuickRankings(rankings) {
  const tbody = document.getElementById("quick-rankings");
  if (!rankings.length) {
    tbody.innerHTML = '<tr><td colspan="4" class="loading">No data yet — ingestion running…</td></tr>';
    return;
  }

  tbody.innerHTML = rankings.slice(0, 5).map((r) => {
    const aqi = r.latest_aqi ?? "—";
    const color = r.aqi_color;
    return `
      <tr>
        <td>${r.rank}</td>
        <td><a href="city.html?id=${r.city.id}">${r.city.name}</a></td>
        <td>${r.city.country}</td>
        <td>
          <span class="aqi-badge" style="background:${color}">${aqi}</span>
          <span style="margin-left:.5rem;font-size:.8rem;color:var(--muted)">${r.aqi_category}</span>
        </td>
      </tr>
    `;
  }).join("");
}

document.addEventListener("DOMContentLoaded", loadDashboard);
