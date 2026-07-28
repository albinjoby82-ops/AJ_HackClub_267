import gsap from 'gsap';
import { allImageUrls } from './assets.js';
import { grainDataUri } from './dom.js';
import { FPS, WIDTH, HEIGHT, SCENES, TOTAL_DURATION, TOTAL_FRAMES } from './timing.js';

import { build as buildPowerOn } from './scenes/scene01PowerOn.js';
import { build as buildRobotics } from './scenes/scene02Robotics.js';
import { build as buildMakerthon } from './scenes/scene03Makerthon.js';
import { build as buildRoboExpo } from './scenes/scene04RoboExpo.js';
import { build as buildPivot } from './scenes/scene05Pivot.js';
import { build as buildMazeRun } from './scenes/scene06MazeRun.js';
import { build as buildLogoVideo } from './scenes/scene07LogoVideo.js';
import { build as buildTitle } from './scenes/scene08Title.js';

const params = new URLSearchParams(location.search);
const RENDER_MODE = params.get('render') === '1';

const stage = document.getElementById('stage');
const canvas = document.getElementById('maze-canvas');
const video = document.getElementById('logo-video');
const score = document.getElementById('score-audio');
const loader = document.getElementById('loader');

canvas.width = WIDTH;
canvas.height = HEIGHT;

if (RENDER_MODE) document.body.classList.add('-render');

/** Scales the 1080x1920 stage to fit the window during preview only. */
function fitStage() {
  if (RENDER_MODE) return;
  const scale = Math.min(window.innerWidth / WIDTH, (window.innerHeight - 70) / HEIGHT);
  stage.style.setProperty('--fit', scale);
}
window.addEventListener('resize', fitStage);
fitStage();

document.getElementById('grain').style.setProperty('--grain-src', grainDataUri());

// ── Preload ─────────────────────────────────────────────────────────────
async function preload() {
  const urls = allImageUrls();
  let done = 0;
  const label = loader.querySelector('b');
  const total = urls.length + 2;
  const tick = () => {
    done++;
    label.textContent = `${Math.round((done / total) * 100)}%`;
  };
  const mediaReady = (media, name) =>
    new Promise((resolve) => {
      let settled = false;
      const finish = () => {
        if (settled) return;
        settled = true;
        tick();
        resolve();
      };
      if (media.readyState >= 3) return finish();
      media.addEventListener('canplaythrough', finish, { once: true });
      media.addEventListener(
        'error',
        () => {
          console.warn(`[preload] ${name} failed to load`);
          finish();
        },
        { once: true },
      );
      media.load();
    });

  await Promise.all([
    ...urls.map(
      (url) =>
        new Promise((resolve) => {
          const img = new Image();
          const finish = () => {
            tick();
            resolve();
          };
          img.onload = finish;
          img.onerror = () => {
            console.warn('[preload] missing asset', url);
            finish();
          };
          img.src = url;
        }),
    ),
    mediaReady(video, 'logo reveal video'),
    mediaReady(score, 'soundtrack'),
  ]);
}

// ── Build ───────────────────────────────────────────────────────────────
const tl = gsap.timeline({ paused: true });
const sceneRoot = (name) => document.querySelector(`.scene[data-scene="${name}"]`);

let mazeScene = null;
let logoScene = null;

function buildAll() {
  buildPowerOn({ root: sceneRoot('powerOn'), tl, t0: SCENES.powerOn.start, dur: SCENES.powerOn.duration });
  buildRobotics({ root: sceneRoot('robotics'), tl, t0: SCENES.robotics.start, dur: SCENES.robotics.duration });
  buildMakerthon({ root: sceneRoot('makerthon'), tl, t0: SCENES.makerthon.start, dur: SCENES.makerthon.duration });
  buildRoboExpo({ root: sceneRoot('roboExpo'), tl, t0: SCENES.roboExpo.start, dur: SCENES.roboExpo.duration });
  buildPivot({ root: sceneRoot('pivot'), tl, t0: SCENES.pivot.start, dur: SCENES.pivot.duration });

  mazeScene = buildMazeRun({
    root: sceneRoot('mazeRun'),
    tl,
    t0: SCENES.mazeRun.start,
    dur: SCENES.mazeRun.duration,
    canvas,
  });

  logoScene = buildLogoVideo({
    root: sceneRoot('title'),
    tl,
    t0: SCENES.logoVideo.start,
    dur: SCENES.logoVideo.duration,
    video,
    backdrop: document.getElementById('video-backdrop'),
  });

  buildTitle({ root: sceneRoot('title'), tl, t0: SCENES.title.start, dur: SCENES.title.duration });

  // Pin the timeline's full length even if the last tween ends earlier.
  tl.set({}, {}, TOTAL_DURATION);
}

/**
 * Seeks the whole film to an absolute time.
 * Async because the video tail must present its frame before capture.
 */
async function seek(time) {
  const t = Math.max(0, Math.min(TOTAL_DURATION, time));
  tl.time(t, false);

  if (!RENDER_MODE && Math.abs(score.currentTime - t) > 0.12) score.currentTime = t;
  if (mazeScene?.isActive(t)) mazeScene.update(t);
  if (logoScene?.isActive(t)) await logoScene.syncVideo(t);
}

// ── Preview transport ───────────────────────────────────────────────────
function setupScrubber() {
  const playBtn = document.getElementById('play');
  const seekBar = document.getElementById('seek');
  const readout = document.getElementById('readout');

  let playing = false;
  let rafId = null;
  let startWall = 0;
  let startTime = 0;

  const refresh = (t) => {
    seekBar.value = String(Math.round((t / TOTAL_DURATION) * 1000));
    readout.textContent = `${t.toFixed(2)}s`;
  };

  const loop = () => {
    const t = startTime + (performance.now() - startWall) / 1000;
    if (t >= TOTAL_DURATION) {
      seek(TOTAL_DURATION);
      refresh(TOTAL_DURATION);
      stop();
      return;
    }
    seek(t);
    refresh(t);
    rafId = requestAnimationFrame(loop);
  };

  const stop = () => {
    playing = false;
    playBtn.textContent = '▶';
    score.pause();
    if (rafId) cancelAnimationFrame(rafId);
  };

  playBtn.addEventListener('click', () => {
    if (playing) return stop();
    playing = true;
    playBtn.textContent = '❚❚';
    startTime = (Number(seekBar.value) / 1000) * TOTAL_DURATION;
    if (startTime >= TOTAL_DURATION - 0.01) startTime = 0;
    score.currentTime = startTime;
    score.play().catch(() => {});
    startWall = performance.now();
    rafId = requestAnimationFrame(loop);
  });

  seekBar.addEventListener('input', () => {
    stop();
    const t = (Number(seekBar.value) / 1000) * TOTAL_DURATION;
    seek(t);
    refresh(t);
  });

  refresh(0);
}

// ── Boot ────────────────────────────────────────────────────────────────
(async () => {
  await preload();
  buildAll();
  await seek(0);

  loader.classList.add('-done');
  if (!RENDER_MODE) setupScrubber();

  // Capture API.
  window.__reveal = {
    seek,
    FPS,
    WIDTH,
    HEIGHT,
    TOTAL_DURATION,
    TOTAL_FRAMES,
    ready: true,
    debug: () => mazeScene?.debug(),
  };
})();
