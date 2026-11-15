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
  <p>Select a location on the Moon or Mars, inspect its global terrain data, and discover similar measured terrain references on Earth.</p>

  <div class="pd-controls">
    <label>Target planet
      <select id="pd-planet"><option>Moon</option><option>Mars</option></select>
    </label>
    <label>Latitude (degrees)
      <input id="pd-lat" type="number" min="-90" max="90" step="0.1" value="0">
    </label>
    <label>Longitude (degrees)
      <input id="pd-lon" type="number" min="-180" max="180" step="0.1" value="0">
    </label>
    <label>Search location
      <button id="pd-analyze">ANALYZE LOCATION</button>
    </label>
  </div>

  <div class="pd-map-grid">
    <div class="pd-panel">
      <h3 id="pd-target-title">GLOBAL MOON ELEVATION — SELECT A LOCATION</h3>
      <canvas id="pd-target-map" width="720" height="360"></canvas>
      <p>Click anywhere on this map to select a planetary coordinate. Map is a 1° browsing grid.</p>
    </div>
    <div class="pd-panel">
      <h3>EARTH REFERENCE DISTRIBUTION — 648 RECORDS</h3>
      <canvas id="pd-earth-map" width="720" height="360"></canvas>
      <p>Dots represent available Earth reference tile coordinates. They do not represent continuous DEM coverage.</p>
    </div>
  </div>

  <div class="pd-stats" id="pd-stats">
    <div class="pd-stat"><small>MEAN ELEVATION</small><strong id="pd-elevation">—</strong></div>
    <div class="pd-stat"><small>MEAN SLOPE</small><strong id="pd-slope">—</strong></div>
    <div class="pd-stat"><small>ROUGHNESS (~11 KM)</small><strong id="pd-roughness">—</strong></div>
  </div>

  <div class="pd-panel">
    <h3>RANKED EARTH TERRAIN ANALOGUES</h3>
    <div id="pd-status" class="pd-status">Loading local planetary grids and Earth reference records…</div>
    <div style="overflow-x:auto">
      <table class="pd-results">
        <thead><tr><th>Rank</th><th>Earth reference</th><th>Coordinates</th><th>Slope</th><th>Earth roughness (1.35 km; not ranked)</th><th>Screening score</th></tr></thead>
        <tbody id="pd-results"><tr><td colspan="6">Waiting for local data…</td></tr></tbody>
      </table>
    </div>
  </div>
  <div class="pd-note">
    SCIENTIFIC LIMITATION: Earth slope and roughness measurements use different native spatial scales from the planetary grids. The displayed slope similarity index is a preliminary screening measure, not a probability or validated scientific equivalence. Roughness is displayed separately and excluded from ranking because the spatial scales differ. Elevation is excluded because planetary elevation datums differ. Earth results are limited to the 648 available reference tiles.
  </div>
`;
const existingComparison = document.getElementById("planetary-comparison");
if (existingComparison) existingComparison.after(discovery);
else document.body.appendChild(discovery);

const comparisonFooter = existingComparison?.querySelector(".pc-footer");
if (comparisonFooter) {
  comparisonFooter.textContent =
    "COMPARISON COMPLETE · CONTINUE SCROLLING BELOW FOR PLANETARY ANALOG DISCOVERY";
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
  const headers = rows.shift();
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
  if (!pdData) return;
  const name = document.getElementById("pd-planet").value;
  const planet = pdData.planets[name];
  const canvas = document.getElementById("pd-target-map");
  const ctx = canvas.getContext("2d");
  const values = planet.elevation_km.flat().filter(Number.isFinite);
  const sorted = [...values].sort((a,b) => a-b);
  const min = sorted[Math.floor(sorted.length * .02)];
  const max = sorted[Math.floor(sorted.length * .98)];
  const image = ctx.createImageData(360,180);

  for (let y=0; y<180; y++) {
    for (let x=0; x<360; x++) {
      const col=(x+180)%360;
      const color=pdColor(planet.elevation_km[y][col],min,max);
      const rgb=color.match(/\d+/g).map(Number);
      const k=(y*360+x)*4;
      image.data[k]=rgb[0];
      image.data[k+1]=rgb[1];
      image.data[k+2]=rgb[2];
      image.data[k+3]=255;
    }
  }

  const temp=document.createElement("canvas");
  temp.width=360;
  temp.height=180;
  temp.getContext("2d").putImageData(image,0,0);
  ctx.clearRect(0,0,720,360);
  ctx.imageSmoothingEnabled=true;
  ctx.drawImage(temp,0,0,720,360);

  if(pdTarget){
    const x=(pdTarget.lon+180)/360*720;
    const y=(90-pdTarget.lat)/180*360;
    ctx.fillStyle="#ffdf63";
    ctx.strokeStyle="#06111c";
    ctx.lineWidth=3;
    ctx.beginPath();
    ctx.arc(x,y,8,0,Math.PI*2);
    ctx.fill();
    ctx.stroke();
  }

  document.getElementById("pd-target-title").textContent =
    `GLOBAL ${name.toUpperCase()} ELEVATION — CLICK TO SELECT`;
}

function pdDrawEarthMap() {
  const canvas=document.getElementById("pd-earth-map");
  const ctx=canvas.getContext("2d");
  ctx.fillStyle="#081624";
  ctx.fillRect(0,0,720,360);
  ctx.strokeStyle="#24465c";
  ctx.lineWidth=1;

  for(let x=0;x<=720;x+=120){
    ctx.beginPath();
    ctx.moveTo(x,0);
    ctx.lineTo(x,360);
    ctx.stroke();
  }

  for(let y=0;y<=360;y+=90){
    ctx.beginPath();
    ctx.moveTo(0,y);
    ctx.lineTo(720,y);
    ctx.stroke();
  }

  ctx.fillStyle="#55d7ff";
  for(const r of pdEarth){
    const x=(r.lon+180)/360*720;
    const y=(90-r.lat)/180*360;
    ctx.fillRect(x-2,y-2,4,4);
  }
}

function pdAnalyze() {
  if(!pdData || !pdEarth.length) return;

  const name=document.getElementById("pd-planet").value;
  const lat=Number(document.getElementById("pd-lat").value);
  const lon=Number(document.getElementById("pd-lon").value);

  if(!Number.isFinite(lat)||!Number.isFinite(lon)||
     lat < -90||lat > 90||lon < -180||lon > 180){
    document.getElementById("pd-status").textContent =
      "Enter a valid latitude (-90 to 90) and longitude (-180 to 180).";
    return;
  }

  const planet=pdData.planets[name];
  const stats=pdRegionStats(planet,lat,lon);

  if(!stats){
    document.getElementById("pd-status").textContent =
      "No valid planetary terrain cells were found in this regional window. Select another location.";
    return;
  }

  pdTarget={lat,lon};
  document.getElementById("pd-elevation").textContent =
    stats.elevation.toFixed(3)+" km";
  document.getElementById("pd-slope").textContent =
    stats.slope.toFixed(2)+"°";
  document.getElementById("pd-roughness").textContent =
    (stats.roughness*1000).toFixed(1)+" m";

  pdDrawPlanetMap();

  // Slope-only screening: roughness is displayed separately because
  // Earth and planetary roughness measurements use different scales.
  const ranked=pdEarth.map(r=>{
    const slopeDiff=Math.abs(r.slope-stats.slope);
    const score=100/(1+(slopeDiff/5));
    return {...r,score,slopeDiff};
  }).sort((a,b)=>b.score-a.score).slice(0,10);

  document.getElementById("pd-results").innerHTML=ranked.map((r,i)=>`
    <tr>
      <td>${i+1}</td>
      <td>${r.name}</td>
      <td>${r.lat.toFixed(1)}°, ${r.lon.toFixed(1)}°</td>
      <td>${r.slope.toFixed(2)}°</td>
      <td>${r.rough.toFixed(2)} m</td>
      <td>${r.score.toFixed(1)}/100</td>
    </tr>`).join("");

  document.getElementById("pd-status").textContent =
    `${name} regional analysis at ${lat.toFixed(2)}°, ${lon.toFixed(2)}°: `+
    `${stats.cells} valid 1° grid cells analyzed. `+
    `Ranked ${pdEarth.length} available Earth references by slope similarity. `+
    `This is a preliminary screening index, not a validated analogue probability.`;
}
document.getElementById("pd-target-map").addEventListener("click",e=>{
  const rect=e.currentTarget.getBoundingClientRect();
  const x=(e.clientX-rect.left)/rect.width;
  const y=(e.clientY-rect.top)/rect.height;
  const lon=x*360-180,lat=90-y*180;
  document.getElementById("pd-lat").value=lat.toFixed(2);
  document.getElementById("pd-lon").value=lon.toFixed(2);
  pdAnalyze();
});
document.getElementById("pd-analyze").addEventListener("click",pdAnalyze);
document.getElementById("pd-planet").addEventListener("change",()=>{
  pdDrawPlanetMap();pdAnalyze();
});

Promise.all([
  fetch("/data/planetary/planetary_grids.json").then(r=>{if(!r.ok)throw Error("Planetary grids not found");return r.json();}),
  fetch("/data/earth/global_advanced_terrain_summary.csv").then(r=>{if(!r.ok)throw Error("Earth summary CSV not found");return r.text();})
]).then(([data,csv])=>{
  pdData=data;
  const rows=pdRecords(csv);
  pdEarth=rows.map(r=>{
    const m=r.location.match(/_(n|s)(\d+)_00_(e|w)(\d+)_00_/i);
    if(!m)return null;
    let lat=Number(m[2]),lon=Number(m[4]);
    if(m[1].toLowerCase()==="s")lat=-lat;
    if(m[3].toLowerCase()==="w")lon=-lon;
    return {name:r.location,lat,lon,slope:Number(r.slope_mean_degrees),rough:Number(r.roughness_1350m_mean)};
  }).filter(r=>r&&Number.isFinite(r.slope)&&Number.isFinite(r.rough));
  pdDrawEarthMap();pdDrawPlanetMap();pdAnalyze();
}).catch(err=>{
  document.getElementById("pd-status").textContent="Could not load local data: "+err.message;
});

