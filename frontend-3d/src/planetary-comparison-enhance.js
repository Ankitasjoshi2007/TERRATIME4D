const pcStyle = document.createElement("style");
pcStyle.textContent = `
#pc-visuals {
  display:grid;grid-template-columns:repeat(3,minmax(0,1fr));
  gap:16px;margin:20px 0 28px;
}
.pc-visual-card {
  background:#0b2033;border:1px solid #24516a;border-radius:10px;
  padding:17px;min-width:0;
}
.pc-visual-card h3 {color:#62dcff;font-size:13px;margin:0 0 5px}
.pc-visual-card .pc-unit {color:#8daabd;font-size:10px;margin-bottom:20px}
.pc-bar-row {margin:15px 0}
.pc-bar-label {display:flex;justify-content:space-between;gap:8px;
  font-size:11px;color:#d9edf8;margin-bottom:7px}
.pc-bar-track {height:11px;background:#142e43;border-radius:10px;overflow:hidden}
.pc-bar-fill {height:100%;border-radius:10px;background:linear-gradient(90deg,#1688b9,#62e2ff)}
.pc-visual-note {color:#91adbf;font-size:10px;line-height:1.6;margin-top:13px}
#pc-dashboard {margin:28px 0 35px;background:#0a1c2d;
  border:1px solid #24516a;border-radius:10px;overflow:hidden}
#pc-dashboard h3 {font-size:14px;color:#62dcff;letter-spacing:1px;
  padding:16px 18px;margin:0}
#pc-dashboard img {width:100%;height:auto;display:block;background:#071421}
#pc-dashboard p {padding:0 18px 14px;color:#9bb5c8;font-size:11px}
@media(max-width:760px) {
  #pc-visuals {grid-template-columns:1fr}
}
`;
document.head.appendChild(pcStyle);

const tableWrap = document.querySelector("#planetary-comparison .pc-table-wrap");
const gallery = document.querySelector("#pc-gallery");

if (tableWrap && !document.querySelector("#pc-visuals")) {
  const visualSection = document.createElement("div");
  visualSection.id = "pc-visuals";
  tableWrap.before(visualSection);
}

if (gallery && !document.querySelector("#pc-dashboard")) {
  const dashboard = document.createElement("div");
  dashboard.id = "pc-dashboard";
  dashboard.innerHTML = `
    <h3>PLANETARY TERRAIN — SCIENTIFIC COMPARISON DASHBOARD</h3>
    <img src="/maps/07_planetary_comparison_dashboard.png"
         alt="Member 3 planetary comparison dashboard" loading="lazy">
    <p>Combined scientific analysis figure generated from the Member 3 research outputs.</p>
  `;
  gallery.before(dashboard);
}

function pcParseCSV(text) {
  return text.trim().split(/\r?\n/).map(line => {
    const cells = [];
    let value = "", quoted = false;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      if (c === '"' && line[i + 1] === '"' && quoted) {
        value += '"'; i++;
      } else if (c === '"') quoted = !quoted;
      else if (c === "," && !quoted) {
        cells.push(value); value = "";
      } else value += c;
    }
    cells.push(value);
    return cells;
  });
}

function pcNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function pcRenderCharts(rows) {
  const headers = rows[0];
  const records = rows.slice(1).filter(r => r.length > 1);
  const index = key => headers.indexOf(key);
  const get = (row, key) => {
    const i = index(key);
    return i < 0 ? null : pcNumber(row[i]);
  };

  const planets = records.map(row => {
    const name = row[index("Planet")];
    let roughness = get(row, "Mean_Roughness_m");
    if (String(name).toLowerCase() === "earth") {
      roughness = get(row, "Earth_Roughness_630m_m") ?? roughness;
    }
    return {
      name,
      slope: get(row, "Mean_Slope_Degrees"),
      elevation: get(row, "Mean_Elevation_km"),
      roughness
    };
  }).filter(p => p.name);

  const colors = {Earth:"#4dbbff",Moon:"#c2cbd5",Mars:"#f08a63"};
  const metrics = [
    {key:"slope",title:"MEAN TERRAIN SLOPE",unit:"Degrees (°)",digits:2,
     note:"Average terrain slope reported by each dataset."},
    {key:"elevation",title:"MEAN ELEVATION",unit:"Kilometres (km)",digits:3,
     note:"Elevation values are relative to each body's dataset reference."},
    {key:"roughness",title:"MEAN TERRAIN ROUGHNESS",unit:"Metres (m)",digits:2,
     note:"Earth uses the 630 m reference scale; Moon and Mars use approximately 11 km scale. These are not directly equivalent."}
  ];

  const root = document.querySelector("#pc-visuals");
  if (!root) return;
  root.replaceChildren();

  metrics.forEach(metric => {
    const card = document.createElement("article");
    card.className = "pc-visual-card";
    const title = document.createElement("h3");
    title.textContent = metric.title;
    const unit = document.createElement("div");
    unit.className = "pc-unit";
    unit.textContent = metric.unit;
    card.append(title, unit);

    const values = planets.map(p => p[metric.key]).filter(v => v !== null);
    const max = Math.max(...values.map(Math.abs), 0.000001);

    planets.forEach(planet => {
      const value = planet[metric.key];
      const row = document.createElement("div");
      row.className = "pc-bar-row";

      const label = document.createElement("div");
      label.className = "pc-bar-label";
      const name = document.createElement("span");
      name.textContent = planet.name;
      const number = document.createElement("strong");
      number.textContent = value === null ? "Not available" : value.toFixed(metric.digits);
      label.append(name, number);

      const track = document.createElement("div");
      track.className = "pc-bar-track";
      const fill = document.createElement("div");
      fill.className = "pc-bar-fill";
      fill.style.width = value === null ? "0%" :
        Math.max(2, Math.abs(value) / max * 100) + "%";
      fill.style.background = colors[planet.name] || "#62dcff";
      track.appendChild(fill);
      row.append(label, track);
      card.appendChild(row);
    });

    const note = document.createElement("p");
    note.className = "pc-visual-note";
    note.textContent = metric.note;
    card.appendChild(note);
    root.appendChild(card);
  });

  const existing = document.querySelector("#pc-table");
  if (existing) {
    const table = existing.querySelector("table");
    if (table) {
      table.querySelectorAll("tbody tr").forEach(tr => {
        const cells = tr.querySelectorAll("td");
        const planet = cells[0]?.textContent.trim();
        if (planet === "Earth" && cells[3]) {
          const earth = planets.find(p => p.name === "Earth");
          if (earth && earth.roughness !== null) {
            cells[3].textContent = earth.roughness.toFixed(2);
          }
        }
      });
    }
  }

  const status = document.querySelector("#pc-data-status");
  if (status) {
    status.textContent = "Visual comparison generated from " +
      planets.length + " local planetary records.";
  }
}

fetch("/data/planetary_comparison_values_v3.csv")
  .then(response => {
    if (!response.ok) throw new Error("Local comparison CSV unavailable");
    return response.text();
  })
  .then(pcParseCSV)
  .then(pcRenderCharts)
  .catch(error => {
    const root = document.querySelector("#pc-visuals");
    if (root) root.textContent = "Comparison charts could not load: " + error.message;
  });
