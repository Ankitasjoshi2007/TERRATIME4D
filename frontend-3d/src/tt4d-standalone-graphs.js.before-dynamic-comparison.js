(() => {
  const W = 900, H = 450;
  const EARTH_URL = "/data/earth/global_advanced_terrain_summary.csv";
  const PLANET_URL = "/data/planetary/planetary_grids.json";

  const esc = s => String(s).replace(/[&<>"']/g, c =>
    ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c]
  );

  function parseCSV(s) {
    const rows = [];
    let row = [], cell = "", quoted = false;
    for (let i = 0; i < s.length; i++) {
      const c = s[i];
      if (c === '"' && quoted && s[i+1] === '"') { cell += '"'; i++; }
      else if (c === '"') quoted = !quoted;
      else if (c === "," && !quoted) { row.push(cell); cell = ""; }
      else if ((c === "\n" || c === "\r") && !quoted) {
        if (c === "\r" && s[i+1] === "\n") i++;
        row.push(cell);
        if (row.some(x => x.trim())) rows.push(row);
        row = []; cell = "";
      } else cell += c;
    }
    row.push(cell);
    if (row.some(x => x.trim())) rows.push(row);
    const headers = rows.shift().map(x => x.trim().replace(/^\uFEFF/, ""));
    return rows.map(r => Object.fromEntries(headers.map((h,i) => [h,r[i] ?? ""])));
  }

  function coords(row) {
    const s = String(row.location || row.raster_file || row.candidate || "");
    let lat = Number(row.latitude ?? row.lat);
    let lon = Number(row.longitude ?? row.lon);
    const m = s.match(/_(n|s)(\d{2})_00_(e|w)(\d{3})_00(?:_|$)/i);
    if (m) {
      lat = Number(m[2]) * (m[1].toLowerCase() === "s" ? -1 : 1);
      lon = Number(m[4]) * (m[3].toLowerCase() === "w" ? -1 : 1);
    }
    return {lat, lon, name:s};
  }

  function earthSVG(rows) {
    const pts = rows.map(coords).filter(p =>
      Number.isFinite(p.lat) && Number.isFinite(p.lon) &&
      Math.abs(p.lat) <= 90 && Math.abs(p.lon) <= 180
    );
    let grid = "";
    for (let lon=-180; lon<=180; lon+=30) {
      const x=(lon+180)/360*W;
      grid += `<path d="M${x} 0V${H}" stroke="#31516a"/>`;
    }
    for (let lat=-60; lat<=60; lat+=30) {
      const y=(90-lat)/180*H;
      grid += `<path d="M0 ${y}H${W}" stroke="#31516a"/>`;
    }
    const dots = pts.map(p => {
      const x=(p.lon+180)/360*W, y=(90-p.lat)/180*H;
      return `<circle cx="${x}" cy="${y}" r="4" fill="#35dff1"><title>${esc(p.name)} ${p.lat.toFixed(2)}, ${p.lon.toFixed(2)}</title></circle>`;
    }).join("");
    return `<h3 style="color:#55dfff">EARTH TERRAIN LOCATION DISTRIBUTION</h3>
      <svg viewBox="0 0 ${W} ${H}" style="display:block;width:100%;height:auto;background:#091c2c">
      <rect width="${W}" height="${H}" fill="#091c2c"/>${grid}${dots}</svg>
      <p style="color:#b4d4e9">${pts.length} available Earth locations plotted. Hover over points for coordinates.</p>`;
  }

  function findPlanet(root, name) {
    const p = root?.planets || root;
    if (!p) return null;
    const k = Object.keys(p).find(x => x.toLowerCase() === name.toLowerCase());
    return k ? p[k] : null;
  }

  function findElevation(root) {
    const seen = new Set();
    let best = null;
    function flatten(v, a) {
      if (typeof v === "number") a.push(Number.isFinite(v) ? v : null);
      else if (Array.isArray(v) || ArrayBuffer.isView(v)) for (const x of v) flatten(x,a);
    }
    function walk(o, path, d) {
      if (!o || typeof o !== "object" || d > 12 || seen.has(o)) return;
      seen.add(o);
      for (const [k,v] of Object.entries(o)) {
        if (/elevation/i.test(k) && (Array.isArray(v) || ArrayBuffer.isView(v))) {
          const a=[]; flatten(v,a);
          if (a.length > (best?.values.length || 0)) best={values:a,path:path+"."+k};
        }
        if (v && typeof v === "object") walk(v,path+"."+k,d+1);
      }
    }
    walk(root,"planet",0);
    return best;
  }

  function planetSVG(name, root) {
    const f=findElevation(root);
    if (!f || f.values.length < 1000) return `<p style="color:#ffd28a">${name}: elevation grid could not be identified in the local JSON.</p>`;
    const a=f.values, cols=360, rows=Math.floor(a.length/cols);
    const valid=a.filter(Number.isFinite);
    if (rows < 10 || !valid.length) return `<p style="color:#ffd28a">${name}: invalid elevation grid.</p>`;
    let min=Infinity,max=-Infinity;
    for (const v of valid) { if(v<min)min=v; if(v>max)max=v; }
    let cells="";
    for(let y=0;y<90;y++) for(let x=0;x<180;x++){
      const v=a[Math.floor(y*rows/90)*cols+Math.floor(x*cols/180)];
      if(!Number.isFinite(v)) continue;
      const t=Math.max(0,Math.min(1,(v-min)/((max-min)||1)));
      cells+=`<rect x="${x*5}" y="${y*5}" width="5.2" height="5.2" fill="rgb(${Math.round(25+220*t)},${Math.round(55+125*t)},${Math.round(120-55*t)})"/>`;
    }
    return `<h3 style="color:#55dfff">${name.toUpperCase()} ELEVATION HEATMAP</h3>
      <svg viewBox="0 0 900 450" style="display:block;width:100%;height:auto;background:#091522">
      <rect width="900" height="450" fill="#091522"/>${cells}</svg>
      <p style="color:#b4d4e9">Source: ${esc(f.path)} | Minimum ${min.toFixed(3)} | Maximum ${max.toFixed(3)}</p>`;
  }

  async function run() {
    const earthCanvas=document.getElementById("pd-earth-map");
    const planetCanvas=document.getElementById("pd-target-map");
    if (!earthCanvas || !planetCanvas) throw Error("Original map canvases are missing.");

    // Preserve canvases and all surrounding controls; append graph areas only.
    const earthPanel=earthCanvas.closest(".pd-panel");
    const planetPanel=planetCanvas.closest(".pd-panel");
    if (!earthPanel || !planetPanel) throw Error("Original map panels were not found.");

    function host(id, canvas) {
      let el=document.getElementById(id);
      if (!el) {
        el=document.createElement("div");
        el.id=id;
        canvas.insertAdjacentElement("afterend",el);
      }
      canvas.style.display="none";
      return el;
    }

    const eh=host("tt4d-earth-graph-output",earthCanvas);
    const ph=host("tt4d-planet-graph-output",planetCanvas);
    eh.style.cssText="display:block;width:100%;margin-top:10px";
    ph.style.cssText="display:block;width:100%;margin-top:10px";

    const [er,pr]=await Promise.all([fetch(EARTH_URL),fetch(PLANET_URL)]);
    if(!er.ok) throw Error("Earth CSV HTTP "+er.status);
    if(!pr.ok) throw Error("Planetary JSON HTTP "+pr.status);
    const [csv,json]=await Promise.all([er.text(),pr.json()]);
    eh.innerHTML=earthSVG(parseCSV(csv));
    const moon=findPlanet(json,"Moon"), mars=findPlanet(json,"Mars");
    if(!moon || !mars) throw Error("Moon/Mars entries missing in planetary JSON.");
    ph.innerHTML=planetSVG("Moon",moon)+planetSVG("Mars",mars);
    console.info("Standalone graphs rendered; original selectors and controls preserved.");
  }

  let attempts=0;
  const timer=setInterval(()=>{
    attempts++;
    if(document.getElementById("pd-earth-map") && document.getElementById("pd-target-map")){
      clearInterval(timer);
      run().catch(e=>{
        console.error("TERRATIME4D graphs:",e);
        const panel=document.querySelector(".pd-map-grid .pd-panel");
        if(panel){
          const msg=document.createElement("p");
          msg.style.color="#ffb1a8";
          msg.textContent="Graph error: "+e.message;
          panel.appendChild(msg);
        }
      });
    } else if(attempts>=60) clearInterval(timer);
  },500);
})();
