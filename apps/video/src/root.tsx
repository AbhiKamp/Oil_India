import React from 'react';
import {Composition} from 'remotion';
import {BeforeTheNextMetre} from './video';
import {NwisShort, SHORT_FRAMES} from './short';

export const Root: React.FC = () => (
  <>
  <Composition
    id="NwisShort"
    component={NwisShort}
    durationInFrames={SHORT_FRAMES}
    fps={30}
    width={1920}
    height={1080}
  />
  <Composition
    id="BeforeTheNextMetre"
    component={BeforeTheNextMetre}
    durationInFrames={4227}
    fps={30}
    width={1920}
    height={1080}
  />
  </>
);
