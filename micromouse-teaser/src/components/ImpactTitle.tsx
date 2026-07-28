import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {condensed} from '../fonts';
// @ts-expect-error - plain-JS single source of truth
import {COLORS, SAFE} from '../timeline.mjs';

type Props = {
  word: string;
  durationInFrames: number;
  /** Vertical placement as a fraction of frame height. */
  anchorY: number;
};

/**
 * One of SMALLER. / FASTER. / SMARTER.
 *
 * Each word lands hard on its own audio impact and clears before the next one,
 * so the three are never on screen together. They sit off the robot's centre
 * line so the animation stays readable underneath.
 */
export const ImpactTitle: React.FC<Props> = ({word, durationInFrames, anchorY}) => {
  const frame = useCurrentFrame();

  // Snap in over 4 frames, hold, then cut away quickly.
  const punch = interpolate(frame, [0, 4], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const out = interpolate(
    frame,
    [durationInFrames - 6, durationInFrames - 1],
    [1, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.in(Easing.quad),
    },
  );

  const opacity = punch * out;
  const scale = interpolate(punch, [0, 1], [1.09, 1]);
  const barWidth = interpolate(frame, [1, 9], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'flex-start',
        alignItems: 'center',
        paddingTop: anchorY * 1920,
        paddingLeft: SAFE.side,
        paddingRight: SAFE.side,
        opacity,
      }}
    >
      <div style={{transform: `scale(${scale})`, textAlign: 'center'}}>
        <div
          style={{
            ...condensed(700, 75),
            fontSize: 132,
            letterSpacing: 2,
            color: COLORS.offWhite,
            lineHeight: 1,
            textShadow: '0 10px 60px rgba(3,19,26,0.9)',
          }}
        >
          {word}
        </div>
        <div
          style={{
            marginTop: 18,
            height: 4,
            width: 220 * barWidth,
            backgroundColor: COLORS.orange,
            marginLeft: 'auto',
            marginRight: 'auto',
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
