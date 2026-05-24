let mapInstance = null;

function initMap(elementId = "map") {
  if (mapInstance) return mapInstance;

  mapInstance = L.map(elementId, {
    center: [50.5, 10.0],
    zoom: 4,
    zoomControl: true,
  });

  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    attribution: '© <a href="https://carto.com/">CARTO</a>',
    maxZoom: 18,
  }).addTo(mapInstance);

  return mapInstance;
}

function aqiColor(aqi) {
  if (aqi === null || aqi === undefined) return "#9e9e9e";
  if (aqi <= 50)  return "#4caf50";
  if (aqi <= 100) return "#ffeb3b";
  if (aqi <= 150) return "#ff9800";
  if (aqi <= 200) return "#f44336";
  if (aqi <= 300) return "#9c27b0";
  return "#7b1fa2";
}

function aqiCategory(aqi) {
  if (aqi === null || aqi === undefined) return "Unknown";
  if (aqi <= 50)  return "Good";
  if (aqi <= 100) return "Moderate";
  if (aqi <= 150) return "Unhealthy for Sensitive Groups";
  if (aqi <= 200) return "Unhealthy";
  if (aqi <= 300) return "Very Unhealthy";
  return "Hazardous";
}

function renderCityMarkers(rankings) {
  if (!mapInstance) return;

  rankings.forEach((r) => {
    const { city, latest_aqi, aqi_category } = r;
    const color = aqiColor(latest_aqi);
    const label = latest_aqi !== null ? String(latest_aqi) : "?";

    const marker = L.circleMarker([city.latitude, city.longitude], {
      radius: 18,
      fillColor: color,
      color: "#fff",
      weight: 2,
      fillOpacity: 0.9,
    }).addTo(mapInstance);

    marker.bindPopup(`
      <div style="min-width:160px;font-family:system-ui">
        <strong style="font-size:1rem">${city.name}</strong>
        <div style="color:#666;font-size:.8rem">${city.country}</div>
        <div style="margin:.5rem 0">
          <span style="background:${color};color:#000;padding:.15em .5em;border-radius:4px;font-weight:700">
            AQI ${label}
          </span>
        </div>
        <div style="font-size:.8rem;color:#444">${aqi_category}</div>
        <div style="margin-top:.5rem">
          <a href="city.html?id=${city.id}" style="color:#3b82f6;font-size:.85rem">View details →</a>
        </div>
      </div>
    `);

    const divIcon = L.divIcon({
      className: "",
      html: `<div style="
        position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
        font-size:11px;font-weight:700;color:#000;white-space:nowrap;
        pointer-events:none;
      ">${label}</div>`,
      iconSize: [36, 36],
      iconAnchor: [18, 18],
    });
    L.marker([city.latitude, city.longitude], { icon: divIcon }).addTo(mapInstance);
  });
}
