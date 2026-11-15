const EARTH_URL = "/data/earth/global_advanced_terrain_summary.csv";
const PLANET_URL = "/data/planetary/planetary_grids.json";

const W = 900, H = 450;

function esc(v) {
  return String(v).replace(/[&<>"']/g, c => ({
    "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"
  }[c]));
}

function csvParse(s) {
  const rows = [];
  let row = [], cell = "", quoted = false;

  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (c === '"' && quoted && s[i + 1] === '"') {
      cell += '"'; i++;
    } else if (c === '"') quoted = !quoted;
    else if (c === "," && !quoted) {
      row.push(cell); cell = "";
    } else if ((c === "\n" || c === "\r") && !quoted) {
      if (c === "\r" && s[i + 1] === "\n") i++;
      row.push(cell);
      if (row.some(x => x.trim())) rows.push(row);
      row = []; cell = "";
    } else cell += c;
  }
  row.push(cell);
  if (row.some(x => x.trim())) rows.push(row);

  const headers = rows.shift().map(x => x.trim().replace(/^\uFEFF/, ""));
  return rows.map(r => Object.fromEntries(headers.map((h, i) => [h, r[i] ?? ""])));
}

function earthCoordinates(row) {
  const src = String(row.location || row.raster_file || row.candidate || "");
  let lat = Number(row.latitude ?? row.lat);
  let lon = Number(row.longitude ?? row.lon);
  const m = src.match(/_(n|s)(\d{2})_00_(e|w)(\d{3})_00(?:_|$)/i);

  if (m) {
    lat = Number(m[2]) * (m[1].toLowerCase() === "s" ? -1 : 1);
    lon = Number(m[4]) * (m[3].toLowerCase() === "w" ? -1 : 1);
  }
  return {lat, lon, src};
}

function earthGraph(rows) {
  const pts = rows.map(earthCoordinates).filter(p =>
    Number.isFinite(p.lat) && Number.isFinite(p.lon) &&
    Math.abs(p.lat) <= 90 && Math.abs(p.lon) <= 180
  );

  if (!pts.length) throw Error("CSV loaded, but no valid Earth coordinates were found.");

  let grid = "";
  for (let lon = -180; lon <= 180; lon += 30) {
    const x = (lon + 180) / 360 * W;
    grid += `<path d="M${x} 0V${H}" stroke="#29465d"/>`;
    grid += `<text x="${x + 3}" y="18" fill="#9bb7cb" font-size="12">${lon}°</text>`;
  }
  for (let lat = -60; lat <= 60; lat += 30) {
    const y = (90 - lat) / 180 * H;
    grid += `<path d="M0 ${y}H${W}" stroke="#29465d"/>`;
    grid += `<text x="5" y="${y - 4}" fill="#9bb7cb" font-size="12">${lat}°</text>`;
  }

  const dots = pts.map(p => {
    const x = (p.lon + 180) / 360 * W;
    const y = (90 - p.lat) / 180 * H;
    return `<circle cx="${x}" cy="${y}" r="4" fill="#36d9ed" stroke="#eaffff" stroke-width=".8"><title>${esc(p.src)} | ${p.lat.toFixed(2)}°, ${p.lon.toFixed(2)}°</title></circle>`;
  }).join("");

  return `<div style="color:#eaf6ff;font:13px Arial">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;margin:8px 0">
      <b style="color:#55dfff">EARTH TERRAIN DISTRIBUTION</b>
      <b>${pts.length} locations plotted</b>
    </div>
    <svg viewBox="0 0 ${W} ${H}" style="display:block;width:100%;height:auto;background:#091c2c">
      <rect width="${W}" height="${H}" fill="#091c2c"/>${grid}${dots}
    </svg>
    <p style="color:#a9c5dc">Cyan points represent available Earth terrain tiles. Hover over a point to see its coordinates.</p>
  </div>`;
}

function findPlanet(root, name) {
  const planets = root?.planets || root;
  if (!planets || typeof planets !== "object") return null;
  const key = Object.keys(planets).find(k => k.toLowerCase() === name.toLowerCase());
  return key ? planets[key] : null;
}

function findElevationField(root) {
  const seen = new Set();
  let best = null;

  function flatten(v, out) {
    if (typeof v === "number") {
      out.push(Number.isFinite(v) ? v : null);
    } else if (Array.isArray(v)) {
      for (const item of v) flatten(item, out);
    }
  }

  function walk(obj, path, depth) {
    if (!obj || typeof obj !== "object" || depth > 12 || seen.has(obj)) return;
    seen.add(obj);

    for (const [key, value] of Object.entries(obj)) {
      if (/elevation/i.test(key) && (Array.isArray(value) || ArrayBuffer.isView(value))) {
        const vals = [];
        flatten(value, vals);
        if (vals.length > (best?.values.length || 0)) {
          best = {values: vals, path: path + "." + key};
        }
      }
      if (value && typeof value === "object") walk(value, path + "." + key, depth + 1);
    }
  }

  walk(root, "planet", 0);
  return best;
}

function planetGraph(name, planetRoot) {
  const field = findElevationField(planetRoot);

  if (!field || field.values.length < 1000) {
    throw Error(name + ": no usable elevation array was found in the planetary data.");
  }

  const vals = field.values;
  const cols = 360;
  const rows = Math.floor(vals.length / cols);

  if (rows < 10) throw Error(name + ": unexpected elevation grid dimensions.");

  const valid = vals.filter(Number.isFinite);
  if (!valid.length) throw Error(name + ": elevation grid contains no valid values.");

  const min = Math.min(...valid);
  const max = Math.max(...valid);
  const outCols = 180, outRows = 90;
  const stepX = Math.max(1, Math.floor(cols / outCols));
  const stepY = Math.max(1, Math.floor(rows / outRows));

  let cells = "";
  for (let y = 0; y < outRows; y++) {
    for (let x = 0; x < outCols; x++) {
      const v = vals[(y * stepY) * cols + x * stepX];
      if (!Number.isFinite(v)) continue;
      const t = Math.max(0, Math.min(1, (v - min) / ((max - min) || 1)));
      const color = `rgb(${Math.round(30 + 220*t)},${Math.round(55 + 130*t)},${Math.round(110 + 110*(1-t))})`;
      cells += `<rect x="${x*W/outCols}" y="${y*H/outRows}" width="${W/outCols + .3}" height="${H/outRows + .3}" fill="${color}"/>`;
    }
  }

  return `<div style="margin-top:15px;color:#eaf6ff;font:13px Arial">
    <b style="color:#55dfff">${name.toUpperCase()} GLOBAL ELEVATION HEATMAP</b>
    <svg viewBox="0 0 ${W} ${H}" style="display:block;width:100%;height:auto;background:#091522;margin-top:8px">
      <rect width="${W}" height="${H}" fill="#091522"/>${cells}
    </svg>
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;color:#b9d5e8;margin-top:7px">
      <span>Minimum: ${min.toFixed(3)}</span><span>Maximum: ${max.toFixed(3)}</span>
    </div>
    <p style="color:#9bb4c8">Source field: ${esc(field.path)} | ${vals.length.toLocaleString()} source values | Downsampled for display.</p>
  </div>`;
}

async function render() {
  const panels = [...document.querySelectorAll(".pd-map-grid .pd-panel")];

  if (panels.length < 2) {
    throw Error("Could not find the two planetary map panels in the page.");
  }

  const planetPanel = panels.find(p => /GLOBAL MOON|MOON.*MARS/i.test(p.innerText)) || panels[0];
  const earthPanel = panels.find(p => /EARTH REFERENCE/i.test(p.innerText)) || panels[1];

  // Replace the old blank map content, regardless of whether it is a canvas or div.
  planetPanel.innerHTML = `<h3 style="color:#55dfff">MOON AND MARS ELEVATION GRAPHS</h3><div id="tt4d-planet-output" style="min-height:250px"></div>`;
  earthPanel.innerHTML = `<h3 style="color:#55dfff">EARTH TERRAIN DISTRIBUTION GRAPH</h3><div id="tt4d-earth-output" style="min-height:250px"></div>`;

  const eout = document.getElementById("tt4d-earth-output");
  const pout = document.getElementById("tt4d-planet-output");

  try {
    const response = await fetch(EARTH_URL);
    if (!response.ok) throw Error("Earth CSV HTTP " + response.status);
    const rows = csvParse(await response.text());
    eout.innerHTML = earthGraph(rows);
  } catch (e) {
    eout.innerHTML = `<p style="color:#ffb1a8">Earth graph error: ${esc(e.message)}</p>`;
  }

  try {
    const response = await fetch(PLANET_URL);
    if (!response.ok) throw Error("Planetary JSON HTTP " + response.status);
    const data = await response.json();

    const moon = findPlanet(data, "Moon");
    const mars = findPlanet(data, "Mars");
    if (!moon || !mars) throw Error("Moon/Mars entries were not found in planetary_grids.json.");

    pout.innerHTML = planetGraph("Moon", moon) + planetGraph("Mars", mars);
  } catch (e) {
    pout.innerHTML = `<p style="color:#ffb1a8">Planet graph error: ${esc(e.message)}</p>`;
  }
}

render().catch(e => console.error("TERRATIME4D graph renderer:", e));
