import React from 'react';
import {Easing, interpolate} from 'remotion';
import type {SpotKey} from './timeline';

export type SpotState = {x: number; y: number; rx: number; ry: number; it: number};

/**
 * Sample a spotlight keyframe track at a frame, with an organic multi-sine
 * wobble so the beam never moves like a "flashlight app". `calm` scales the
 * wobble down (used once the light settles on the final announcement).
 */
export const sampleTrack = (track: SpotKey[], frame: number, calm = 1): SpotState => {
  const first = track[0];
  const last = track[track.length - 1];
  let x = first.x;
  let y = first.y;
  let rx = first.rx;
  let ry = first.ry;
  let it = first.it;

  if (frame >= last.f) {
    ({x, y, rx, ry, it} = last);
  } else if (frame > first.f) {
    for (let i = 0; i < track.length - 1; i++) {
      const a = track[i];
      const b = track[i + 1];
      if (frame >= a.f && frame < b.f) {
        const jump = b.f - a.f <= 6; // beat jumps snap with a fast ease-out
        const ease = jump ? Easing.out(Easing.cubic) : Easing.inOut(Easing.quad);
        const t = interpolate(frame, [a.f, b.f], [0, 1], {easing: ease});
        x = a.x + (b.x - a.x) * t;
        y = a.y + (b.y - a.y) * t;
        rx = a.rx + (b.rx - a.rx) * t;
        ry = a.ry + (b.ry - a.ry) * t;
        it = a.it + (b.it - a.it) * t;
        break;
      }
    }
  }

  const w = calm;
  x += w * (10 * Math.sin(frame * 0.061 + 2.0) + 6 * Math.sin(frame * 0.142 + 0.5));
  y += w * (8 * Math.sin(frame * 0.053 + 1.1) + 5 * Math.sin(frame * 0.127 + 2.6));
  rx *= 1 + w * 0.03 * Math.sin(frame * 0.083 + 0.7);
  ry *= 1 + w * 0.03 * Math.sin(frame * 0.097 + 1.9);
  return {x, y, rx, ry, it};
};

const abs = (extra: React.CSSProperties = {}): React.CSSProperties => ({
  position: 'absolute',
  inset: 0,
  pointerEvents: 'none',
  ...extra,
});

/**
 * The spotlight is built as darkness with a feathered hole, not a lifted
 * image: a near-black overlay carrying a radial-gradient hole (≈120 px
 * feather), a uniform dim layer that caps the in-beam brightness at `it`,
 * a lagged volumetric haze, a faint warm edge and a subtle bloom.
 */
export const SpotlightRig: React.FC<{spot: SpotState; haze: SpotState}> = ({spot, haze}) => {
  const {x, y, rx, ry, it} = spot;
  const feather = Math.min(150, Math.max(90, (rx + ry) / 5));
  const clearPct = Math.max(0, (1 - feather / ((rx + ry) / 2)) * 88);

  return (
    <>
      <div
        style={abs({
          background: `radial-gradient(${haze.rx * 2.3}px ${haze.ry * 2.3}px at ${haze.x}px ${haze.y}px, rgba(168,190,205,${(0.05 * it).toFixed(3)}) 0%, rgba(168,190,205,0) 65%)`,
          mixBlendMode: 'screen',
        })}
      />
      <div
        style={abs({
          background: `radial-gradient(${rx}px ${ry}px at ${x}px ${y}px, rgba(1,3,5,0) 0%, rgba(1,3,5,0.02) ${(clearPct * 0.6).toFixed(1)}%, rgba(1,3,5,0.2) ${clearPct.toFixed(1)}%, rgba(1,3,5,0.93) 96%, rgb(1,3,5) 100%)`,
        })}
      />
      <div style={abs({background: 'rgb(1,3,5)', opacity: 1 - it})} />
      <div
        style={abs({
          background: `radial-gradient(${rx * 1.12}px ${ry * 1.12}px at ${x}px ${y}px, rgba(0,0,0,0) 0%, rgba(0,0,0,0) 76%, rgba(255,138,66,${(0.09 * it).toFixed(3)}) 90%, rgba(255,138,66,0) 100%)`,
          mixBlendMode: 'screen',
        })}
      />
      <div
        style={abs({
          background: `radial-gradient(${rx * 1.5}px ${ry * 1.5}px at ${x}px ${y}px, rgba(255,214,170,${(0.12 * it).toFixed(3)}) 0%, rgba(255,214,170,0) 58%)`,
          mixBlendMode: 'screen',
        })}
      />
    </>
  );
};

const GRAIN_URI = `data:image/svg+xml;utf8,${encodeURIComponent(
  `<svg xmlns="http://www.w3.org/2000/svg" width="360" height="360"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter><rect width="360" height="360" filter="url(%23n)"/></svg>`,
)}`;

/** Film grain — overlay blend so true blacks stay black. */
export const Grain: React.FC<{frame: number; opacity?: number}> = ({frame, opacity = 0.04}) => (
  <div
    style={{
      position: 'absolute',
      inset: -40,
      pointerEvents: 'none',
      backgroundImage: `url("${GRAIN_URI}")`,
      backgroundPosition: `${(frame % 4) * 89}px ${(frame % 3) * 71}px`,
      mixBlendMode: 'overlay',
      opacity,
    }}
  />
);

export const Vignette: React.FC<{strength?: number}> = ({strength = 0.38}) => (
  <div
    style={abs({
      background: `radial-gradient(130% 130% at 50% 50%, rgba(0,0,0,0) 52%, rgba(0,0,0,${strength}) 100%)`,
    })}
  />
);
