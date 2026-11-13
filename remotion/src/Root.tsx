import React from 'react';
import {Composition} from 'remotion';
import {Explainer, ExplainerProps} from './Explainer';
import {Data, DATA_FRAMES} from './Data';

const sample: ExplainerProps = {
  durationInFrames: 300,
  handle: '@suksesishqip',
  beats: [
    {type: 'hook', from: 0, dur: 75, text: 'Një punë anash që s’kërkon asnjë lek kapital.'},
    {type: 'number', from: 75, dur: 75, value: 0, prefix: '', suffix: '€', label: 'kapital për të nisur', from_value: 500},
    {type: 'list', from: 150, dur: 90, title: 'Të duhen vetëm:', items: ['ChatGPT', 'Canva', 'Një telefon']},
    {type: 'text', from: 240, dur: 60, text: 'Klienti i parë vjen nga njerëzit që njeh.', highlight: 'Fillo sot.'},
  ],
};

export const Root: React.FC = () => (
  <>
  <Composition id="Data" component={Data} width={1080} height={1920} fps={30} durationInFrames={DATA_FRAMES} />
  <Composition
    id="Explainer"
    component={Explainer}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={sample.durationInFrames}
    defaultProps={sample}
    calculateMetadata={({props}) => ({durationInFrames: props.durationInFrames})}
  />
  </>
);
