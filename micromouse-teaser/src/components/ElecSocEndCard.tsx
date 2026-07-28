import React from 'react';
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import {condensed} from '../fonts';
import {MazeCircuit} from './MazeOverlay';
// @ts-expect-error - plain-JS single source of truth
import {ASSETS, COLORS, COPY, END_CARD} from '../timeline.mjs';

/**
 * Layout constants. The card is built as live type and the official logo
 * bitmap at its native aspect ratio (376x235) — nothing here is an upscale of
 * the source video's own end card.
 */
const LOGO_WIDTH = 320;
const LOGO_HEIGHT = Math.round((LOGO_WIDTH * 235) / 376); // 200
const LOGO_LEFT = (1080 - LOGO_WIDTH) / 2;
const LOGO_TOP = 470;

/** Centre and radius of the circuit emblem inside the logo bitmap. */
const EMBLEM = {
  x: LOGO_LEFT + LOGO_WIDTH * 0.234,
  y: LOGO_TOP + LOGO_HEIGHT * 0.498,
  r: LOGO_WIDTH * 0.181,
};

/**
 * Where the orange route line finished drawing its circle at the end of the
 * bridge shot. The ring starts here so the cut reads as a match on the circle.
 */
const ROUTE_CIRCLE = {x: 475, y: 700, r: 361};

const ease = (frame: number, from: number, duration: number) =>
  interpolate(frame, [from, from + duration], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

export const ElecSocEndCard: React.FC<{durationInFrames: number}> = ({
  durationInFrames,
}) => {
  const frame = useCurrentFrame();

  const ringP = ease(frame, END_CARD.ring.from, END_CARD.ring.durationInFrames);
  const logoP = ease(frame, END_CARD.logo.from, END_CARD.logo.durationInFrames);
  const titleP = ease(frame, END_CARD.title.from, END_CARD.title.durationInFrames);
  const taglineP = ease(
    frame,
    END_CARD.tagline.from,
    END_CARD.tagline.durationInFrames,
  );
  const soonP = ease(
    frame,
    END_CARD.comingSoon.from,
    END_CARD.comingSoon.durationInFrames,
  );

  // Controlled fade to black. Everything is frozen from END_CARD.settledAt
  // until END_CARD.holdUntil, so the completed card is genuinely motionless.
  const fade = interpolate(
    frame,
    [END_CARD.holdUntil, durationInFrames],
    [1, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.inOut(Easing.quad),
    },
  );

  const ringRadius = interpolate(ringP, [0, 1], [ROUTE_CIRCLE.r, EMBLEM.r]);
  const ringX = interpolate(ringP, [0, 1], [ROUTE_CIRCLE.x, EMBLEM.x]);
  const ringY = interpolate(ringP, [0, 1], [ROUTE_CIRCLE.y, EMBLEM.y]);
  const ringOpacity = interpolate(ringP, [0, 0.7, 1], [0.9, 0.35, 0]);

  const taglineTracking = interpolate(taglineP, [0, 1], [26, 12]);

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.navy}}>
      <AbsoluteFill style={{opacity: fade}}>
        {/* Static base wash — no movement during the hold. */}
        <AbsoluteFill
          style={{
            background: `radial-gradient(ellipse 70% 44% at 50% 42%, ${COLORS.teal}55 0%, ${COLORS.navy} 68%)`,
          }}
        />

        <MazeCircuit opacity={0.13 * ease(frame, END_CARD.blackLead, 34)} />

        {/* Match cut: the route circle contracts into the logo emblem. */}
        {ringOpacity > 0.001 ? (
          <AbsoluteFill>
            <svg width={1080} height={1920} viewBox="0 0 1080 1920">
              <circle
                cx={ringX}
                cy={ringY}
                r={ringRadius}
                fill="none"
                stroke={COLORS.orange}
                strokeWidth={interpolate(ringP, [0, 1], [7, 3])}
                opacity={ringOpacity}
              />
            </svg>
          </AbsoluteFill>
        ) : null}

        {/* 1. Official ElecSoc logo, small, upper section. */}
        <div
          style={{
            position: 'absolute',
            left: LOGO_LEFT,
            top: LOGO_TOP,
            width: LOGO_WIDTH,
            height: LOGO_HEIGHT,
            opacity: logoP,
            transform: `scale(${interpolate(logoP, [0, 1], [0.94, 1])})`,
          }}
        >
          <Img
            src={staticFile(ASSETS.logo)}
            style={{width: '100%', height: '100%', display: 'block'}}
          />
        </div>

        {/* 2. Main title — the dominant element. */}
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: 830,
            textAlign: 'center',
            opacity: titleP,
            transform: `scale(${interpolate(titleP, [0, 1], [1.05, 1])})`,
          }}
        >
          <div
            style={{
              ...condensed(700, 75),
              fontSize: 126,
              letterSpacing: 1,
              color: COLORS.offWhite,
              lineHeight: 1,
              textShadow: '0 10px 60px rgba(3,19,26,0.7)',
            }}
          >
            {COPY.title}
          </div>
        </div>

        {/* 3. Tagline — smaller, pale cyan, widely tracked. */}
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: 1010,
            textAlign: 'center',
            opacity: taglineP,
          }}
        >
          <div
            style={{
              ...condensed(600, 78),
              fontSize: 34,
              letterSpacing: taglineTracking,
              color: COLORS.cyan,
              lineHeight: 1.2,
            }}
          >
            {COPY.tagline}
          </div>
        </div>

        {/* 4. COMING SOON — orange, clearly separated, lower section. */}
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: 1290,
            textAlign: 'center',
            opacity: soonP,
          }}
        >
          <div
            style={{
              ...condensed(700, 78),
              fontSize: 46,
              letterSpacing: 16,
              color: COLORS.orange,
              lineHeight: 1.2,
            }}
          >
            {COPY.comingSoon}
          </div>
          <div
            style={{
              margin: '22px auto 0',
              height: 3,
              width: 132 * soonP,
              backgroundColor: COLORS.orange,
              opacity: 0.55,
            }}
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
