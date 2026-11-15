const css = document.createElement("style");
css.textContent = `
.discovery{margin:25px 0;padding:22px;background:linear-gradient(135deg,#0c2038,#07111f);border:1px solid #27617b;border-radius:14px}
.discovery h2{margin:8px 0 12px}
.discovery-tabs{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}
.discovery-tabs button{background:#102943;color:#a9c9df;border:1px solid #315675;padding:12px 22px;border-radius:8px;cursor:pointer}
.discovery-tabs button.active{background:#075071;border-color:#5ce4ff;color:white;box-shadow:0 0 18px #32cfff44}
.discovery-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.discovery-stat{background:#10243a;border:1px solid #24435d;border-radius:9px;padding:15px}
.discovery-stat small{display:block;color:#8caec8;margin-bottom:8px}
.discovery-stat strong{font-size:22px;color:#76e6ff}
.discovery-action{margin-top:18px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.discovery-action button{background:#08749a;color:white;border:0;border-radius:8px;padding:13px 20px;cursor:pointer;font-weight:bold}
.discovery-progress{height:8px;background:#1c344b;border-radius:8px;overflow:hidden;margin-top:15px}
.discovery-progress i{display:block;width:0;height:100%;background:#55e4ff;transition:width .2s}
.discovery-fact{margin-top:14px;padding:15px;background:#102a3c;border-left:3px solid #62dcff;color:#c5d9e8;line-height:1.6;min-height:52px}
@media(max-width:700px){.discovery-grid{grid-template-columns:1fr}}
`;
document.head.appendChild(css);

const main=document.querySelector("main");
if(main&&!document.querySelector("#planetDiscovery")){
 const section=document.createElement("section");
 section.id="planetDiscovery";
 section.className="discovery";
 section.innerHTML=`
 <div class="eyebrow">INTERACTIVE SCIENCE / DISCOVERY MODE</div>
 <h2>Planetary Discovery Console</h2>
 <p class="sub">Choose a world. Scan its terrain. Discover how its surface compares with other planetary environments.</p>
 <div class="discovery-tabs">
  <button class="active" data-world="Earth">🌍 EARTH</button>
  <button data-world="Moon">🌙 MOON</button>
  <button data-world="Mars">🔴 MARS</button>
 </div>
 <div class="discovery-grid" id="discoveryStats">
  <div class="discovery-stat"><small>MEAN SLOPE</small><strong>Loading</strong></div>
  <div class="discovery-stat"><small>MEAN ELEVATION</small><strong>Loading</strong></div>
  <div class="discovery-stat"><small>ROUGHNESS</small><strong>Loading</strong></div>
 </div>
 <div class="discovery-action">
  <button id="runPlanetScan">▶ RUN PLANET SCAN</button>
  <span id="scanStatus" class="sub">Scan not started</span>
 </div>
 <div class="discovery-progress"><i id="scanProgress"></i></div>
 <div class="discovery-fact" id="discoveryFact">Select a planet and run a scan to unlock its scientific briefing.</div>
 `;
 main.prepend(section);
}

const worlds={
 Earth:{slope:null,elevation:null,rough:null,coverage:"Regional processed Earth terrain tiles",fact:"Earth is the reference environment. Its processed terrain data represents selected regional tiles, not complete global coverage."},
 Moon:{slope:null,elevation:null,rough:null,coverage:"Global lunar elevation grid",fact:"The Moon has no substantial atmosphere. Earth analog sites cannot reproduce lunar vacuum, gravity or radiation conditions."},
 Mars:{slope:null,elevation:null,rough:null,coverage:"Global Martian elevation grid",fact:"Mars has a thin atmosphere and different gravity and radiation conditions. Earth analogs can support partial terrain and operations studies, not full environmental replication."}
};
let selected="Earth",loaded=false;
function number(row,key){const n=Number(row?.[key]);return row&&row[key]!==""&&Number.isFinite(n)?n:null}
function showNumber(n,d=2){return n===null?"Unavailable":n.toFixed(d)}
function render(){
 const w=worlds[selected];
 document.querySelectorAll(".discovery-tabs button").forEach(b=>b.classList.toggle("active",b.dataset.world===selected));
 document.querySelector("#discoveryStats").innerHTML=`
 <div class="discovery-stat"><small>MEAN SLOPE</small><strong>${showNumber(w.slope)}°</strong></div>
 <div class="discovery-stat"><small>MEAN ELEVATION</small><strong>${showNumber(w.elevation)} km</strong></div>
 <div class="discovery-stat"><small>ROUGHNESS</small><strong>${showNumber(w.rough)} m</strong></div>`;
 document.querySelector("#discoveryFact").textContent=w.fact;
 document.querySelector("#scanStatus").textContent="Selected: "+selected;
 document.querySelector("#scanProgress").style.width="0%";
}
async function load(){
 try{
  const [a,b]=await Promise.all([
   fetch("./data/planetary_comparison_values_v3.csv"),
   fetch("./data/moon_mars_physical_summary_v3.csv")
  ]);
  if(!a.ok||!b.ok)throw Error("Could not load planetary comparison CSV files");
  const [earthText,otherText]=await Promise.all([a.text(),b.text()]);
  const parse=t=>{
   const lines=t.trim().split(/\r?\n/);
   const headers=lines[0].split(",");
   return lines.slice(1).map(line=>{
    const cells=line.split(",");
    return Object.fromEntries(headers.map((h,i)=>[h,cells[i]??""]));
   });
  };
  const earth=parse(earthText).find(x=>x.Planet==="Earth");
  const other=parse(otherText);
  const moon=other.find(x=>x.planet==="Moon");
  const mars=other.find(x=>x.planet==="Mars");
  if(earth){
   worlds.Earth.slope=number(earth,"Mean_Slope_Degrees");
   worlds.Earth.elevation=number(earth,"Mean_Elevation_km");
   worlds.Earth.rough=number(earth,"Earth_Roughness_630m_m");
  }
  for(const [name,row] of [["Moon",moon],["Mars",mars]]){
   if(row){
    worlds[name].slope=number(row,"slope_area_weighted_mean_degrees");
    worlds[name].elevation=number(row,"elevation_area_weighted_mean_km");
    const r=number(row,"roughness_area_weighted_mean_km");
    worlds[name].rough=r===null?null:r*1000;
   }
  }
  loaded=true;render();
 }catch(e){
  document.querySelector("#discoveryFact").textContent="Dataset loading issue: "+e.message;
  console.error(e);
 }
}
document.querySelectorAll(".discovery-tabs button").forEach(b=>b.addEventListener("click",()=>{
 selected=b.dataset.world;render();
}));
document.querySelector("#runPlanetScan").addEventListener("click",()=>{
 if(!loaded){document.querySelector("#scanStatus").textContent="Waiting for datasets";return}
 const btn=document.querySelector("#runPlanetScan");
 const progress=document.querySelector("#scanProgress");
 const status=document.querySelector("#scanStatus");
 const fact=document.querySelector("#discoveryFact");
 btn.disabled=true;let p=0;
 status.textContent="Scanning "+selected+" terrain…";
 const timer=setInterval(()=>{
  p=Math.min(100,p+5);progress.style.width=p+"%";
  if(p===100){
   clearInterval(timer);btn.disabled=false;
   status.textContent="SCAN COMPLETE · "+selected;
   fact.textContent=worlds[selected].fact+" Measurements are derived from the project's supplied planetary comparison datasets. Coverage and scale differ between worlds.";
  }
 },60);
});
load();
