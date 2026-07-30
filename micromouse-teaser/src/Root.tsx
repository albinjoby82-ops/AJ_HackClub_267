import React from 'react';
import {Composition} from 'remotion';
import {Teaser} from './Teaser';
import {DublinTeaser} from './dublin/DublinTeaser';
import {
  DURATION_IN_FRAMES as DUBLIN_DURATION,
  FPS as DUBLIN_FPS,
  HEIGHT as DUBLIN_HEIGHT,
  WIDTH as DUBLIN_WIDTH,
} from './dublin/timeline';
// @ts-expect-error - plain-JS single source of truth
import {DURATION_IN_FRAMES, FPS, HEIGHT, WIDTH} from './timeline.mjs';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="Teaser"
      component={Teaser}
      durationInFrames={DURATION_IN_FRAMES}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
    <Composition
      id="DublinTeaser"
      component={DublinTeaser}
      durationInFrames={DUBLIN_DURATION}
      fps={DUBLIN_FPS}
      width={DUBLIN_WIDTH}
      height={DUBLIN_HEIGHT}
    />
  </>
);
