import React from 'react';
import {Audio, Video} from '@remotion/media';
import {AbsoluteFill, Easing, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';

// 60 s cut. Score is 96 BPM, one bar = 2.5 s = 75 frames; every cut lands on a bar line.
const BAR = 75;
const ivory = '#f1eee6';
const muted = '#9aa6a8';
const amber = '#e7b76c';
const cyan = '#77c7d6';
const sans = 'Helvetica Neue, Arial, sans-serif';
const mono = 'JetBrainsMono NF, monospace';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const ease = Easing.bezier(0.16, 1, 0.3, 1);

const fadeIn = (frame: number, start: number, len = 18) => interpolate(frame, [start, start + len], [0, 1], {...clamp, easing: ease});
const rise = (frame: number, start: number, len = 24) => interpolate(frame, [start, start + len], [28, 0], {...clamp, easing: ease});

// Deterministic starfield.
const STARS = (() => {
  let s = 26121;
  const r = () => ((s = (s * 1664525 + 1013904223) % 4294967296) / 4294967296);
  return Array.from({length: 380}, () => ({x: r() * 2 - 1, y: r() * 2 - 1, z: r(), tint: r()}));
})();

const Starfield: React.FC<{distance: number}> = ({distance}) => <svg viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0}}>
  {STARS.map((star, i) => {
    const z = (((star.z - distance) % 1) + 1) % 1 + 0.02;
    const x = 960 + (star.x / z) * 520;
    const y = 540 + (star.y / z) * 520;
    if (x < -20 || x > 1940 || y < -20 || y > 1100) return null;
    const near = 1 - z;
    return <circle key={i} cx={x} cy={y} r={0.4 + near * 2.4} fill={star.tint > 0.85 ? amber : '#dfe8ec'} opacity={Math.min(1, near * 1.4)}/>;
  })}
</svg>;

const Horizon: React.FC<{lift: number}> = ({lift}) => <svg viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0}}>
  <defs>
    <radialGradient id="planet" cx="50%" cy="0%" r="70%"><stop stopColor="#24363b"/><stop offset="1" stopColor="#05090b"/></radialGradient>
    <radialGradient id="rim" cx="50%" cy="100%" r="60%"><stop stopColor={amber} stopOpacity=".55"/><stop offset="1" stopColor={amber} stopOpacity="0"/></radialGradient>
  </defs>
  <ellipse cx="960" cy={1080 + 2200 - lift} rx="2600" ry="2300" fill="url(#rim)" opacity=".7"/>
  <ellipse cx="960" cy={1080 + 2280 - lift} rx="2500" ry="2300" fill="url(#planet)" stroke={amber} strokeOpacity=".75" strokeWidth="2"/>
</svg>;

const Strata: React.FC<{depth: number}> = ({depth}) => <svg viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0}}>
  {Array.from({length: 14}, (_, i) => {
    const y = ((i * 120 - depth) % 1680 + 1680) % 1680 - 300;
    const hot = i % 5 === 3;
    return <path key={i} d={`M0 ${y} C420 ${y - 60} 760 ${y + 70} 1100 ${y + 10} S1600 ${y - 50} 1920 ${y + 40} L1920 ${y + 118} C1600 ${y + 70} 1400 ${y + 150} 1100 ${y + 128} S420 ${y + 60} 0 ${y + 118}Z`}
      fill={hot ? 'rgba(231,183,108,.10)' : i % 2 ? 'rgba(120,140,135,.07)' : 'rgba(60,78,80,.10)'} stroke={hot ? amber : '#8fa19c'} strokeOpacity={hot ? 0.5 : 0.16}/>;
  })}
  <line x1="1290" y1="0" x2="1290" y2="1080" stroke={ivory} strokeOpacity=".7" strokeWidth="3"/>
</svg>;

const Headline: React.FC<{children: React.ReactNode; frame: number; start: number; size?: number; color?: string}> = ({children, frame, start, size = 84, color = ivory}) =>
  <div style={{fontSize: size, lineHeight: 1.08, letterSpacing: -2, color, opacity: fadeIn(frame, start), transform: `translateY(${rise(frame, start)}px)`, filter: `blur(${interpolate(frame, [start, start + 16], [10, 0], clamp)}px)`}}>{children}</div>;

const ColdOpen: React.FC = () => {
  const frame = useCurrentFrame();
  const distance = frame * 0.0022 + Math.pow(Math.max(0, frame - 230) / 70, 3) * 0.6;
  const out = interpolate(frame, [270, 300], [1, 0], clamp);
  return <AbsoluteFill style={{background: '#020406', fontFamily: sans, opacity: out}}>
    <Starfield distance={distance}/>
    <Horizon lift={interpolate(frame, [0, 300], [0, 380], {...clamp, easing: Easing.inOut(Easing.quad)})}/>
    <div style={{position: 'absolute', left: 0, right: 0, top: 380, textAlign: 'center'}}>
      {frame < 140 ? <Headline frame={frame} start={20} size={64} color={muted}>Somewhere beneath the next rig,</Headline>
        : <Headline frame={frame} start={150} size={92}>a lesson is already written.</Headline>}
    </div>
    <div style={{position: 'absolute', left: 80, top: 64, color: muted, fontSize: 16, letterSpacing: 4, opacity: fadeIn(frame, 10, 30)}}>HEALIX 1 · SIH 2026 · PS 26121</div>
  </AbsoluteFill>;
};

const Problem: React.FC = () => {
  const frame = useCurrentFrame();
  const second = frame >= BAR;
  return <AbsoluteFill style={{background: '#070b0e', fontFamily: sans}}>
    <div style={{position: 'absolute', inset: 0, opacity: 0.9}}><Strata depth={frame * 6}/></div>
    <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(90deg,#070b0e 25%,rgba(7,11,14,.2) 80%)'}}/>
    <div style={{position: 'absolute', left: 140, top: 360, width: 1000}}>
      <div style={{color: amber, fontFamily: mono, fontSize: 20, letterSpacing: 4, opacity: fadeIn(frame, 0)}}>THE KNOWLEDGE GAP</div>
      <div style={{marginTop: 30}}>{second
        ? <Headline frame={frame} start={BAR}>Its lessons stay<br/>buried in the archive.</Headline>
        : <Headline frame={frame} start={4}>Every well drilled<br/>leaves a report.</Headline>}</div>
    </div>
  </AbsoluteFill>;
};

const Title: React.FC = () => {
  const frame = useCurrentFrame();
  const spacing = interpolate(frame, [0, BAR], [60, 14], {...clamp, easing: ease});
  return <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 55%,#13222a 0%,#030507 70%)', fontFamily: sans, display: 'grid', placeItems: 'center'}}>
    <Starfield distance={frame * 0.001}/>
    <div style={{textAlign: 'center', opacity: fadeIn(frame, 0, 14)}}>
      <div style={{fontSize: 118, fontWeight: 700, letterSpacing: spacing, color: ivory, textShadow: `0 0 60px rgba(231,183,108,${0.25 + 0.25 * Math.sin(frame / 8)})`}}>STRATASENTRY<span style={{color: amber}}> NWIS</span></div>
      <div style={{marginTop: 26, color: cyan, fontFamily: mono, fontSize: 24, letterSpacing: 8, opacity: fadeIn(frame, 18)}}>NEARBY WELLS INTELLIGENCE SYSTEM</div>
    </div>
  </AbsoluteFill>;
};

type Focus = {x: number; y: number; w: number; h: number; max?: number; free?: boolean};
type Chapter = {verb: string; line: string; from: number; rate: number; bars: number; focus: Focus; label?: 'left' | 'right' | 'top'};

// `from` is seconds into the 1600×900 workflow recording; focus is in recording pixels.
const CHAPTERS: Chapter[] = [
  {verb: 'FIND', line: 'Offset wells within any search radius', from: 1.5, rate: 2, bars: 2, focus: {x: 30, y: 330, w: 520, h: 460, max: 2}, label: 'right'},
  {verb: 'CONNECT', line: 'Past incidents mapped to the interval ahead', from: 14, rate: 1.6, bars: 2, focus: {x: 1050, y: 340, w: 530, h: 440, max: 2}},
  {verb: 'TRACE', line: 'Every warning cites its source report', from: 23.5, rate: 1.4, bars: 2, focus: {x: 230, y: 60, w: 980, h: 820}},
  {verb: 'REVIEW', line: 'Engineers approve what gets extracted', from: 32, rate: 2.4, bars: 2, focus: {x: 790, y: 20, w: 780, h: 640, max: 1.7}},
  {verb: 'HAND OVER', line: 'Decisions carry to the next shift', from: 52, rate: 2.4, bars: 2, focus: {x: 70, y: 100, w: 1460, h: 700}},
  {verb: 'WATCH', line: 'Replayed signals beside historical context', from: 70, rate: 9.6, bars: 2, focus: {x: 60, y: 290, w: 1480, h: 610}},
  {verb: 'ALERT', line: 'A heuristic flag, with the evidence attached', from: 120, rate: 2.4, bars: 1, focus: {x: 60, y: 610, w: 1000, h: 240, max: 1.9, free: true}, label: 'top'},
];

const Footage: React.FC<{chapter: Chapter; index: number}> = ({chapter, index}) => {
  const frame = useCurrentFrame();
  const total = chapter.bars * BAR;
  const p = interpolate(frame, [0, total], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const {x, y, w, h, max = 2.2, free = false} = chapter.focus;
  const base = 1920 / 1600;
  const k = base + (Math.min(max, 1920 / w, 1080 / h) - base) * p;
  const half = (size: number) => size / 2 / k;
  const cx = Math.min(1600 - half(1920), Math.max(half(1920), 800 + (x + w / 2 - 800) * p));
  const ty = 450 + (y + h / 2 - 450) * p;
  // free: pan past the recording edge (page background matches) to centre content stuck at the bottom.
  const cy = free ? ty : Math.min(900 - half(1080), Math.max(half(1080), ty));
  const flash = interpolate(frame, [0, 8], [1, 0], clamp);
  const side = chapter.label ?? 'left';
  const place: React.CSSProperties = side === 'top' ? {left: 96, top: 120} : side === 'right' ? {right: 96, bottom: 92, textAlign: 'right'} : {left: 96, bottom: 92};
  return <AbsoluteFill style={{background: '#05080a', fontFamily: sans, overflow: 'hidden'}}>
    <div style={{position: 'absolute', width: 1600, height: 900, transformOrigin: '0 0', transform: `translate(${960 - cx * k}px,${540 - cy * k}px) scale(${k})`}}>
      <Video src={staticFile('captures/workflow.webm')} muted trimBefore={Math.round(chapter.from * 30)} playbackRate={chapter.rate} style={{width: 1600, height: 900}}/>
      <div style={{position: 'absolute', left: 0, right: 0, top: 850, height: 52, background: 'linear-gradient(180deg,rgba(5,8,10,0),#05080a)'}}/>
    </div>
    <div style={{position: 'absolute', inset: 0, background: `linear-gradient(${side === 'top' ? '180deg' : '0deg'},rgba(3,6,8,.95) 0%,rgba(3,6,8,.55) 24%,rgba(3,6,8,0) 45%)`}}/>
    <div style={{position: 'absolute', ...place, opacity: fadeIn(frame, 4, 14), transform: `translateX(${interpolate(frame, [4, 22], [side === 'right' ? 40 : -40, 0], {...clamp, easing: ease})}px)`}}>
      <div style={{color: amber, fontFamily: mono, fontSize: 22, letterSpacing: 4}}>{String(index + 1).padStart(2, '0')} / {String(CHAPTERS.length).padStart(2, '0')}</div>
      <div style={{color: ivory, fontSize: 92, fontWeight: 700, letterSpacing: 6, marginTop: 6, textShadow: '0 4px 30px #000'}}>{chapter.verb}</div>
      <div style={{color: '#d6dcdc', fontSize: 34, marginTop: 4, textShadow: '0 2px 12px #000'}}>{chapter.line}</div>
    </div>
    <div style={{position: 'absolute', top: 36, right: 48, padding: '9px 16px', color: ivory, background: 'rgba(3,6,8,.85)', border: `1px solid ${cyan}66`, fontFamily: mono, fontSize: 15, letterSpacing: 2}}>ACTUAL PROTOTYPE · SYNTHETIC DATA · NOT LIVE eRTMAC</div>
    <div style={{position: 'absolute', left: 96, right: 96, bottom: 44, display: 'flex', gap: 10}}>
      {CHAPTERS.map((_, i) => <div key={i} style={{flex: 1, height: 4, background: 'rgba(241,238,230,.18)'}}><div style={{height: '100%', width: i < index ? '100%' : i > index ? 0 : `${(frame / total) * 100}%`, background: amber}}/></div>)}
    </div>
    <AbsoluteFill style={{background: '#f6efe0', opacity: flash * 0.35}}/>
  </AbsoluteFill>;
};

const Silence: React.FC = () => {
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{background: '#000', fontFamily: sans, display: 'grid', placeItems: 'center'}}>
    <div style={{color: ivory, fontSize: 56, letterSpacing: 2, opacity: fadeIn(frame, 37, 20)}}>Before the next metre.</div>
  </AbsoluteFill>;
};

const Ending: React.FC = () => {
  const frame = useCurrentFrame();
  const lockup = frame >= 105;
  const out = interpolate(frame, [200, 225], [1, 0], clamp);
  return <AbsoluteFill style={{background: '#020406', fontFamily: sans, opacity: out}}>
    <Starfield distance={frame * 0.0008}/>
    <Horizon lift={interpolate(frame, [0, 225], [120, 300], clamp)}/>
    <div style={{position: 'absolute', left: 0, right: 0, top: lockup ? 300 : 400, textAlign: 'center'}}>
      {!lockup ? <><Headline frame={frame} start={6} size={96}>Every well leaves a lesson.</Headline>
        <div style={{marginTop: 26, fontSize: 38, color: muted, opacity: fadeIn(frame, 40)}}>The next one should not have to learn it again.</div></>
        : <div style={{opacity: fadeIn(frame, 105, 20)}}>
          <div style={{fontSize: 96, fontWeight: 700, letterSpacing: 14, color: ivory}}>STRATASENTRY<span style={{color: amber}}> NWIS</span></div>
          <div style={{marginTop: 30, color: amber, fontFamily: mono, fontSize: 24, letterSpacing: 5}}>HEALIX 1 · TEAM 172547 · SIH 2026 · PS 26121</div>
          <div style={{marginTop: 18, color: muted, fontSize: 24, letterSpacing: 2}}>Oil India Limited · read-only decision support · synthetic prototype</div>
          <div style={{marginTop: 30, color: cyan, fontFamily: mono, fontSize: 26}}>github.com/Fadhil006/Oil_India</div>
        </div>}
    </div>
  </AbsoluteFill>;
};

export const SHORT_FRAMES = 1800;

export const NwisShort: React.FC = () => {
  let at = 7 * BAR;
  const clips = CHAPTERS.map((chapter, i) => {
    const el = <Sequence key={chapter.verb} from={at} durationInFrames={chapter.bars * BAR}><Footage chapter={chapter} index={i}/></Sequence>;
    at += chapter.bars * BAR;
    return el;
  });
  return <AbsoluteFill style={{background: '#000'}}>
    <Audio src={staticFile('score-original.wav')}/>
    <Sequence durationInFrames={4 * BAR}><ColdOpen/></Sequence>
    <Sequence from={4 * BAR} durationInFrames={2 * BAR}><Problem/></Sequence>
    <Sequence from={6 * BAR} durationInFrames={BAR}><Title/></Sequence>
    {clips}
    <Sequence from={20 * BAR} durationInFrames={BAR}><Silence/></Sequence>
    <Sequence from={21 * BAR} durationInFrames={3 * BAR}><Ending/></Sequence>
  </AbsoluteFill>;
};
