import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {condensed} from '../fonts';
// @ts-expect-error - plain-JS single source of truth
import {COLORS, SAFE} from '../timeline.mjs';

type Props = {
  text: string;
  durationInFrames: number;
  /** Vertical placement as a fraction of frame height. */
  anchorY: number;
};

/**
 * The single foreshadowing line. It resolves cleanly as one block — no
 * per-letter scramble — and holds long enough to be read comfortably before
 * the chase begins.
 */
export const TeaserText: React.FC<Props> = ({
  text,
  durationInFrames,
  anchorY,
}) => {
  const frame = useCurrentFrame();

  const easeIn = interpolate(frame, [0, 12], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const easeOut = interpolate(
    frame,
    [durationInFrames - 12, durationInFrames],
    [1, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.in(Easing.cubic),
    },
  );
  const opacity = easeIn * easeOut;

  // A very small settle, not a slide. Movement here should feel like focus
  // resolving rather than a motion-graphics flourish.
  const lift = interpolate(easeIn, [0, 1], [14, 0]);
  const rule = interpolate(frame, [4, 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill
      style={{
        // Sits above the robot's centre line so the animation stays readable.
        justifyContent: 'flex-start',
        alignItems: 'center',
        paddingTop: anchorY * 1920,
        paddingLeft: SAFE.side,
        paddingRight: SAFE.side,
        opacity,
      }}
    >
      <div style={{transform: `translateY(${lift}px)`, textAlign: 'center'}}>
        <div
          style={{
            ...condensed(700, 75),
            fontSize: 76,
            letterSpacing: 6,
            color: COLORS.offWhite,
            lineHeight: 1.1,
            textShadow: '0 6px 40px rgba(3,19,26,0.85)',
          }}
        >
          {text}
        </div>
        <div
          style={{
            marginTop: 26,
            height: 3,
            width: 168 * rule,
            backgroundColor: COLORS.orange,
            marginLeft: 'auto',
            marginRight: 'auto',
            opacity: 0.9,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
