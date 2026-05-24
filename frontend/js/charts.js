const CHART_DEFAULTS = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: { labels: { color: "#94a3b8", font: { size: 12 } } },
    tooltip: { mode: "index", intersect: false },
  },
  scales: {
    x: {
      ticks: { color: "#64748b", maxTicksLimit: 8 },
      grid: { color: "rgba(255,255,255,0.05)" },
    },
    y: {
      ticks: { color: "#64748b" },
      grid: { color: "rgba(255,255,255,0.05)" },
    },
  },
};


function renderAqiChart(canvasId, readings) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const labels = readings.map((r) =>
    new Date(r.recorded_at).toLocaleString("en-GB", {
      month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
    })
  );
  const aqiData  = readings.map((r) => r.aqi);
  const pm25Data = readings.map((r) => r.pm25);

  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "AQI",
          data: aqiData,
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59,130,246,0.15)",
          tension: 0.3,
          fill: true,
          pointRadius: 3,
        },
        {
          label: "PM2.5 (µg/m³)",
          data: pm25Data,
          borderColor: "#f59e0b",
          backgroundColor: "transparent",
          tension: 0.3,
          pointRadius: 2,
          borderDash: [4, 4],
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: {
        ...CHART_DEFAULTS.plugins,
        title: { display: true, text: "Air Quality Index (48h)", color: "#e2e8f0" },
      },
    },
  });
}


function renderWeatherChart(canvasId, readings) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const labels = readings.map((r) =>
    new Date(r.recorded_at).toLocaleString("en-GB", {
      month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
    })
  );

  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Temperature (°C)",
          data: readings.map((r) => r.temperature),
          borderColor: "#ef4444",
          backgroundColor: "rgba(239,68,68,0.1)",
          tension: 0.3,
          fill: true,
          pointRadius: 2,
          yAxisID: "yTemp",
        },
        {
          label: "Humidity (%)",
          data: readings.map((r) => r.humidity),
          borderColor: "#06b6d4",
          backgroundColor: "transparent",
          tension: 0.3,
          borderDash: [4, 4],
          pointRadius: 2,
          yAxisID: "yHumid",
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: {
        ...CHART_DEFAULTS.plugins,
        title: { display: true, text: "Temperature & Humidity (48h)", color: "#e2e8f0" },
      },
      scales: {
        x: CHART_DEFAULTS.scales.x,
        yTemp: {
          type: "linear",
          position: "left",
          ticks: { color: "#ef4444" },
          grid: { color: "rgba(255,255,255,0.05)" },
        },
        yHumid: {
          type: "linear",
          position: "right",
          min: 0, max: 100,
          ticks: { color: "#06b6d4" },
          grid: { drawOnChartArea: false },
        },
      },
    },
  });
}


function renderWindChart(canvasId, readings) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const labels = readings.map((r) =>
    new Date(r.recorded_at).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })
  );

  new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Wind Speed (m/s)",
        data: readings.map((r) => r.wind_speed),
        backgroundColor: "rgba(99,102,241,0.6)",
        borderColor: "#6366f1",
        borderWidth: 1,
      }],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: {
        ...CHART_DEFAULTS.plugins,
        title: { display: true, text: "Wind Speed (48h)", color: "#e2e8f0" },
      },
    },
  });
}
