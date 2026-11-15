async function loadCSV(file) {
  const response = await fetch("/data/" + file);
  if (!response.ok) throw new Error("Cannot load " + file);
  const text = await response.text();

  const rows = [];
  let row = [], field = "", quoted = false;

  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === '"' && quoted && text[i + 1] === '"') {
      field += '"'; i++;
    } else if (c === '"') quoted = !quoted;
    else if (c === "," && !quoted) {
      row.push(field); field = "";
    } else if ((c === "\n" || c === "\r") && !quoted) {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field);
      if (row.some(v => v.trim())) rows.push(row);
      row = []; field = "";
    } else field += c;
  }

  row.push(field);
  if (row.some(v => v.trim())) rows.push(row);

  const headers = rows.shift().map(x => x.trim());
  return rows.map(values => Object.fromEntries(
    headers.map((h, i) => [h, (values[i] || "").trim()])
  ));
}

const n = v => Number.isFinite(Number(v)) ? Number(v) : null;
const fmt = (v, d = 2) => n(v) === null ? "N/A" : n(v).toFixed(d);

async function initOfflineMap() {
  const map = document.getElementById("candidateMap");
  if (!map) return;

  try {
    const [candidates, missions, planets] = await Promise.all([
      loadCSV("integrated_candidate_evidence.csv"),
      loadCSV("integrated_mission_scores.csv"),
      loadCSV("planetary_comparison_values_v3.csv")
    ]);

    map.innerHTML = `
      <div class="offline-map">
        <div class="offline-map-title">GLOBAL RESEARCH CANDIDATES</div>
        <svg id="candidateSvg" viewBox="0 0 720 330" role="img" aria-label="Offline world map showing research candidate locations">
          <defs>
            <pattern id="mapGrid" width="36" height="33" patternUnits="userSpaceOnUse">
              <path d="M36 0H0V33" fill="none" stroke="#23445a" stroke-width=".7"/>
            </pattern>
          </defs>
          <rect width="720" height="330" fill="#071a2a"/>
          <rect width="720" height="330" fill="url(#mapGrid)"/>
          <g fill="#173e50" stroke="#347087" stroke-width="1.2" opacity=".95">
            <path d="M75 65 L105 40 150 43 173 61 190 91 171 111 156 145 133 153 119 131 94 119 80 91Z"/>
            <path d="M160 158 L190 170 208 202 199 238 181 282 165 255 155 217 143 185Z"/>
            <path d="M300 62 L330 45 367 49 389 68 380 89 353 93 341 111 318 96Z"/>
            <path d="M330 111 L371 105 399 128 391 174 368 222 342 207 321 166Z"/>
            <path d="M389 67 L432 43 489 50 531 77 570 91 590 123 561 143 522 129 489 151 458 126 424 132 400 105Z"/>
            <path d="M516 178 L551 165 579 184 567 209 541 220 520 205Z"/>
            <path d="M620 253 L646 246 661 261 647 276 624 271Z"/>
          </g>
          <g stroke="#4a8295" opacity=".4" fill="none">
            <path d="M0 165H720 M360 0V330"/>
            <ellipse cx="360" cy="165" rx="180" ry="165"/>
            <ellipse cx="360" cy="165" rx="360" ry="165"/>
          </g>
          <g id="candidateMarkers"></g>
        </svg>
        <div class="offline-map-legend">● SCIENTIFIC CANDIDATE LOCATION</div>
        <div id="candidateDetails">Select a marker to view its scientific evidence.</div>
      </div>`;

    const svg = document.getElementById("candidateSvg");
    const markerGroup = document.getElementById("candidateMarkers");
    const details = document.getElementById("candidateDetails");

    const x = lon => 360 + (lon / 180) * 340;
    const y = lat => 165 - (lat / 90) * 145;

    function selectedPlanet() {
      return (document.getElementById("selectedName")?.textContent || "EARTH").trim();
    }

    function showCandidate(c) {
      const planet = selectedPlanet();
      const scoreRows = missions.filter(m =>
        m.candidate === c.candidate &&
        (m.target_planet?.toLowerCase() === planet.toLowerCase() ||
         m.target_planet === "Not planet-specific")
      );
      const score = scoreRows.find(m =>
        m.target_planet?.toLowerCase() === planet.toLowerCase()
      ) || scoreRows[0];

      details.innerHTML = `
        <strong>${c.candidate}</strong>
        <div>Coordinates: ${fmt(c.latitude)}°, ${fmt(c.longitude)}°</div>
        <div>Elevation: ${fmt(c.elevation_m)} m</div>
        <div>Mean slope: ${fmt(c.slope_mean_degrees)}°</div>
        <div>Mean roughness: ${fmt(c.roughness_mean_m)} m</div>
        <div>Mean temperature: ${fmt(c.mean_temperature_c)} °C</div>
        <div>Mission suitability: ${score ? fmt(score.screening_index_0_100) + " / 100" : "No matching score"}</div>
        <div>Evidence sources: ${c.evidence_sources_present}/${c.evidence_sources_expected}</div>`;
    }

    candidates.forEach((c, i) => {
      const lon = n(c.longitude), lat = n(c.latitude);
      if (lat === null || lon === null) return;

      const cx = x(lon), cy = y(lat);
      const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
      group.setAttribute("class", "candidate-marker");
      group.setAttribute("tabindex", "0");
      group.style.cursor = "pointer";

      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", cx);
      circle.setAttribute("cy", cy);
      circle.setAttribute("r", "7");
      circle.setAttribute("fill", "#16c9f4");
      circle.setAttribute("stroke", "#d9f9ff");
      circle.setAttribute("stroke-width", "2");

      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("x", cx + 9);
      label.setAttribute("y", cy - 9);
      label.setAttribute("fill", "#d8f6ff");
      label.setAttribute("font-size", "10");
      label.textContent = c.candidate;

      group.append(circle, label);
      group.addEventListener("click", () => showCandidate(c));
      group.addEventListener("keydown", e => {
        if (e.key === "Enter" || e.key === " ") showCandidate(c);
      });
      markerGroup.appendChild(group);
    });

    function updatePlanet() {
      const planet = selectedPlanet();
      const p = planets.find(v => v.Planet.toLowerCase() === planet.toLowerCase());
      if (!p) return;

      const blocks = document.querySelectorAll(".right-panel .data-block");
      if (blocks[1]) {
        blocks[1].querySelector("b").textContent =
          `Slope ${fmt(p.Mean_Slope_Degrees)}° · Elevation ${fmt(p.Mean_Elevation_km, 3)} km`;
      }
      if (blocks[2]) {
        blocks[2].querySelector("b").textContent =
          n(p.Mean_Roughness_m) === null
            ? `Earth reference · ${p.Reference_Coverage}`
            : `Mean roughness ${fmt(p.Mean_Roughness_m)} m`;
      }
    }

    document.querySelectorAll(".planet").forEach(b =>
      b.addEventListener("click", () => setTimeout(updatePlanet, 0))
    );

    document.getElementById("mapNote").textContent =
      `${candidates.length} scientific candidate locations · Offline map · Member 4 evidence`;

    updatePlanet();
    if (candidates.length) showCandidate(candidates[0]);

    console.log("Offline scientific map loaded", candidates.length, "candidates.");
  } catch (error) {
    console.error(error);
    map.textContent = "Scientific map could not load: " + error.message;
  }
}

initOfflineMap();