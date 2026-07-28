import * as THREE from 'three';
import { ASSETS } from '../assets.js';
import { envType, fill } from '../dom.js';
import { frames, WIDTH, HEIGHT } from '../timing.js';
import { buildMaze, COLS, ROWS, CELL, WALL_T, WALL_H, POST } from '../maze/maze.js';
import { buildPath } from '../maze/path.js';
import { createMouse, MOUSE_H, WHEEL_R } from '../maze/mouse.js';

/**
 * SCENE 6 — MICROMOUSE MAZE RUN (0:27–0:38)
 *
 * The hero sequence. A real connected maze with solid walls, a differential
 * drive mouse on an arc-length path, and a chase camera that is clamped to the
 * corridor so it can never travel through geometry.
 *
 * The scene ends craned into a top-down view so it cuts straight into the
 * supplied logo reveal, which opens on its own top-down circuit.
 */

/** Normalised distance keyframes — the speed ramp of the whole run. */
const SPEED_KEYS = [
  [0.0, 0.0],
  [0.1, 0.04],
  [0.3, 0.24],
  [0.5, 0.46],
  [0.62, 0.55],
  [0.8, 0.76],
  [1.0, 1.0],
];

const smoothstep = (t) => t * t * (3 - 2 * t);

function distanceCurve(p) {
  const x = Math.max(0, Math.min(1, p));
  for (let i = 0; i < SPEED_KEYS.length - 1; i++) {
    const [p0, d0] = SPEED_KEYS[i];
    const [p1, d1] = SPEED_KEYS[i + 1];
    if (x <= p1) {
      const t = (x - p0) / (p1 - p0);
      return d0 + (d1 - d0) * smoothstep(t);
    }
  }
  return 1;
}

/** Converts an already-loaded image into a monochrome texture. */
function monoTexture(url) {
  const img = new Image();
  const canvas = document.createElement('canvas');
  const texture = new THREE.CanvasTexture(canvas);
  img.onload = () => {
    canvas.width = 512;
    canvas.height = Math.round((img.height / img.width) * 512) || 512;
    const ctx = canvas.getContext('2d');
    ctx.filter = 'grayscale(1) contrast(1.25) brightness(0.9)';
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    texture.needsUpdate = true;
  };
  img.src = url;
  return texture;
}

export function build({ root, tl, t0, dur, canvas }) {
  const maze = buildMaze();
  const path = buildPath();

  // ── Renderer ──────────────────────────────────────────────────────────
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
  renderer.setPixelRatio(1);
  renderer.setSize(WIDTH, HEIGHT, false);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.35;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x061014);
  // Far plane has to clear the final crane (camera reaches ~y10) or the maze
  // fogs out completely at the handoff into the logo reveal.
  scene.fog = new THREE.Fog(0x061014, 3.4, 18);

  const camera = new THREE.PerspectiveCamera(68, WIDTH / HEIGHT, 0.02, 60);

  // ── Floor ─────────────────────────────────────────────────────────────
  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(COLS * CELL + 4, ROWS * CELL + 4),
    new THREE.MeshStandardMaterial({ color: 0x102a33, roughness: 0.92, metalness: 0.05 }),
  );
  floor.rotation.x = -Math.PI / 2;
  floor.position.set(((COLS - 1) * CELL) / 2, 0, ((ROWS - 1) * CELL) / 2);
  floor.receiveShadow = true;
  scene.add(floor);

  // ── Walls (solid, filled geometry — instanced for cost) ───────────────
  const wallMat = new THREE.MeshStandardMaterial({ color: 0x21596a, roughness: 0.72, metalness: 0.08 });
  const wallGeo = new THREE.BoxGeometry(CELL, WALL_H, WALL_T);
  const walls = new THREE.InstancedMesh(wallGeo, wallMat, maze.walls.length);
  walls.castShadow = true;
  walls.receiveShadow = true;

  const dummy = new THREE.Object3D();
  maze.walls.forEach((w, i) => {
    dummy.position.set(w.x, WALL_H / 2, w.z);
    dummy.rotation.y = w.horizontal ? 0 : Math.PI / 2;
    dummy.updateMatrix();
    walls.setMatrixAt(i, dummy.matrix);
  });
  walls.instanceMatrix.needsUpdate = true;
  scene.add(walls);

  // Mint capping strip along the top of every wall — reads the maze in silhouette.
  const capMat = new THREE.MeshStandardMaterial({
    color: 0x6ff0d2,
    emissive: 0x3fbfa2,
    emissiveIntensity: 1.4,
    roughness: 0.5,
  });
  const capGeo = new THREE.BoxGeometry(CELL, 0.02, WALL_T * 1.25);
  const caps = new THREE.InstancedMesh(capGeo, capMat, maze.walls.length);
  maze.walls.forEach((w, i) => {
    dummy.position.set(w.x, WALL_H + 0.008, w.z);
    dummy.rotation.y = w.horizontal ? 0 : Math.PI / 2;
    dummy.updateMatrix();
    caps.setMatrixAt(i, dummy.matrix);
  });
  caps.instanceMatrix.needsUpdate = true;
  scene.add(caps);

  // Corner posts, as on a real micromouse board.
  const postGeo = new THREE.BoxGeometry(POST, WALL_H + 0.03, POST);
  const postMat = new THREE.MeshStandardMaterial({ color: 0x18414e, roughness: 0.8 });
  const postCount = (COLS + 1) * (ROWS + 1);
  const posts = new THREE.InstancedMesh(postGeo, postMat, postCount);
  let pi = 0;
  for (let c = 0; c <= COLS; c++) {
    for (let r = 0; r <= ROWS; r++) {
      dummy.position.set(c * CELL - CELL / 2, (WALL_H + 0.03) / 2, r * CELL - CELL / 2);
      dummy.rotation.y = 0;
      dummy.updateMatrix();
      posts.setMatrixAt(pi++, dummy.matrix);
    }
  }
  posts.instanceMatrix.needsUpdate = true;
  scene.add(posts);

  // ── Wall memories ─────────────────────────────────────────────────────
  // Faint monochrome fragments of last year, projected onto wall faces.
  const memorySpecs = [
    { url: ASSETS.makerthon.crowdWide, s: 5.2 },
    { url: ASSETS.roboexpo.heroCrowd, s: 11.0 },
    { url: ASSETS.makerlabs.group, s: 17.5 },
    { url: ASSETS.roboexpo.demoersRoom, s: 23.0 },
  ];
  const memories = memorySpecs.map((spec) => {
    const at = path.pointAt(spec.s);
    const tan = path.tangentAt(spec.s);
    // Sit the plane on the wall to the mouse's left.
    const nx = -tan.z;
    const nz = tan.x;
    const mesh = new THREE.Mesh(
      new THREE.PlaneGeometry(0.8, 0.36),
      new THREE.MeshBasicMaterial({
        map: monoTexture(spec.url),
        transparent: true,
        opacity: 0,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
      }),
    );
    mesh.position.set(at.x + nx * (CELL / 2 - WALL_T), WALL_H * 0.55, at.z + nz * (CELL / 2 - WALL_T));
    mesh.lookAt(at.x, WALL_H * 0.55, at.z);
    scene.add(mesh);
    return { mesh, s: spec.s };
  });

  // ── Mouse ─────────────────────────────────────────────────────────────
  const mouse = createMouse();
  scene.add(mouse.group);

  // Glowing route the mouse leaves behind — this is what completes the logo.
  // Built as a ribbon rather than a Line: WebGL ignores linewidth, so a
  // THREE.Line would render one hairline pixel and vanish on the crane.
  const TRAIL_SEGMENTS = 420;
  const TRAIL_W = 0.032;
  const trailGeo = new THREE.BufferGeometry();
  const trailPositions = new Float32Array(TRAIL_SEGMENTS * 2 * 3);
  trailGeo.setAttribute('position', new THREE.BufferAttribute(trailPositions, 3));
  const trailIndex = [];
  for (let i = 0; i < TRAIL_SEGMENTS - 1; i++) {
    const a = i * 2;
    trailIndex.push(a, a + 1, a + 2, a + 1, a + 3, a + 2);
  }
  trailGeo.setIndex(trailIndex);
  const trail = new THREE.Mesh(
    trailGeo,
    new THREE.MeshBasicMaterial({
      color: 0xff5b2e,
      transparent: true,
      opacity: 0.78,
      side: THREE.DoubleSide,
      depthWrite: false,
    }),
  );
  trail.renderOrder = 2;
  scene.add(trail);

  // ── Lighting ──────────────────────────────────────────────────────────
  // The corridor is enclosed on both sides, so most of a single key light is
  // shadowed out. Ambient plus a hemisphere does the real work here.
  scene.add(new THREE.AmbientLight(0x5d93a0, 1.15));
  scene.add(new THREE.HemisphereLight(0x9fdbe8, 0x0d2229, 0.85));

  const key = new THREE.DirectionalLight(0xd8f6f8, 1.0);
  key.position.set(4, 8, 2);
  key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);
  key.shadow.camera.left = -10;
  key.shadow.camera.right = 10;
  key.shadow.camera.top = 14;
  key.shadow.camera.bottom = -14;
  scene.add(key);

  // Soft fill riding with the camera keeps the mouse readable in the corridor.
  const fillLight = new THREE.PointLight(0x8fd8e0, 2.2, 4.5, 2);
  scene.add(fillLight);

  // ── Camera rig ────────────────────────────────────────────────────────
  const HALF_CORRIDOR = CELL / 2 - WALL_T / 2 - 0.06;

  /** Keeps the camera inside the walls of whatever cell it is in. */
  function clampToCorridor(pos) {
    const c = Math.round(pos.x / CELL);
    const r = Math.round(pos.z / CELL);
    const cx = c * CELL;
    const cz = r * CELL;
    const cell = maze.cells[Math.max(0, Math.min(COLS - 1, c))]?.[Math.max(0, Math.min(ROWS - 1, r))];
    if (!cell) return pos;
    if (cell.e) pos.x = Math.min(pos.x, cx + HALF_CORRIDOR);
    if (cell.w) pos.x = Math.max(pos.x, cx - HALF_CORRIDOR);
    if (cell.n) pos.z = Math.min(pos.z, cz + HALF_CORRIDOR);
    if (cell.s) pos.z = Math.max(pos.z, cz - HALF_CORRIDOR);
    return pos;
  }

  const camPos = new THREE.Vector3();
  const camTarget = new THREE.Vector3();

  function updateCamera(p, s, mousePos, tangent) {
    const curvature = path.curvatureAt(s);

    // Chase: trailing along the path so the camera stays in the corridor.
    // The lag closes hard through corners. At a full 1.15 the camera is still
    // in the previous leg while the mouse is around the bend, and the corner
    // post sits directly between them.
    const turn = Math.min(1, Math.abs(curvature) * 1.45);
    // Only a moderate close-up: dropping to ~0.35 makes the mouse subtend a
    // huge angle, so any lateral offset throws it off the edge of the frame.
    const lag = 1.15 - 0.45 * turn;
    const lagPoint = path.pointAt(s - lag);
    // Low, just under wall-cap height. In a 9:16 frame a higher camera shows
    // mostly floor and empty space above the walls; down here the corridor
    // walls fill the tall frame.
    camPos.set(lagPoint.x, 0.2, lagPoint.z);

    // Cut toward the inside of the corner. Combined with the shorter lag this
    // clears the corner post from the line of sight; clampToCorridor below
    // guarantees it can never push through a wall.
    const inside = Math.sign(curvature) || 0;
    const lateral = { x: -tangent.z, z: tangent.x };
    camPos.x += lateral.x * 0.24 * turn * inside;
    camPos.z += lateral.z * 0.24 * turn * inside;
    // Aim along the camera→mouse ray, pushed past the mouse by lookAhead.
    // On a straight this is identical to aiming down the corridor, but through
    // a corner it keeps the mouse exactly on the optical axis. A portrait
    // frame only has ~43 degrees of horizontal view, so aiming off the mouse
    // by even 15 degrees puts it at the edge.
    const dx = mousePos.x - camPos.x;
    const dz = mousePos.z - camPos.z;
    const d = Math.hypot(dx, dz) || 1;
    const lookAhead = 0.9 * (1 - turn);
    const reach = d + lookAhead;
    camTarget.set(
      camPos.x + (dx / d) * reach,
      // Aiming above the mouse drops it into the lower third of the frame.
      0.3,
      camPos.z + (dz / d) * reach,
    );
    // Curvature peaks near 0.7 on the corner arcs; 0.12 keeps the roll inside
    // the 3-5 degree range the brief asks for.
    let roll = -curvature * 0.12;

    // Wheel-level pass. A true side-on shot is impossible in a 1-cell
    // corridor, so this drops to axle height and offsets laterally only as far
    // as the corridor allows, staying behind the mouse.
    if (p > 0.35 && p < 0.45) {
      const k = smoothstep(Math.min(1, Math.abs(p - 0.4) / 0.05));
      const side = { x: -tangent.z, z: tangent.x };
      const low = path.pointAt(s - 0.62);
      const sidePos = new THREE.Vector3(low.x + side.x * 0.13, 0.072, low.z + side.z * 0.13);
      camPos.lerp(sidePos, 1 - k);
      // Aim slightly ahead of the mouse, not at it, or the lateral offset
      // walks it to the edge of the frame.
      camTarget.lerp(
        new THREE.Vector3(mousePos.x + tangent.x * 0.2, 0.1, mousePos.z + tangent.z * 0.2),
        1 - k,
      );
      roll *= k;
    }

    // One very brief overhead junction shot.
    if (p > 0.55 && p < 0.62) {
      const k = smoothstep(Math.min(1, Math.abs(p - 0.585) / 0.035));
      const overhead = new THREE.Vector3(mousePos.x, 2.4, mousePos.z - 0.4);
      camPos.lerp(overhead, 1 - k);
      camTarget.lerp(new THREE.Vector3(mousePos.x, 0, mousePos.z), 1 - k);
      roll *= k;
    }

    clampToCorridor(camPos);

    // Final crane to top-down, handing off to the logo reveal.
    if (p > 0.88) {
      const k = smoothstep((p - 0.88) / 0.12);
      const top = new THREE.Vector3(mousePos.x, 0.3 + k * 9.5, mousePos.z - 0.4 * (1 - k));
      camPos.lerp(top, k);
      camTarget.lerp(new THREE.Vector3(mousePos.x, 0, mousePos.z), k);
      roll *= 1 - k;
    }

    camera.position.copy(camPos);
    camera.up.set(0, 1, 0);
    camera.lookAt(camTarget);
    camera.rotateZ(roll);
  }

  // ── Per-frame update ──────────────────────────────────────────────────
  let trailCount = 0;

  // The mouse starts one camera-lag into the path so the chase camera has real
  // corridor behind it. Without this the camera clamps to the path origin and
  // ends up sitting inside the mouse on the first frames.
  const START_OFFSET = 1.25;

  function update(globalTime) {
    const local = globalTime - t0;
    const p = Math.max(0, Math.min(1, local / dur));
    const s = START_OFFSET + distanceCurve(p) * (path.length - START_OFFSET);

    const pos = path.pointAt(s);
    const tan = path.tangentAt(s);

    mouse.group.position.set(pos.x, 0, pos.z);
    mouse.group.rotation.y = Math.atan2(tan.x, tan.z);

    // Wheel spin tracks real distance travelled, not wall time.
    const spin = -s / WHEEL_R;
    for (const w of mouse.wheels) {
      w.rotation.x = spin;
      w.userData.hub.rotation.x = spin;
    }

    // A tiny plausible slip on the hardest turn — body yaws a few degrees
    // beyond the path tangent, then recovers.
    const curvature = path.curvatureAt(s);
    mouse.group.rotation.y += curvature * 0.16;
    mouse.group.rotation.z = -curvature * 0.1;

    // Trail ribbon: every vertex is placed by arc-length, so the geometry is
    // identical for a given time no matter how the timeline was reached.
    const wanted = Math.min(TRAIL_SEGMENTS, Math.floor((s / path.length) * TRAIL_SEGMENTS) + 1);
    if (wanted !== trailCount) {
      for (let i = 0; i < TRAIL_SEGMENTS; i++) {
        const si = Math.min(START_OFFSET + (i / (TRAIL_SEGMENTS - 1)) * (path.length - START_OFFSET), s);
        const pt = path.pointAt(si);
        const tg = path.tangentAt(si);
        const nx = -tg.z * TRAIL_W;
        const nz = tg.x * TRAIL_W;
        const o = i * 6;
        trailPositions[o] = pt.x + nx;
        trailPositions[o + 1] = 0.012;
        trailPositions[o + 2] = pt.z + nz;
        trailPositions[o + 3] = pt.x - nx;
        trailPositions[o + 4] = 0.012;
        trailPositions[o + 5] = pt.z - nz;
      }
      trailGeo.attributes.position.needsUpdate = true;
      trailGeo.computeBoundingSphere();
      trailCount = wanted;
    }

    // Memories glow only as the mouse passes them.
    for (const m of memories) {
      const d = Math.abs(s - m.s);
      m.mesh.material.opacity = Math.max(0, 0.34 * (1 - d / 1.6));
    }

    // Sensor emitters pulse faster as the run speeds up.
    const pulse = 0.6 + 0.4 * Math.sin(s * 9);
    for (const e of mouse.emitters) e.material.emissiveIntensity = 1.2 + pulse;

    updateCamera(p, s, pos, tan);
    fillLight.position.set(camera.position.x, camera.position.y + 0.35, camera.position.z);
    renderer.render(scene, camera);
  }

  // ── Overlay: environmental typography ────────────────────────────────
  // Vignette closes off the empty space above the walls and keeps the type
  // legible over the brightest corridor sections.
  const vignette = fill(
    'radial-gradient(120% 62% at 50% 46%, rgba(0,0,0,0) 38%, rgba(4,8,10,.62) 82%, rgba(4,8,10,.9) 100%)',
  );
  vignette.style.opacity = '1';
  root.append(vignette);

  const words = [
    { text: 'Smaller.', at: 1.6, top: 780 },
    { text: 'Faster.', at: 4.8, top: 900 },
    { text: 'Smarter.', at: 8.0, top: 1020 },
  ];

  for (const w of words) {
    const node = envType(w.text, { top: w.top });
    root.append(node);
    const start = t0 + w.at;
    tl.set(node, { opacity: 0 }, start - 0.01);
    tl.fromTo(node, { opacity: 0, scale: 1.14, filter: 'blur(14px)' }, { opacity: 1, scale: 1, filter: 'blur(0px)', duration: frames(4), ease: 'power3.out' }, start);
    // Under one second each — the run never stops for the type.
    tl.to(node, { opacity: 0, scale: 0.97, duration: frames(4), ease: 'power2.in' }, start + 0.62);
  }

  // Canvas visibility is timeline-driven so it never bleeds into other scenes.
  tl.set(canvas, { opacity: 1 }, t0);
  tl.set(root, { opacity: 1 }, t0);
  tl.set(canvas, { opacity: 0 }, t0 + dur);
  tl.set(root, { opacity: 0 }, t0 + dur);

  return {
    update,
    isActive: (time) => time >= t0 - 0.1 && time <= t0 + dur + 0.1,
    debug: () => ({
      /** Mouse position in normalised device coords; |x|,|y| > 1 is off-frame. */
      ndc: (() => {
        const v = mouse.group.position.clone();
        v.y = MOUSE_H * 0.5;
        v.project(camera);
        return { x: +v.x.toFixed(2), y: +v.y.toFixed(2) };
      })(),
      camera: camera.position.toArray().map((n) => +n.toFixed(3)),
      target: camTarget.toArray().map((n) => +n.toFixed(3)),
      mouse: mouse.group.position.toArray().map((n) => +n.toFixed(3)),
      distToMouse: +camera.position.distanceTo(mouse.group.position).toFixed(3),
      pathLength: +path.length.toFixed(2),
      wallCount: maze.walls.length,
    }),
  };
}
