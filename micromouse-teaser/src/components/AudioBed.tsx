import React from 'react';
import {Audio, staticFile} from 'remotion';
// @ts-expect-error - plain-JS single source of truth
import {ASSETS} from '../timeline.mjs';

/**
 * The original score, synthesised by tools/generate-audio.mjs and loudness
 * normalised to the targets in timeline.mjs. The source video's own audio is
 * muted in PrimaryFootage, so this is the only sound in the teaser.
 */
export const AudioBed: React.FC = () => (
  <Audio src={staticFile(ASSETS.score)} />
);
