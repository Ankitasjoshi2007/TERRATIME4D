const discoveryStyle = document.createElement("style");
discoveryStyle.textContent = `
#planetary-discovery {
  margin:35px auto;padding:24px;max-width:1450px;
  color:#e5f5ff;background:#071827;border:1px solid #24516a;
  border-radius:14px;font-family:inherit;
}
#planetary-discovery h2 {color:#63dcff;letter-spacing:2px;font-size:22px}
#planetary-discovery p {color:#9bb6c9;line-height:1.6;font-size:13px}
#planetary-discovery .pd-controls {
  display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:20px 0
}
#planetary-discovery label {display:flex;flex-direction:column;gap:7px;color:#91b4ca;font-size:11px}
#planetary-discovery input,#planetary-discovery select,#planetary-discovery button {
  background:#102b40;color:#e5f5ff;border:1px solid #315b73;
  border-radius:6px;padding:11px;min-width:0
}
#planetary-discovery button {cursor:pointer}
#planetary-discovery button:hover {border-color:#5bdcff}
#planetary-discovery .pd-map-grid {
  display:grid;grid-template-columns:1fr 1fr;gap:16px
}
#planetary-discovery .pd-panel {
  background:#0b2033;border:1px solid #24516a;border-radius:9px;padding:14px;min-width:0
}
#planetary-discovery .pd-panel h3 {font-size:13px;color:#62dcff;margin:0 0 12px}
#planetary-discovery canvas {width:100%;height:auto;display:block;cursor:crosshair;background:#06111c}
#planetary-discovery .pd-stats {
  display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:18px 0
}
#planetary-discovery .pd-stat {
  padding:14px;background:#10283b;border:1px solid #254a61;border-radius:8px
}
#planetary-discovery .pd-stat small {display:block;color:#91b4ca;font-size:10px}
#planetary-discovery .pd-stat strong {display:block;color:#e6f8ff;font-size:19px;margin-top:6px}
#planetary-discovery .pd-results {width:100%;border-collapse:collapse;font-size:12px}
#planetary-discovery .pd-results th,#planetary-discovery .pd-results td {
  text-align:left;padding:10px;border-bottom:1px solid #24445a
}
#planetary-discovery .pd-results th {color:#63dcff}
#planetary-discovery .pd-note {
  border-left:3px solid #e5b45b;padding:10px 13px;background:#18283a;
  color:#c8d5df;font-size:11px;line-height:1.6;margin-top:15px
}
#planetary-discovery .pd-status {color:#63dcff;font-size:12px;margin:12px 0}
@media(max-width:760px) {
  #planetary-discovery .pd-controls {grid-template-columns:1fr 1fr}
  #planetary-discovery .pd-map-grid {grid-template-columns:1fr}
  #planetary-discovery .pd-stats {grid-template-columns:1fr 1fr}
  #planetary-discovery {padding:13px}
}
`;
document.head.appendChild(discoveryStyle);

const discovery = document.createElement("section");
discovery.id = "planetary-discovery";
discovery.innerHTML = `
  <div style="color:#63dcff;font-size:10px;letter-spacing:3px">INTERACTIVE SCIENTIFIC EXPLORATION</div>
  <h2>PLANETARY ANALOG DISCOVERY</h2>
    <p>EARTH IS THE INPUT. Choose a named Earth location. TERRATIME 4D will search the Moon and Mars grids for terrain with similar characteristics.</p>

  <div class="pd-controls">
    <label>Choose Earth location
      <input id="pd-place-search" type="text" placeholder="Search Earth locations..." autocomplete="off">
      <select id="pd-place" size="6">
        <option value="">Loading Earth candidates...</option>
      </select>
    </label>

    <input id="pd-lat" type="hidden" value="">
    <input id="pd-lon" type="hidden" value="">
    <select id="pd-planet" style="display:none"><option value="Moon">Moon</option></select>

    <label>Find planetary matches
      <button id="pd-analyze" disabled>FIND MOON & MARS MATCHES</button>
    </label>
  </div>

  <div class="pd-map-grid">
    <div class="pd-panel">
      <h3 id="pd-target-title">GLOBAL MOON ELEVATION Ã¢â‚¬â€ SELECT A LOCATION</h3>
      <canvas id="pd-target-map" width="720" height="360"></canvas>
      <p>Click anywhere on this map to select a planetary coordinate. Map is a 1Ã‚Â° browsing grid.</p>
    </div>
    <div class="pd-panel">
      <h3>EARTH REFERENCE DISTRIBUTION Ã¢â‚¬â€ 648 RECORDS</h3>
      <canvas id="pd-earth-map" width="720" height="360"></canvas>
      <p>Dots represent available Earth reference tile coordinates. They do not represent continuous DEM coverage.</p>
    </div>
  </div>

  <div class="pd-stats" id="pd-stats">
    <div class="pd-stat"><small>MEAN ELEVATION</small><strong id="pd-elevation">Ã¢â‚¬â€</strong></div>
    <div class="pd-stat"><small>MEAN SLOPE</small><strong id="pd-slope">Ã¢â‚¬â€</strong></div>
    <div class="pd-stat"><small>ROUGHNESS (~11 KM)</small><strong id="pd-roughness">Ã¢â‚¬â€</strong></div>
  </div>

  <div class="pd-panel">
    <h3>RANKED MOON MATCHES</h3>
    <div style="overflow-x:auto">
      <table class="pd-results">
        <thead><tr><th>Rank</th><th>Grid location</th><th>Coordinates</th><th>Slope</th><th>Roughness (~11 km)</th><th>Similarity</th></tr></thead>
        <tbody id="pd-moon-results"><tr><td colspan="6">Choose an Earth location and run the analysis.</td></tr></tbody>
      </table>
    </div>
  </div>
  <div class="pd-panel" style="margin-top:14px">
    <h3>RANKED MARS MATCHES</h3>
    <div style="overflow-x:auto">
      <table class="pd-results">
        <thead><tr><th>Rank</th><th>Grid location</th><th>Coordinates</th><th>Slope</th><th>Roughness (~11 km)</th><th>Similarity</th></tr></thead>
        <tbody id="pd-mars-results"><tr><td colspan="6">Waiting for Earth input.</td></tr></tbody>
      </table>
    </div>
  </div>
  <div class="pd-note">
  <div class="pd-note">
    SCIENTIFIC LIMITATION: Earth slope and roughness measurements use different native spatial scales from the planetary grids. The displayed slope similarity index is a preliminary screening measure, not a probability or validated scientific equivalence. Roughness is displayed separately and excluded from ranking because the spatial scales differ. Elevation is excluded because planetary elevation datums differ. Earth results are limited to the 648 available reference tiles.
  </div>
`;
const existingComparison = document.getElementById("planetary-comparison");
const existingApp = document.getElementById("app");

if (existingApp) existingApp.before(discovery);
else if (existingComparison) existingComparison.before(discovery);
else document.body.appendChild(discovery);


const comparisonFooter = existingComparison?.querySelector(".pc-footer");
if (comparisonFooter) {
  comparisonFooter.textContent =
    "COMPARISON COMPLETE Ã‚Â· CONTINUE SCROLLING BELOW FOR PLANETARY ANALOG DISCOVERY";
}

function pdParseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  return lines.map(line => {
    const cells = [];
    let value = "", quoted = false;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      if (c === '"' && line[i + 1] === '"' && quoted) { value += '"'; i++; }
      else if (c === '"') quoted = !quoted;
      else if (c === "," && !quoted) { cells.push(value); value = ""; }
      else value += c;
    }
    cells.push(value);
    return cells;
  });
}

function pdRecords(csv) {
  const rows = pdParseCSV(csv);
  const headers = rows.shift().map(h => String(h).trim().replace(/^\uFEFF/, ""));
  return rows.map(row => Object.fromEntries(headers.map((h,i)=>[h,row[i]])));
}

let pdData = null;
let pdEarth = [];
let pdTarget = null;

function pdRegionStats(planet, lat, lon) {
  const fields = ["elevation_km", "slope_degrees", "roughness_11km_km"];
  const sums = { elevation_km: 0, slope_degrees: 0, roughness_11km_km: 0 };
  let totalWeight = 0;
  let cells = 0;
  const visited = new Set();

  const centerRow = Math.max(0, Math.min(179, Math.floor(90 - lat)));
  const centerCol = ((Math.floor(lon) + 360) % 360);

  for (let dr = -1; dr <= 1; dr++) {
    for (let dc = -1; dc <= 1; dc++) {
      const row = centerRow + dr;
      const col = (centerCol + dc + 360) % 360;

      if (row < 0 || row >= 180) continue;

      const key = `${row},${col}`;
      if (visited.has(key)) continue;
      visited.add(key);

      if (!planet.valid || Number(planet.valid[row][col]) <= 0) continue;

      const values = {};
      let usable = true;

      for (const field of fields) {
        values[field] = Number(planet[field][row][col]);
        if (!Number.isFinite(values[field])) usable = false;
      }

      if (!usable) continue;

      // Approximate area weighting for latitude-longitude grid cells.
      const cellLat = 89.5 - row;
      const weight = Math.max(0.000001, Math.cos(cellLat * Math.PI / 180));

      for (const field of fields) {
        sums[field] += values[field] * weight;
      }

      totalWeight += weight;
      cells++;
    }
  }

  if (!cells || totalWeight <= 0) return null;

  return {
    elevation: sums.elevation_km / totalWeight,
    slope: sums.slope_degrees / totalWeight,
    roughness: sums.roughness_11km_km / totalWeight,
    cells
  };
}

function pdColor(value, min, max) {
  if (!Number.isFinite(value)) return "rgb(8,22,36)";

  const range = Math.max(max - min, 0.000001);
  const t = Math.max(0, Math.min(1, (value - min) / range));

  const stops = [
    [8, 24, 48],
    [20, 75, 115],
    [35, 145, 165],
    [130, 180, 130],
    [220, 190, 110],
    [245, 230, 190]
  ];

  const position = t * (stops.length - 1);
  const index = Math.min(Math.floor(position), stops.length - 2);
  const fraction = position - index;

  const a = stops[index];
  const b = stops[index + 1];

  const r = Math.round(a[0] + (b[0] - a[0]) * fraction);
  const g = Math.round(a[1] + (b[1] - a[1]) * fraction);
  const blue = Math.round(a[2] + (b[2] - a[2]) * fraction);

  return `rgb(${r},${g},${blue})`;
}
function pdDrawPlanetMap() {
  const canvas = document.getElementById("pd-target-map");
  if (!canvas || !pdData || !pdData.planets) return;

  const selector = document.getElementById("pd-planet");
  const name = selector ? selector.value : "Moon";
  const planet = pdData.planets[name];

  if (!planet || !planet.elevation_km || !planet.valid) {
    console.error("Planetary map data unavailable:", name);
    return;
  }

  canvas.width = 720;
  canvas.height = 360;
  canvas.style.width = "100%";
  canvas.style.height = "auto";
  canvas.style.display = "block";

  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const width = 360;
  const height = 180;
  let min = Infinity;
  let max = -Infinity;

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (Number(planet.valid[y][x]) <= 0) continue;
      const v = Number(planet.elevation_km[y][x]);
      if (Number.isFinite(v)) {
        min = Math.min(min, v);
        max = Math.max(max, v);
      }
    }
  }

  if (!Number.isFinite(min) || !Number.isFinite(max)) {
    ctx.fillStyle = "#081624";
    ctx.fillRect(0, 0, 720, 360);
    ctx.fillStyle = "#ffffff";
    ctx.fillText("No valid elevation values", 20, 30);
    return;
  }

  const image = ctx.createImageData(width, height);

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const sourceCol = (x + 180) % 360;
      const valid = Number(planet.valid[y][sourceCol]) > 0;
      const value = Number(planet.elevation_km[y][sourceCol]);
      const k = (y * width + x) * 4;

      if (!valid || !Number.isFinite(value)) {
        image.data[k] = 5;
        image.data[k + 1] = 17;
        image.data[k + 2] = 29;
        image.data[k + 3] = 255;
        continue;
      }

      const t = max === min ? 0.5 : Math.max(0, Math.min(1, (value - min) / (max - min)));

      let r, g, b;
      if (t < 0.5) {
        const q = t * 2;
        r = 12 + q * 105;
        g = 39 + q * 105;
        b = 105 + q * 65;
      } else {
        const q = (t - 0.5) * 2;
        r = 117 + q * 125;
        g = 144 + q * 90;
        b = 170 + q * 65;
      }

      image.data[k] = Math.round(r);
      image.data[k + 1] = Math.round(g);
      image.data[k + 2] = Math.round(b);
      image.data[k + 3] = 255;
    }
  }

  const temp = document.createElement("canvas");
  temp.width = width;
  temp.height = height;
  temp.getContext("2d").putImageData(image, 0, 0);

  ctx.fillStyle = "#06111c";
  ctx.fillRect(0, 0, 720, 360);
  ctx.imageSmoothingEnabled = true;
  ctx.drawImage(temp, 0, 0, 720, 360);

  ctx.strokeStyle = "rgba(130,190,220,0.25)";
  ctx.lineWidth = 1;
  for (let x = 0; x <= 720; x += 120) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, 360);
    ctx.stroke();
  }
  for (let y = 0; y <= 360; y += 90) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(720, y);
    ctx.stroke();
  }

  if (pdTarget && Number.isFinite(pdTarget.lat) && Number.isFinite(pdTarget.lon)) {
    const x = (pdTarget.lon + 180) / 360 * 720;
    const y = (90 - pdTarget.lat) / 180 * 360;
    ctx.beginPath();
    ctx.arc(x, y, 8, 0, Math.PI * 2);
    ctx.fillStyle = "#ffe36b";
    ctx.fill();
    ctx.strokeStyle = "#071522";
    ctx.lineWidth = 3;
    ctx.stroke();
  }

  const title = document.getElementById("pd-target-title");
  if (title) title.textContent = "GLOBAL " + name.toUpperCase() + " ELEVATION";
}
function pdDrawEarthMap() {
  const canvas = document.getElementById("pd-earth-map");
  if (!canvas) return;

  canvas.width = 720;
  canvas.height = 360;
  canvas.style.width = "100%";
  canvas.style.height = "auto";
  canvas.style.display = "block";

  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  ctx.fillStyle = "#081624";
  ctx.fillRect(0, 0, 720, 360);

  ctx.strokeStyle = "rgba(95,160,195,0.35)";
  ctx.lineWidth = 1;

  for (let x = 0; x <= 720; x += 60) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, 360);
    ctx.stroke();
  }

  for (let y = 0; y <= 360; y += 45) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(720, y);
    ctx.stroke();
  }

  // Latitude reference lines and labels.
  ctx.fillStyle = "#91b7cc";
  ctx.font = "11px Arial";
  [-60, -30, 0, 30, 60].forEach(lat => {
    const y = (90 - lat) / 180 * 360;
    ctx.fillText(lat + "°", 5, y - 4);
  });

  let plotted = 0;

  for (const point of pdEarth) {
    if (!Number.isFinite(point.lat) || !Number.isFinite(point.lon)) continue;

    const x = (point.lon + 180) / 360 * 720;
    const y = (90 - point.lat) / 180 * 360;

    ctx.beginPath();
    ctx.arc(x, y, 3.2, 0, Math.PI * 2);
    ctx.fillStyle = "#55d7ff";
    ctx.fill();
    plotted++;
  }

  ctx.fillStyle = "#d8f4ff";
  ctx.font = "bold 13px Arial";
  ctx.fillText("EARTH TERRAIN LOCATIONS: " + plotted, 15, 22);

  if (pdTarget) {
    const x = (pdTarget.lon + 180) / 360 * 720;
    const y = (90 - pdTarget.lat) / 180 * 360;
    ctx.beginPath();
    ctx.arc(x, y, 8, 0, Math.PI * 2);
    ctx.fillStyle = "#ffe36b";
    ctx.fill();
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 2;
    ctx.stroke();
  }
}
let pdCandidates = [];

function pdAnalyze() {
  if (!pdData || !pdCandidates.length) return;

  const selected = document.getElementById("pd-place").value;
  if (selected === "") {
    document.getElementById("pd-status").textContent =
      "Please select an Earth location first.";
    return;
  }

  const earth = pdCandidates[Number(selected)];
  if (!earth) return;

  document.getElementById("pd-lat").value = earth.latitude;
  document.getElementById("pd-lon").value = earth.longitude;

  document.getElementById("pd-elevation").textContent =
    (earth.elevation / 1000).toFixed(3) + " km";
  document.getElementById("pd-slope").textContent =
    earth.slope.toFixed(2) + "Â°";
  document.getElementById("pd-roughness").textContent =
    earth.roughness.toFixed(2) + " m";

  function rankPlanet(planetName) {
    const grid = pdData.planets[planetName];
    const matches = [];

    for (let row = 0; row < 180; row++) {
      for (let col = 0; col < 360; col++) {
        if (!grid.valid[row][col]) continue;

        const slope = Number(grid.slope_degrees[row][col]);
        if (!Number.isFinite(slope)) continue;

        const difference = Math.abs(slope - earth.slope);
        const score = 100 / (1 + difference / 5);

        const roughness = Number(grid.roughness_11km_km[row][col]);
        const latitude = 89.5 - row;
        const longitude = col - 179.5;

        matches.push({
          latitude,
          longitude,
          slope,
          roughness,
          score
        });
      }
    }

    matches.sort((a, b) => b.score - a.score);
    return matches.slice(0, 10);
  }

  function renderRows(id, matches) {
    document.getElementById(id).innerHTML = matches.map((r, i) => `
      <tr>
        <td>${i + 1}</td>
        <td>Grid cell ${i + 1}</td>
        <td>${r.latitude.toFixed(1)}Â°, ${r.longitude.toFixed(1)}Â°</td>
        <td>${r.slope.toFixed(2)}Â°</td>
        <td>${Number.isFinite(r.roughness) ? (r.roughness * 1000).toFixed(1) + " m" : "N/A"}</td>
        <td>${r.score.toFixed(1)}/100</td>
      </tr>
    `).join("");
  }

  const moonMatches = rankPlanet("Moon");
  const marsMatches = rankPlanet("Mars");

  renderRows("pd-moon-results", moonMatches);
  renderRows("pd-mars-results", marsMatches);

  document.getElementById("pd-status").textContent =
    `Earth input: ${earth.name} (${earth.latitude.toFixed(2)}Â°, ${earth.longitude.toFixed(2)}Â°). ` +
    `Compared its slope against valid 1Â° grid cells on the Moon and Mars. ` +
    `Showing the top 10 matches for each planetary body.`;

  pdTarget = { lat: earth.latitude, lon: earth.longitude };
}


function pdBuildPlaceCatalog() {
  if (!pdData || !pdData.planets) return;

  for (const name of ["Moon", "Mars"]) {
    const grid = pdData.planets[name];
    const places = [];

    // Include named observation locations from local repository data.
    if (name === "Moon") {
      places.push({
        label: "Diviner North Polar sample location",
        lat: 75.905227661,
        lon: -45.015949249
      });
      places.push({
        label: "Diviner South Polar sample location",
        lat: -75.905227661,
        lon: -45.015949249
      });
    }

    if (name === "Mars") {
      places.push({
        label: "THEMIS IA7300002EQR observation footprint",
        lat: -36.4449245,
        lon: 89.9485855
      });
    }

    // Add every valid cell from the complete local 1-degree planetary grid.
    for (let row = 0; row < grid.height; row++) {
      for (let col = 0; col < grid.width; col++) {
        if (!grid.valid[row] || !grid.valid[row][col]) continue;

        const lat = 89.5 - row;
        const lon = ((col + 180) % 360) - 179.5;

        const region = lat >= 60 ? "North Polar Region" :
                       lat >= 20 ? "Northern Region" :
                       lat > -20 ? "Equatorial Region" :
                       lat > -60 ? "Southern Region" :
                       "South Polar Region";
        const sector = Math.floor((lon + 180) / 30) + 1;

        places.push({
          label: region + " | Sector " + String(sector).padStart(2, "0") +
                 " | Grid Cell " + String(row + 1).padStart(3, "0") +
                 "-" + String(col + 1).padStart(3, "0"),
          lat,
          lon
        });
      }
    }

    pdPlaceCatalog[name] = places;
  }
}

function pdPopulatePlaces() {
  if (!pdData) return;

  const planet = document.getElementById("pd-planet").value;
  const placeSelect = document.getElementById("pd-place");
  const search = document.getElementById("pd-place-search");
  const analyzeButton = document.getElementById("pd-analyze");
  const places = pdPlaceCatalog[planet] || [];

  placeSelect.innerHTML = '<option value="">Select a location</option>';
  for (let i = 0; i < Math.min(places.length, 300); i++) {
    const option = document.createElement("option");
    option.value = String(i);
    option.textContent = places[i].label;
    placeSelect.appendChild(option);
  }

  search.value = "";
  document.getElementById("pd-lat").value = "";
  document.getElementById("pd-lon").value = "";
  analyzeButton.disabled = true;
  document.getElementById("pd-status").textContent =
    places.length.toLocaleString() + " local " + planet +
    " locations available. Search coordinates to find a location.";
}

document.getElementById("pd-place-search").addEventListener("input", () => {
  const planet = document.getElementById("pd-planet").value;
  const places = pdPlaceCatalog[planet] || [];
  const query = document.getElementById("pd-place-search").value.trim().toLowerCase();
  const select = document.getElementById("pd-place");
  select.innerHTML = '<option value="">Select a location</option>';

  if (!query) {
    for (let i = 0; i < Math.min(places.length, 300); i++) {
      const option = document.createElement("option");
      option.value = String(i);
      option.textContent = places[i].label;
      select.appendChild(option);
    }
    return;
  }

  let matches = 0;
  for (let i = 0; i < places.length && matches < 300; i++) {
    if (places[i].label.toLowerCase().includes(query) ||
        String(places[i].lat).includes(query) ||
        String(places[i].lon).includes(query)) {
      const option = document.createElement("option");
      option.value = String(i);
      option.textContent = places[i].label;
      select.appendChild(option);
      matches++;
    }
  }

  document.getElementById("pd-status").textContent =
    matches + " matching locations shown.";
});

document.getElementById("pd-place").addEventListener("change", () => {
  const planet = document.getElementById("pd-planet").value;
  const selected = document.getElementById("pd-place").value;
  const analyzeButton = document.getElementById("pd-analyze");

  if (selected === "") {
    document.getElementById("pd-lat").value = "";
    document.getElementById("pd-lon").value = "";
    analyzeButton.disabled = true;
    return;
  }

  const place = pdPlaceCatalog[planet][Number(selected)];

  if (!place) return;

  document.getElementById("pd-lat").value = place.lat;
  document.getElementById("pd-lon").value = place.lon;
  analyzeButton.disabled = false;

  document.getElementById("pd-status").textContent =
    "Selected " + place.label +
    ". Coordinates loaded from the local planetary catalogue. Press ANALYZE LOCATION.";
});

pdPopulatePlaces();
document.getElementById("pd-target-map").addEventListener("click",e=>{
  const rect=e.currentTarget.getBoundingClientRect();
  const x=(e.clientX-rect.left)/rect.width;
  const y=(e.clientY-rect.top)/rect.height;
  const lon=x*360-180,lat=90-y*180;
  document.getElementById("pd-lat").value=lat.toFixed(2);
  document.getElementById("pd-lon").value=lon.toFixed(2);
  pdAnalyze();
});
const pdAnalyzeControl = document.getElementById("pd-analyze"); if (pdAnalyzeControl) pdAnalyzeControl.addEventListener("click",pdAnalyze);
const pdPlanetControl = document.getElementById("pd-planet");
if (pdPlanetControl) {
  pdPlanetControl.addEventListener("change",()=>{
    pdDrawPlanetMap();
    if (typeof pdPopulatePlaces === "function") pdPopulatePlaces();
  });
}

(async function loadEarthDiscoveryData() {
  const status = document.getElementById("pd-status");
  const search = document.getElementById("pd-place-search");
  const select = document.getElementById("pd-place");

  try {
    if (status) status.textContent = "Loading local Earth terrain catalogue...";

    const [gridResponse, earthResponse, candidateResponse] =
      await Promise.all([
        fetch("/data/planetary/planetary_grids.json"),
        fetch("/data/earth/global_advanced_terrain_summary.csv"),
        fetch("/data/integrated_candidate_evidence.csv")
      ]);

    if (!gridResponse.ok) throw Error("Planetary grid file unavailable: " + gridResponse.status);
    if (!earthResponse.ok) throw Error("Earth terrain CSV unavailable: " + earthResponse.status);
    if (!candidateResponse.ok) throw Error("Earth evidence CSV unavailable: " + candidateResponse.status);

    pdData = await gridResponse.json();

    const earthCSV = await earthResponse.text();
    const candidateCSV = await candidateResponse.text();

    const earthRows = pdRecords(earthCSV);
    const detailedRows = pdRecords(candidateCSV);

    function numberFrom(row, names) {
      for (const name of names) {
        if (row[name] !== undefined && row[name] !== "") {
          const n = Number(row[name]);
          if (Number.isFinite(n)) return n;
        }
      }
      return NaN;
    }

    function coordinatesFrom(row) {
      const location = String(row.location || row.raster_file || row.candidate || "");
      let lat = numberFrom(row, ["latitude", "lat", "center_latitude"]);
      let lon = numberFrom(row, ["longitude", "lon", "center_longitude"]);

      // Example: copernicus_dsm_cog_30_n02_00_e012_00_dem
      const match = location.match(/_(n|s)(\d{2})_00_(e|w)(\d{3})_00(?:_|$)/i);

      if (match) {
        lat = Number(match[2]) * (match[1].toLowerCase() === "s" ? -1 : 1);
        lon = Number(match[4]) * (match[3].toLowerCase() === "w" ? -1 : 1);
      }

      return { lat, lon, location };
    }
    pdEarth = [];

    const tileCandidates = earthRows.map((row, index) => {
      const point = coordinatesFrom(row);

      const slope = numberFrom(row, [
        "slope_mean_degrees",
        "mean_slope_degrees",
        "average_slope_degrees",
        "slope"
      ]);

      const elevation = numberFrom(row, [
        "elevation_mean_m",
        "mean_elevation_m",
        "average_elevation_m",
        "elevation_m"
      ]);

      const roughness = numberFrom(row, [
        "roughness_mean_1350m",
        "roughness_mean_m",
        "roughness_1350m_mean",
        "mean_roughness_m",
        "roughness_mean_630m",
        "roughness"
      ]);

      if (!Number.isFinite(point.lat) ||
          !Number.isFinite(point.lon) ||
          !Number.isFinite(slope)) return null;

      const candidate = {
        name: "Earth terrain tile " + (index + 1),
        latitude: point.lat,
        longitude: point.lon,
        elevation: elevation,
        slope: slope,
        roughness: roughness,
        temperature: NaN,
        water: NaN,
        aerosol: NaN
      };

      pdEarth.push({
        lat: point.lat,
        lon: point.lon,
        slope: slope,
        elevation: elevation,
        rough: roughness
      });

      return candidate;
    }).filter(Boolean);

    const namedCandidates = detailedRows.map(row => ({
      name: String(row.candidate || "").trim(),
      latitude: Number(row.latitude),
      longitude: Number(row.longitude),
      elevation: Number(row.elevation_m),
      slope: Number(row.slope_mean_degrees),
      roughness: Number(row.roughness_mean_m),
      temperature: Number(row.mean_temperature_c),
      water: Number(row.mean_water_occurrence_percent),
      aerosol: Number(row.annual_mean_aod_55)
    })).filter(row =>
      row.name &&
      Number.isFinite(row.latitude) &&
      Number.isFinite(row.longitude) &&
      Number.isFinite(row.slope)
    );

    // Use all available Earth terrain tiles, plus detailed named evidence.
    pdCandidates = tileCandidates.concat(namedCandidates);

    if (!pdCandidates.length) {
      throw Error(
        "Earth CSV loaded, but no coordinates could be extracted. " +
        "Check its location column and coordinate format."
      );
    }

    // Replace the selector contents directly; do not depend on old handlers.
    const freshSearch = search.cloneNode(true);
    const freshSelect = select.cloneNode(false);

    freshSelect.id = "pd-place";
    freshSelect.innerHTML = "";

    search.replaceWith(freshSearch);
    select.replaceWith(freshSelect);

    function populateEarthSelector() {
      const query = freshSearch.value.trim().toLowerCase();
      freshSelect.innerHTML =
        '<option value="">Choose an Earth location</option>';

      let count = 0;

      pdCandidates.forEach((candidate, index) => {
        const label =
          candidate.name + " (" +
          candidate.latitude.toFixed(2) + "°, " +
          candidate.longitude.toFixed(2) + "°)";

        if (query && !label.toLowerCase().includes(query)) return;

        const option = document.createElement("option");
        option.value = String(index);
        option.textContent = label;
        freshSelect.appendChild(option);
        count++;
      });

      status.textContent =
        count + " Earth locations shown; " +
        tileCandidates.length + " terrain tiles and " +
        namedCandidates.length + " named evidence locations loaded locally.";
    }

    freshSearch.addEventListener("input", populateEarthSelector);

    freshSelect.addEventListener("change", () => {
      const chosen = pdCandidates[Number(freshSelect.value)];
      const button = document.getElementById("pd-analyze");
      if (button) button.disabled = !chosen;

      if (chosen) {
        document.getElementById("pd-lat").value = chosen.latitude;
        document.getElementById("pd-lon").value = chosen.longitude;
        pdAnalyze();
      }
    });

    const analyzeButton = document.getElementById("pd-analyze");
    if (analyzeButton) {
      analyzeButton.disabled = false;
      analyzeButton.onclick = pdAnalyze;
    }

    populateEarthSelector();

    if (typeof pdDrawEarthMap === "function") pdDrawEarthMap();
    if (typeof pdDrawPlanetMap === "function") pdDrawPlanetMap();

    console.log("TERRATIME4D local Earth tiles:", tileCandidates.length);
    console.log("TERRATIME4D detailed Earth candidates:", namedCandidates.length);

  } catch (error) {
    console.error("Earth discovery data loading failed:", error);
    if (status) status.textContent = "EARTH DATA ERROR: " + error.message;

    if (select) {
      select.innerHTML =
        '<option value="">Earth data error - see status message</option>';
    }
  }
})();

// TT4D_EARTH_MISSION_TEST_V1
// Earth analogue mission assessment using local repository evidence.

const pdMissionPanel = document.createElement("div");
pdMissionPanel.id = "pd-earth-mission-test";
pdMissionPanel.className = "pd-panel";
pdMissionPanel.style.cssText = "margin-top:22px;padding:20px;border:1px solid #3685a5;background:#0b2033;border-radius:10px";

pdMissionPanel.innerHTML = `
  <div style="color:#63dcff;font-size:11px;letter-spacing:2px">MISSION PREPARATION / EARTH ANALOGUE TESTING</div>
  <h3 style="font-size:20px;color:#e5f5ff;margin:12px 0">TEST YOUR PLANETARY MISSION ON EARTH</h3>
  <p>Select one of the ranked Earth terrain matches and evaluate your proposed mission using available local terrain and mission evidence.</p>

  <div class="pd-controls" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px">
    <label>Selected Earth analogue
      <select id="pd-earth-choice"><option value="">Analyse a planetary location first</option></select>
    </label>
    <label>Mission objective
      <select id="pd-mission-choice">
        <option value="rover">Rover mobility</option>
        <option value="landing">Landing site assessment</option>
        <option value="geology">Geological research</option>
        <option value="resource">Resource exploration</option>
        <option value="human">Human operations</option>
      </select>
    </label>
  </div>

  <button id="pd-run-mission" style="background:#07516c;border:1px solid #56d9ff;padding:13px 20px;margin-top:12px">
    RUN EARTH ANALOGUE MISSION TEST
  </button>

  <div id="pd-mission-output" style="margin-top:18px;padding:15px;background:#071827;border-radius:8px">
    <div style="color:#63dcff">AWAITING EARTH ANALOGUE SELECTION</div>
    Select a planetary location, choose an Earth match and run the mission assessment.
  </div>
  <div id="pd-mission-evidence" style="margin-top:12px;color:#a9c4d8;font-size:12px"></div>
`;

const pdNote = document.querySelector("#planetary-discovery .pd-note");
if (pdNote) pdNote.before(pdMissionPanel);

let pdMissionCandidates = [];
let pdMissionProfiles = [];

function pdMissionNumber(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function pdMissionNearest(lat, lon) {
  if (!pdMissionCandidates.length) return null;

  return pdMissionCandidates.map(r => {
    const dlat = Number(r.latitude) - lat;
    const dlon = (Number(r.longitude) - lon) *
      Math.cos(lat * Math.PI / 180);
    return {...r, distance: Math.hypot(dlat, dlon)};
  }).sort((a,b) => a.distance-b.distance)[0];
}

function pdRefreshMissionChoices() {
  const select = document.getElementById("pd-earth-choice");
  if (!select) return;

  const previous = select.value;
  const rows = [...document.querySelectorAll("#pd-results tr")];

  const names = rows.map(row => {
    const cells = row.querySelectorAll("td");
    if (cells.length < 6) return null;
    return cells[1].textContent.trim();
  }).filter(Boolean);

  const records = names.map(name => pdEarth.find(r => r.name === name))
    .filter(Boolean);

  select.innerHTML = records.length
    ? '<option value="">Choose an Earth analogue</option>' +
      records.map((r,i) =>
        `<option value="${i}">${i+1}. ${r.name} (${r.lat.toFixed(1)}Â°, ${r.lon.toFixed(1)}Â°)</option>`
      ).join("")
    : '<option value="">Analyse a planetary location first</option>';

  if (previous && Number(previous) < records.length) {
    select.value = previous;
  }

  window.pdMissionEarthRecords = records;
}

// Wrap the existing analysis without changing its scientific calculations.
const pdOriginalAnalyzeForMission = pdAnalyze;
pdAnalyze = function() {
  pdOriginalAnalyzeForMission();
  pdRefreshMissionChoices();
};

function pdRunEarthMission() {
  const select = document.getElementById("pd-earth-choice");
  const mission = document.getElementById("pd-mission-choice").value;
  const output = document.getElementById("pd-mission-output");
  const evidenceOutput = document.getElementById("pd-mission-evidence");

  const records = window.pdMissionEarthRecords || [];
  const earth = records[Number(select.value)];

  if (!earth) {
    output.innerHTML = "Please analyse a Moon/Mars location and select an Earth analogue first.";
    return;
  }

  const slope = Number(earth.slope);
  const rough = Number(earth.rough);
  const nearest = pdMissionNearest(earth.lat, earth.lon);

  let risk = "LOW";
  let reasons = [];
  let assessment = "";

  if (mission === "rover") {
    const slopeRisk = slope >= 15 ? "HIGH" : slope >= 8 ? "MEDIUM" : "LOW";
    const roughRisk = rough >= 30 ? "HIGH" : rough >= 10 ? "MEDIUM" : "LOW";
    risk = slopeRisk === "HIGH" || roughRisk === "HIGH" ? "HIGH" :
      slopeRisk === "MEDIUM" || roughRisk === "MEDIUM" ? "MEDIUM" : "LOW";
    reasons = [
      `Mean terrain slope: ${slope.toFixed(2)}Â°`,
      `Earth reference roughness at 1.35 km scale: ${rough.toFixed(2)} m`,
      "Roughness is shown as Earth reference evidence, not a scale-equivalent planetary measurement."
    ];
    assessment = "Preliminary rover terrain screening based on available Earth slope and roughness.";
  }

  if (mission === "landing") {
    risk = slope >= 8 || rough >= 20 ? "HIGH" :
      slope >= 3 || rough >= 5 ? "MEDIUM" : "LOW";
    reasons = [
      `Mean slope: ${slope.toFixed(2)}Â°`,
      `Reference roughness: ${rough.toFixed(2)} m`,
      "No validated landing hazard, boulder or subsurface assessment is available in this screening."
    ];
    assessment = "Preliminary terrain screening only; not a certified landing safety assessment.";
  }

  if (mission === "geology") {
    const count = nearest ? Number(nearest.mineral_geological_records || 0) : 0;
    risk = count > 0 ? "LOW" : "MEDIUM";
    reasons = [
      `Available geological records at nearest evidence site: ${count}`,
      `Terrain slope at selected Earth analogue: ${slope.toFixed(2)}Â°`
    ];
    assessment = "Geological evidence availability screening. A terrain match alone does not establish geological equivalence.";
  }

  if (mission === "resource") {
    const water = nearest ? Number(nearest.mean_water_occurrence_percent || 0) : 0;
    const minerals = nearest ? Number(nearest.mineral_geological_records || 0) : 0;
    risk = water > 5 || minerals > 0 ? "LOW" :
      water > 0 ? "MEDIUM" : "HIGH";
    reasons = [
      `Water occurrence at nearest evidence site: ${water.toFixed(3)}%`,
      `Mineral/geological records: ${minerals}`,
      "Resource evidence is available only for the nearest supplied Earth evidence location."
    ];
    assessment = "Evidence availability screening, not confirmation of recoverable resources.";
  }

  if (mission === "human") {
    const temp = nearest ? Number(nearest.annual_mean_temperature_c) : null;
    const water = nearest ? Number(nearest.mean_water_occurrence_percent || 0) : 0;
    risk = temp === null ? "HIGH" :
      temp < -10 ? "HIGH" : temp < 5 ? "MEDIUM" : "LOW";
    reasons = [
      `Nearest evidence-site annual mean temperature: ${temp === null ? "Unavailable" : temp.toFixed(2)+" Â°C"}`,
      `Water occurrence at nearest evidence site: ${water.toFixed(3)}%`,
      "Earth climate measurements cannot represent Moon/Mars environmental conditions."
    ];
    assessment = "Earth environmental analogue context only; not a human habitability assessment.";
  }

  const color = risk === "HIGH" ? "#ff7474" :
    risk === "MEDIUM" ? "#ffd078" : "#65e6a5";

  output.innerHTML = `
    <div style="font-size:11px;letter-spacing:2px;color:#63dcff">EARTH ANALOGUE MISSION REPORT</div>
    <h3 style="color:#e5f5ff;font-size:19px">${mission.toUpperCase()} TEST</h3>
    <div style="font-size:25px;font-weight:bold;color:${color};margin:12px 0">${risk} RISK</div>
    <div style="line-height:1.9;color:#d5e8f4">
      <b>Test location:</b> ${earth.name}<br>
      <b>Coordinates:</b> ${earth.lat.toFixed(2)}Â°, ${earth.lon.toFixed(2)}Â°<br>
      <b>Mean slope:</b> ${slope.toFixed(2)}Â°<br>
      <b>Earth reference roughness:</b> ${rough.toFixed(2)} m
    </div>
    <h4 style="color:#63dcff">ASSESSMENT EVIDENCE</h4>
    <ul>${reasons.map(x=>`<li>${x}</li>`).join("")}</ul>
    <p>${assessment}</p>
    <div style="border-top:1px solid #315b73;padding-top:10px;font-size:11px;color:#a9c4d8">
      Risk categories are preliminary screening rules, not validated engineering safety thresholds.
      This test uses the selected Earth terrain record and does not simulate actual Moon/Mars physics.
    </div>
  `;

  if (nearest) {
    evidenceOutput.innerHTML =
      `<b>Nearest detailed Earth mission-evidence location:</b> ${nearest.candidate} ` +
      `(${Number(nearest.latitude).toFixed(2)}Â°, ${Number(nearest.longitude).toFixed(2)}Â°). ` +
      `Distance from selected terrain reference: ${nearest.distance.toFixed(2)}Â°.` +
      `<br>Environmental and geological evidence shown above belongs to this nearest evidence location, not necessarily the selected terrain tile.`;
  } else {
    evidenceOutput.textContent =
      "Detailed mission-evidence records were unavailable. Assessment uses the selected terrain reference only.";
  }
}

document.getElementById("pd-run-mission")
  .addEventListener("click", pdRunEarthMission);

// Load the existing integrated mission evidence from local project files.
Promise.all([
  fetch("/data/integrated_candidate_evidence.csv").then(r => {
    if (!r.ok) throw Error("Candidate evidence CSV unavailable");
    return r.text();
  }),
  fetch("/data/integrated_mission_scores.csv").then(r => {
    if (!r.ok) throw Error("Mission scores CSV unavailable");
    return r.text();
  })
]).then(([candidateCsv, scoreCsv]) => {
  pdMissionCandidates = pdRecords(candidateCsv);
  pdMissionProfiles = pdRecords(scoreCsv);
  pdRefreshMissionChoices();

  document.getElementById("pd-mission-evidence").textContent =
    `Loaded ${pdMissionCandidates.length} detailed Earth mission-evidence locations and ` +
    `${pdMissionProfiles.length} existing mission screening records from local repository data.`;
}).catch(error => {
  document.getElementById("pd-mission-evidence").textContent =
    "Detailed mission evidence unavailable: " + error.message +
    ". Terrain-based assessment remains available.";
});


// TT4D_USER_FIRST_LOCATION_FLOW
const tt4dApp = document.getElementById("app");
const tt4dComparison = document.getElementById("planetary-comparison");

if (tt4dApp) tt4dApp.style.display = "none";
if (tt4dComparison) tt4dComparison.style.display = "none";

const tt4dRevealResults = () => {
    if (!pdTarget) return;

    if (tt4dApp) tt4dApp.style.display = "";
    if (tt4dComparison) tt4dComparison.style.display = "";

    const status = document.getElementById("pd-status");
    if (status) {
        status.scrollIntoView({behavior:"smooth",block:"center"});
    }
};

document.getElementById("pd-analyze")?.addEventListener(
    "click", tt4dRevealResults
);

document.getElementById("pd-target-map")?.addEventListener(
    "click", () => {
        if (pdTarget) tt4dRevealResults();
    }
);








