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
      <h3 id="pd-target-title">GLOBAL MOON / MARS ELEVATION</h3>
      <canvas id="pd-target-map" width="720" height="360"></canvas>
      <p>Click anywhere on this map to select a planetary coordinate. Map is a 1ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â° browsing grid.</p>
    </div>
    <div class="pd-panel">
      <h3>EARTH REFERENCE DISTRIBUTION</h3>
      <canvas id="pd-earth-map" width="720" height="360"></canvas>
      <p>Dots represent available Earth reference tile coordinates. They do not represent continuous DEM coverage.</p>
    </div>
  </div>

  <div class="pd-map-grid" id="pd-separate-match-maps">
  <div class="pd-panel">
    <h3>MOON Ã¢â‚¬â€ SELECTED EARTH LOCATION ANALOGUES</h3>
    <canvas id="pd-moon-match-map" width="720" height="360" style="width:100%;height:auto;background:#101827"></canvas>
    <p>Global lunar slope map. Highlighted points show the top 10 matches for the selected Earth location.</p>
  </div>
  <div class="pd-panel">
    <h3>MARS Ã¢â‚¬â€ SELECTED EARTH LOCATION ANALOGUES</h3>
    <canvas id="pd-mars-match-map" width="720" height="360" style="width:100%;height:auto;background:#101827"></canvas>
    <p>Global Martian slope map. Highlighted points show the top 10 matches for the selected Earth location.</p>
  </div>
</div>
<section id="pd-dynamic-graphs" class="pd-panel">
    <h3>LOCATION-SPECIFIC TERRAIN COMPARISON GRAPHS</h3>
    <p id="pd-graph-subtitle">Select an Earth location and find planetary matches to generate graphs.</p>

    <div class="pd-graph-grid">
      <div class="pd-panel">
        <h3>EARTH vs MOON Ã¢â‚¬â€ TERRAIN PARAMETERS</h3>
        <canvas id="pd-earth-moon-chart" width="720" height="360"></canvas>
      </div>

      <div class="pd-panel">
        <h3>EARTH vs MARS Ã¢â‚¬â€ TERRAIN PARAMETERS</h3>
        <canvas id="pd-earth-mars-chart" width="720" height="360"></canvas>
      </div>

      <div class="pd-panel">
        <h3>MOON vs MARS Ã¢â‚¬â€ SIMILARITY SCORES</h3>
        <canvas id="pd-similarity-chart" width="720" height="360"></canvas>
      </div>

      <div class="pd-panel">
        <h3>TERRAIN PARAMETER COMPARISON</h3>
        <canvas id="pd-parameter-chart" width="720" height="360"></canvas>
      </div>
    </div>
  </section>
  <div class="pd-stats" id="pd-stats">
    <div class="pd-stat"><small>MEAN ELEVATION</small><strong id="pd-elevation">ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â</strong></div>
    <div class="pd-stat"><small>MEAN SLOPE</small><strong id="pd-slope">ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â</strong></div>
    <div class="pd-stat"><small>ROUGHNESS (~11 KM)</small><strong id="pd-roughness">ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â</strong></div>
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
    "COMPARISON COMPLETE ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â· CONTINUE SCROLLING BELOW FOR PLANETARY ANALOG DISCOVERY";
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
    ctx.fillText(lat + "Ãƒâ€šÃ‚Â°", 5, y - 4);
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

function pdDrawDiscoveryChart(canvasId, labels, values, title, unit) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  canvas.width = 900;
  canvas.height = 320;
  canvas.style.width = "100%";
  canvas.style.height = "320px";
  canvas.style.display = "block";

  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;

  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = "#101827";
  ctx.fillRect(0, 0, w, h);

  ctx.fillStyle = "#ffffff";
  ctx.font = "bold 19px Arial";
  ctx.textAlign = "left";
  ctx.fillText(title, 24, 34);

  const valid = values.map((v, i) => ({
    label: labels[i],
    value: Number(v)
  })).filter(x => Number.isFinite(x.value));

  if (!valid.length) {
    ctx.fillStyle = "#cccccc";
    ctx.font = "15px Arial";
    ctx.fillText("No comparison data available", 25, 100);
    return;
  }

  const max = Math.max(...valid.map(x => Math.abs(x.value)), 0.01);
  const chartTop = 75;
  const chartBottom = h - 65;
  const chartHeight = chartBottom - chartTop;
  const slot = (w - 80) / valid.length;
  const barWidth = Math.min(90, slot * 0.58);

  valid.forEach((item, i) => {
    const barHeight = Math.max(3, Math.abs(item.value) / max * chartHeight);
    const x = 40 + i * slot + (slot - barWidth) / 2;
    const y = chartBottom - barHeight;

    ctx.fillStyle = i === 0 ? "#38bdf8" :
                    i === 1 ? "#a78bfa" :
                    i === 2 ? "#fb923c" : "#34d399";

    ctx.fillRect(x, y, barWidth, barHeight);

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 15px Arial";
    ctx.textAlign = "center";
    ctx.fillText(
      item.value.toFixed(2) + unit,
      x + barWidth / 2,
      Math.max(58, y - 12)
    );

    ctx.font = "13px Arial";
    ctx.fillStyle = "#d1d5db";
    ctx.fillText(
      item.label,
      x + barWidth / 2,
      chartBottom + 25
    );
  });

  ctx.textAlign = "left";
}

function pdDrawDiscoveryGraphs(earth, moonMatches, marsMatches) {
  if (!earth || !moonMatches || !marsMatches) return;

  const moon = moonMatches[0];
  const mars = marsMatches[0];

  if (!moon || !mars) return;

  // GRAPH 1: Selected Earth location versus its best Moon match
  pdDrawDiscoveryChart(
    "pd-earth-moon-chart",
    ["Selected Earth", "Best Moon Match"],
    [earth.slope, moon.slope],
    "EARTH vs BEST MOON - MEAN SLOPE",
    "\u00B0"
  );

  // GRAPH 2: Selected Earth location versus its best Mars match
  pdDrawDiscoveryChart(
    "pd-earth-mars-chart",
    ["Selected Earth", "Best Mars Match"],
    [earth.slope, mars.slope],
    "EARTH vs BEST MARS - MEAN SLOPE",
    "\u00B0"
  );

  // GRAPH 3: Top five Moon and Mars similarity scores
  const similarityLabels = [];
  const similarityValues = [];

  for (let i = 0; i < 5; i++) {
    if (moonMatches[i]) {
      similarityLabels.push("Moon " + (i + 1));
      similarityValues.push(moonMatches[i].score);
    }

    if (marsMatches[i]) {
      similarityLabels.push("Mars " + (i + 1));
      similarityValues.push(marsMatches[i].score);
    }
  }

  pdDrawDiscoveryChart(
    "pd-similarity-chart",
    similarityLabels,
    similarityValues,
    "TOP 5 MOON / MARS MATCH SCORES",
    ""
  );

  // GRAPH 4: Roughness comparison
  // Earth roughness is already in metres.
  // Moon and Mars roughness values are converted from km to metres.
  pdDrawDiscoveryChart(
    "pd-parameter-chart",
    ["Selected Earth", "Best Moon", "Best Mars"],
    [
      Number(earth.roughness),
      Number(moon.roughness) * 1000,
      Number(mars.roughness) * 1000
    ],
    "ROUGHNESS COMPARISON - METRES",
    " m"
  );

  const subtitle = document.getElementById("pd-graph-subtitle");

  if (subtitle) {
    subtitle.textContent =
      "Selected Earth: " + earth.name +
      " | Earth coordinates: " +
      earth.latitude.toFixed(2) + "\u00B0, " +
      earth.longitude.toFixed(2) + "\u00B0" +
      " | Best Moon: " +
      moon.latitude.toFixed(1) + "\u00B0, " +
      moon.longitude.toFixed(1) + "\u00B0" +
      " | Best Mars: " +
      mars.latitude.toFixed(1) + "\u00B0, " +
      mars.longitude.toFixed(1) +
      "\u00B0. Roughness values are displayed in metres; measurement scales differ between datasets.";
  }
}
function pdDrawSelectedPlanetMapV2(canvasId, planetName, matches) {
  const canvas = document.getElementById(canvasId);
  const grid = pdData && pdData.planets && pdData.planets[planetName];
  if (!canvas || !grid || !grid.valid || !grid.slope_degrees) return;

  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  const image = ctx.createImageData(w, h);

  for (let row = 0; row < 180; row++) {
    for (let col = 0; col < 360; col++) {
      const valid = grid.valid[row] && grid.valid[row][col];
      const slope = valid ? Number(grid.slope_degrees[row][col]) : NaN;

      let r = 13, g = 23, b = 39;
      if (Number.isFinite(slope)) {
        const t = Math.max(0, Math.min(1, slope / 20));
        r = Math.round(35 + 215 * t);
        g = Math.round(85 + 115 * t);
        b = Math.round(190 - 145 * t);
      }

      for (let dy = 0; dy < 2; dy++) {
        const y = row * 2 + dy;
        for (let dx = 0; dx < 2; dx++) {
          const x = col * 2 + dx;
          const p = (y * w + x) * 4;
          image.data[p] = r;
          image.data[p + 1] = g;
          image.data[p + 2] = b;
          image.data[p + 3] = 255;
        }
      }
    }
  }

  ctx.putImageData(image, 0, 0);

  // Highlight the selected location's actual best-match regions.
  (matches || []).forEach((m, i) => {
    const x = ((m.longitude + 180) / 360) * w;
    const y = ((90 - m.latitude) / 180) * h;

    ctx.beginPath();
    ctx.arc(x, y, i === 0 ? 9 : 5, 0, Math.PI * 2);
    ctx.strokeStyle = i === 0 ? "#ffffff" : "#ffdf55";
    ctx.lineWidth = i === 0 ? 3 : 2;
    ctx.stroke();

    if (i === 0) {
      ctx.fillStyle = "#ff553d";
      ctx.fill();
    }
  });

  ctx.fillStyle = "#ffffff";
  ctx.font = "bold 15px Arial";
  ctx.fillText(planetName + " Ã¢â‚¬â€ TOP 10 MATCH LOCATIONS", 14, 22);

  ctx.font = "12px Arial";
  ctx.fillStyle = "#ffdf55";
  ctx.fillText("Yellow circles: other top matches", 14, h - 12);
  ctx.fillStyle = "#ffffff";
  ctx.fillText("Red circle: best match", 14, h - 29);
}

function pdDrawSelectedGraphV2(canvasId, labels, values, title, unit) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = "#101827";
  ctx.fillRect(0, 0, w, h);

  ctx.fillStyle = "#ffffff";
  ctx.font = "bold 17px Arial";
  ctx.fillText(title, 18, 28);

  const valid = values.map((v, i) => ({
    label: labels[i],
    value: Number(v)
  })).filter(x => Number.isFinite(x.value));

  if (!valid.length) return;

  const max = Math.max(...valid.map(x => Math.abs(x.value)), 0.01);
  const baseY = h - 65;
  const chartHeight = h - 125;
  const slot = (w - 50) / valid.length;
  const barWidth = Math.min(65, slot * 0.55);

  valid.forEach((item, i) => {
    const bh = Math.max(2, Math.abs(item.value) / max * chartHeight);
    const x = 25 + i * slot + (slot - barWidth) / 2;
    const y = baseY - bh;

    ctx.fillStyle = ["#38bdf8", "#a78bfa", "#fb923c", "#34d399"][i % 4];
    ctx.fillRect(x, y, barWidth, bh);

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 13px Arial";
    ctx.textAlign = "center";
    ctx.fillText(item.value.toFixed(2) + unit, x + barWidth / 2, Math.max(48, y - 8));

    ctx.font = "12px Arial";
    ctx.fillStyle = "#d1d5db";
    ctx.fillText(item.label, x + barWidth / 2, baseY + 22);
  });

  ctx.textAlign = "left";
}

function pdRefreshSelectedComparisonV2(earth, moonMatches, marsMatches) {
  if (!earth || !moonMatches.length || !marsMatches.length) return;

  const moon = moonMatches[0];
  const mars = marsMatches[0];

  // Two selected-location-dependent planetary maps.
  pdDrawSelectedPlanetMapV2("pd-moon-match-map", "Moon", moonMatches);
  pdDrawSelectedPlanetMapV2("pd-mars-match-map", "Mars", marsMatches);

  // Earth against the best Moon analogue.
  pdDrawSelectedGraphV2(
    "pd-earth-moon-chart",
    ["Earth", "Best Moon"],
    [earth.slope, moon.slope],
    "EARTH vs MOON Ã¢â‚¬â€ MEAN SLOPE",
    "Ã‚Â°"
  );

  // Earth against the best Mars analogue.
  pdDrawSelectedGraphV2(
    "pd-earth-mars-chart",
    ["Earth", "Best Mars"],
    [earth.slope, mars.slope],
    "EARTH vs MARS Ã¢â‚¬â€ MEAN SLOPE",
    "Ã‚Â°"
  );

  // Top five similarity scores for each planetary body.
  const scoreLabels = [];
  const scoreValues = [];

  for (let i = 0; i < 5; i++) {
    if (moonMatches[i]) {
      scoreLabels.push("Moon " + (i + 1));
      scoreValues.push(moonMatches[i].score);
    }
    if (marsMatches[i]) {
      scoreLabels.push("Mars " + (i + 1));
      scoreValues.push(marsMatches[i].score);
    }
  }

  pdDrawSelectedGraphV2(
    "pd-similarity-chart",
    scoreLabels,
    scoreValues,
    "TOP 5 MOON / MARS SIMILARITY SCORES",
    "/100"
  );

  // Roughness is displayed, but is NOT treated as a scale-equivalent match.
  pdDrawSelectedGraphV2(
    "pd-parameter-chart",
    ["Earth", "Moon", "Mars"],
    [earth.roughness, moon.roughness * 1000, mars.roughness * 1000],
    "ROUGHNESS Ã¢â‚¬â€ DISPLAYED IN METRES",
    " m"
  );

  const subtitle = document.getElementById("pd-graph-subtitle");
  if (subtitle) {
    subtitle.textContent =
      "Selected Earth: " + earth.name +
      " | Best Moon: " + moon.latitude.toFixed(1) + "Ã‚Â°, " +
      moon.longitude.toFixed(1) + "Ã‚Â° | Best Mars: " +
      mars.latitude.toFixed(1) + "Ã‚Â°, " +
      mars.longitude.toFixed(1) +
      "Ã‚Â°. Slope drives the current ranking. Roughness uses different spatial scales. Elevation datums are not directly comparable.";
  }
}

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
    earth.slope.toFixed(2) + "ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°";
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
        <td>${r.latitude.toFixed(1)}ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°, ${r.longitude.toFixed(1)}ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°</td>
        <td>${r.slope.toFixed(2)}ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°</td>
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
    `Earth input: ${earth.name} (${earth.latitude.toFixed(2)}ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°, ${earth.longitude.toFixed(2)}ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°). ` +
    `Compared its slope against valid 1ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â° grid cells on the Moon and Mars. ` +
    `Showing the top 10 matches for each planetary body.`;

  pdTarget = { lat: earth.latitude, lon: earth.longitude };

  pdDrawDiscoveryGraphs(earth, moonMatches, marsMatches);
  pdRefreshSelectedComparisonV2(earth, moonMatches, marsMatches);

  requestAnimationFrame(() => {
    if (typeof pdDrawEarthMap === "function") pdDrawEarthMap();
    if (typeof pdDrawPlanetMap === "function") pdDrawPlanetMap();
  });
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

    // FINAL MAP RENDER RETRY: redraw after the panel and loaded data settle.
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        try {
          const earthCanvas = document.getElementById("pd-earth-map");
          const planetCanvas = document.getElementById("pd-target-map");

          if (earthCanvas) {
            earthCanvas.style.display = "block";
            earthCanvas.style.visibility = "visible";
          }
          if (planetCanvas) {
            planetCanvas.style.display = "block";
            planetCanvas.style.visibility = "visible";
          }

          if (typeof pdDrawEarthMap === "function") pdDrawEarthMap();
          if (typeof pdDrawPlanetMap === "function") pdDrawPlanetMap();

          let attempts = 0;
          const retry = setInterval(() => {
            attempts++;
            try {
              if (typeof pdDrawEarthMap === "function") pdDrawEarthMap();
              if (typeof pdDrawPlanetMap === "function") pdDrawPlanetMap();
            } catch (error) {
              console.error("TERRATIME4D map redraw:", error);
            }
            if (attempts >= 8) clearInterval(retry);
          }, 700);
        } catch (error) {
          console.error("TERRATIME4D map initialization:", error);
        }
      });
    });
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
        name: (
          point.lat >= 0
            ? (point.lon >= -170 && point.lon <= -30 ? "North America" :
               point.lon > -30 && point.lon <= 60 ? "Europe / Africa" :
               point.lon > 60 && point.lon <= 180 ? "Asia" : "Pacific Region")
            : (point.lon >= -85 && point.lon <= -30 ? "South America" :
               point.lon > -30 && point.lon <= 60 ? "Africa" :
               point.lon > 60 && point.lon <= 180 ? "Oceania / Asia" :
               "South Pacific Region")
        ) + " Ã¢â‚¬â€ Earth Terrain"
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
        let displayName = candidate.name;

        if (index < tileCandidates.length) {
          let nearest = null;
          let nearestDistance = Infinity;

          for (const place of namedCandidates) {
            const distance =
              Math.pow(place.latitude - candidate.latitude, 2) +
              Math.pow(place.longitude - candidate.longitude, 2);

            if (distance < nearestDistance) {
              nearestDistance = distance;
              nearest = place;
            }
          }

          displayName =
            nearest && nearestDistance <= 25
              ? nearest.name
              : "Earth terrain region";
        }

        const label = displayName;

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
        requestAnimationFrame(() => {
          if (typeof pdDrawEarthMap === "function") pdDrawEarthMap();
          if (typeof pdDrawPlanetMap === "function") pdDrawPlanetMap();
        });
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
        `<option value="${i}">${i+1}. ${r.name} (${r.lat.toFixed(1)}ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°, ${r.lon.toFixed(1)}ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°)</option>`
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
      `Mean terrain slope: ${slope.toFixed(2)}ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°`,
      `Earth reference roughness at 1.35 km scale: ${rough.toFixed(2)} m`,
      "Roughness is shown as Earth reference evidence, not a scale-equivalent planetary measurement."
    ];
    assessment = "Preliminary rover terrain screening based on available Earth slope and roughness.";
  }

  if (mission === "landing") {
    risk = slope >= 8 || rough >= 20 ? "HIGH" :
      slope >= 3 || rough >= 5 ? "MEDIUM" : "LOW";
    reasons = [
      `Mean slope: ${slope.toFixed(2)}ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°`,
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
      `Terrain slope at selected Earth analogue: ${slope.toFixed(2)}ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°`
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
      `Nearest evidence-site annual mean temperature: ${temp === null ? "Unavailable" : temp.toFixed(2)+" ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°C"}`,
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
      <b>Coordinates:</b> ${earth.lat.toFixed(2)}ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°, ${earth.lon.toFixed(2)}ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°<br>
      <b>Mean slope:</b> ${slope.toFixed(2)}ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°<br>
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
      `(${Number(nearest.latitude).toFixed(2)}ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°, ${Number(nearest.longitude).toFixed(2)}ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°). ` +
      `Distance from selected terrain reference: ${nearest.distance.toFixed(2)}ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°.` +
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










(function TERRATIME4D_SVG_MAPS() {
  const W = 960, H = 480;

  function renderEarth() {
    const host = document.getElementById("pd-earth-svg-map");
    if (!host || !Array.isArray(pdEarth) || !pdEarth.length) return false;

    let marks = "";
    for (const p of pdEarth) {
      const lat = Number(p.lat), lon = Number(p.lon);
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) continue;
      const x = (lon + 180) / 360 * W;
      const y = (90 - lat) / 180 * H;
      marks += `<circle cx="${x}" cy="${y}" r="3" fill="#32d7ec"><title>${String(p.location || "Earth tile")} (${lat.toFixed(2)}, ${lon.toFixed(2)})</title></circle>`;
    }

    let lines = "";
    for (let lon = -180; lon <= 180; lon += 30) {
      const x = (lon + 180) / 360 * W;
      lines += `<path d="M${x} 0V${H}" stroke="#355064"/>`;
    }
    for (let lat = -60; lat <= 60; lat += 30) {
      const y = (90 - lat) / 180 * H;
      lines += `<path d="M0 ${y}H${W}" stroke="#355064"/>`;
    }

    host.innerHTML = `<div style="padding:12px;color:white;font:14px Arial"><b>EARTH TERRAIN LOCATIONS (${pdEarth.length})</b><svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;display:block;background:#091c2c;margin-top:8px"><rect width="${W}" height="${H}" fill="#091c2c"/>${lines}${marks}</svg><p style="color:#9bb4c8">Cyan points show the available Earth terrain tiles by latitude and longitude.</p></div>`;
    return true;
  }

  function locateGrid(obj, depth = 0, seen = new Set()) {
    if (!obj || typeof obj !== "object" || depth > 7 || seen.has(obj)) return null;
    seen.add(obj);

    for (const [key, val] of Object.entries(obj)) {
      if (/elevation/i.test(key) && Array.isArray(val)) {
        const flat = [];
        const visit = a => {
          if (typeof a === "number") flat.push(a);
          else if (Array.isArray(a)) a.forEach(visit);
        };
        visit(val);
        if (flat.length >= 10000) return flat;
      }
    }

    for (const val of Object.values(obj)) {
      const result = locateGrid(val, depth + 1, seen);
      if (result) return result;
    }
    return null;
  }

  function renderPlanet(name, hostId) {
    const host = document.getElementById(hostId);
    if (!host || !pdData || !pdData.planets) return false;
    const key = Object.keys(pdData.planets).find(k => k.toLowerCase() === name.toLowerCase());
    if (!key) return false;

    const vals = locateGrid(pdData.planets[key]);
    if (!vals) {
      host.innerHTML = `<p style="color:#ffd28a;padding:12px">${name}: elevation array not found in local data.</p>`;
      return false;
    }

    const cols = 360, rows = Math.floor(vals.length / cols);
    if (rows < 10) return false;
    const stepX = Math.max(1, Math.floor(cols / 180));
    const stepY = Math.max(1, Math.floor(rows / 90));
    const sample = [];
    for (let y = 0; y < 90; y++) {
      for (let x = 0; x < 180; x++) {
        const v = vals[(y * stepY) * cols + x * stepX];
        if (Number.isFinite(v)) sample.push(v);
      }
    }
    if (!sample.length) return false;

    const min = Math.min(...sample), max = Math.max(...sample);
    let cells = "";
    for (let y = 0; y < 90; y++) {
      for (let x = 0; x < 180; x++) {
        const v = vals[(y * stepY) * cols + x * stepX];
        if (!Number.isFinite(v)) continue;
        const t = Math.max(0, Math.min(1, (v - min) / ((max - min) || 1)));
        const color = `rgb(${Math.round(30 + 220*t)},${Math.round(55 + 115*t)},${Math.round(100 + 100*(1-t))})`;
        cells += `<rect x="${x*W/180}" y="${y*H/90}" width="${W/180+0.3}" height="${H/90+0.3}" fill="${color}"/>`;
      }
    }

    host.innerHTML = `<div style="padding:12px;color:white;font:14px Arial"><b>${name.toUpperCase()} GLOBAL ELEVATION</b><svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;display:block;background:#091522;margin-top:8px">${cells}</svg><p style="color:#9bb4c8">Elevation range in source values: ${min.toFixed(3)} to ${max.toFixed(3)}. Local planetary grid.</p></div>`;
    return true;
  }

  let count = 0;
  const timer = setInterval(() => {
    count++;
    try {
      const e = renderEarth();
      const m = renderPlanet("Moon", "pd-moon-svg-map");
      const r = renderPlanet("Mars", "pd-mars-svg-map");
      if ((e && m && r) || count >= 90) clearInterval(timer);
    } catch (err) {
      console.error("TERRATIME4D SVG map error:", err);
      if (count >= 90) clearInterval(timer);
    }
  }, 1000);
})();



// TERRATIME4D_FORCE_MAP_RENDERER_V1
(function () {
  function pdMapGridValue(grid, names, row, col) {
    for (const name of names) {
      const source = grid && grid[name];
      if (source && source[row] && source[row][col] !== undefined) {
        const value = Number(source[row][col]);
        if (Number.isFinite(value)) return value;
      }
    }
    return NaN;
  }

  function pdMapValid(grid, row, col) {
    if (!grid) return false;
    const valid = grid.valid;
    if (valid && valid[row] && valid[row][col] !== undefined) {
      return !!valid[row][col];
    }
    return Number.isFinite(pdMapGridValue(
      grid, ["slope_degrees", "slope", "elevation_km", "elevation"], row, col
    ));
  }

  function pdMapColor(value, min, max) {
    if (!Number.isFinite(value)) return "rgb(24,31,43)";
    const t = Math.max(0, Math.min(1, (value - min) / (max - min || 1)));
    const stops = [
      [15, 34, 67], [24, 91, 125], [40, 145, 139],
      [160, 174, 93], [225, 177, 91], [238, 226, 190]
    ];
    const p = t * (stops.length - 1);
    const i = Math.min(stops.length - 2, Math.floor(p));
    const f = p - i;
    const c = stops[i].map((v, k) => Math.round(v + (stops[i + 1][k] - v) * f));
    return "rgb(" + c.join(",") + ")";
  }

  function pdMapCanvas(id, title) {
    const canvas = document.getElementById(id);
    if (!canvas) return null;

    canvas.style.display = "block";
    canvas.style.visibility = "visible";
    canvas.style.width = "100%";
    canvas.style.height = "auto";
    canvas.style.minHeight = "260px";
    canvas.style.background = "#101a2a";
    canvas.style.border = "1px solid #52647d";
    canvas.style.borderRadius = "8px";

    const width = Math.max(720, canvas.parentElement
      ? canvas.parentElement.clientWidth : 720);
    const height = 360;
    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext("2d");
    if (!ctx) return null;

    ctx.fillStyle = "#101a2a";
    ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = "#f0f4fa";
    ctx.font = "bold 15px Arial";
    ctx.fillText(title, 14, 22);

    return { canvas, ctx, width, height };
  }

  function pdDrawBodyMap(ctx, x, y, w, h, grid, body, earth, matchColor) {
    const rows = 180, cols = 360;
    ctx.fillStyle = "#17243a";
    ctx.fillRect(x, y, w, h);

    if (!grid) {
      ctx.fillStyle = "#ffffff";
      ctx.fillText(body + " dataset unavailable", x + 12, y + 25);
      return;
    }

    let min = Infinity, max = -Infinity;
    const values = [];

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        if (!pdMapValid(grid, r, c)) {
          values.push(NaN);
          continue;
        }
        const v = pdMapGridValue(
          grid, ["slope_degrees", "slope"], r, c
        );
        values.push(v);
        if (Number.isFinite(v)) {
          min = Math.min(min, v);
          max = Math.max(max, v);
        }
      }
    }

    if (!Number.isFinite(min) || !Number.isFinite(max)) {
      min = 0; max = 10;
    }
    if (max === min) max = min + 1;

    const cw = w / cols, ch = h / rows;
    let index = 0;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++, index++) {
        const value = values[index];
        ctx.fillStyle = pdMapColor(value, min, max);
        ctx.fillRect(x + c * cw, y + r * ch, cw + 0.5, ch + 0.5);
      }
    }

    // Latitude and longitude grid.
    ctx.strokeStyle = "rgba(255,255,255,0.22)";
    ctx.lineWidth = 1;
    for (let lon = 0; lon <= 360; lon += 60) {
      const px = x + (lon / 360) * w;
      ctx.beginPath(); ctx.moveTo(px, y); ctx.lineTo(px, y + h); ctx.stroke();
    }
    for (let lat = 0; lat <= 180; lat += 30) {
      const py = y + (lat / 180) * h;
      ctx.beginPath(); ctx.moveTo(x, py); ctx.lineTo(x + w, py); ctx.stroke();
    }

    // Selected Earth-location analogue marker.
    if (earth && Number.isFinite(earth.slope)) {
      const matches = [];
      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          const v = pdMapGridValue(grid, ["slope_degrees", "slope"], r, c);
          if (!pdMapValid(grid, r, c) || !Number.isFinite(v)) continue;
          matches.push({
            row: r, col: c,
            difference: Math.abs(v - earth.slope)
          });
        }
      }
      matches.sort((a, b) => a.difference - b.difference);

      for (const m of matches.slice(0, 10)) {
        const px = x + (m.col + 0.5) * cw;
        const py = y + (m.row + 0.5) * ch;
        ctx.beginPath();
        ctx.arc(px, py, 4, 0, Math.PI * 2);
        ctx.fillStyle = matchColor;
        ctx.fill();
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 1.2;
        ctx.stroke();
      }
    }

    ctx.strokeStyle = "#dce7f7";
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, w, h);

    ctx.fillStyle = "#eaf1fa";
    ctx.font = "11px Arial";
    ctx.fillText("90Ã‚Â°N", x + 4, y + 12);
    ctx.fillText("0Ã‚Â°", x + 4, y + h / 2);
    ctx.fillText("90Ã‚Â°S", x + 4, y + h - 4);
    ctx.fillText("180Ã‚Â°W", x + 4, y + h - 8);
    ctx.fillText("180Ã‚Â°E", x + w - 45, y + h - 8);
  }

  function pdForceDrawMaps() {
    if (typeof pdData === "undefined" || !pdData || !pdData.planets) {
      return false;
    }

    const selected = document.getElementById("pd-place");
    const earth = typeof pdCandidates !== "undefined" && selected &&
      selected.value !== ""
      ? pdCandidates[Number(selected.value)]
      : null;

    const moon = pdData.planets.Moon || pdData.planets.moon;
    const mars = pdData.planets.Mars || pdData.planets.mars;

    const target = pdMapCanvas(
      "pd-target-map", "MOON AND MARS Ã¢â‚¬â€ GLOBAL TERRAIN SLOPE MAPS"
    );

    if (target) {
      const gap = 18;
      const panelW = (target.width - 3 * gap) / 2;
      const mapY = 42;
      const mapH = 270;

      pdDrawBodyMap(
        target.ctx, gap, mapY, panelW, mapH,
        moon, "MOON", earth, "#ffdc62"
      );
      pdDrawBodyMap(
        target.ctx, 2 * gap + panelW, mapY, panelW, mapH,
        mars, "MARS", earth, "#66e5ff"
      );

      target.ctx.fillStyle = "#ffdc62";
      target.ctx.font = "12px Arial";
      target.ctx.fillText("Ã¢â€”Â Top 10 Moon slope matches", gap, 335);
      target.ctx.fillStyle = "#66e5ff";
      target.ctx.fillText("Ã¢â€”Â Top 10 Mars slope matches", gap + 250, 335);
    }

    const earthMap = pdMapCanvas(
      "pd-earth-map", "EARTH Ã¢â‚¬â€ AVAILABLE REFERENCE TERRAIN LOCATIONS"
    );

    if (earthMap) {
      const ctx = earthMap.ctx;
      const x = 12, y = 38, w = earthMap.width - 24, h = 285;
      ctx.fillStyle = "#17243a";
      ctx.fillRect(x, y, w, h);

      // Equirectangular Earth reference map.
      ctx.strokeStyle = "rgba(255,255,255,0.2)";
      for (let lon = 0; lon <= 360; lon += 30) {
        const px = x + lon / 360 * w;
        ctx.beginPath(); ctx.moveTo(px, y); ctx.lineTo(px, y + h); ctx.stroke();
      }
      for (let lat = 0; lat <= 180; lat += 30) {
        const py = y + lat / 180 * h;
        ctx.beginPath(); ctx.moveTo(x, py); ctx.lineTo(x + w, py); ctx.stroke();
      }

      if (typeof pdCandidates !== "undefined" && pdCandidates) {
        for (let i = 0; i < pdCandidates.length; i++) {
          const p = pdCandidates[i];
          if (!Number.isFinite(Number(p.latitude)) ||
              !Number.isFinite(Number(p.longitude))) continue;

          const px = x + ((Number(p.longitude) + 180) / 360) * w;
          const py = y + ((90 - Number(p.latitude)) / 180) * h;
          const chosen = earth && p === earth;

          ctx.beginPath();
          ctx.arc(px, py, chosen ? 7 : 2.4, 0, Math.PI * 2);
          ctx.fillStyle = chosen ? "#ffdc62" : "#59d6b5";
          ctx.fill();
          if (chosen) {
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.stroke();
          }
        }
      }

      ctx.strokeStyle = "#dce7f7";
      ctx.strokeRect(x, y, w, h);
      ctx.fillStyle = "#eaf1fa";
      ctx.font = "12px Arial";
      ctx.fillText("Ã¢â€”Â Earth reference tiles", 15, 345);
      ctx.fillStyle = "#ffdc62";
      ctx.fillText("Ã¢â€”Â Selected Earth location", 175, 345);
    }

    return !!(target || earthMap);
  }

  // Keep the existing analysis logic, then refresh maps after every selection.
  if (typeof pdAnalyze === "function" && !window.__pdMapAnalyzeWrapped) {
    const originalAnalyze = pdAnalyze;
    pdAnalyze = function () {
      const result = originalAnalyze.apply(this, arguments);
      requestAnimationFrame(() => {
        pdForceDrawMaps();
        if (typeof pdDrawDiscoveryGraphs === "function" &&
            typeof pdCandidates !== "undefined") {
          const select = document.getElementById("pd-place");
          const earth = select && select.value !== ""
            ? pdCandidates[Number(select.value)] : null;
          if (earth) {
            // The original analysis function already updates the graphs.
            // This call ensures they refresh for the newly selected location.
          }
        }
      });
      return result;
    };
    window.__pdMapAnalyzeWrapped = true;
  }

  document.addEventListener("change", function (event) {
    if (event.target && event.target.id === "pd-place") {
      requestAnimationFrame(pdForceDrawMaps);
    }
  });

  // Draw once data is already loaded; analysis redraws them after selection.
  document.addEventListener("DOMContentLoaded", function () {
    requestAnimationFrame(pdForceDrawMaps);
  });

  setTimeout(pdForceDrawMaps, 500);
  setTimeout(pdForceDrawMaps, 1500);
})();

// TERRATIME4D_LOCATION_MAP_V2
(function () {
  function getGridValue(grid, key, r, c) {
    const a = grid && grid[key];
    if (!a || !a[r] || a[r][c] === undefined) return NaN;
    const n = Number(a[r][c]);
    return Number.isFinite(n) ? n : NaN;
  }

  function isValidCell(grid, r, c) {
    if (!grid) return false;
    if (grid.valid && grid.valid[r]) return !!grid.valid[r][c];
    return Number.isFinite(getGridValue(grid, "slope_degrees", r, c));
  }

  function terrainColor(v, lo, hi) {
    if (!Number.isFinite(v)) return "#111b2a";
    const colors = [
      [15, 37, 72], [22, 91, 130], [37, 145, 143],
      [126, 171, 111], [210, 170, 94], [245, 226, 181]
    ];
    const t = Math.max(0, Math.min(0.9999, (v - lo) / (hi - lo || 1)));
    const p = t * (colors.length - 1);
    const i = Math.floor(p);
    const f = p - i;
    const rgb = colors[i].map((x, k) =>
      Math.round(x + (colors[i + 1][k] - x) * f)
    );
    return "rgb(" + rgb.join(",") + ")";
  }

  function getMatches(grid, earth) {
    const found = [];
    if (!grid || !earth) return found;

    for (let r = 0; r < 180; r++) {
      for (let c = 0; c < 360; c++) {
        if (!isValidCell(grid, r, c)) continue;

        const slope = getGridValue(grid, "slope_degrees", r, c);
        if (!Number.isFinite(slope)) continue;

        found.push({
          row: r,
          col: c,
          slope: slope,
          latitude: 89.5 - r,
          longitude: c - 179.5,
          difference: Math.abs(slope - Number(earth.slope))
        });
      }
    }

    found.sort((a, b) => a.difference - b.difference);
    return found.slice(0, 10);
  }

  function drawRegionalMap(ctx, grid, earth, body, x, y, w, h, color) {
    ctx.fillStyle = "#101b2c";
    ctx.fillRect(x, y, w, h);

    if (!grid) {
      ctx.fillStyle = "#fff";
      ctx.fillText(body + " local dataset not loaded", x + 12, y + 25);
      return;
    }

    const matches = getMatches(grid, earth);
    if (!matches.length) {
      ctx.fillStyle = "#fff";
      ctx.fillText("No valid terrain cells found", x + 12, y + 25);
      return;
    }

    // Zoom around the best matching planetary grid cell.
    const best = matches[0];
    const rowRadius = 18;
    const colRadius = 28;
    const startRow = Math.max(0, best.row - rowRadius);
    const endRow = Math.min(179, best.row + rowRadius);
    const startCol = best.col - colRadius;
    const endCol = best.col + colRadius;

    let min = Infinity, max = -Infinity;
    for (let r = startRow; r <= endRow; r++) {
      for (let c = startCol; c <= endCol; c++) {
        const cc = (c + 360) % 360;
        if (!isValidCell(grid, r, cc)) continue;
        const v = getGridValue(grid, "slope_degrees", r, cc);
        if (!Number.isFinite(v)) continue;
        min = Math.min(min, v);
        max = Math.max(max, v);
      }
    }
    if (!Number.isFinite(min)) { min = 0; max = 10; }
    if (max <= min) max = min + 1;

    const cols = endCol - startCol + 1;
    const rows = endRow - startRow + 1;
    const cellW = w / cols;
    const cellH = (h - 62) / rows;

    for (let r = startRow; r <= endRow; r++) {
      for (let c = startCol; c <= endCol; c++) {
        const cc = (c + 360) % 360;
        const v = isValidCell(grid, r, cc)
          ? getGridValue(grid, "slope_degrees", r, cc) : NaN;

        ctx.fillStyle = terrainColor(v, min, max);
        ctx.fillRect(
          x + (c - startCol) * cellW,
          y + 34 + (r - startRow) * cellH,
          cellW + 0.5,
          cellH + 0.5
        );
      }
    }

    // Draw the ten best matching cells.
    matches.forEach((m, i) => {
      const px = x + (m.col - startCol) * cellW + cellW / 2;
      const py = y + 34 + (m.row - startRow) * cellH + cellH / 2;

      if (px < x || px > x + w || py < y + 34 || py > y + h - 28) return;

      ctx.beginPath();
      ctx.arc(px, py, i === 0 ? 7 : 4, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 1.5;
      ctx.stroke();
    });

    ctx.strokeStyle = "#d9e7fa";
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y + 34, w, h - 62);

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 15px Arial";
    ctx.fillText(body + " Ã¢â‚¬â€ LOCATION-SPECIFIC ANALOGUE", x + 8, y + 20);

    ctx.font = "12px Arial";
    ctx.fillStyle = color;
    ctx.fillText(
      "Best match: " + best.latitude.toFixed(1) + "Ã‚Â°, " +
      best.longitude.toFixed(1) + "Ã‚Â°",
      x + 8, y + h - 12
    );
    ctx.fillStyle = "#ffffff";
    ctx.fillText(
      "Slope difference: " + best.difference.toFixed(3) + "Ã‚Â°",
      x + 230, y + h - 12
    );
  }

  function drawEarthReference(ctx, candidates, selected, x, y, w, h) {
    ctx.fillStyle = "#101b2c";
    ctx.fillRect(x, y, w, h);

    // Earth reference tile positions from the local CSV-derived catalogue.
    ctx.strokeStyle = "rgba(255,255,255,0.18)";
    for (let lon = 0; lon <= 360; lon += 30) {
      const px = x + lon / 360 * w;
      ctx.beginPath();
      ctx.moveTo(px, y);
      ctx.lineTo(px, y + h);
      ctx.stroke();
    }
    for (let lat = 0; lat <= 180; lat += 30) {
      const py = y + lat / 180 * h;
      ctx.beginPath();
      ctx.moveTo(x, py);
      ctx.lineTo(x + w, py);
      ctx.stroke();
    }

    (candidates || []).forEach(p => {
      const lat = Number(p.latitude);
      const lon = Number(p.longitude);
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;

      const px = x + (lon + 180) / 360 * w;
      const py = y + (90 - lat) / 180 * h;
      const active = p === selected;

      ctx.beginPath();
      ctx.arc(px, py, active ? 7 : 2.2, 0, Math.PI * 2);
      ctx.fillStyle = active ? "#ffdb61" : "#55d8b4";
      ctx.fill();

      if (active) {
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.stroke();
      }
    });

    ctx.strokeStyle = "#dce8f8";
    ctx.strokeRect(x, y, w, h);
  }

  function renderLocationMaps() {
    if (typeof pdData === "undefined" || !pdData ||
        !pdData.planets || typeof pdCandidates === "undefined") return;

    const selector = document.getElementById("pd-place");
    const selected = selector && selector.value !== ""
      ? pdCandidates[Number(selector.value)] : null;

    const canvas = document.getElementById("pd-target-map");
    if (!canvas) return;

    canvas.style.display = "block";
    canvas.style.visibility = "visible";
    canvas.style.width = "100%";
    canvas.style.height = "auto";
    canvas.style.minHeight = "400px";
    canvas.style.background = "#101b2c";

    const width = Math.max(900, canvas.parentElement
      ? canvas.parentElement.clientWidth : 900);
    const height = 500;
    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.fillStyle = "#101b2c";
    ctx.fillRect(0, 0, width, height);

    if (!selected) {
      ctx.fillStyle = "#ffffff";
      ctx.font = "bold 19px Arial";
      ctx.fillText("SELECT AN EARTH LOCATION TO GENERATE PLANETARY MAPS", 20, 35);
      ctx.font = "14px Arial";
      ctx.fillText("Maps will update using the local Moon and Mars terrain grids.", 20, 65);
      return;
    }

    const gap = 20;
    const panelW = (width - 3 * gap) / 2;
    const panelH = 420;

    drawRegionalMap(
      ctx, pdData.planets.Moon || pdData.planets.moon,
      selected, "MOON", gap, 55, panelW, panelH, "#ffdc61"
    );

    drawRegionalMap(
      ctx, pdData.planets.Mars || pdData.planets.mars,
      selected, "MARS", 2 * gap + panelW, 55,
      panelW, panelH, "#64e6ff"
    );

    ctx.fillStyle = "#ffffff";
    ctx.font = "13px Arial";
    ctx.fillText(
      "Earth input: " + selected.name + " | " +
      Number(selected.latitude).toFixed(2) + "Ã‚Â°, " +
      Number(selected.longitude).toFixed(2) + "Ã‚Â°",
      20, 25
    );

    // Earth reference map.
    const earthCanvas = document.getElementById("pd-earth-map");
    if (earthCanvas) {
      earthCanvas.style.display = "block";
      earthCanvas.style.visibility = "visible";
      earthCanvas.style.width = "100%";
      earthCanvas.style.height = "auto";
      earthCanvas.width = width;
      earthCanvas.height = 300;

      const ectx = earthCanvas.getContext("2d");
      if (ectx) {
        ectx.fillStyle = "#101b2c";
        ectx.fillRect(0, 0, width, 300);
        drawEarthReference(
          ectx, pdCandidates, selected, 12, 12, width - 24, 260
        );
        ectx.fillStyle = "#ffffff";
        ectx.font = "13px Arial";
        ectx.fillText(
          "Local Earth reference tiles Ã¢â‚¬â€ selected location highlighted",
          14, 292
        );
      }
    }
  }

  // Connect the map renderer to the existing location analysis.
  function installMapHooks() {
    if (typeof pdAnalyze === "function" && !window.__pdLocationMapHook) {
      const original = pdAnalyze;
      pdAnalyze = function () {
        const result = original.apply(this, arguments);
        requestAnimationFrame(renderLocationMaps);
        setTimeout(renderLocationMaps, 250);
        return result;
      };
      window.__pdLocationMapHook = true;
    }

    const selector = document.getElementById("pd-place");
    if (selector && !selector.__pdMapChangeHook) {
      selector.addEventListener("change", () => {
        requestAnimationFrame(renderLocationMaps);
      });
      selector.__pdMapChangeHook = true;
    }

    renderLocationMaps();
  }

  document.addEventListener("DOMContentLoaded", installMapHooks);
  window.addEventListener("load", installMapHooks);
  setTimeout(installMapHooks, 500);
  setTimeout(installMapHooks, 1500);
  setTimeout(installMapHooks, 3000);
})();

// TERRATIME4D_OFFLINE_MAP_GRAPH_FINAL
(function () {
  const $ = id => document.getElementById(id);

  function gridValue(grid, key, r, c) {
    const a = grid && grid[key];
    if (!a || !a[r] || a[r][c] === undefined) return NaN;
    const n = Number(a[r][c]);
    return Number.isFinite(n) ? n : NaN;
  }

  function validCell(grid, r, c) {
    if (!grid) return false;
    if (grid.valid && grid.valid[r]) return !!grid.valid[r][c];
    return Number.isFinite(gridValue(grid, "slope_degrees", r, c));
  }

  function canvasSetup(id, height) {
    const el = $(id);
    if (!el) return null;

    el.style.display = "block";
    el.style.visibility = "visible";
    el.style.width = "100%";
    el.style.height = "auto";
    el.style.minHeight = height + "px";
    el.style.background = "#101827";
    el.style.border = "1px solid #43536b";
    el.style.borderRadius = "8px";

    const width = Math.max(650, el.parentElement?.clientWidth || 900);
    el.width = width;
    el.height = height;

    const ctx = el.getContext("2d");
    if (!ctx) return null;

    ctx.fillStyle = "#101827";
    ctx.fillRect(0, 0, width, height);
    return { el, ctx, width, height };
  }

  function color(v, min, max) {
    if (!Number.isFinite(v)) return "#172235";
    const t = Math.max(0, Math.min(1, (v - min) / (max - min || 1)));
    const stops = [
      [18, 43, 78], [24, 91, 132], [36, 145, 143],
      [134, 174, 105], [220, 174, 93], [244, 228, 190]
    ];
    const p = t * (stops.length - 1);
    const i = Math.min(stops.length - 2, Math.floor(p));
    const f = p - i;
    return "rgb(" + stops[i].map((v, k) =>
      Math.round(v + (stops[i + 1][k] - v) * f)
    ).join(",") + ")";
  }

  function matchesFor(grid, earth) {
    const result = [];
    if (!grid || !earth) return result;

    const rows = grid.slope_degrees?.length || 180;
    const cols = grid.slope_degrees?.[0]?.length || 360;

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        if (!validCell(grid, r, c)) continue;
        const slope = gridValue(grid, "slope_degrees", r, c);
        if (!Number.isFinite(slope)) continue;

        const roughness = gridValue(grid, "roughness_11km_km", r, c);
        result.push({
          row: r,
          col: c,
          lat: 90 - (r + 0.5) * 180 / rows,
          lon: (c + 0.5) * 360 / cols - 180,
          slope,
          roughness,
          difference: Math.abs(slope - Number(earth.slope))
        });
      }
    }

    result.sort((a, b) => a.difference - b.difference);
    return result.slice(0, 10);
  }

  function drawPlanetMap(ctx, grid, earth, x, y, w, h, title, markerColor) {
    ctx.fillStyle = "#172235";
    ctx.fillRect(x, y, w, h);

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 16px Arial";
    ctx.fillText(title, x + 8, y + 20);

    if (!grid || !grid.slope_degrees) {
      ctx.font = "13px Arial";
      ctx.fillText("Local planetary grid not loaded.", x + 10, y + 50);
      return;
    }

    const rows = grid.slope_degrees.length;
    const cols = grid.slope_degrees[0]?.length || 0;
    if (!rows || !cols) return;

    let min = Infinity, max = -Infinity;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        if (!validCell(grid, r, c)) continue;
        const v = gridValue(grid, "slope_degrees", r, c);
        if (!Number.isFinite(v)) continue;
        min = Math.min(min, v);
        max = Math.max(max, v);
      }
    }

    if (!Number.isFinite(min)) { min = 0; max = 10; }
    if (max <= min) max = min + 1;

    const top = y + 32;
    const mapH = h - 62;
    const cw = w / cols;
    const ch = mapH / rows;

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const v = validCell(grid, r, c)
          ? gridValue(grid, "slope_degrees", r, c) : NaN;
        ctx.fillStyle = color(v, min, max);
        ctx.fillRect(x + c * cw, top + r * ch, cw + 0.5, ch + 0.5);
      }
    }

    const matches = matchesFor(grid, earth);
    matches.forEach((m, i) => {
      const px = x + (m.col + 0.5) * cw;
      const py = top + (m.row + 0.5) * ch;
      ctx.beginPath();
      ctx.arc(px, py, i === 0 ? 7 : 4, 0, Math.PI * 2);
      ctx.fillStyle = markerColor;
      ctx.fill();
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 1.5;
      ctx.stroke();
    });

    ctx.strokeStyle = "#ffffff";
    ctx.strokeRect(x, top, w, mapH);

    ctx.font = "11px Arial";
    ctx.fillStyle = "#ffffff";
    ctx.fillText("90Ã‚Â°N", x + 3, top + 12);
    ctx.fillText("90Ã‚Â°S", x + 3, top + mapH - 3);

    if (matches.length) {
      ctx.fillStyle = markerColor;
      ctx.font = "12px Arial";
      ctx.fillText(
        "Best match: " + matches[0].lat.toFixed(1) + "Ã‚Â°, " +
        matches[0].lon.toFixed(1) + "Ã‚Â° | Slope difference: " +
        matches[0].difference.toFixed(2) + "Ã‚Â°",
        x + 6, y + h - 8
      );
    }
  }

  function drawEarthMap(earth) {
    const box = canvasSetup("pd-earth-map", 300);
    if (!box) return;

    const { ctx, width } = box;
    const x = 12, y = 12, w = width - 24, h = 250;

    ctx.fillStyle = "#172235";
    ctx.fillRect(x, y, w, h);

    ctx.strokeStyle = "rgba(255,255,255,.2)";
    for (let lon = 0; lon <= 360; lon += 30) {
      const px = x + lon / 360 * w;
      ctx.beginPath(); ctx.moveTo(px, y); ctx.lineTo(px, y + h); ctx.stroke();
    }
    for (let lat = 0; lat <= 180; lat += 30) {
      const py = y + lat / 180 * h;
      ctx.beginPath(); ctx.moveTo(x, py); ctx.lineTo(x + w, py); ctx.stroke();
    }

    if (typeof pdCandidates !== "undefined") {
      pdCandidates.forEach(p => {
        const lat = Number(p.latitude), lon = Number(p.longitude);
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;

        const px = x + (lon + 180) / 360 * w;
        const py = y + (90 - lat) / 180 * h;
        const active = p === earth;

        ctx.beginPath();
        ctx.arc(px, py, active ? 7 : 2.5, 0, Math.PI * 2);
        ctx.fillStyle = active ? "#ffdc60" : "#55d8b4";
        ctx.fill();
        if (active) {
          ctx.strokeStyle = "#ffffff";
          ctx.lineWidth = 2;
          ctx.stroke();
        }
      });
    }

    ctx.strokeStyle = "#ffffff";
    ctx.strokeRect(x, y, w, h);
    ctx.fillStyle = "#ffffff";
    ctx.font = "12px Arial";
    ctx.fillText("Local Earth reference tile locations", 14, 284);
  }

  function drawLineGraph(id, title, labels, series, unit) {
    const box = canvasSetup(id, 290);
    if (!box) return;

    const { ctx, width, height } = box;
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 15px Arial";
    ctx.fillText(title, 14, 22);

    const left = 55, right = width - 20, top = 45, bottom = height - 48;
    const all = series.flatMap(s => s.values).filter(Number.isFinite);
    if (!all.length) {
      ctx.font = "13px Arial";
      ctx.fillText("Select an Earth location to display comparison.", 15, 65);
      return;
    }

    let min = Math.min(0, ...all);
    let max = Math.max(...all);
    if (max <= min) max = min + 1;
    const pad = (max - min) * 0.12;
    min -= pad; max += pad;

    ctx.strokeStyle = "rgba(255,255,255,.2)";
    ctx.fillStyle = "#dce7f5";
    ctx.font = "11px Arial";

    for (let i = 0; i <= 4; i++) {
      const yy = bottom - i / 4 * (bottom - top);
      ctx.beginPath();
      ctx.moveTo(left, yy);
      ctx.lineTo(right, yy);
      ctx.stroke();
      ctx.fillText((min + i / 4 * (max - min)).toFixed(2), 5, yy + 4);
    }

    series.forEach((s, si) => {
      const usable = s.values.map((v, i) => ({ v, i }))
        .filter(p => Number.isFinite(p.v));
      if (!usable.length) return;

      const colors = ["#ffcf58", "#54d7ff", "#71e0a0"];
      ctx.strokeStyle = colors[si % colors.length];
      ctx.fillStyle = colors[si % colors.length];
      ctx.lineWidth = 2;
      ctx.beginPath();

      usable.forEach((p, j) => {
        const px = left + (labels.length <= 1 ? 0 :
          p.i / (labels.length - 1) * (right - left));
        const py = bottom - (p.v - min) / (max - min) * (bottom - top);
        if (j === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
        ctx.fillRect(px - 3, py - 3, 6, 6);
      });
      ctx.stroke();

      const lx = left + si * 155;
      ctx.fillRect(lx, height - 20, 10, 3);
      ctx.fillText(s.name + " (" + unit + ")", lx + 15, height - 16);
    });

    labels.forEach((label, i) => {
      if (labels.length > 10 && i % Math.ceil(labels.length / 10) !== 0) return;
      const px = left + (labels.length <= 1 ? 0 :
        i / (labels.length - 1) * (right - left));
      ctx.fillStyle = "#dce7f5";
      ctx.fillText(label, px - 12, bottom + 17);
    });
  }

  function renderAll() {
    if (typeof pdData === "undefined" || !pdData ||
        !pdData.planets || typeof pdCandidates === "undefined") return;

    const selector = $("pd-place");
    const earth = selector && selector.value !== ""
      ? pdCandidates[Number(selector.value)] : null;

    const map = canvasSetup("pd-target-map", 490);
    if (map) {
      const gap = 18;
      const panelW = (map.width - 3 * gap) / 2;
      drawPlanetMap(
        map.ctx, pdData.planets.Moon || pdData.planets.moon,
        earth, gap, 35, panelW, 420, "MOON Ã¢â‚¬â€ GLOBAL TERRAIN", "#ffdc60"
      );
      drawPlanetMap(
        map.ctx, pdData.planets.Mars || pdData.planets.mars,
        earth, 2 * gap + panelW, 35, panelW, 420,
        "MARS Ã¢â‚¬â€ GLOBAL TERRAIN", "#54d7ff"
      );
      if (!earth) {
        map.ctx.fillStyle = "#ffffff";
        map.ctx.font = "bold 16px Arial";
        map.ctx.fillText("Choose an Earth location to highlight its planetary analogues.", 18, 480);
      }
    }

    drawEarthMap(earth);

    const moon = pdData.planets.Moon || pdData.planets.moon;
    const mars = pdData.planets.Mars || pdData.planets.mars;
    const mm = matchesFor(moon, earth);
    const ma = matchesFor(mars, earth);

    const labels = Array.from({ length: 10 }, (_, i) => "Match " + (i + 1));
    const selectedSlope = earth ? Number(earth.slope) : NaN;

    drawLineGraph("pd-earth-moon-chart", "EARTH vs MOON Ã¢â‚¬â€ SLOPE", labels, [
      { name: "Earth", values: labels.map(() => selectedSlope) },
      { name: "Moon", values: mm.map(m => m.slope) }
    ], "degrees");

    drawLineGraph("pd-earth-mars-chart", "EARTH vs MARS Ã¢â‚¬â€ SLOPE", labels, [
      { name: "Earth", values: labels.map(() => selectedSlope) },
      { name: "Mars", values: ma.map(m => m.slope) }
    ], "degrees");

    drawLineGraph("pd-similarity-chart", "TOP MATCH SLOPE DIFFERENCE", labels, [
      { name: "Moon", values: mm.map(m => m.difference) },
      { name: "Mars", values: ma.map(m => m.difference) }
    ], "degrees");

    drawLineGraph("pd-parameter-chart", "PLANETARY MATCH ROUGHNESS", labels, [
      { name: "Moon", values: mm.map(m => m.roughness * 1000) },
      { name: "Mars", values: ma.map(m => m.roughness * 1000) }
    ], "metres");
  }

  function install() {
    if (typeof pdAnalyze === "function" && !window.__pdFinalGraphHook) {
      const original = pdAnalyze;
      pdAnalyze = function () {
        const result = original.apply(this, arguments);
        requestAnimationFrame(renderAll);
        setTimeout(renderAll, 300);
        return result;
      };
      window.__pdFinalGraphHook = true;
    }

    const selector = $("pd-place");
    if (selector && !selector.__pdFinalMapHook) {
      selector.addEventListener("change", () => requestAnimationFrame(renderAll));
      selector.__pdFinalMapHook = true;
    }

    renderAll();
  }

  document.addEventListener("DOMContentLoaded", install);
  window.addEventListener("load", install);
  setTimeout(install, 500);
  setTimeout(install, 1500);
  setTimeout(install, 3000);
  setTimeout(install, 5000);
})();

// ============================================================
// TERRATIME4D SECOND-ROW MOON / MARS MAP FIX V3
// Uses existing offline planetary grids and selected Earth data.
// ============================================================
(function () {
  if (window.__pdMatchMapsFixV3) return;
  window.__pdMatchMapsFixV3 = true;

  function pdV3GetMatches(planetName, earth) {
    const grid = pdData && pdData.planets && pdData.planets[planetName];
    if (!grid || !grid.valid || !grid.slope_degrees) return [];

    const matches = [];
    const height = grid.height || grid.valid.length;
    const width = grid.width || (grid.valid[0] ? grid.valid[0].length : 0);

    for (let row = 0; row < height; row++) {
      if (!grid.valid[row] || !grid.slope_degrees[row]) continue;

      for (let col = 0; col < width; col++) {
        if (!grid.valid[row][col]) continue;

        const slope = Number(grid.slope_degrees[row][col]);
        if (!Number.isFinite(slope)) continue;

        const roughness = Number(
          grid.roughness_11km_km &&
          grid.roughness_11km_km[row]
            ? grid.roughness_11km_km[row][col]
            : NaN
        );

        const difference = Math.abs(slope - Number(earth.slope));
        const score = 100 / (1 + difference / 5);

        matches.push({
          latitude: 89.5 - row,
          longitude: col - 179.5,
          slope: slope,
          roughness: roughness,
          score: score
        });
      }
    }

    matches.sort((a, b) => b.score - a.score);
    return matches.slice(0, 10);
  }

  function pdV3DrawMatchMap(canvasId, planetName, matches) {
    const canvas = document.getElementById(canvasId);
    const grid = pdData && pdData.planets && pdData.planets[planetName];

    if (!canvas) return;

    canvas.width = 720;
    canvas.height = 360;
    canvas.style.display = "block";
    canvas.style.width = "100%";
    canvas.style.height = "auto";
    canvas.style.minHeight = "180px";
    canvas.style.background = "#101827";

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.fillStyle = "#101827";
    ctx.fillRect(0, 0, 720, 360);

    if (!grid || !grid.valid || !grid.slope_degrees) {
      ctx.fillStyle = "#ffffff";
      ctx.font = "18px Arial";
      ctx.fillText("Local " + planetName + " grid unavailable", 25, 45);
      return;
    }

    const height = grid.height || grid.valid.length;
    const width = grid.width || (grid.valid[0] ? grid.valid[0].length : 0);

    let min = Infinity;
    let max = -Infinity;

    for (let row = 0; row < height; row++) {
      if (!grid.valid[row] || !grid.slope_degrees[row]) continue;

      for (let col = 0; col < width; col++) {
        if (!grid.valid[row][col]) continue;
        const value = Number(grid.slope_degrees[row][col]);
        if (!Number.isFinite(value)) continue;
        min = Math.min(min, value);
        max = Math.max(max, value);
      }
    }

    if (!Number.isFinite(min) || !Number.isFinite(max)) {
      ctx.fillStyle = "#ffffff";
      ctx.font = "18px Arial";
      ctx.fillText("No valid slope values available", 25, 45);
      return;
    }

    // Draw the actual global slope grid.
    for (let row = 0; row < height; row++) {
      if (!grid.valid[row] || !grid.slope_degrees[row]) continue;

      const y1 = Math.floor(row * 360 / height);
      const y2 = Math.ceil((row + 1) * 360 / height);

      for (let col = 0; col < width; col++) {
        if (!grid.valid[row][col]) continue;

        const value = Number(grid.slope_degrees[row][col]);
        if (!Number.isFinite(value)) continue;

        const t = max === min ? 0.5 : (value - min) / (max - min);

        const red = Math.round(25 + 220 * t);
        const green = Math.round(115 - 65 * t);
        const blue = Math.round(225 - 180 * t);

        ctx.fillStyle = "rgb(" + red + "," + green + "," + blue + ")";

        const x1 = Math.floor(col * 720 / width);
        const x2 = Math.ceil((col + 1) * 720 / width);

        ctx.fillRect(
          x1,
          y1,
          Math.max(1, x2 - x1),
          Math.max(1, y2 - y1)
        );
      }
    }

    // Map border and equator.
    ctx.strokeStyle = "rgba(255,255,255,0.35)";
    ctx.lineWidth = 1;
    ctx.strokeRect(0, 0, 719, 359);

    ctx.beginPath();
    ctx.moveTo(0, 180);
    ctx.lineTo(720, 180);
    ctx.stroke();

    // Highlight the ten best matching locations.
    (matches || []).forEach(function (point, index) {
      const x = ((point.longitude + 180) / 360) * 720;
      const y = ((90 - point.latitude) / 180) * 360;

      ctx.beginPath();
      ctx.arc(x, y, 7, 0, Math.PI * 2);
      ctx.fillStyle = "#ff3030";
      ctx.fill();

      ctx.lineWidth = 2;
      ctx.strokeStyle = "#ffffff";
      ctx.stroke();

      ctx.fillStyle = "#ffffff";
      ctx.font = "bold 12px Arial";
      ctx.fillText(String(index + 1), x + 9, y - 7);
    });

    // Map title and legend.
    ctx.fillStyle = "rgba(10,15,25,0.85)";
    ctx.fillRect(8, 8, 285, 43);

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 15px Arial";
    ctx.fillText(planetName.toUpperCase() + " GLOBAL SLOPE MAP", 17, 26);

    ctx.font = "12px Arial";
    ctx.fillText("Top 10 selected-Earth analogues: red markers", 17, 43);

    ctx.fillStyle = "#ffffff";
    ctx.font = "12px Arial";
    ctx.fillText("0Ã‚Â°", 5, 354);
    ctx.fillText("180Ã‚Â°", 350, 354);
    ctx.fillText("360Ã‚Â°", 680, 354);
  }

  function pdV3Refresh() {
    if (!pdData || !Array.isArray(pdCandidates)) return;

    const selector = document.getElementById("pd-place");
    if (!selector || selector.value === "") return;

    const earth = pdCandidates[Number(selector.value)];
    if (!earth) return;

    const moonMatches = pdV3GetMatches("Moon", earth);
    const marsMatches = pdV3GetMatches("Mars", earth);

    pdV3DrawMatchMap("pd-moon-match-map", "Moon", moonMatches);
    pdV3DrawMatchMap("pd-mars-match-map", "Mars", marsMatches);

    // Refresh all existing comparison graphs using the same selected Earth.
    if (typeof pdDrawDiscoveryGraphs === "function") {
      pdDrawDiscoveryGraphs(earth, moonMatches, marsMatches);
    }

    const subtitle = document.getElementById("pd-graph-subtitle");
    if (subtitle) {
      subtitle.textContent =
        "Location: " + (earth.name || "Selected Earth location") +
        " | Moon and Mars top 10 terrain analogues";
    }
  }

  // Wrap the existing analysis without replacing its calculations or tables.
  if (typeof pdAnalyze === "function" && !window.__pdV3AnalyzeWrapped) {
    const previousAnalyze = pdAnalyze;

    pdAnalyze = function () {
      let result;

      try {
        result = previousAnalyze.apply(this, arguments);
      } finally {
        requestAnimationFrame(pdV3Refresh);
        setTimeout(pdV3Refresh, 250);
        setTimeout(pdV3Refresh, 800);
      }

      return result;
    };

    window.__pdV3AnalyzeWrapped = true;
  }

  // Refresh whenever the selected Earth location changes.
  const placeSelector = document.getElementById("pd-place");

  if (placeSelector && !placeSelector.__pdV3MapListener) {
    placeSelector.addEventListener("change", function () {
      setTimeout(pdV3Refresh, 100);
    });
    placeSelector.__pdV3MapListener = true;
  }

  // Initial rendering if a location is already selected.
  document.addEventListener("DOMContentLoaded", pdV3Refresh);
  window.addEventListener("load", pdV3Refresh);
  setTimeout(pdV3Refresh, 500);
  setTimeout(pdV3Refresh, 1500);
})();

