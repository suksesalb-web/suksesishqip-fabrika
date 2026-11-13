import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Sequence, continueRender, delayRender, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig, Easing, random} from 'remotion';

// "Histori me numra" look: black, gold and cream, film motifs, serif headlines, red only for the stamp.
const BG = '#0B0A08';
const GOLD = '#D4AF37';
const CREAM = '#F3EBDD';
const RED = '#D7263D';
const GREY = '#7D766A';
const W = 1080;
const FPS = 30;
const sec = (s: number) => Math.round(s * FPS);

const FONTS: [string, string, string][] = [
  ['SukInter', 'fonts/i700.ttf', '700'], ['SukInter', 'fonts/i800.ttf', '800'],
  ['SukSerif', 'fonts/s700.ttf', '700'], ['SukMono', 'fonts/mono700.ttf', '700'],
];
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([fam, src, weight]) => new FontFace(fam, `url(${staticFile(src)})`, {weight})
      .load().then((l) => document.fonts.add(l)))).then(() => continueRender(h)).catch(() => continueRender(h));
  }, [h]);
};
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const useIn = (delay = 0, damping = 13) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: f - delay, fps, config: {damping, mass: 0.6}});
};
const goldGlow = `0 0 30px ${GOLD}55`;

// ---------- shared pieces ----------
const Sprockets: React.FC = () => {   // film edges, slowly running
  const f = useCurrentFrame();
  const off = (f * 2) % 90;
  const col = (x: number) => (
    <div style={{position: 'absolute', left: x, top: -90 + off, width: 46, height: 2100}}>
      {Array.from({length: 24}).map((_, i) => <div key={i} style={{width: 46, height: 52, marginBottom: 38, borderRadius: 8,
        border: `3px solid ${GOLD}33`}} />)}
    </div>);
  return <AbsoluteFill>{col(22)}{col(W - 68)}</AbsoluteFill>;
};

const Caption: React.FC<{text: string; gold?: string[]; from: number; to: number}> = ({text, gold = [], from, to}) => {
  const f = useCurrentFrame();
  const words = text.split(' ');
  const shown = Math.ceil(interpolate(f, [from, to], [0, words.length], clamp));
  return <div style={{position: 'absolute', top: 1270, left: 110, right: 110, textAlign: 'center', fontFamily: 'SukInter',
    fontWeight: 800, fontSize: 52, lineHeight: 1.3, color: CREAM}}>
    {words.map((w, i) => {
      const on = i < shown;
      const g = gold.some((x) => w.toLowerCase().includes(x.toLowerCase()));
      return <span key={i} style={{opacity: on ? 1 : 0.12, color: g ? GOLD : CREAM, transition: 'none'}}>{w} </span>;
    })}
  </div>;
};

const Kicker: React.FC<{text: string; top?: number; delay?: number; color?: string}> = ({text, top = 250, delay = 0, color = GOLD}) => {
  const p = useIn(delay);
  return <div style={{position: 'absolute', top, left: 0, right: 0, textAlign: 'center', opacity: p}}>
    <span style={{fontFamily: 'SukInter', fontWeight: 800, fontSize: 36, letterSpacing: 10, color}}>{text}</span>
    <div style={{width: 80 * p, height: 4, background: color, margin: '16px auto 0'}} />
  </div>;
};

// Flip-clock year: digits roll from `from` to `to`.
const Year: React.FC<{from: number; to: number; start: number; dur: number; top: number; size?: number}> = ({from, to, start, dur, top, size = 210}) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [start, start + dur], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const v = Math.round(from + (to - from) * t);
  const p = useIn(start - 6);
  return <div style={{position: 'absolute', top, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 16,
    transform: `scale(${0.8 + 0.2 * p})`, opacity: p}}>
    {String(v).split('').map((d, i) => (
      <div key={i} style={{width: size * 0.7, height: size * 1.05, borderRadius: 18, background: 'linear-gradient(#1C1914 50%, #15120E 50%)',
        border: `3px solid ${GOLD}66`, display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative'}}>
        <span style={{fontFamily: 'SukSerif', fontWeight: 700, fontSize: size * 0.82, color: GOLD, textShadow: goldGlow}}>{d}</span>
        <div style={{position: 'absolute', left: 0, right: 0, top: '50%', height: 3, background: BG}} />
      </div>))}
  </div>;
};

const draw = (f: number, start: number, len = 24) => interpolate(f, [start, start + len], [1, 0], clamp);

const Camera: React.FC<{top: number; start: number; scale?: number}> = ({top, start, scale = 1}) => {
  const f = useCurrentFrame();
  const d = draw(f, start);
  const st = {fill: 'none', stroke: GOLD, strokeWidth: 7, pathLength: 1, strokeDasharray: 1, strokeDashoffset: d, strokeLinejoin: 'round' as const};
  return <svg style={{position: 'absolute', top, left: W / 2 - 170 * scale}} width={340 * scale} height={240 * scale} viewBox="0 0 340 240">
    <rect x={20} y={60} width={300} height={160} rx={18} {...st} />
    <path d="M110 60 L130 25 L210 25 L230 60" {...st} />
    <circle cx={170} cy={140} r={50} {...st} />
    <circle cx={170} cy={140} r={24} {...st} />
    <rect x={260} y={80} width={36} height={20} rx={4} {...st} />
  </svg>;
};

// ---------- scenes (times in seconds, measured on Riko's voice) ----------
const S1: React.FC = () => {   // 0.00 - 5.99
  const f = useCurrentFrame();
  const drawer = interpolate(f, [sec(3.7), sec(4.1)], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const drop = interpolate(f, [sec(4.0), sec(4.5)], [0, 1], {...clamp, easing: Easing.in(Easing.quad)});
  const close = interpolate(f, [sec(4.6), sec(5.0)], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const dx = (1 - close) * drawer * 260;
  return <AbsoluteFill>
    <Kicker text="KODAK · 1975" delay={0} />
    <Year from={1975} to={1975} start={2} dur={1} top={360} size={170} />
    <div style={{position: 'absolute', left: 0, right: 0, top: 0, transform: `translateY(${drop * 330}px) scale(${1 - drop * 0.35})`,
      opacity: 1 - close}}><Camera top={600} start={sec(1.5)} /></div>
    {/* the drawer */}
    <div style={{position: 'absolute', top: 980, left: 230 + dx, width: 620, height: 170, opacity: drawer,
      border: `6px solid ${GOLD}`, borderRadius: 10, background: '#16130E', boxShadow: '0 20px 40px #000'}}>
      <div style={{width: 120, height: 16, borderRadius: 8, background: GOLD, margin: '76px auto 0'}} />
    </div>
    <Caption text="Në 1975, Kodak shpiku kamerën dixhitale dhe e fshehu në sirtar." gold={['1975', 'kamerën', 'dixhitale', 'sirtar']} from={0} to={sec(4.9)} />
  </AbsoluteFill>;
};

const S2: React.FC = () => {   // 5.99 - 10.05 (local frames)
  const f = useCurrentFrame();
  const run = f * 6;
  const lock = useIn(sec(2.7), 9);
  return <AbsoluteFill>
    <Kicker text="BIZNESI I VËRTETË" />
    <div style={{position: 'absolute', top: 470, left: -200 - (run % 260), display: 'flex', gap: 20, height: 330,
      padding: '30px 0', background: '#17140F', borderTop: `4px solid ${GOLD}`, borderBottom: `4px solid ${GOLD}`}}>
      {Array.from({length: 9}).map((_, i) => <div key={i} style={{width: 240, height: 270, borderRadius: 8, border: `3px solid ${GOLD}88`,
        display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'SukSerif', fontWeight: 700, fontSize: 130, color: GOLD,
        background: 'radial-gradient(#2A2418, #15120D)'}}>$</div>)}
    </div>
    <div style={{position: 'absolute', top: 540, left: W / 2 - 110, width: 220, height: 220, transform: `scale(${2 - lock}) `, opacity: lock}}>
      <svg width={220} height={220} viewBox="0 0 220 220">
        <rect x={35} y={95} width={150} height={115} rx={16} fill={BG} stroke={CREAM} strokeWidth={10} />
        <path d="M65 95 V65 a45 45 0 0 1 90 0 V95" fill="none" stroke={CREAM} strokeWidth={10} />
        <circle cx={110} cy={150} r={14} fill={GOLD} />
      </svg>
    </div>
    <Caption text="Paratë i fitonte nga filmi dhe nuk deshi ta rrezikonte." gold={['filmi', 'rrezikonte']} from={sec(0.17)} to={sec(3.1)} />
  </AbsoluteFill>;
};

const S3: React.FC = () => {   // 10.05 - 13.65
  const f = useCurrentFrame();
  const s = interpolate(f, [sec(1.75), sec(1.95)], [3, 1], {...clamp, easing: Easing.out(Easing.back(2))});
  const o = interpolate(f, [sec(1.75), sec(1.85)], [0, 1], clamp);
  const shake = f > sec(1.95) && f < sec(2.25) ? (random(`s${f}`) - 0.5) * 24 : 0;
  return <AbsoluteFill style={{transform: `translate(${shake}px, ${shake * 0.6}px)`}}>
    <Kicker text="37 VITE MË VONË" />
    <Year from={1975} to={2012} start={2} dur={sec(1.3)} top={380} />
    <div style={{position: 'absolute', top: 760, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: o}}>
      <div style={{transform: `rotate(-8deg) scale(${s})`, border: `10px solid ${RED}`, borderRadius: 16, padding: '18px 44px',
        fontFamily: 'SukInter', fontWeight: 800, fontSize: 104, letterSpacing: 6, color: RED, mixBlendMode: 'screen'}}>FALIMENTIM</div>
    </div>
    <Caption text="Në 2012, Kodak falimentoi." gold={['2012']} from={sec(0.07)} to={sec(2.5)} />
  </AbsoluteFill>;
};

const Person: React.FC<{delay: number}> = ({delay}) => {
  const p = useIn(delay, 10);
  return <svg width={78} height={110} viewBox="0 0 78 110" style={{transform: `scale(${p})`, opacity: p}}>
    <circle cx={39} cy={26} r={20} fill={GOLD} />
    <path d="M6 108 Q6 56 39 56 Q72 56 72 108 Z" fill={GOLD} />
  </svg>;
};

const S4: React.FC = () => {   // 13.65 - 19.78
  const f = useCurrentFrame();
  const t0 = sec(3.0);
  const t = interpolate(f, [t0, t0 + sec(1.6)], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const v = Math.round(1e9 * t);
  const money = '$' + String(v).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  const done = t >= 1;
  return <AbsoluteFill>
    <Kicker text="PO ATË VIT · 2012" />
    <div style={{position: 'absolute', top: 390, left: 0, right: 0, textAlign: 'center', fontFamily: 'SukSerif', fontWeight: 700,
      fontSize: 86, color: CREAM, opacity: useIn(4)}}>Instagram</div>
    <div style={{position: 'absolute', top: 530, left: 170, width: 740, display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 22}}>
      {Array.from({length: 13}).map((_, i) => <Person key={i} delay={sec(1.4) + i * 2} />)}
    </div>
    <div style={{position: 'absolute', top: 820, left: 0, right: 0, textAlign: 'center', fontFamily: 'SukInter', fontWeight: 800,
      fontSize: 44, letterSpacing: 8, color: GOLD, opacity: useIn(sec(2.0))}}>13 PUNONJËS</div>
    <div style={{position: 'absolute', top: 930, left: 0, right: 0, textAlign: 'center', fontFamily: 'SukMono', fontWeight: 700,
      fontSize: 92, color: done ? GOLD : CREAM, textShadow: done ? goldGlow : 'none', opacity: f >= t0 - 3 ? 1 : 0,
      transform: `scale(${done ? 1 + 0.04 * Math.sin((f - t0) / 3) : 1})`}}>{money}</div>
    <Caption text="Po atë vit, Instagram-i me 13 punonjës u shit për 1 miliard dollarë." gold={['13', 'miliard']} from={sec(0.16)} to={sec(5.2)} />
  </AbsoluteFill>;
};

const S5: React.FC = () => {   // 19.78 - 23.43
  const a = useIn(sec(0.4), 11);
  const b = useIn(sec(2.1), 9);
  const row = (label: string, mark: string, c: string, p: number) => (
    <div style={{display: 'flex', alignItems: 'center', gap: 34, opacity: p, transform: `translateX(${(1 - p) * -80}px)`}}>
      <div style={{width: 120, height: 120, borderRadius: 60, border: `6px solid ${c}`, display: 'flex', alignItems: 'center',
        justifyContent: 'center', fontFamily: 'SukInter', fontWeight: 800, fontSize: 70, color: c}}>{mark}</div>
      <div style={{fontFamily: 'SukSerif', fontWeight: 700, fontSize: 100, color: c}}>{label}</div>
    </div>);
  return <AbsoluteFill>
    <Kicker text="PSE HUMBI KODAK?" />
    <div style={{position: 'absolute', top: 470, left: 230, display: 'flex', flexDirection: 'column', gap: 70}}>
      {row('Ideja', '✓', GOLD, a)}
      {row('Frika', '✕', RED, b)}
    </div>
    <Caption text="Kodak nuk humbi nga mungesa e idesë, por nga frika." gold={['idesë', 'frika']} from={0} to={sec(2.65)} />
  </AbsoluteFill>;
};

const S6: React.FC = () => {   // 23.43 - 30.34
  const f = useCurrentFrame();
  const morph = interpolate(f, [sec(2.6), sec(3.0)], [0, 1], clamp);
  const ai = useIn(sec(2.8), 8);
  const q = useIn(sec(4.5), 12);
  return <AbsoluteFill>
    <Kicker text="SOT" delay={0} />
    <div style={{opacity: 1 - morph, transform: `scale(${1 - morph * 0.4})`}}><Camera top={420} start={sec(0.4)} scale={1.1} /></div>
    <div style={{position: 'absolute', top: 360, left: 0, right: 0, textAlign: 'center', fontFamily: 'SukSerif', fontWeight: 700,
      fontSize: 300, color: GOLD, textShadow: `0 0 60px ${GOLD}88`, opacity: ai, transform: `scale(${0.6 + 0.4 * ai})`}}>AI</div>
    <div style={{position: 'absolute', top: 820, left: 90, right: 90, textAlign: 'center', fontFamily: 'SukSerif', fontWeight: 700,
      fontSize: 72, whiteSpace: 'nowrap', lineHeight: 1.15, color: CREAM, opacity: q, transform: `translateY(${(1 - q) * 40}px)`}}>Ti, çfarë po bën me të?</div>
    <div style={{position: 'absolute', top: 1110, left: 0, right: 0, textAlign: 'center', fontFamily: 'SukInter', fontWeight: 800,
      fontSize: 38, color: GREY, opacity: q}}>@suksesishqip</div>
    <Caption text="Sot kamera dixhitale quhet AI, ti çfarë po bën me të?" gold={['AI', 'ti']} from={sec(0.1)} to={sec(6.1)} />
  </AbsoluteFill>;
};

export const STORY_SCENES: [React.FC, number][] = [
  [S1, 5.99], [S2, 10.05], [S3, 13.65], [S4, 19.78], [S5, 23.43], [S6, 30.34],
].map(([C, end], i, arr) => [C as React.FC, sec(end as number) - (i ? sec(arr[i - 1][1] as number) : 0)]);
export const STORY_FRAMES = STORY_SCENES.reduce((a, [, d]) => a + d, 0);

const Cut: React.FC<{children: React.ReactNode}> = ({children}) => {   // quick light-leak + slide on every cut
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 5], [0, 1], clamp);
  const y = interpolate(f, [0, 7], [40, 0], {...clamp, easing: Easing.out(Easing.cubic)});
  const leak = interpolate(f, [0, 6], [0.5, 0], clamp);
  return <AbsoluteFill style={{opacity: o, transform: `translateY(${y}px)`}}>
    {children}
    <AbsoluteFill style={{background: `linear-gradient(120deg, transparent 20%, ${GOLD} 50%, transparent 80%)`, opacity: leak,
      mixBlendMode: 'screen'}} />
  </AbsoluteFill>;
};

export const Story: React.FC = () => {
  useFonts();
  const f = useCurrentFrame();
  let from = 0;
  return (
    <AbsoluteFill style={{background: BG}}>
      <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 40%, #221D14 0%, ${BG} 70%)`}} />
      <Sprockets />
      <AbsoluteFill style={{transform: `scale(${1 + 0.015 * Math.sin(f / 60)})`}}>
        {STORY_SCENES.map(([C, d], i) => {
          const s = from; from += d;
          return <Sequence key={i} from={s} durationInFrames={d}><Cut><C /></Cut></Sequence>;
        })}
      </AbsoluteFill>
      <AbsoluteFill style={{opacity: 0.06, backgroundImage:
        `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence baseFrequency='0.9' seed='${f % 8}'/></filter><rect width='200' height='200' filter='url(%23n)'/></svg>")`}} />
    </AbsoluteFill>
  );
};
