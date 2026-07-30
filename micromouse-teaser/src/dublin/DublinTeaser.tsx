import React from 'react';
import {
  AbsoluteFill,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import {
  ASSETS,
  BEATS,
  CUTS,
  END_FADE,
  POSTER1_TRACK,
  POSTER2_TRACK,
  TURN2_DIP,
} from './timeline';
import {Grain, SpotlightRig, Vignette, sampleTrack} from './layers';
import type {SpotKey} from './timeline';

const BLACK = 'rgb(1,3,5)';

/** A poster behind darkness, revealed only through the moving spotlight. */
const PosterReveal: React.FC<{
  src: string;
  track: SpotKey[];
  scaleAt: (frame: number) => number;
  calmAt?: (frame: number) => number;
  frameOffset: number; // sequence start, so track frames (absolute) line up
}> = ({src, track, scaleAt, calmAt, frameOffset}) => {
  const local = useCurrentFrame();
  const frame = local + frameOffset;
  const calm = calmAt ? calmAt(frame) : 1;
  const spot = sampleTrack(track, frame, calm);
  const haze = sampleTrack(track, Math.max(track[0].f, frame - 6), calm);
  const scale = scaleAt(frame);

  return (
    <AbsoluteFill style={{backgroundColor: BLACK}}>
      <Img
        src={staticFile(src)}
        style={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transform: `scale(${scale})`,
        }}
      />
      <SpotlightRig spot={spot} haze={haze} />
      <Grain frame={frame} />
      <Vignette />
    </AbsoluteFill>
  );
};

/** Sharp-turn shot 1 — full frame, overhead corner snap. */
const Turn1: React.FC = () => (
  <AbsoluteFill style={{backgroundColor: BLACK}}>
    <OffthreadVideo
      muted
      src={staticFile(ASSETS.turn1)}
      style={{
        width: '100%',
        height: '100%',
        objectFit: 'cover',
        filter: 'contrast(1.05) saturate(1.06) brightness(0.98)',
      }}
    />
    <Vignette strength={0.45} />
  </AbsoluteFill>
);

/**
 * Sharp-turn shot 2 — banked low-angle turn, reframed to a bottom-anchored
 * 720×1280 window scaled 1.5× (crops the source's "SMARTER." overlay out of
 * the top of frame entirely). Ends on a 3-frame near-black impact dip.
 */
const Turn2: React.FC = () => {
  const local = useCurrentFrame();
  // Window pans from the right (where the mouse enters banked) to centre.
  const x0 = interpolate(local, [0, 14], [330, 180], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const y0 = 640;
  const dip = TURN2_DIP.reduce(
    (acc, [f, o]) => (local + CUTS.turn1End >= f ? o : acc),
    0,
  );

  return (
    <AbsoluteFill style={{backgroundColor: BLACK, overflow: 'hidden'}}>
      <OffthreadVideo
        muted
        src={staticFile(ASSETS.turn2)}
        style={{
          position: 'absolute',
          width: 1080 * 1.5,
          height: 1920 * 1.5,
          transform: `translate(${-x0 * 1.5}px, ${-y0 * 1.5}px)`,
          filter: 'contrast(1.05) saturate(1.06) brightness(0.98)',
        }}
      />
      <Vignette strength={0.45} />
      <AbsoluteFill style={{backgroundColor: BLACK, opacity: dip}} />
    </AbsoluteFill>
  );
};

export const DublinTeaser: React.FC = () => {
  const frame = useCurrentFrame();

  // Poster 1: static 1.02 until the 3.7 s hit, then a slow push to 1.05.
  const poster1Scale = (f: number) =>
    interpolate(f, [111, CUTS.poster1End], [1.02, 1.05], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });

  // Poster 2: tiny continuous cinematic push across beats and hold.
  const poster2Scale = (f: number) =>
    interpolate(f, [CUTS.turn2End, CUTS.end], [1.0, 1.035], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });

  // The light steadies once it settles on the final announcement.
  const poster2Calm = (f: number) =>
    interpolate(f, [CUTS.beatsEnd, CUTS.beatsEnd + 14], [0.8, 0.45], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });

  const endFade = interpolate(frame, [END_FADE.start, CUTS.end - 1], [0, END_FADE.opacity], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{backgroundColor: BLACK}}>
      <Sequence durationInFrames={CUTS.poster1End}>
        <PosterReveal
          src={ASSETS.poster1}
          track={POSTER1_TRACK}
          scaleAt={poster1Scale}
          frameOffset={0}
        />
      </Sequence>

      <Sequence from={CUTS.poster1End} durationInFrames={CUTS.turn1End - CUTS.poster1End}>
        <Turn1 />
      </Sequence>

      <Sequence from={CUTS.turn1End} durationInFrames={CUTS.turn2End - CUTS.turn1End}>
        <Turn2 />
      </Sequence>

      <Sequence from={CUTS.turn2End} durationInFrames={CUTS.end - CUTS.turn2End}>
        <PosterReveal
          src={ASSETS.poster2}
          track={POSTER2_TRACK}
          scaleAt={poster2Scale}
          calmAt={poster2Calm}
          frameOffset={CUTS.turn2End}
        />
      </Sequence>

      <AbsoluteFill style={{backgroundColor: BLACK, opacity: endFade}} />
    </AbsoluteFill>
  );
};

export {BEATS};
