import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, Sequence, continueRender, delayRender, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig, Easing, OffthreadVideo, Loop, random,
} from 'remotion';

const GOLD = '#D4AF37';
const INK = '#0C0C0C';
const W = 1080;
const H = 1920;
const CENTER_Y = 0.42 * H;   // Reels safe band: UI covers top ~12% and bottom ~25%

export type Beat = {
  type: 'hook' | 'text' | 'list' | 'number' | 'compare' | 'steps';
  from: number; dur: number;
  text?: string; highlight?: string;
  title?: string; items?: string[]; item_times?: number[];
  value?: number; from_value?: number; prefix?: string; suffix?: string; label?: string; decimals?: number;
  left?: {label: string; items: string[]}; right?: {label: string; items: string[]};
  bg?: string; bg_frames?: number;   // background footage (public/ path) and its length in frames
};
export type ExplainerProps = {durationInFrames: number; handle: string; beats: Beat[]};

// ---------- fonts ----------
const FONTS: [string, string, string][] = [
  ['SukInter', 'fonts/i400.ttf', '400'], ['SukInter', 'fonts/i700.ttf', '700'], ['SukInter', 'fonts/i800.ttf', '800'],
  ['SukSerif', 'fonts/s700.ttf', '700'],
];
const useFonts = () => {
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([fam, src, weight]) => {
      const f = new FontFace(fam, `url(${staticFile(src)})`, {weight});
      return f.load().then((l) => document.fonts.add(l));
    })).then(() => continueRender(handle)).catch(() => continueRender(handle));
  }, [handle]);
};

// ---------- helpers ----------
const useEnter = (delay = 0, damping = 14) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: frame - delay, fps, config: {damping, mass: 0.6}});
};

const Exit: React.FC<{dur: number; children: React.ReactNode}> = ({dur, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [dur - 6, dur], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const s = interpolate(frame, [dur - 6, dur], [1, 0.96], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o, transform: `scale(${s})`}}>{children}</AbsoluteFill>;
};

const Band: React.FC<{children: React.ReactNode}> = ({children}) => (
  <div style={{position: 'absolute', left: 90, right: 90, top: CENTER_Y, transform: 'translateY(-50%)',
    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 36}}>{children}</div>
);

const Highlight: React.FC<{text: string; delay: number}> = ({text, delay}) => {
  const p = useEnter(delay, 10);
  return (
    <div style={{background: GOLD, color: INK, fontFamily: 'SukInter', fontWeight: 800, fontSize: 66,
      padding: '12px 28px', lineHeight: 1.2, textAlign: 'center', borderRadius: 6,
      transform: `scale(${interpolate(p, [0, 1], [0.6, 1])})`, opacity: p}}>{text}</div>
  );
};

// ---------- beats ----------
const Hook: React.FC<{b: Beat}> = ({b}) => {
  const frame = useCurrentFrame();
  const words = (b.text || '').split(' ');
  return (
    <Band>
      <div style={{fontFamily: 'SukSerif', fontWeight: 700, fontSize: 112, lineHeight: 1.15, color: 'white',
        textAlign: 'center', textShadow: '0 4px 24px rgba(0,0,0,.5)'}}>
        {words.map((w, i) => {
          // visible from frame 0 (muted viewers), each word settles in quickly
          const p = interpolate(frame, [i * 1.5, i * 1.5 + 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
          return <span key={i} style={{display: 'inline-block', marginRight: 26, opacity: 0.7 + 0.3 * p,
            transform: `translateY(${(1 - p) * 18}px)`}}>{w}</span>;
        })}
      </div>
      {b.highlight ? <Highlight text={b.highlight} delay={14} /> : null}
    </Band>
  );
};

const Text: React.FC<{b: Beat}> = ({b}) => {
  const p = useEnter(0);
  return (
    <Band>
      <div style={{fontFamily: 'SukInter', fontWeight: 800, fontSize: 92, lineHeight: 1.2, color: 'white',
        textAlign: 'center', opacity: p, transform: `translateY(${(1 - p) * 70}px)`}}>{b.text}</div>
      {b.highlight ? <Highlight text={b.highlight} delay={Math.round(b.dur * 0.45)} /> : null}
    </Band>
  );
};

const itemDelay = (b: Beat, i: number, n: number) =>
  b.item_times?.[i] ?? Math.round(8 + (i * (b.dur * 0.7 - 8)) / Math.max(1, n));

const List: React.FC<{b: Beat}> = ({b}) => {
  const t = useEnter(0);
  const items = b.items || [];
  return (
    <Band>
      {b.title ? <div style={{fontFamily: 'SukInter', fontWeight: 700, fontSize: 64, color: GOLD, opacity: t,
        transform: `translateY(${(1 - t) * 40}px)`, textAlign: 'center'}}>{b.title}</div> : null}
      <div style={{display: 'flex', flexDirection: 'column', gap: 26, width: '100%'}}>
        {items.map((it, i) => <ListItem key={i} n={i + 1} text={it} delay={itemDelay(b, i, items.length)} />)}
      </div>
    </Band>
  );
};
const ListItem: React.FC<{n: number; text: string; delay: number}> = ({n, text, delay}) => {
  const p = useEnter(delay, 12);
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 30, opacity: p,
      transform: `translateX(${(1 - p) * -120}px)`, background: 'rgba(12,12,14,0.62)', backdropFilter: 'blur(6px)',
      border: '2px solid rgba(212,175,55,0.35)', borderRadius: 22, padding: '22px 30px'}}>
      <div style={{width: 76, height: 76, borderRadius: 38, background: GOLD, color: INK, flexShrink: 0,
        fontFamily: 'SukInter', fontWeight: 800, fontSize: 44, display: 'flex', alignItems: 'center',
        justifyContent: 'center', transform: `scale(${p})`}}>{n}</div>
      <div style={{fontFamily: 'SukInter', fontWeight: 800, fontSize: 68, color: 'white', lineHeight: 1.15}}>{text}</div>
    </div>
  );
};

const Steps: React.FC<{b: Beat}> = ({b}) => {
  const items = b.items || [];
  const t = useEnter(0);
  return (
    <Band>
      {b.title ? <div style={{fontFamily: 'SukInter', fontWeight: 700, fontSize: 64, color: GOLD, opacity: t,
        textAlign: 'center'}}>{b.title}</div> : null}
      {items.map((it, i) => <Step key={i} text={it} last={i === items.length - 1}
        delay={itemDelay(b, i, items.length)} />)}
    </Band>
  );
};
const Step: React.FC<{text: string; last: boolean; delay: number}> = ({text, last, delay}) => {
  const p = useEnter(delay, 12);
  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18, opacity: p,
      transform: `scale(${interpolate(p, [0, 1], [0.8, 1])})`}}>
      <div style={{fontFamily: 'SukInter', fontWeight: 800, fontSize: 64, color: 'white', textAlign: 'center',
        background: 'rgba(12,12,14,0.62)', border: `3px solid ${GOLD}`, borderRadius: 24,
        padding: '18px 40px'}}>{text}</div>
      {!last ? <div style={{color: GOLD, fontSize: 84, lineHeight: 0.8}}>↓</div> : null}
    </div>
  );
};

const NumberBeat: React.FC<{b: Beat}> = ({b}) => {
  const frame = useCurrentFrame();
  const p = useEnter(0, 16);
  const runFrames = Math.min(36, Math.round(b.dur * 0.6));
  const v = interpolate(frame, [4, 4 + runFrames], [b.from_value ?? 0, b.value ?? 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const d = b.decimals ?? 0;
  const shown = v.toLocaleString('de-DE', {minimumFractionDigits: d, maximumFractionDigits: d});
  const done = frame >= 4 + runFrames;
  const pulse = done ? 1 + 0.06 * Math.max(0, 1 - (frame - 4 - runFrames) / 8) : 1;
  return (
    <Band>
      <div style={{fontFamily: 'SukInter', fontWeight: 800, fontSize: 230, color: GOLD, lineHeight: 1,
        transform: `scale(${interpolate(p, [0, 1], [0.7, 1]) * pulse})`, opacity: p,
        textShadow: '0 8px 40px rgba(212,175,55,0.35)', fontVariantNumeric: 'tabular-nums'}}>
        {b.prefix}{shown}{b.suffix}
      </div>
      {b.label ? <div style={{fontFamily: 'SukInter', fontWeight: 700, fontSize: 64, color: 'white',
        textAlign: 'center', opacity: interpolate(frame, [10, 20], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>{b.label}</div> : null}
    </Band>
  );
};

const Compare: React.FC<{b: Beat}> = ({b}) => {
  const cols = [b.left, b.right];
  return (
    <Band>
      <div style={{display: 'flex', gap: 28, width: '100%'}}>
        {cols.map((c, ci) => c ? <CompareCol key={ci} c={c} gold={ci === 1}
          delay={ci === 0 ? 0 : Math.round(b.dur * 0.35)} /> : null)}
      </div>
    </Band>
  );
};
const CompareCol: React.FC<{c: {label: string; items: string[]}; gold: boolean; delay: number}> = ({c, gold, delay}) => {
  const p = useEnter(delay, 13);
  return (
    <div style={{flex: 1, borderRadius: 26, padding: '30px 26px', opacity: p,
      transform: `translateY(${(1 - p) * 80}px)`,
      background: gold ? 'rgba(40,32,10,0.72)' : 'rgba(12,12,14,0.62)',
      border: `3px solid ${gold ? GOLD : 'rgba(255,255,255,0.25)'}`}}>
      <div style={{fontFamily: 'SukInter', fontWeight: 800, fontSize: 60, color: gold ? GOLD : '#BBBBBB',
        marginBottom: 22, textAlign: 'center'}}>{c.label}</div>
      {c.items.map((it, i) => <div key={i} style={{fontFamily: 'SukInter', fontWeight: 700, fontSize: 52,
        color: 'white', lineHeight: 1.25, marginBottom: 14, textAlign: 'center'}}>{it}</div>)}
    </div>
  );
};

// ---------- background ----------
const Particles: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      {new Array(34).fill(0).map((_, i) => {
        const x = random(`x${i}`) * W;
        const speed = 0.6 + random(`s${i}`) * 1.6;
        const y = (H + 40) - ((random(`y${i}`) * H + frame * speed) % (H + 80));
        const r = 3 + random(`r${i}`) * 7;
        const o = 0.15 + random(`o${i}`) * 0.45;
        return <div key={i} style={{position: 'absolute', left: x + Math.sin(frame / 40 + i) * 20, top: y,
          width: r, height: r, borderRadius: r, background: GOLD, opacity: o, filter: 'blur(1px)',
          boxShadow: `0 0 ${r * 3}px ${GOLD}`}} />;
      })}
    </AbsoluteFill>
  );
};

const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const a = frame / 90;
  const blob = (x: number, y: number, r: number, c: string, ph: number) => (
    <div style={{position: 'absolute', left: x + Math.sin(a + ph) * 120, top: y + Math.cos(a * 0.8 + ph) * 160,
      width: r, height: r, borderRadius: r, background: c, filter: 'blur(110px)'}} />
  );
  const sweep = ((frame % 150) / 150) * (W + 1400) - 900;
  return (
    <AbsoluteFill style={{background: 'linear-gradient(170deg, #0b0b10 0%, #17130a 55%, #0b0b10 100%)', overflow: 'hidden'}}>
      {blob(-200, 200, 760, 'rgba(212,175,55,0.30)', 0)}
      {blob(560, 1050, 700, 'rgba(120,90,30,0.40)', 2)}
      {blob(250, 1450, 560, 'rgba(212,175,55,0.16)', 4)}
      <div style={{position: 'absolute', top: -400, left: sweep, width: 260, height: H + 800,
        background: 'linear-gradient(90deg, transparent, rgba(255,230,160,0.10), transparent)',
        transform: 'rotate(18deg)'}} />
      <Particles />
    </AbsoluteFill>
  );
};

const FootageBg: React.FC<{src: string; frames: number; dur: number}> = ({src, frames, dur}) => {
  const frame = useCurrentFrame();
  const z = 1.12 + 0.08 * (frame / Math.max(1, dur));
  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <Loop durationInFrames={Math.max(30, frames - 35)}>
        <AbsoluteFill style={{transform: `scale(${z})`}}>
          <OffthreadVideo src={staticFile(src)} muted startFrom={30}
            style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'blur(10px) brightness(0.42) saturate(0.85)'}} />
        </AbsoluteFill>
      </Loop>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 42%, rgba(0,0,0,0.15) 0%, rgba(0,0,0,0.55) 70%, rgba(0,0,0,0.75) 100%)'}} />
      <Particles />
    </AbsoluteFill>
  );
};

const Progress: React.FC<{total: number}> = ({total}) => {
  const frame = useCurrentFrame();
  return <div style={{position: 'absolute', left: 90, right: 90, top: 0.705 * H, height: 6,
    background: 'rgba(255,255,255,0.12)', borderRadius: 3}}>
    <div style={{width: `${(100 * frame) / total}%`, height: '100%', background: GOLD, borderRadius: 3}} />
  </div>;
};

const COMPONENTS: Record<Beat['type'], React.FC<{b: Beat}>> = {
  hook: Hook, text: Text, list: List, number: NumberBeat, compare: Compare, steps: Steps,
};

export const Explainer: React.FC<ExplainerProps> = ({beats, handle, durationInFrames}) => {
  useFonts();
  return (
    <AbsoluteFill style={{backgroundColor: '#0b0b10'}}>
      <Background />
      {beats.map((b, i) => b.bg ? (
        <Sequence key={'bg' + i} from={b.from} durationInFrames={b.dur}>
          <FootageBg src={b.bg} frames={b.bg_frames || 150} dur={b.dur} />
        </Sequence>) : null)}
      {beats.map((b, i) => {
        const C = COMPONENTS[b.type] || Text;
        return (
          <Sequence key={i} from={b.from} durationInFrames={b.dur}>
            {i === beats.length - 1 ? <C b={b} /> : <Exit dur={b.dur}><C b={b} /></Exit>}
          </Sequence>
        );
      })}
      <div style={{position: 'absolute', top: 0.68 * H, width: '100%', textAlign: 'center',
        fontFamily: 'SukInter', fontWeight: 700, fontSize: 34, color: GOLD}}>{handle}</div>
      <Progress total={durationInFrames} />
    </AbsoluteFill>
  );
};
