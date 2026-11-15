import { initScientificDashboard } from './science.js';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import './style.css';

const canvas = document.querySelector('#space');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x020611);
scene.fog = new THREE.FogExp2(0x020611, 0.0007);

const camera = new THREE.PerspectiveCamera(48, innerWidth / innerHeight, 0.1, 2000);
camera.position.set(0, 38, 112);

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  powerPreference: 'high-performance'
});
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.35;

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.045;
controls.minDistance = 18;
controls.maxDistance = 260;

scene.add(new THREE.AmbientLight(0xc4d9ff, 1.5));
scene.add(new THREE.HemisphereLight(0x9fcaff, 0x3b2630, 0.8));

const sunLight = new THREE.PointLight(0xffd49b, 2200, 500);
sunLight.position.set(-35, 10, 0);
scene.add(sunLight);

const textureLoader = new THREE.TextureLoader();
textureLoader.setCrossOrigin('anonymous');

function loadTexture(url) {
  return textureLoader.load(url, texture => {
    texture.colorSpace = THREE.SRGBColorSpace;
  }, undefined, error => {
    console.warn('Planet texture unavailable:', url, error);
  });
}

const earthTexture = loadTexture('https://threejs.org/examples/textures/planets/earth_atmos_2048.jpg');
const moonTexture = loadTexture('https://threejs.org/examples/textures/planets/moon_1024.jpg');
const marsTexture = loadTexture('https://threejs.org/examples/textures/planets/mars_1k_color.jpg');

function makeSphere(name, radius, color, position, texture = null) {
  const material = new THREE.MeshStandardMaterial({
    color,
    map: texture,
    roughness: 0.95,
    metalness: 0.0
  });

  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(radius, 72, 56),
    material
  );
  mesh.name = name;
  mesh.position.copy(position);
  scene.add(mesh);
  return mesh;
}

function makeGlow(color, size) {
  const c = document.createElement('canvas');
  c.width = c.height = 128;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(64,64,1,64,64,64);
  g.addColorStop(0,'rgba(255,255,255,1)');
  g.addColorStop(.12,color);
  g.addColorStop(1,'rgba(255,150,50,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0,0,128,128);

  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
    map: new THREE.CanvasTexture(c),
    transparent:true,
    blending:THREE.AdditiveBlending,
    depthWrite:false
  }));
  sprite.scale.set(size,size,1);
  return sprite;
}

// SUN
const sun = makeSphere('Sun', 8, 0xffb54a, new THREE.Vector3(-35,0,0));
sun.material.emissive = new THREE.Color(0xff751b);
sun.material.emissiveIntensity = 1.4;
sun.add(makeGlow('rgba(255,170,65,0.8)',45));
sun.add(makeGlow('rgba(255,100,25,0.35)',75));

// ORBIT PATHS
function createOrbit(radius, color, parent = scene) {
  const points = [];
  for(let i=0;i<=300;i++) {
    const a = i / 300 * Math.PI * 2;
    points.push(new THREE.Vector3(Math.cos(a)*radius,0,Math.sin(a)*radius));
  }
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const line = new THREE.LineLoop(geometry,new THREE.LineBasicMaterial({
    color, transparent:true, opacity:.42
  }));
  parent.add(line);
  return line;
}

const earthOrbit = createOrbit(35,0x4d9fc9);
const marsOrbit = createOrbit(62,0xb76b52);

// EARTH
const earthPivot = new THREE.Group();
scene.add(earthPivot);

const earth = makeSphere('Earth',4.8,0xffffff,new THREE.Vector3(35,0,0),earthTexture);
earthPivot.add(earth);
scene.remove(earth);

const earthAtmosphere = new THREE.Mesh(
  new THREE.SphereGeometry(5.05,64,48),
  new THREE.MeshBasicMaterial({
    color:0x3b9eff,
    transparent:true,
    opacity:.14,
    side:THREE.BackSide
  })
);
earth.add(earthAtmosphere);

// MOON
const moonOrbit = createOrbit(10,0x91c8e9,earth);
const moon = makeSphere('Moon',1.45,0xffffff,new THREE.Vector3(0,0,0),moonTexture);
earth.add(moon);
moon.position.set(10,0,0);

// MARS
const marsPivot = new THREE.Group();
scene.add(marsPivot);

const mars = makeSphere(
  'Mars',
  4.6,
  0xd95b2b,
  new THREE.Vector3(62, 0, 0)
);

mars.material = new THREE.MeshStandardMaterial({
  color: 0xe8753b,
  emissive: 0x8c260b,
  emissiveIntensity: 0.32,
  roughness: 0.9,
  metalness: 0
});

mars.geometry.dispose();
mars.geometry = new THREE.SphereGeometry(4.6, 128, 96);
marsPivot.add(mars);
scene.remove(mars);

mars.add(makeGlow('rgba(255,105,45,0.22)', 8));
// SATELLITE
const satelliteOrbit = createOrbit(7.5,0x68dfff,earth);
const satellite = new THREE.Group();
earth.add(satellite);

const satBody = new THREE.Mesh(
  new THREE.BoxGeometry(.9,.55,.7),
  new THREE.MeshStandardMaterial({color:0xd8e2ee,metalness:.8,roughness:.25})
);
satellite.add(satBody);

for(const side of [-1,1]) {
  const panel = new THREE.Mesh(
    new THREE.BoxGeometry(1.8,.07,.8),
    new THREE.MeshStandardMaterial({color:0x2259a4,metalness:.4,roughness:.4})
  );
  panel.position.x = side*1.3;
  satellite.add(panel);
}
satellite.position.set(7.5,0,0);

// STAR FIELD
const starGeometry = new THREE.BufferGeometry();
const starPositions = [];

for (let i = 0; i < 3500; i++) {
  starPositions.push(
    (Math.random() - 0.5) * 900,
    (Math.random() - 0.5) * 500,
    (Math.random() - 0.5) * 900
  );
}

starGeometry.setAttribute(
  'position',
  new THREE.Float32BufferAttribute(starPositions, 3)
);

const stars = new THREE.Points(
  starGeometry,
  new THREE.PointsMaterial({
    color: 0xffffff,
    size: 1.15,
    sizeAttenuation: true
  })
);
scene.add(stars);

// AMBIENT PARTICLES
const particleGeometry = new THREE.BufferGeometry();
const particlePositions = [];

for (let i = 0; i < 500; i++) {
  particlePositions.push(
    (Math.random() - 0.5) * 180,
    (Math.random() - 0.5) * 100,
    (Math.random() - 0.5) * 180
  );
}

particleGeometry.setAttribute(
  'position',
  new THREE.Float32BufferAttribute(particlePositions, 3)
);

const particles = new THREE.Points(
  particleGeometry,
  new THREE.PointsMaterial({
    color: 0x65dfff,
    size: 0.35,
    transparent: true,
    opacity: 0.65
  })
);
scene.add(particles);
// COMET
const comet=new THREE.Group();
scene.add(comet);
const cometHead=new THREE.Mesh(
  new THREE.SphereGeometry(.65,16,12),
  new THREE.MeshBasicMaterial({color:0xd9f6ff})
);
comet.add(cometHead);

const cometTail=new THREE.Mesh(
  new THREE.ConeGeometry(.5,13,16),
  new THREE.MeshBasicMaterial({color:0x58c8ff,transparent:true,opacity:.3})
);
cometTail.rotation.z=-Math.PI/2;
cometTail.position.x=-6;
comet.add(cometTail);

// USER CONTROLS
let paused=false;
let elapsed=0;
let speed=1;
let selected='Earth';

const targets={
  Earth:new THREE.Vector3(0,0,0),
  Moon:new THREE.Vector3(0,0,0),
  Mars:new THREE.Vector3(0,0,0)
};

function selectPlanet(name) {
  selected=name;
  document.querySelectorAll('.planet').forEach(button=>{
    button.classList.toggle('active',button.dataset.target===name);
  });

  document.querySelector('#sceneName').textContent=name.toUpperCase()+' SYSTEM';
  document.querySelector('#selectedName').textContent=name.toUpperCase();

  const descriptions={
    Earth:'The Blue Planet · Earth–Moon system',
    Moon:'Lunar exploration · Moon terrain',
    Mars:'The Red Planet · Martian terrain'
  };
  document.querySelector('#sceneDescription').textContent=descriptions[name];

  const target=name==='Mars' ? new THREE.Vector3(62,0,0) : new THREE.Vector3(0,0,0);
  controls.target.copy(target);
  camera.position.copy(target.clone().add(new THREE.Vector3(0,16,38)));
  controls.update();
}

document.querySelectorAll('.planet').forEach(button=>{
  button.addEventListener('click',()=>selectPlanet(button.dataset.target));
});

document.querySelector('#mission').addEventListener('change',e=>{
  document.querySelector('#missionName').textContent=e.target.value;
});

document.querySelector('#speed').addEventListener('input',e=>{
  speed=Number(e.target.value);
  document.querySelector('#speedValue').textContent=speed.toFixed(1)+'×';
});

document.querySelector('#pause').addEventListener('click',e=>{
  paused=!paused;
  e.currentTarget.textContent=paused?'▶ PLAY ANIMATION':'Ⅱ PAUSE ANIMATION';
});

document.querySelector('#reset').addEventListener('click',()=>{
  camera.position.set(0,38,112);
  controls.target.set(0,0,0);
  controls.update();
});

document.querySelector('#orbitToggle').addEventListener('change',e=>{
  [earthOrbit,marsOrbit,moonOrbit,satelliteOrbit].forEach(o=>o.visible=e.target.checked);
});

document.querySelector('#satToggle').addEventListener('change',e=>{
  satellite.visible=e.target.checked;
});

document.querySelector('#starsToggle').addEventListener('change',e=>{
  stars.visible=e.target.checked;
  particles.visible=e.target.checked;
});

document.querySelector('#timeline').addEventListener('input',e=>{
  const value=Number(e.target.value);
  const minutes=Math.floor(value*1.44);
  document.querySelector('#timeLabel').textContent=
    'T + '+String(Math.floor(minutes/60)).padStart(2,'0')+':'+String(minutes%60).padStart(2,'0');
});

// ANIMATION
const clock=new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);

  const delta=Math.min(clock.getDelta(),.04);

  if(!paused) {
    elapsed+=delta*speed;

    sun.rotation.y+=delta*.035*speed;
    earth.rotation.y+=delta*.12*speed;
    mars.rotation.y+=delta*.08*speed;
    moon.rotation.y+=delta*.025*speed;

    // Earth orbit around Sun
    const earthAngle=elapsed*.09;
    earth.position.set(
      Math.cos(earthAngle)*35,
      0,
      Math.sin(earthAngle)*35
    );

    // Satellite orbit around Earth
    const satAngle=elapsed*1.4;
    satellite.position.set(
      Math.cos(satAngle)*7.5,
      Math.sin(satAngle*.7)*2.2,
      Math.sin(satAngle)*7.5
    );
    satellite.rotation.y+=delta*.6;

    // Moving comet
    comet.position.set(
      ((elapsed*13)%220)-110,
      35+Math.sin(elapsed*.5)*15,
      -55
    );
    comet.rotation.z=.15;

    stars.rotation.y+=delta*.0007;
    particles.rotation.y+=delta*.002;
  }

  controls.update();
  renderer.render(scene,camera);
}

function resize() {
  camera.aspect=innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
}

window.addEventListener('resize',resize);

animate();

// Finish loading screen - works even without internet
setTimeout(() => {
  const loading = document.querySelector('#loading');
  if (loading) {
    loading.style.opacity = '0';
    setTimeout(() => loading.remove(), 1000);
  }
}, 2000);

initScientificDashboard();
