import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
// @ts-expect-error - plain-JS single source of truth
import {COLORS} from '../timeline.mjs';

/**
 * Deterministic maze/circuit line work drawn from the palette.
 *
 * Two uses: a single faint pulse over the cold open, and the very low-contrast
 * background lattice behind the end card. Geometry is hard-coded rather than
 * random so every render is byte-identical.
 */

const LATTICE: string[] = [
  'M 0 300 H 250 V 470 H 470',
  'M 1080 250 H 830 V 430 H 640',
  'M 0 1500 H 190 V 1320 H 430',
  'M 1080 1560 H 900 V 1400 H 700',
  'M 120 1780 V 1650 H 360',
  'M 960 1750 V 1620 H 760',
  'M 40 760 H 160 V 900',
  'M 1040 820 H 930 V 960',
];

export const MazeCircuit: React.FC<{opacity: number}> = ({opacity}) => (
  <AbsoluteFill style={{opacity}}>
    <svg width={1080} height={1920} viewBox="0 0 1080 1920">
      {LATTICE.map((d, i) => (
        <path
          key={i}
          d={d}
          fill="none"
          stroke={i % 3 === 0 ? COLORS.orange : COLORS.cyan}
          strokeWidth={i % 3 === 0 ? 3 : 2}
          strokeLinecap="square"
        />
      ))}
      <circle cx={250} cy={470} r={7} fill={COLORS.cyan} />
      <circle cx={830} cy={430} r={7} fill={COLORS.cyan} />
      <circle cx={190} cy={1320} r={7} fill={COLORS.orange} />
      <circle cx={900} cy={1400} r={7} fill={COLORS.cyan} />
    </svg>
  </AbsoluteFill>
);

/**
 * The cold open's single faint pulse — one ring easing outward in the dark,
 * before any of the robot is shown.
 */
export const ColdOpenPulse: React.FC<{durationInFrames: number}> = ({
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  const radius = interpolate(progress, [0, 1], [10, 260]);
  const opacity = interpolate(progress, [0, 0.22, 1], [0, 0.72, 0]);

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.navy}}>
      <svg width={1080} height={1920} viewBox="0 0 1080 1920">
        <circle
          cx={540}
          cy={820}
          r={radius}
          fill="none"
          stroke={COLORS.orange}
          strokeWidth={2.5}
          opacity={opacity}
        />
        <circle
          cx={540}
          cy={820}
          r={radius * 0.45}
          fill="none"
          stroke={COLORS.cyan}
          strokeWidth={1.5}
          opacity={opacity * 0.7}
        />
      </svg>
    </AbsoluteFill>
  );
};

/**
 * A single restrained sensor sweep, used sparingly during the activation beat.
 */
export const SensorSweep: React.FC<{durationInFrames: number}> = ({
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.quad),
  });

  const y = interpolate(progress, [0, 1], [-200, 2120]);
  const opacity = interpolate(progress, [0, 0.2, 0.8, 1], [0, 0.32, 0.32, 0]);

  return (
    <AbsoluteFill style={{opacity}}>
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: y,
          height: 190,
          background: `linear-gradient(180deg, rgba(145,190,193,0) 0%, rgba(145,190,193,0.5) 50%, rgba(145,190,193,0) 100%)`,
          mixBlendMode: 'screen',
        }}
      />
    </AbsoluteFill>
  );
};
