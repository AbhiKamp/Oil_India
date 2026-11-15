import React from 'react';
import {Composition} from 'remotion';
import {BeforeTheNextMetre} from './video';

export const Root: React.FC = () => (
  <Composition
    id="BeforeTheNextMetre"
    component={BeforeTheNextMetre}
    durationInFrames={4227}
    fps={30}
    width={1920}
    height={1080}
  />
);
