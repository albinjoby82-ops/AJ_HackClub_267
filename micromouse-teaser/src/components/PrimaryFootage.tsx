import React from 'react';
import {
  AbsoluteFill,
  Easing,
  interpolate,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
} from 'remotion';
// @ts-expect-error - plain-JS single source of truth
import {ASSETS, COLORS, SOURCE} from '../timeline.mjs';

type Props = {
  /** Frame of the source video this segment starts on. */
  sourceStartFrame: number;
  durationInFrames: number;
  /** [start, end] scale. 1 = full frame. Used for digital push-ins and crops. */
  zoom?: [number, number];
  /** Normalised point of the source placed at the centre of the visible crop. */
  focus?: [number, number];
  /** [start, end] brightness multiplier, for the cold open ramp. */
  brightness?: [number, number];
  vignette?: number;
};

/**
 * One cut of the primary micromouse animation.
 *
 * The source is pre-upscaled to 1080x1920 with Lanczos (see
 * tools/prepare-media.mjs), so this component only ever scales *up* from a
 * full-frame fit. That keeps the robot and maze walls sharp and guarantees no
 * letterboxing or geometric distortion.
 */
export const PrimaryFootage: React.FC<Props> = ({
  sourceStartFrame,
  durationInFrames,
  zoom = [1, 1],
  focus = [0.5, 0.5],
  brightness,
  vignette = 0.55,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, Math.max(1, durationInFrames - 1)], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.quad),
  });

  const scale = interpolate(progress, [0, 1], zoom);
  const brightnessValue = brightness
    ? interpolate(progress, [0, 1], brightness)
    : 1;

  // At scale s the visible window is 1/s of the frame. Keeping `focus` at least
  // half a window from each edge guarantees the crop never runs off the source,
  // which is what would introduce black padding.
  const half = 0.5 / scale;
  const focusX = Math.min(Math.max(focus[0], half), 1 - half);
  const focusY = Math.min(Math.max(focus[1], half), 1 - half);

  // scale() about the centre combined with a translate puts `focus` exactly at
  // the centre of frame. Using transform-origin instead would pin the focus
  // point in place rather than centre it, which offsets the crop.
  const transform =
    `scale(${scale}) ` +
    `translate(${((0.5 - focusX) * 100).toFixed(4)}%, ${((0.5 - focusY) * 100).toFixed(4)}%)`;

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.navy, overflow: 'hidden'}}>
      <AbsoluteFill style={{transform}}>
        <OffthreadVideo
          src={staticFile(SOURCE.video)}
          trimBefore={sourceStartFrame}
          // The teaser carries its own score; the source audio is muted.
          muted
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            filter:
              brightnessValue === 1
                ? undefined
                : `brightness(${brightnessValue})`,
          }}
        />
      </AbsoluteFill>

      {vignette > 0 ? (
        <AbsoluteFill
          style={{
            background: `radial-gradient(ellipse 78% 62% at 50% 48%, rgba(3,19,26,0) 42%, rgba(3,19,26,${vignette}) 100%)`,
          }}
        />
      ) : null}
    </AbsoluteFill>
  );
};
