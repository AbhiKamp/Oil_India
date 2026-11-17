import React from 'react';
import {Audio, Video} from '@remotion/media';
import {AbsoluteFill, Easing, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const ivory = '#f1eee6';
const muted = '#a0a9aa';
const amber = '#e7b76c';
const cyan = '#77c7d6';

const captions = [
  {from: 0, to: 8, text: 'The next drilling risk may already be written down—in the report of a well drilled years ago.'},
  {from: 8, to: 16, text: 'eRTMAC shows what is happening now. Historical lessons are buried in scattered reports.'},
  {from: 16, to: 24, text: 'NWIS connects those lessons to the interval ahead—with the source beside the warning.'},
  {from: 24, to: 31, text: 'At 5 km, this synthetic demo returns one offset. Radius is a first filter, not a geology match.'},
  {from: 31, to: 36, text: 'Expand to 50 km: three offsets. Surface distance alone does not establish geological similarity.'},
  {from: 36, to: 41, text: 'Compare the reported formation intervals on a shared measured-depth scale.'},
  {from: 41, to: 46, text: 'A historical pack-off is listed 32.9 m MD ahead using approximate formation-top mapping.'},
  {from: 46, to: 51, text: 'Open marker 19 in the synthetic text report. It is not a verified physical PDF page.'},
  {from: 51, to: 56, text: 'A generated training-only PDF becomes a structured event with its physical page reference.'},
  {from: 56, to: 61, text: 'The extracted event starts in review. An engineer must explicitly approve it.'},
  {from: 61, to: 66, text: 'After review, the event can enter historical context. Its source remains attached.'},
  {from: 66, to: 71, text: 'The engineer records a decision for the active well, citing an offset-well event.'},
  {from: 71, to: 76, text: 'The handover note survives reload. Reviewer identity is self-entered, not authenticated.'},
  {from: 76, to: 105, text: 'The synthetic pack-off replay changes pressure, torque, and penetration rate. This is not live eRTMAC telemetry.'},
  {from: 105, to: 124, text: 'A labeled, uncalibrated heuristic surfaces an assessment. No incident countdown or field performance is claimed.'},
  {from: 124, to: 141, text: 'Every well leaves a lesson. The next well should not have to learn it again.'},
];

const Panel: React.FC<{children: React.ReactNode}> = ({children}) => <div style={{position: 'absolute', right: 104, top: 190, width: 770, height: 520, boxSizing: 'border-box', padding: 42, border: '1px solid rgba(197,211,210,.2)', background: 'linear-gradient(145deg,rgba(25,35,40,.9),rgba(12,18,22,.85))', boxShadow: '0 30px 100px rgba(0,0,0,.32)'}}>{children}</div>;
const Kicker: React.FC<{children: React.ReactNode}> = ({children}) => <div style={{color: amber, fontSize: 17, letterSpacing: 3, fontWeight: 600}}>{children}</div>;

const Geology: React.FC<{progress: number}> = ({progress}) => <svg viewBox="0 0 1920 1080" preserveAspectRatio="none" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}} aria-hidden="true">
  <defs><linearGradient id="earth" x1="0" y1="0" x2=".8" y2="1"><stop stopColor="#66716b" stopOpacity=".24"/><stop offset="1" stopColor="#171f21" stopOpacity=".04"/></linearGradient><radialGradient id="light"><stop stopColor="#e7b76c" stopOpacity=".19"/><stop offset="1" stopColor="#e7b76c" stopOpacity="0"/></radialGradient></defs>
  <ellipse cx="1410" cy="550" rx="650" ry="540" fill="url(#light)"/><path d="M0 380 Q280 300 600 392 T1200 374 T1920 408 L1920 1080 L0 1080Z" fill="url(#earth)"/>
  {[440, 525, 615, 710, 812, 920].map((y, i) => <path key={y} d={`M0 ${y} C300 ${y - 35 + i * 3} 510 ${y + 74} 850 ${y + 8} S1460 ${y - 40} 1920 ${y + 48}`} fill="none" stroke={i === 3 ? amber : '#93a39d'} strokeOpacity={i === 3 ? .4 : .14} strokeWidth={i === 3 ? 2 : 1}/>)}
  <path d={`M1080 0 C${1050 - 42 * progress} 250 ${1120 + 50 * progress} 420 1150 650`} fill="none" stroke={ivory} strokeOpacity=".68" strokeWidth="3"/><circle cx="1150" cy="650" r="7" fill={amber}/><circle cx="1150" cy="650" r="22" fill="none" stroke={amber} strokeOpacity=".4"/>
</svg>;

const Caption: React.FC<{localTime: number; bottom?: number}> = ({localTime, bottom = 108}) => {
  const item = captions.find((cue) => localTime >= cue.from && localTime < cue.to);
  if (!item) return null;
  return <div style={{position: 'absolute', left: 150, right: 150, bottom, minHeight: 74, display: 'grid', placeItems: 'center', padding: '16px 28px', background: 'rgba(5,10,13,.95)', borderLeft: `3px solid ${amber}`, color: ivory, fontSize: 29, lineHeight: 1.35, textAlign: 'center', textShadow: '0 2px 4px #000'}}>{item.text}</div>;
};

const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const second = frame / fps;
  const first = second < 8;
  const secondScene = second >= 8 && second < 16;
  const opacity = interpolate(frame % (8 * fps), [0, 20], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(.16, 1, .3, 1)});
  return <AbsoluteFill style={{background: '#080d11', color: ivory, fontFamily: 'Arial,sans-serif'}}>
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at 72% 48%,#1b282a 0%,#10191d 45%,#080d11 100%)'}}/>
    <div style={{position: 'absolute', inset: 0, overflow: 'hidden', opacity: .8}}><Geology progress={second / 24}/></div>
    <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(90deg,#080d11 0%,rgba(8,13,17,.94) 35%,rgba(8,13,17,.34) 77%,rgba(8,13,17,.18) 100%)'}}/>
    <div style={{position: 'absolute', left: 105, top: 65, color: muted, fontSize: 16, letterSpacing: 3}}>OIL INDIA LIMITED&nbsp;&nbsp; / &nbsp;&nbsp;HEALIX 1</div>
    <div style={{position: 'absolute', left: 105, top: 260, width: 700, opacity}}>
      <Kicker>{first ? 'THE KNOWLEDGE GAP' : secondScene ? 'STRATASENTRY NWIS' : 'READ-ONLY DECISION SUPPORT'}</Kicker>
      <div style={{fontSize: 68, lineHeight: 1.08, letterSpacing: -1.8, marginTop: 30}}>{first ? <>A lesson from<br/>the last well.</> : secondScene ? <>Evidence for<br/>the interval ahead.</> : <>Context beside<br/>what is happening now.</>}</div>
      <div style={{fontSize: 24, lineHeight: 1.65, color: muted, marginTop: 27}}>{first ? 'The next drilling risk may already be written down.' : secondScene ? 'Historical reports, formation context, source links.' : 'A local synthetic demonstration. Not connected to eRTMAC.'}</div>
      <div style={{marginTop: 46, color: '#8b9899', fontSize: 15, letterSpacing: 1.7}}>ILLUSTRATIVE OPENING · GEOLOGY IS NOT MEASURED DATA</div>
    </div>
    <Panel><Kicker>FROM REPORT TO FORMATION</Kicker><div style={{display: 'flex', alignItems: 'center', gap: 30, marginTop: 55}}><div style={{width: 260, height: 300, padding: 24, border: '1px solid #647071', background: 'rgba(255,255,255,.025)'}}><div style={{color: muted, fontSize: 14, letterSpacing: 2}}>HISTORICAL REPORT</div>{[0,1,2,3,4,5,6].map((n) => <div key={n} style={{height: n === 3 ? 8 : 2, width: `${90 - n * 5}%`, marginTop: 23, background: n === 3 ? amber : '#899493', opacity: n === 3 ? .9 : .4}}/>)}<div style={{marginTop: 30, color: muted, fontSize: 15}}>CONCEPTUAL TEXT HIGHLIGHT</div></div><div style={{color: amber, fontSize: 38}}>→</div><div style={{width: 255, height: 300, position: 'relative', borderLeft: '2px solid #93a39d'}}><div style={{position: 'absolute', top: 130, left: -2, width: 255, height: 3, background: amber}}/><div style={{position: 'absolute', top: 153, left: 16, color: ivory, fontSize: 18}}>FORMATION INTERVAL</div><div style={{position: 'absolute', bottom: 0, left: 12, color: muted, fontSize: 14}}>ILLUSTRATIVE ONLY</div></div></div><div style={{position: 'absolute', bottom: 30, right: 42, color: muted, fontSize: 14, letterSpacing: 1.5}}>EXPLANATORY GRAPHIC · NOT AN EXTRACTED EVENT</div></Panel>
    <Caption localTime={second}/><div style={{position: 'absolute', left: 105, right: 105, bottom: 60, height: 1, background: 'rgba(238,232,217,.24)'}}/><div style={{position: 'absolute', left: 105, bottom: 32, color: muted, fontSize: 14, letterSpacing: 2}}>BEFORE THE NEXT METRE · SIH 2026 · PS 26121</div>
  </AbsoluteFill>;
};

const ProductFootage: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const second = 24 + frame / fps;
  return <AbsoluteFill style={{background: '#090e12', fontFamily: 'Arial,sans-serif'}}>
     <Video src={staticFile('captures/workflow.webm')} muted playbackRate={1.3} objectFit="fill" style={{position: 'absolute', left: 110, top: 0, width: 1700, height: 956}}/>
    <div style={{position: 'absolute', top: 34, left: 46, padding: '10px 16px', color: ivory, background: 'rgba(5,10,13,.92)', border: '1px solid rgba(119,199,214,.45)', fontSize: 17, letterSpacing: 1.7}}>ACTUAL UI FOOTAGE · SYNTHETIC DEMO</div>
    <Caption localTime={second} bottom={24}/>
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 4, background: 'rgba(4,8,10,.8)'}}><div style={{height: '100%', width: `${(frame / (110 * fps)) * 100}%`, background: amber}}/></div>
  </AbsoluteFill>;
};

const Ending: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const progress = frame / (16 * fps);
  const opacity = interpolate(frame, [0, 24], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{background: '#080d11', color: ivory, fontFamily: 'Arial,sans-serif'}}>
    <div style={{position: 'absolute', inset: 0, opacity: .85}}><Geology progress={progress}/></div><div style={{position: 'absolute', inset: 0, background: 'linear-gradient(90deg,rgba(8,13,17,.98),rgba(8,13,17,.55))'}}/>
     <div style={{position: 'absolute', left: 150, top: 240, width: 1400, opacity}}><Kicker>HEALIX 1 · TEAM 172547 · SIH 2026 · PS 26121</Kicker><div style={{fontSize: 76, lineHeight: 1.08, marginTop: 30}}>Every well leaves<br/>a lesson.</div><div style={{fontSize: 34, lineHeight: 1.4, color: muted, marginTop: 26}}>The next well should not have to learn it again.</div><div style={{color: amber, fontSize: 22, letterSpacing: 2, marginTop: 44}}>STRATASENTRY NWIS · BEFORE THE NEXT METRE</div><div style={{color: ivory, fontSize: 20, marginTop: 34}}>github.com/Fadhil006/Oil_India</div></div>
     <Caption localTime={124 + progress * 17}/><div style={{position: 'absolute', left: 105, bottom: 32, color: muted, fontSize: 14, letterSpacing: 2}}>SYNTHETIC PROTOTYPE · PRODUCTION INTEGRATION PROPOSED</div>
  </AbsoluteFill>;
};

export const BeforeTheNextMetre: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return <AbsoluteFill>
    <Audio src={staticFile('ambient-original.wav')} volume={interpolate(frame, [0, 132.6 * fps, 136.6 * fps], [0.95, 0.95, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}/>
    <Sequence from={0} durationInFrames={24 * fps}><Intro/></Sequence>
    <Sequence from={24 * fps} durationInFrames={3027}><ProductFootage/></Sequence>
    <Sequence from={3027 + 24 * fps} durationInFrames={16 * fps}><Ending/></Sequence>
  </AbsoluteFill>;
};
