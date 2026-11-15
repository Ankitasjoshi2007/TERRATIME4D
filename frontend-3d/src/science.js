function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  function parseLine(line) {
    return line.match(/("(?:[^"]|"")*"|[^,]*)(?:,|$)/g)
      .filter((v, i, a) => i < a.length - 1 || v !== "")
      .map(v => v.replace(/,$/, "").replace(/^"|"$/g, "").replace(/""/g, '"'));
  }
  const headers = parseLine(lines[0]);
  return lines.slice(1).filter(Boolean).map(line => {
    const values = parseLine(line);
    return Object.fromEntries(headers.map((h, i) => [h, values[i] ?? ""]));
  });
}

const number = value => {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
};

const fmt = (value, digits = 2) =>
  value === null || value === undefined ? "Not available" : Number(value).toFixed(digits);

let planetary = [];
let physical = [];
let missions = [];
let candidates = [];
let selectedPlanet = "Earth";

const missionKeywords = {
  "Rover Mobility": /rover|mobility/i,
  "Landing Site Assessment": /landing|site/i,
  "Geological Research": /geolog/i,
  "Resource Exploration": /resource|mineral/i,
  "Human Operations": /human|habitat|crew|cold-region/i
};

function addScientificStyles() {
  if (document.querySelector("#science-styles")) return;
  const style = document.createElement("style");
  style.id = "science-styles";
  style.textContent = `
    .science-extra { margin-top:14px; }
    .science-extra h3 { font-size:11px; letter-spacing:1.5px; color:#83dfff; margin:16px 0 9px; }
    .science-metric { display:flex; justify-content:space-between; gap:8px; padding:8px 0; border-bottom:1px solid #ffffff16; font-size:11px; }
    .science-metric span { color:#9eafc6; }
    .science-metric b { color:#f2f7ff; text-align:right; }
    .science-candidate { padding:9px; margin:7px 0; border:1px solid #ffffff20; border-radius:7px; background:#07182b99; }
    .science-candidate b { display:block; color:#e9f6ff; font-size:12px; }
    .science-candidate small { display:block; color:#9eb2c9; margin-top:5px; line-height:1.5; }
    .science-score { color:#65e6cb !important; }
    .science-note { font-size:10px; color:#93a8c0; line-height:1.5; margin-top:9px; }
    .science-map-point { position:absolute; width:8px; height:8px; border-radius:50%; background:#62f4d0; box-shadow:0 0 10px #62f4d0; transform:translate(-50%,-50%); z-index:5; }
    .science-status { color:#63e6c0 !important; }
  `;
  document.head.appendChild(style);
}

function renderPlanet() {
  const p = planetary.find(x => x.Planet?.toLowerCase() === selectedPlanet.toLowerCase());
  const q = physical.find(x => x.planet?.toLowerCase() === selectedPlanet.toLowerCase());

  let elevation = null, slope = null, roughness = null;
  let roughnessLabel = "";

  if (selectedPlanet === "Earth" && p) {
    elevation = number(p.Mean_Elevation_km);
    slope = number(p.Mean_Slope_Degrees);
    roughness = number(p.Earth_Roughness_630m_m);
    roughnessLabel = "630 m reference scale";
  } else if (q) {
    elevation = number(q.elevation_area_weighted_mean_km);
    slope = number(q.slope_area_weighted_mean_degrees);
    roughness = number(q.roughness_area_weighted_mean_km);
    if (roughness !== null) roughness *= 1000;
    roughnessLabel = "Approximately 11 km target scale";
  }

  const blocks = document.querySelectorAll(".right-panel .data-block");
  if (blocks.length >= 3) {
    blocks[0].innerHTML = `<small>SELECTED MISSION</small><b id="missionName">${document.querySelector("#mission").value}</b>`;
    blocks[1].innerHTML = `
      <small>REAL SCIENTIFIC DATA · ${selectedPlanet.toUpperCase()}</small>
      <b class="cyan">${slope === null ? "Data unavailable" : `Mean slope: ${fmt(slope)}°`}</b>
      <small style="display:block;margin-top:7px;color:#a6b7ca">
        Mean elevation: ${elevation === null ? "N/A" : fmt(elevation, 3) + " km"}<br>
        Mean roughness: ${roughness === null ? "N/A" : fmt(roughness) + " m"}
      </small>`;
    blocks[2].innerHTML = `
      <small>MISSION SUITABILITY</small>
      <b>Member 4 mission screening</b>
      <small style="display:block;margin-top:6px;color:#9fb3c9">See candidate rankings below</small>`;
  }

  const title = document.querySelector("#selectedName");
  if (title) title.textContent = selectedPlanet.toUpperCase();

  const extra = document.querySelector("#science-extra");
  if (extra) {
    extra.innerHTML = `
      <h3>PLANETARY MEASUREMENTS</h3>
      <div class="science-metric"><span>Mean elevation</span><b>${elevation === null ? "N/A" : fmt(elevation, 3) + " km"}</b></div>
      <div class="science-metric"><span>Mean slope</span><b>${slope === null ? "N/A" : fmt(slope) + "°"}</b></div>
      <div class="science-metric"><span>Mean roughness</span><b>${roughness === null ? "N/A" : fmt(roughness) + " m"}</b></div>
      <p class="science-note">Roughness scale: ${roughnessLabel || "Not available"}. Earth uses reference tile coverage; Moon and Mars use global gridded datasets. These measurements are not directly scale-equivalent.</p>`;
  }

  renderMissions();
}

function renderMissions() {
  const holder = document.querySelector("#mission-results");
  if (!holder) return;

  const objective = document.querySelector("#mission").value;
  const keyword = missionKeywords[objective];
  let rows = missions.filter(m => keyword.test(m.mission_profile || ""));

  if (!rows.length) rows = missions;

  rows.sort((a, b) =>
    (number(a.mission_rank) ?? 9999) - (number(b.mission_rank) ?? 9999)
  );

  holder.innerHTML = rows.slice(0, 4).map(m => {
    const score = number(m.screening_index_0_100);
    return `<div class="science-candidate">
      <b>${m.candidate || "Candidate not named"}</b>
      <small>${m.mission_profile || "Mission profile"} · Rank ${m.mission_rank || "N/A"}</small>
      <small class="science-score">${score === null ? "No screening score reported" : `Screening index: ${fmt(score)} / 100`}</small>
    </div>`;
  }).join("") || "<p class='science-note'>No matching mission records found.</p>";
}

function renderCandidates() {
  const map = document.querySelector(".map-placeholder");
  const note = document.querySelector(".map-note");
  if (!map) return;

  const valid = candidates.filter(c =>
    number(c.latitude) !== null && number(c.longitude) !== null
  );

  const markers = valid.map((c, i) => {
    const x = ((number(c.longitude) + 180) / 360) * 900;
    const y = ((90 - number(c.latitude)) / 180) * 420;
    return `<g class="candidate-marker" data-index="${i}" tabindex="0" style="cursor:pointer">
      <circle cx="${x}" cy="${y}" r="11" fill="#62f4d0" opacity=".2"/>
      <circle cx="${x}" cy="${y}" r="5" fill="#62f4d0" stroke="#ffffff" stroke-width="1.5"/>
      <title>${c.candidate} (${c.latitude}, ${c.longitude})</title>
    </g>`;
  }).join("");

  map.innerHTML = `
    <div class="offline-map">
      <div class="offline-map-title">EARTH · GLOBAL CANDIDATE LOCATIONS</div>
      <svg id="candidateSvg" viewBox="0 0 900 420" role="img" aria-label="Offline world map with candidate locations">
        <defs>
          <pattern id="mapGrid" width="45" height="35" patternUnits="userSpaceOnUse">
            <path d="M 45 0 L 0 0 0 35" fill="none" stroke="#39718a" stroke-width="1" opacity=".35"/>
          </pattern>
          <linearGradient id="ocean" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#123c58"/>
            <stop offset="100%" stop-color="#061827"/>
          </linearGradient>
        </defs>
        <rect width="900" height="420" fill="url(#ocean)"/>
        <rect width="900" height="420" fill="url(#mapGrid)"/>
        <g fill="#28634c" stroke="#65a77c" stroke-width="2" opacity=".9">
          <path d="M90 75 L130 42 185 48 220 76 205 112 180 125 170 165 140 185 118 150 95 130 70 100Z"/>
          <path d="M185 190 L220 205 238 250 220 300 205 355 185 325 175 270 160 230Z"/>
          <path d="M350 75 L390 58 430 70 450 95 430 120 400 112 380 135 355 115Z"/>
          <path d="M405 135 L455 120 490 145 480 205 450 260 420 230 395 180Z"/>
          <path d="M470 75 L530 45 605 55 655 80 710 75 770 105 790 145 750 165 700 150 665 185 620 165 585 190 550 155 510 145 480 115Z"/>
          <path d="M680 245 L725 230 770 250 755 290 720 310 685 285Z"/>
          <path d="M820 320 L850 310 865 335 845 350Z"/>
          <path d="M300 50 L315 38 330 48 320 62Z"/>
        </g>
        <g fill="none" stroke="#7dc7df" stroke-width="1" opacity=".45">
          <path d="M0 105 H900 M0 210 H900 M0 315 H900"/>
          <path d="M225 0 V420 M450 0 V420 M675 0 V420"/>
        </g>
        ${markers}
      </svg>
      <div class="offline-map-legend">● Candidate evidence locations · Select a glowing marker</div>
    </div>
  `;

  map.querySelectorAll(".candidate-marker").forEach(marker => {
    const showDetails = () => {
      const c = valid[Number(marker.dataset.index)];
      const details = document.querySelector("#candidateDetails");
      if (details) {
        details.innerHTML = `<strong>${c.candidate}</strong><br>
          Latitude: ${fmt(number(c.latitude), 2)}°<br>
          Longitude: ${fmt(number(c.longitude), 2)}°<br>
          Slope: ${fmt(number(c.slope_mean_degrees))}°<br>
          Roughness: ${fmt(number(c.roughness_mean_m))} m<br>
          Temperature: ${fmt(number(c.annual_mean_temperature_c))} °C`;
      }
    };
    marker.addEventListener("click", showDetails);
    marker.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") showDetails();
    });
  });

  if (note) {
    note.textContent = `${valid.length} candidate locations plotted from Member 4 evidence. Select a marker to inspect its measurements.`;
  }

  const list = document.querySelector("#candidate-results");
  if (list) {
    list.innerHTML = `<h3>REAL CANDIDATE EVIDENCE</h3>` + valid.slice(0, 8).map(c => `
      <div class="science-candidate">
        <b>${c.candidate}</b>
        <small>Coordinates: ${fmt(number(c.latitude), 2)}°, ${fmt(number(c.longitude), 2)}°</small>
        <small>Slope: ${fmt(number(c.slope_mean_degrees))}° · Roughness: ${fmt(number(c.roughness_mean_m))} m</small>
        <small>Temperature: ${fmt(number(c.annual_mean_temperature_c))} °C</small>
      </div>`).join("");
  }
}
function addScienceSections() {
  const panel = document.querySelector(".right-panel");
  if (!panel || document.querySelector("#science-extra")) return;

  const mapNote = panel.querySelector(".map-note");
  const moduleLine = panel.querySelector(".member");

  const science = document.createElement("div");
  science.id = "science-extra";
  science.className = "science-extra";
  if (moduleLine) panel.insertBefore(science, moduleLine);

  const mission = document.createElement("div");
  mission.id = "mission-results";
  mission.className = "science-extra";
  if (moduleLine) panel.insertBefore(mission, moduleLine);
  mission.innerHTML = "<h3>MISSION CANDIDATE RANKINGS</h3>";

  const candidate = document.createElement("div");
  candidate.id = "candidate-results";
  candidate.className = "science-extra";
  if (mapNote) mapNote.insertAdjacentElement("afterend", candidate);
  candidate.innerHTML = "<h3>REAL CANDIDATE EVIDENCE</h3>";

  document.querySelectorAll(".member").forEach((el, i) => {
    const status = el.querySelector("i");
    if (!status) return;
    status.textContent = i >= 2 ? "Connected" : "Repository data";
    status.classList.add("science-status");
  });

  // Rover was removed from the 3D scene; remove its obsolete control.
  const roverToggle = document.querySelector("#roverToggle");
  if (roverToggle) roverToggle.closest(".toggle-row")?.remove();
}

export async function initScientificDashboard() {
  addScientificStyles();
  addScienceSections();

  try {
    const files = [
      "planetary_comparison_values_v3.csv",
      "moon_mars_physical_summary_v3.csv",
      "integrated_mission_scores.csv",
      "integrated_candidate_evidence.csv"
    ];

    const data = await Promise.all(files.map(async file => {
      const response = await fetch(`/data/${file}`);
      if (!response.ok) throw new Error(`Could not load ${file}: ${response.status}`);
      return parseCSV(await response.text());
    }));

    [planetary, physical, missions, candidates] = data;

    document.querySelectorAll(".member").forEach((el, i) => {
      const status = el.querySelector("i");
      if (!status) return;
      status.textContent = i === 2 || i === 3 ? "Connected" : "Repository data";
    });

    renderPlanet();
    renderCandidates();

    document.querySelector("#mission")?.addEventListener("change", renderMissions);

    document.querySelectorAll(".planet").forEach(button => {
      button.addEventListener("click", () => {
        selectedPlanet = button.dataset.target;
        renderPlanet();
      });
    });

    console.log("TERRATIME4D scientific datasets loaded successfully.");
  } catch (error) {
    console.error("Scientific data integration error:", error);
    const block = document.querySelector(".right-panel");
    if (block) {
      const warning = document.createElement("p");
      warning.className = "science-note";
      warning.textContent = "Scientific data could not be loaded. Check the browser console and data file paths.";
      block.appendChild(warning);
    }
  }
}
