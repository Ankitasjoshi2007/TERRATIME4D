const style = document.createElement("style");
style.textContent = `
#roverGameBtn{position:fixed;top:105px;right:25px;z-index:10000;padding:12px 17px;background:#09253b;color:#7ceaff;border:1px solid #42cfff;border-radius:8px;cursor:pointer;font-weight:bold;letter-spacing:1px}
#roverGame{position:fixed;inset:0;z-index:20000;background:#030916f5;color:#eaf8ff;display:none;font-family:Arial,sans-serif;padding:22px;overflow:auto}
#roverGame .rg-head{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
#roverGame button{background:#102e49;color:#8deaff;border:1px solid #3d9cbd;border-radius:7px;padding:10px 14px;cursor:pointer}
#roverGame .rg-board{position:relative;width:min(850px,95vw);height:420px;margin:25px auto;background:radial-gradient(ellipse,#183d4b,#071726 70%);border:1px solid #36718a;border-radius:12px;overflow:hidden;background-image:linear-gradient(#ffffff0b 1px,transparent 1px),linear-gradient(90deg,#ffffff0b 1px,transparent 1px),radial-gradient(ellipse,#183d4b,#071726 70%);background-size:35px 35px,35px 35px,auto}
#roverGame .rg-rover{position:absolute;left:8%;top:75%;font-size:30px;transition:left .12s,top .12s;filter:drop-shadow(0 0 9px #65eaff)}
#roverGame .rg-point{position:absolute;font-size:24px;filter:drop-shadow(0 0 8px #ffdb70)}
#roverGame .rg-hud{max-width:850px;margin:auto;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
#roverGame .rg-info{max-width:850px;margin:14px auto;color:#a9c4d8;line-height:1.7}
#roverGame .rg-controls{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin:15px}
#roverGame .rg-bar{height:9px;background:#19344a;border-radius:10px;overflow:hidden;max-width:850px;margin:10px auto}
#roverGame .rg-bar i{display:block;height:100%;width:0;background:#57dcff}
`;
document.head.appendChild(style);

const open=document.createElement("button");
open.id="roverGameBtn";
open.textContent="🚀 ROVER EXPLORATION";
document.body.appendChild(open);

const game=document.createElement("div");
game.id="roverGame";
game.innerHTML=`
<div class="rg-head">
 <div><small style="color:#62dfff;letter-spacing:2px">TERRATIME⁴D / EXPLORATION SIMULATOR</small><h2>ROVER EXPLORATION MODE</h2></div>
 <button id="rgClose">✕ EXIT MISSION</button>
</div>
<div class="rg-hud">
 <span>MISSION: COLLECT 3 SCAN POINTS</span>
 <span id="rgScore">SCORE: 0</span>
 <span id="rgStatus">STATUS: READY</span>
</div>
<div class="rg-bar"><i id="rgProgress"></i></div>
<div class="rg-board" id="rgBoard">
 <div class="rg-rover" id="rgRover">🚙</div>
 <div class="rg-point" id="rgP0">✦</div>
 <div class="rg-point" id="rgP1">✦</div>
 <div class="rg-point" id="rgP2">✦</div>
</div>
<div class="rg-controls">
 <button data-move="up">▲ UP</button>
 <button data-move="left">◀ LEFT</button>
 <button data-move="down">▼ DOWN</button>
 <button data-move="right">RIGHT ▶</button>
 <button id="rgReset">↻ RESTART</button>
</div>
<div class="rg-info">
 <b>Mission briefing:</b> Navigate the rover across the simulated terrain and visit all three scan points. Use WASD or arrow keys, or the on-screen controls. Each scan point increases your exploration score.
 <br><span style="color:#f0c879">Simulation:</span> This is a playable rover-navigation prototype, not a real planetary surface or a physics-accurate rover model.
</div>`;
document.body.appendChild(game);

const rover=document.getElementById("rgRover");
const points=[document.getElementById("rgP0"),document.getElementById("rgP1"),document.getElementById("rgP2")];
const positions=[[78,20],[48,72],[82,55]];
let x=8,y=75,score=0,found=[false,false,false],active=false;
function reset(){
 x=8;y=75;score=0;found=[false,false,false];
 positions.forEach((p,i)=>{points[i].style.left=p[0]+"%";points[i].style.top=p[1]+"%";points[i].style.display="block"});
 update();
}
function update(){
 rover.style.left=x+"%";rover.style.top=y+"%";
 document.getElementById("rgScore").textContent="SCORE: "+score;
 document.getElementById("rgProgress").style.width=(score/3*100)+"%";
 document.getElementById("rgStatus").textContent=score===3?"MISSION COMPLETE!":"STATUS: EXPLORING";
}
function move(dir){
 if(!active)return;
 if(dir==="up")y=Math.max(3,y-3);
 if(dir==="down")y=Math.min(88,y+3);
 if(dir==="left")x=Math.max(2,x-3);
 if(dir==="right")x=Math.min(90,x+3);
 positions.forEach((p,i)=>{
  if(!found[i]&&Math.hypot(x-p[0],y-p[1])<8){
   found[i]=true;score++;points[i].style.display="none";
  }
 });
 update();
}
open.onclick=()=>{game.style.display="block";active=true;};
document.getElementById("rgClose").onclick=()=>{game.style.display="none";active=false;};
document.getElementById("rgReset").onclick=reset;
document.querySelectorAll("#roverGame [data-move]").forEach(b=>{
 b.onclick=()=>move(b.dataset.move);
});
document.addEventListener("keydown",e=>{
 if(!active)return;
 const key=e.key.toLowerCase();
 const dirs={arrowup:"up",w:"up",arrowdown:"down",s:"down",arrowleft:"left",a:"left",arrowright:"right",d:"right"};
 if(dirs[key]){e.preventDefault();move(dirs[key]);}
});
reset();
