import React from 'react';
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';
// @ts-expect-error - plain-JS single source of truth
import {ASSETS, COLORS, END_CARD} from '../timeline.mjs';

/**
 * V3 end card: the supplied 1080x1920 announcement poster, revealed.
 *
 * The chase hard-cuts onto black and the poster lights up out of it over eight
 * frames — brightness and opacity rise together while a whisper of scale
 * settles out, so it reads as a light coming up on the artwork rather than a
 * dissolve. A three-frame orange flash lands on the bass hit at the cut.
 *
 * From frame 8 nothing moves at all, and there is no fade-out: the teaser ends
 * holding the poster at full strength. The artwork already carries the ElecSoc
 * logo, the headline, the event name and the date line, so it is laid in at its
 * native resolution and nothing is drawn on top of it.
 */
export const ElecSocEndCard: React.FC<{durationInFrames: number}> = () => {
  const frame = useCurrentFrame();

  // One reveal for the whole poster. Clamped at both ends so the hold that
  // follows is frame-for-frame identical.
  const reveal = interpolate(frame, [0, END_CARD.settleFrames], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  const opacity = reveal;
  const brightness = interpolate(reveal, [0, 1], [0.35, 1]);
  const scale = interpolate(reveal, [0, 1], [1.03, 1]);

  // Brief accent flash that lands with the bass hit on the cut.
  const flash = interpolate(frame, [0, END_CARD.flashFrames], [0.16, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.quad),
  });

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.navy}}>
      <Img
        src={staticFile(ASSETS.endPoster)}
        style={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          opacity,
          filter: `brightness(${brightness.toFixed(3)})`,
          transform: `scale(${scale.toFixed(4)})`,
        }}
      />

      {flash > 0.001 ? (
        <AbsoluteFill style={{backgroundColor: COLORS.orange, opacity: flash}} />
      ) : null}
    </AbsoluteFill>
  );
};
