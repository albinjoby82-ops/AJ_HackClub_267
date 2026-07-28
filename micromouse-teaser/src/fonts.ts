import React from 'react';
import {cancelRender, continueRender, delayRender, staticFile} from 'remotion';
// @ts-expect-error - plain-JS single source of truth
import {ASSETS} from './timeline.mjs';

export const FONT_FAMILY = 'TeaserCondensed';

/**
 * Bahnschrift is the brief's first-choice condensed technical sans and ships
 * with Windows. It is a variable font, so the condensed cut comes from the
 * `wdth` axis rather than a separate file.
 *
 * The face is embedded from public/ rather than relied on as an installed
 * system font, so the render is identical on any host. The FontFace API is
 * used directly — injecting @font-face CSS and awaiting document.fonts.load()
 * can hang indefinitely for a variable face, which stalls the renderer.
 */
let loader: Promise<void> | null = null;

const loadTeaserFont = () => {
  if (loader) return loader;

  loader = (async () => {
    const face = new FontFace(
      FONT_FAMILY,
      `url(${staticFile(ASSETS.font)}) format('truetype')`,
      {weight: '100 900', stretch: '75% 100%'},
    );
    await face.load();
    document.fonts.add(face);
  })();

  return loader;
};

/**
 * Blocks the render until the face is available. Called from the composition
 * so the handle belongs to the render pass rather than to bundle evaluation.
 */
export const useTeaserFont = () => {
  const [handle] = React.useState(() =>
    delayRender('Loading Bahnschrift Condensed'),
  );

  React.useEffect(() => {
    loadTeaserFont()
      .then(() => continueRender(handle))
      .catch((error) => cancelRender(error));
  }, [handle]);
};

/** Condensed + bold instance of the variable face. */
export const condensed = (weight = 700, width = 75): React.CSSProperties => ({
  fontFamily: `'${FONT_FAMILY}', 'Arial Narrow', 'Segoe UI', sans-serif`,
  fontWeight: weight,
  fontVariationSettings: `'wght' ${weight}, 'wdth' ${width}`,
  fontStretch: `${width}%`,
});
