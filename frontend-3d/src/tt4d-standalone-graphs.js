(() => {
  const EARTH_URL = "/data/earth/global_advanced_terrain_summary.csv";
  const PLANET_URL = "/data/planetary/planetary_grids.json";
  const W = 900, H = 450;

  const esc = s => String(s ?? "").replace(/[&<>"']/g, c =>
    ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c]
  );

  function parseCSV(s) {
    const rows=[]; let row=[], cell="", quoted=false;
    for(let i=0;i<s.length;i++){
      const c=s[i];
      if(c==='"' && quoted && s[i+1]==='"'){cell+='"';i++;}
      else if(c==='"') quoted=!quoted;
      else if(c==="," && !quoted){row.push(cell);cell="";}
      else if((c==="\n"||c==="\r")&&!quoted){
        if(c==="\r"&&s[i+1]==="\n")i++;
        row.push(cell);
        if(row.some(x=>x.trim()))rows.push(row);
        row=[];cell="";
      } else cell+=c;
    }
    row.push(cell); if(row.some(x=>x.trim()))rows.push(row);
    const headers=rows.shift().map(x=>x.trim().replace(/^\uFEFF/,""));
    return rows.map(r=>Object.fromEntries(headers.map((h,i)=>[h,r[i]??""])));
  }

  const num = v => {
    const n=Number(v);
    return Number.isFinite(n)?n:null;
  };

  function findEarthRow(rows, option) {
    const label=(option.textContent||"").trim();
    const value=(option.value||"").trim();

    let row=rows.find(r =>
      r.location && label.includes(r.location)
    );
    if(row)return row;

    row=rows.find(r =>
      r.raster_file && label.includes(r.raster_file)
    );
    if(row)return row;

    const coord=label.match(/(-?\d+(?:\.\d+)?)\s*°?\s*[,/]\s*(-?\d+(?:\.\d+)?)\s*°?/);
    if(coord){
      const lat=Number(coord[1]),lon=Number(coord[2]);
      row=rows.find(r=>{
        const s=String(r.location||"");
        const m=s.match(/_(n|s)(\d{2})_00_(e|w)(\d{3})_00(?:_|$)/i);
        return m &&
          Number(m[2])*(m[1].toLowerCase()==="s"?-1:1)===Math.round(lat) &&
          Number(m[4])*(m[3].toLowerCase()==="w"?-1:1)===Math.round(lon);
      });
      if(row)return row;
    }

    const index=Number(value);
    if(Number.isInteger(index)&&index>=0&&index<rows.length)return rows[index];

    return null;
  }

  function planetData(root,name){
    const p=root?.planets?.[name] || root?.planets?.[name.toLowerCase()];
    if(!p)throw Error(name+" data not found.");
    return p;
  }

  function flattenGrid(grid,valid){
    const cells=[];
    for(let y=0;y<grid.length;y++){
      for(let x=0;x<(grid[y]||[]).length;x++){
        const v=num(grid[y][x]);
        const ok=valid?.[y]?.[x] !== false;
        if(v!==null&&ok)cells.push({x,y,value:v});
      }
    }
    return cells;
  }

  function rankPlanet(planet,earthSlope){
    const cells=flattenGrid(planet.slope_degrees,planet.valid);
    const maxDiff=Math.max(1,...cells.map(c=>Math.abs(c.value-earthSlope)));
    cells.forEach(c=>{
      c.difference=Math.abs(c.value-earthSlope);
      c.score=Math.max(0,100*(1-c.difference/maxDiff));
      c.lat=90-c.y*planet.resolution_degrees;
      c.lon=-180+c.x*planet.resolution_degrees;
    });
    cells.sort((a,b)=>a.difference-b.difference);
    return cells;
  }

  function slopeHeatmap(planet,ranked,name){
    const grid=planet.slope_degrees;
    const all=flattenGrid(grid,planet.valid);
    const values=all.map(c=>c.value);
    const min=Math.min(...values),max=Math.max(...values);
    const markers=ranked.slice(0,20);
    let cells="";

    for(let y=0;y<grid.length;y++){
      for(let x=0;x<grid[y].length;x++){
        const v=num(grid[y][x]);
        if(v===null||planet.valid?.[y]?.[x]===false)continue;
        const t=Math.max(0,Math.min(1,(v-min)/((max-min)||1)));
        const color=`rgb(${Math.round(25+220*t)},${Math.round(70+100*(1-t))},${Math.round(150-90*t)})`;
        const cw=W/grid[y].length,ch=H/grid.length;
        cells+=`<rect x="${x*cw}" y="${y*ch}" width="${cw+.2}" height="${ch+.2}" fill="${color}"/>`;
      }
    }

    const dots=markers.map((c,i)=>{
      const x=(c.x+.5)*W/grid[0].length;
      const y=(c.y+.5)*H/grid.length;
      return `<circle cx="${x}" cy="${y}" r="${i===0?8:4.5}" fill="${i===0?"#fff000":"#ffffff"}" stroke="#111" stroke-width="1"><title>Rank ${i+1}: ${c.lat.toFixed(1)}°, ${c.lon.toFixed(1)}° | slope ${c.value.toFixed(2)}° | score ${c.score.toFixed(1)}%</title></circle>`;
    }).join("");

    return `<h3>${name} - selected Earth's closest slope matches</h3>
      <svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;display:block;background:#091522">
        <rect width="${W}" height="${H}" fill="#091522"/>${cells}${dots}
      </svg>
      <p style="color:#b8d3e8">Heatmap: planetary slope. Yellow: closest match. White: next 19 closest matches.</p>`;
  }

  function matchesTable(ranked){
    return `<table style="width:100%;border-collapse:collapse;color:#e7f5ff;font-size:12px">
      <thead><tr style="color:#59dcf2"><th align="left">Rank</th><th>Latitude</th><th>Longitude</th><th>Slope</th><th>Similarity</th></tr></thead>
      <tbody>${ranked.slice(0,10).map((c,i)=>`
        <tr style="border-top:1px solid #29465d">
          <td>${i+1}</td><td align="center">${c.lat.toFixed(1)}°</td>
          <td align="center">${c.lon.toFixed(1)}°</td>
          <td align="center">${c.value.toFixed(2)}°</td>
          <td align="center">${c.score.toFixed(1)}%</td>
        </tr>`).join("")}</tbody></table>`;
  }

  function parameterGraph(earth,moon,mars){
    const items=[
      ["Mean slope",earth.slope,moon.slope,mars.slope,"°"],
      ["Mean roughness",earth.rough,moon.rough,mars.rough,"m / km"],
      ["Mean elevation",earth.elev,moon.elev,mars.elev,"km"]
    ];
    return `<h3>Selected Earth location - parameter comparison</h3>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px">
      ${items.map(([label,e,m,r,unit])=>`
        <div style="background:#0b2030;border:1px solid #29465d;border-radius:7px;padding:12px">
          <b style="color:#55dfff">${label}</b>
          <p>Earth: ${e===null?"Unavailable":e.toFixed(3)+" "+unit}</p>
          <p>Moon: ${m===null?"Unavailable":m.toFixed(3)+" "+unit}</p>
          <p>Mars: ${r===null?"Unavailable":r.toFixed(3)+" "+unit}</p>
        </div>`).join("")}</div>`;
  }

  async function initialise(){
    const select=document.getElementById("pd-place");
    const panels=[...document.querySelectorAll(".pd-map-grid .pd-panel")];
    if(!select||panels.length<2)return false;

    const earthPanel=panels.find(p=>/EARTH REFERENCE/i.test(p.innerText))||panels[1];
    const planetPanel=panels.find(p=>/GLOBAL MOON|MOON.*MARS/i.test(p.innerText))||panels[0];

    let earthOut=document.getElementById("tt4d-dynamic-earth");
    if(!earthOut){earthOut=document.createElement("div");earthOut.id="tt4d-dynamic-earth";earthPanel.appendChild(earthOut);}
    let planetOut=document.getElementById("tt4d-dynamic-planets");
    if(!planetOut){planetOut=document.createElement("div");planetOut.id="tt4d-dynamic-planets";planetPanel.appendChild(planetOut);}

    earthOut.style.cssText="display:block;width:100%;margin-top:12px;color:#eaf6ff";
    planetOut.style.cssText="display:block;width:100%;margin-top:12px;color:#eaf6ff";

    const [er,pr]=await Promise.all([fetch(EARTH_URL),fetch(PLANET_URL)]);
    if(!er.ok||!pr.ok)throw Error("Could not load local Earth/planetary datasets.");
    const [rows,json]=await Promise.all([er.text(),pr.json()]);
    const earthRows=parseCSV(rows);
    const moon=planetData(json,"Moon"),mars=planetData(json,"Mars");

    function update(){
      const option=select.options[select.selectedIndex];
      if(!option||!option.value){
        earthOut.innerHTML="<p>Select an Earth location to start the comparison.</p>";
        planetOut.innerHTML="";
        return;
      }

      const row=findEarthRow(earthRows,option);
      if(!row){
        earthOut.innerHTML=`<p style="color:#ffcb78">Could not match this dropdown entry to its exact Earth CSV row: ${esc(option.textContent)}. Existing Earth selector has been preserved.</p>`;
        planetOut.innerHTML="";
        return;
      }

      const slope=num(row.slope_mean_degrees);
      if(slope===null){
        earthOut.innerHTML="<p>Selected Earth row has no valid mean slope.</p>";
        return;
      }

      const rough=num(row.roughness_1350m_mean);
      const elev=num(row.elevation_mean_m);
      const moonRank=rankPlanet(moon,slope);
      const marsRank=rankPlanet(mars,slope);

      const selectedName=row.location||row.raster_file;
      const m=String(selectedName).match(/_(n|s)(\d{2})_00_(e|w)(\d{3})_00/i);
      const lat=m?Number(m[2])*(m[1].toLowerCase()==="s"?-1:1):null;
      const lon=m?Number(m[4])*(m[3].toLowerCase()==="w"?-1:1):null;

      earthOut.innerHTML=`
        <h3 style="color:#55dfff">SELECTED EARTH LOCATION</h3>
        <div style="background:#0b2030;padding:12px;border-radius:7px">
          <b>${esc(selectedName)}</b>
          <p>Coordinates: ${lat===null?"Not encoded":lat+"°"}, ${lon===null?"Not encoded":lon+"°"}</p>
          <p>Mean elevation: ${elev===null?"Unavailable":elev.toFixed(2)+" m"}</p>
          <p>Mean slope: ${slope.toFixed(3)}° | P90 slope: ${num(row.slope_p90_degrees)?.toFixed(3)??"Unavailable"}°</p>
          <p>Roughness: 270 m ${num(row.roughness_270m_mean)?.toFixed(2)??"N/A"} m | 630 m ${num(row.roughness_630m_mean)?.toFixed(2)??"N/A"} m | 1350 m ${rough===null?"N/A":rough.toFixed(2)+" m"}</p>
          <p>Ruggedness: ${num(row.hidden_ruggedness_percent)?.toFixed(2)??"N/A"}% | Transition hotspots: ${num(row.transition_hotspot_percent)?.toFixed(2)??"N/A"}%</p>
        </div>
        ${parameterGraph(
          {slope,rough,elev:elev===null?null:elev/1000},
          {slope:num(moon.slope_degrees.flat().reduce((a,b)=>a+(Number.isFinite(b)?b:0),0)/moon.slope_degrees.flat().filter(Number.isFinite).length),rough:null,elev:null},
          {slope:num(mars.slope_degrees.flat().reduce((a,b)=>a+(Number.isFinite(b)?b:0),0)/mars.slope_degrees.flat().filter(Number.isFinite).length),rough:null,elev:null}
        )}
        <p style="color:#ffce86">Scientific note: slope is the primary quantitative matching parameter. Earth roughness is measured at 1.35 km, while planetary roughness is approximately 11 km; elevation datums also differ. These are not treated as equivalent measurements.</p>
      `;

      planetOut.innerHTML=`
        <h3 style="color:#55dfff">MOON MATCHES FOR THIS EARTH LOCATION</h3>
        <p>Earth slope: ${slope.toFixed(3)}° | Closest Moon slope: ${moonRank[0].value.toFixed(3)}° | Difference: ${moonRank[0].difference.toFixed(3)}°</p>
        ${slopeHeatmap(moon,moonRank,"MOON")}
        <h3 style="color:#55dfff;margin-top:22px">TOP 10 MOON MATCHES</h3>
        ${matchesTable(moonRank)}
        <hr style="border-color:#29465d;margin:20px 0">
        <h3 style="color:#55dfff">MARS MATCHES FOR THIS EARTH LOCATION</h3>
        <p>Earth slope: ${slope.toFixed(3)}° | Closest Mars slope: ${marsRank[0].value.toFixed(3)}° | Difference: ${marsRank[0].difference.toFixed(3)}°</p>
        ${slopeHeatmap(mars,marsRank,"MARS")}
        <h3 style="color:#55dfff;margin-top:22px">TOP 10 MARS MATCHES</h3>
        ${matchesTable(marsRank)}
        <p style="color:#ffce86">Similarity scores are relative slope-distance rankings within each planetary grid, not validated probabilities of geological equivalence.</p>
      `;

      const status=document.getElementById("pd-status");
      if(status)status.textContent="Updated Moon and Mars matches for "+selectedName;
    }

    select.addEventListener("change",update);
    const analyze=document.getElementById("pd-analyze");
    if(analyze)analyze.addEventListener("click",update);

    // Wait for the original loader to populate the selector.
    const observer=new MutationObserver(update);
    observer.observe(select,{childList:true,subtree:true});
    update();
    console.info("Dynamic Earth-to-Moon/Mars comparison ready.");
    return true;
  }

  let tries=0;
  const timer=setInterval(()=>{
    tries++;
    const select=document.getElementById("pd-place");
    if(select&&select.options.length>1){
      clearInterval(timer);
      initialise().catch(e=>console.error("Dynamic comparison error:",e));
    } else if(tries>120){
      clearInterval(timer);
      console.error("Earth location selector did not load.");
    }
  },500);
})();
