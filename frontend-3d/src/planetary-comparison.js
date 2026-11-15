const maps = [
  ["01_mean_slope_comparison.png", "Mean Slope Comparison", "Compare average terrain slope across the three planetary datasets."],
  ["01_moon_global_elevation.png", "Moon Global Elevation", "Global lunar elevation map."],
  ["02_earth_roughness_scales.png", "Earth Roughness Scales", "Earth roughness at multiple spatial scales."],
  ["02_mars_global_elevation.png", "Mars Global Elevation", "Global Martian elevation map."],
  ["03_moon_mars_roughness_comparison.png", "Moon–Mars Roughness", "Compare lunar and Martian terrain roughness."],
  ["04_mean_elevation_comparison.png", "Mean Elevation Comparison", "Mean elevation comparison."],
  ["05_latitude_slope_comparison.png", "Slope by Latitude", "Terrain slope variation with latitude."],
  ["06_latitude_roughness_comparison.png", "Roughness by Latitude", "Terrain roughness variation with latitude."],
  ["07_planetary_comparison_dashboard.png", "Planetary Comparison Dashboard", "Combined scientific comparison dashboard."]
];

const section = document.createElement("section");
section.id = "planetary-comparison";
section.innerHTML = `
  <div class="pc-heading">
    <div class="pc-eyebrow">TERRATIME 4D / SCIENTIFIC ANALYSIS</div>
    <h1>PLANETARY COMPARISON</h1>
    <p>Earth · Moon · Mars | Global and regional terrain evidence</p>
  </div>

  <div class="pc-metrics">
    <div class="pc-card">
      <span>PLANETS ANALYSED</span>
      <strong>03</strong>
      <small>Earth, Moon and Mars</small>
    </div>
    <div class="pc-card">
      <span>SCIENTIFIC MAPS</span>
      <strong>09</strong>
      <small>Locally stored research figures</small>
    </div>
    <div class="pc-card">
      <span>DATA MODE</span>
      <strong>OFFLINE</strong>
      <small>Local project datasets</small>
    </div>
  </div>

  <div class="pc-section-title">
    <h2>01 / TERRAIN COMPARISON</h2>
    <p>Values loaded from the Member 3 planetary comparison dataset.</p>
  </div>
  <div class="pc-table-wrap">
    <div id="pc-data-status">Loading local scientific data...</div>
    <div id="pc-table"></div>
  </div>

  <div class="pc-note">
    <strong>IMPORTANT — DATA INTERPRETATION</strong>
    Earth represents regional reference tiles, while Moon and Mars represent
    global gridded datasets. Their spatial coverage, resolution and roughness
    scales differ. These values should not be interpreted as perfectly
    equivalent measurements or direct planetary analogues.
  </div>

  <div class="pc-section-title">
    <h2>02 / SCIENTIFIC MAP GALLERY</h2>
    <p>Actual Member 3 analysis outputs. Select any map to open its full-size image.</p>
  </div>
  <div class="pc-gallery" id="pc-gallery"></div>
  <div class="pc-footer">TERRATIME 4D · LOCAL SCIENTIFIC DATA · OFFLINE MODE</div>
`;

const style = document.createElement("style");
style.textContent = `
#planetary-comparison {
  position:relative;
  z-index:20;
  width:100%;
  box-sizing:border-box;
  padding:55px clamp(18px,5vw,75px) 35px;
  background:linear-gradient(180deg,#061321,#081a2b 45%,#061321);
  color:#e5f5ff;
  border-top:1px solid rgba(80,210,255,.25);
  font-family:Arial,sans-serif;
}
#planetary-comparison * {box-sizing:border-box}
#planetary-comparison .pc-heading {margin-bottom:30px}
#planetary-comparison .pc-eyebrow {
  color:#5bdcff;font-size:10px;letter-spacing:3px;margin-bottom:12px
}
#planetary-comparison .pc-heading h1 {
  font-size:clamp(24px,4vw,40px);letter-spacing:3px;margin:0 0 10px;
  color:#e8f8ff
}
#planetary-comparison .pc-heading p,
#planetary-comparison .pc-section-title p {
  color:#91abc1;font-size:13px;line-height:1.6
}
#planetary-comparison .pc-metrics {
  display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;
  margin:25px 0 45px
}
#planetary-comparison .pc-card {
  padding:20px;background:#0b2033;border:1px solid #1b4962;
  border-radius:9px;display:flex;flex-direction:column;gap:9px
}
#planetary-comparison .pc-card span {
  color:#8ba9bf;font-size:9px;letter-spacing:1.5px
}
#planetary-comparison .pc-card strong {
  color:#5bdcff;font-size:25px;letter-spacing:1px
}
#planetary-comparison .pc-card small {color:#9bb2c5;font-size:11px}
#planetary-comparison .pc-section-title {
  margin:38px 0 17px;border-left:3px solid #53d9ff;padding-left:14px
}
#planetary-comparison .pc-section-title h2 {
  font-size:17px;letter-spacing:1.5px;margin:0 0 7px
}
#planetary-comparison .pc-section-title p {margin:0}
#planetary-comparison .pc-table-wrap {
  background:#0a1c2d;border:1px solid #21435a;border-radius:9px;
  padding:16px;overflow-x:auto
}
#planetary-comparison table {
  border-collapse:collapse;width:100%;min-width:650px;font-size:12px
}
#planetary-comparison th {
  text-align:left;color:#5bdcff;font-size:10px;letter-spacing:.7px;
  padding:13px 10px;border-bottom:1px solid #31536a
}
#planetary-comparison td {
  color:#d7e9f6;padding:13px 10px;border-bottom:1px solid #183449
}
#planetary-comparison tr:last-child td {border-bottom:0}
#planetary-comparison .pc-note {
  margin-top:17px;padding:16px 18px;background:#10263a;
  border:1px solid #31536a;border-radius:8px;
  color:#a9bfd0;font-size:11px;line-height:1.8
}
#planetary-comparison .pc-note strong {
  display:block;color:#5bdcff;letter-spacing:1px;margin-bottom:6px
}
#planetary-comparison .pc-gallery {
  display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px
}
#planetary-comparison .pc-map {
  background:#0b2033;border:1px solid #21465e;border-radius:9px;
  overflow:hidden;min-width:0
}
#planetary-comparison .pc-map button {
  display:block;width:100%;padding:0;border:0;background:#071421;
  cursor:zoom-in
}
#planetary-comparison .pc-map img {
  display:block;width:100%;height:auto;min-height:150px;object-fit:contain;
  background:#071421
}
#planetary-comparison .pc-map-info {padding:14px}
#planetary-comparison .pc-map-info h3 {
  margin:0 0 7px;font-size:12px;color:#65dcff;letter-spacing:.7px
}
#planetary-comparison .pc-map-info p {
  margin:0;color:#9db5c8;font-size:11px;line-height:1.6
}
#planetary-comparison #pc-data-status {
  color:#a9bfd0;font-size:12px;padding:12px
}
#planetary-comparison .pc-footer {
  text-align:center;color:#64849d;font-size:9px;letter-spacing:2px;
  padding-top:45px
}
@media(max-width:700px) {
  #planetary-comparison .pc-gallery {grid-template-columns:1fr}
  #planetary-comparison .pc-metrics {grid-template-columns:1fr}
  #planetary-comparison {padding:35px 14px}
}
`;
document.head.appendChild(style);

const app = document.querySelector("#app");
if (app) {
  app.insertAdjacentElement("afterend", section);
} else {
  document.body.appendChild(section);
}

const gallery = document.querySelector("#pc-gallery");
maps.forEach(([file, title, description]) => {
  const card = document.createElement("article");
  card.className = "pc-map";

  const button = document.createElement("button");
  button.type = "button";
  button.title = "Open full-size " + title;

  const img = document.createElement("img");
  img.src = "/maps/" + file;
  img.alt = title;
  img.loading = "lazy";
  img.onerror = () => {
    img.alt = title + " — image unavailable";
    img.style.minHeight = "100px";
    img.style.padding = "25px";
  };

  button.appendChild(img);
  button.addEventListener("click", () => {
    window.open("/maps/" + file, "_blank", "noopener");
  });

  const info = document.createElement("div");
  info.className = "pc-map-info";
  info.innerHTML = `<h3></h3><p></p>`;
  info.querySelector("h3").textContent = title;
  info.querySelector("p").textContent = description;

  card.append(button, info);
  gallery.appendChild(card);
});

function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  return lines.map(line => {
    const result = [];
    let value = "";
    let quoted = false;
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      if (char === '"' && line[i + 1] === '"' && quoted) {
        value += '"';
        i++;
      } else if (char === '"') {
        quoted = !quoted;
      } else if (char === "," && !quoted) {
        result.push(value);
        value = "";
      } else {
        value += char;
      }
    }
    result.push(value);
    return result;
  });
}

function displayComparison(rows) {
  const headers = rows[0];
  const records = rows.slice(1).filter(row => row.length > 1);
  const wanted = [
    ["Planet", "Planet"],
    ["Mean_Slope_Degrees", "Mean slope (°)"],
    ["Mean_Elevation_km", "Mean elevation (km)"],
    ["Mean_Roughness_m", "Mean roughness (m)"],
    ["Reference_Coverage", "Reference coverage"]
  ];
  const indices = wanted.map(([key]) => headers.indexOf(key)).filter(i => i >= 0);

  if (!records.length || !indices.length) {
    throw new Error("The comparison CSV has no usable planetary rows or expected columns.");
  }

  const table = document.createElement("table");
  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");

  wanted.forEach(([key, label]) => {
    if (headers.includes(key)) {
      const th = document.createElement("th");
      th.textContent = label;
      headRow.appendChild(th);
    }
  });
  thead.appendChild(headRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  records.forEach(record => {
    const tr = document.createElement("tr");
    wanted.forEach(([key]) => {
      const index = headers.indexOf(key);
      if (index >= 0) {
        const td = document.createElement("td");
        td.textContent = record[index] ?? "—";
        tr.appendChild(td);
      }
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);

  document.querySelector("#pc-table").replaceChildren(table);
  document.querySelector("#pc-data-status").textContent =
    "Loaded " + records.length + " planetary records from the local comparison dataset.";
}

fetch("/data/planetary_comparison_values_v3.csv")
  .then(response => {
    if (!response.ok) throw new Error("Local comparison CSV not found (HTTP " + response.status + ")");
    return response.text();
  })
  .then(parseCSV)
  .then(displayComparison)
  .catch(error => {
    document.querySelector("#pc-data-status").textContent =
      "Could not load local comparison data: " + error.message +
      ". Check that the CSV exists in public/data/.";
  });
