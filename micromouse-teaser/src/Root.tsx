import React from 'react';
import {Composition} from 'remotion';
import {Teaser} from './Teaser';
// @ts-expect-error - plain-JS single source of truth
import {DURATION_IN_FRAMES, FPS, HEIGHT, WIDTH} from './timeline.mjs';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Teaser"
    component={Teaser}
    durationInFrames={DURATION_IN_FRAMES}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
);
