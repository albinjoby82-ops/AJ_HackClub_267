import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {AudioBed} from './components/AudioBed';
import {ElecSocEndCard} from './components/ElecSocEndCard';
import {ImpactTitle} from './components/ImpactTitle';
import {ColdOpenPulse, SensorSweep} from './components/MazeOverlay';
import {PrimaryFootage} from './components/PrimaryFootage';
import {TeaserText} from './components/TeaserText';
import {useTeaserFont} from './fonts';
// @ts-expect-error - plain-JS single source of truth
import {COLORS, COPY, segment, TEXT_CUES, TIMELINE} from './timeline.mjs';

type Segment = {
  id: string;
  kind: 'black' | 'video' | 'endCard';
  from: number;
  durationInFrames: number;
  sourceStartFrame?: number;
  zoom?: [number, number];
  focus?: [number, number];
  brightness?: [number, number];
};

/** Impact words sit in the upper third, clear of the robot. */
const IMPACT_ANCHOR_Y = 0.24;
const TEASER_ANCHOR_Y = 0.27;

const renderSegment = (s: Segment) => {
  if (s.kind === 'black') {
    // The pre-roll carries one faint pulse; the mid-edit gaps are true black
    // dips used as breathing room between the activation details.
    return s.id === 'preBlack' ? (
      <ColdOpenPulse durationInFrames={s.durationInFrames} />
    ) : null;
  }

  if (s.kind === 'endCard') {
    return <ElecSocEndCard durationInFrames={s.durationInFrames} />;
  }

  return (
    <PrimaryFootage
      sourceStartFrame={s.sourceStartFrame as number}
      durationInFrames={s.durationInFrames}
      zoom={s.zoom}
      focus={s.focus}
      brightness={s.brightness}
    />
  );
};

export const Teaser: React.FC = () => {
  useTeaserFont();
  const detailMid = segment('detailMid');

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.navy}}>
      {(TIMELINE as Segment[]).map((s) => {
        const content = renderSegment(s);
        if (content === null) return null;
        return (
          <Sequence
            key={s.id}
            from={s.from}
            durationInFrames={s.durationInFrames}
            name={s.id}
          >
            {content}
          </Sequence>
        );
      })}

      {/* One restrained sensor sweep during the activation beat. */}
      <Sequence
        from={detailMid.from}
        durationInFrames={detailMid.durationInFrames}
        name="sensorSweep"
      >
        <SensorSweep durationInFrames={detailMid.durationInFrames} />
      </Sequence>

      <Sequence
        from={TEXT_CUES.teaser.from}
        durationInFrames={TEXT_CUES.teaser.durationInFrames}
        name="teaserLine"
      >
        <TeaserText
          text={COPY.teaser}
          durationInFrames={TEXT_CUES.teaser.durationInFrames}
          anchorY={TEASER_ANCHOR_Y}
        />
      </Sequence>

      {TEXT_CUES.impacts.map(
        (cue: {word: string; from: number; durationInFrames: number}) => (
          <Sequence
            key={cue.word}
            from={cue.from}
            durationInFrames={cue.durationInFrames}
            name={cue.word}
          >
            <ImpactTitle
              word={cue.word}
              durationInFrames={cue.durationInFrames}
              anchorY={IMPACT_ANCHOR_Y}
            />
          </Sequence>
        ),
      )}

      <AudioBed />
    </AbsoluteFill>
  );
};
