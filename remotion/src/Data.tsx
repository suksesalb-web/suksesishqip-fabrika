import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Sequence, continueRender, delayRender, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig, Easing, random} from 'remotion';

// "Data story" look: dark screen, neon numbers, counters, bars, glitch cuts.
const BG = '#0A0C0B';
const GREEN = '#3DF58A';
const RED = '#FF3B4A';
const GOLD = '#F4B740';
const GREY = '#8A8F8C';
const W = 1080;

const FONTS: [string, string, string][] = [
  ['SukInter', 'fonts/i700.ttf', '700'], ['SukInter', 'fonts/i800.ttf', '800'], ['SukMono', 'fonts/mono700.ttf', '700'],
];
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([fam, src, weight]) => new FontFace(fam, `url(${staticFile(src)})`, {weight})
      .load().then((l) => document.fonts.add(l)))).then(() => continueRender(h)).catch(() => continueRender(h));
  }, [h]);
};

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const glow = (c: string, s = 1) => `0 0 ${18 * s}px ${c}AA, 0 0 ${48 * s}px ${c}55`;
const fmt = (n: number, dec = 0) => {
  const [i, d] = n.toFixed(dec).split('.');
  return i.replace(/\B(?=(\d{3})+(?!\d))/g, '.') + (d ? ',' + d : '');
};

const useIn = (delay = 0, damping = 12) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: f - delay, fps, config: {damping, mass: 0.55}});
};

// Glitch on the first frames of each scene: RGB split + sliced offset + flash.
const Glitch: React.FC<{children: React.ReactNode; len?: number}> = ({children, len = 7}) => {
  const f = useCurrentFrame();
  const g = f < len ? 1 - f / len : 0;
  const dx = g * (random(`x${f}`) - 0.5) * 60;
  const flash = interpolate(f, [0, 3], [0.35, 0], clamp);
  return (
    <AbsoluteFill>
      {g > 0 && <AbsoluteFill style={{transform: `translateX(${dx + 14 * g}px)`, opacity: 0.6, mixBlendMode: 'screen',
        filter: 'sepia(1) saturate(8) hue-rotate(-50deg)'}}>{children}</AbsoluteFill>}
      {g > 0 && <AbsoluteFill style={{transform: `translateX(${-dx - 14 * g}px)`, opacity: 0.6, mixBlendMode: 'screen',
        filter: 'sepia(1) saturate(8) hue-rotate(140deg)'}}>{children}</AbsoluteFill>}
      <AbsoluteFill style={{transform: `translateX(${dx * 0.3}px)`}}>{children}</AbsoluteFill>
      {g > 0 && [0, 1, 2].map((k) => (
        <div key={k} style={{position: 'absolute', left: 0, right: 0, top: random(`t${f}${k}`) * 1920, height: 20 + random(`h${f}${k}`) * 60,
          background: k % 2 ? `${RED}55` : `${GREEN}44`, transform: `translateX(${(random(`o${f}${k}`) - 0.5) * 200}px)`}} />
      ))}
      <AbsoluteFill style={{background: 'white', opacity: flash}} />
    </AbsoluteFill>
  );
};

const Label: React.FC<{text: string; color?: string; top: number; delay?: number; size?: number}> = ({text, color = GREY, top, delay = 0, size = 44}) => {
  const p = useIn(delay);
  return <div style={{position: 'absolute', top, left: 0, right: 0, textAlign: 'center', fontFamily: 'SukInter', fontWeight: 800,
    fontSize: size, letterSpacing: size * 0.22, color, opacity: p, transform: `translateY(${(1 - p) * 30}px)`}}>{text}</div>;
};

const Big: React.FC<{text: string; color: string; top: number; size?: number; delay?: number; mono?: boolean; slam?: boolean}> =
  ({text, color, top, size = 200, delay = 0, mono = true, slam = false}) => {
  const p = useIn(delay, slam ? 9 : 12);
  const s = slam ? interpolate(p, [0, 1], [2.2, 1]) : interpolate(p, [0, 1], [0.85, 1]);
  return <div style={{position: 'absolute', top, left: 0, right: 0, textAlign: 'center', fontFamily: mono ? 'SukMono' : 'SukInter',
    fontWeight: 800, fontSize: size, color, textShadow: glow(color), opacity: Math.min(1, p * 1.5), transform: `scale(${s})`,
    letterSpacing: mono ? -4 : 0}}>{text}</div>;
};

// Odometer-style digit boxes counting up.
const Counter: React.FC<{to: number; from?: number; start: number; dur: number; top: number; prefix?: string; color?: string; size?: number}> =
  ({to, from = 0, start, dur, top, prefix = '€', color = 'white', size = 150}) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [start, start + dur], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const v = Math.round(from + (to - from) * t);
  const s = prefix + fmt(v);
  const done = t >= 1;
  const c = done ? color : 'white';
  const p = useIn(start - 4);
  return (
    <div style={{position: 'absolute', top, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 10, opacity: p}}>
      {s.split('').map((ch, i) => {
        const box = /\d|€/.test(ch);
        return <div key={i} style={{fontFamily: 'SukMono', fontWeight: 700, fontSize: size, color: c, textShadow: done ? glow(c, 0.8) : 'none',
          width: box ? size * 0.68 : size * 0.3, textAlign: 'center', lineHeight: 1.25,
          border: box ? `4px solid ${done ? c + '99' : '#444'}` : 'none', borderRadius: 14, background: box ? '#141716' : 'transparent'}}>{ch}</div>;
      })}
    </div>
  );
};

const PhoneIcon: React.FC<{top: number; color: string; delay?: number}> = ({top, color, delay = 0}) => {
  const f = useCurrentFrame();
  const d = interpolate(f, [delay, delay + 24], [1, 0], clamp);
  return <svg style={{position: 'absolute', top, left: W / 2 - 90}} width={180} height={300} viewBox="0 0 180 300">
    <rect x={8} y={8} width={164} height={284} rx={30} fill="none" stroke={color} strokeWidth={8} pathLength={1}
      strokeDasharray={1} strokeDashoffset={d} style={{filter: `drop-shadow(0 0 12px ${color})`}} />
    <line x1={70} y1={30} x2={110} y2={30} stroke={color} strokeWidth={8} strokeLinecap="round" opacity={1 - d} />
  </svg>;
};

const CarIcon: React.FC<{top: number; color: string}> = ({top, color}) => {
  const f = useCurrentFrame();
  const d = interpolate(f, [0, 26], [1, 0], clamp);
  return <svg style={{position: 'absolute', top, left: W / 2 - 170}} width={340} height={150} viewBox="0 0 340 150">
    <path d="M20 110 L20 80 Q22 70 40 66 L90 60 L130 26 Q140 20 160 20 L230 20 Q250 20 262 34 L292 64 L315 70 Q325 74 325 86 L325 110 Z"
      fill="none" stroke={color} strokeWidth={7} strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={d}
      style={{filter: `drop-shadow(0 0 10px ${color})`}} />
    {[90, 255].map((x) => <circle key={x} cx={x} cy={112} r={24} fill={BG} stroke={color} strokeWidth={7} opacity={1 - d} />)}
  </svg>;
};

// ---------- scenes ----------
const S1: React.FC = () => {
  const f = useCurrentFrame();
  const pulse = 0.6 + 0.4 * Math.sin(f / 4);
  return <Glitch>
    <Label text="SA TË KUSHTON VËRTET?" top={250} color="white" size={50} />
    <PhoneIcon top={400} color={GREEN} delay={4} />
    <Label text="TELEFONI" top={760} color={GREEN} delay={6} />
    <Big text="€1.200" color={GREEN} top={830} size={210} delay={8} />
    <div style={{position: 'absolute', top: 1140, left: 0, right: 0, textAlign: 'center', fontFamily: 'SukMono', fontWeight: 700,
      fontSize: 92, color: RED, opacity: f > 30 ? pulse : 0, textShadow: glow(RED)}}>= ??? DITË PUNË</div>
  </Glitch>;
};

const S2: React.FC = () => (
  <Glitch>
    <Label text="PAGA JOTE" top={480} color={GREEN} />
    <Counter to={800} start={4} dur={30} top={570} color={GREEN} size={170} />
    <Big text="÷ 176 ORË" color={GOLD} top={880} size={120} delay={40} mono />
    <Label text="22 ditë × 8 orë në muaj" top={1050} delay={48} size={40} />
  </Glitch>
);

const S3: React.FC = () => (
  <Glitch>
    <Label text="1 ORË PUNË" top={560} color="white" size={56} />
    <Big text="€4,55" color={GREEN} top={660} size={260} delay={6} slam />
    <Label text="KAQ VLEN ORA JOTE" top={1000} delay={22} color={GREY} size={42} />
  </Glitch>
);

const S4: React.FC = () => {
  const f = useCurrentFrame();
  const filled = Math.floor(interpolate(f, [62, 130], [0, 33], clamp));
  const cell = 70, gap = 12, cols = 11;
  return <Glitch>
    <Label text="TELEFONI €1.200 =" top={260} color={GREEN} size={46} />
    <Counter to={264} start={6} dur={36} top={340} prefix="" color="white" size={160} />
    <Label text="ORË PUNË" top={560} color="white" delay={40} size={50} />
    <div style={{position: 'absolute', top: 700, left: (W - (cols * cell + (cols - 1) * gap)) / 2, width: cols * cell + (cols - 1) * gap,
      display: 'flex', flexWrap: 'wrap', gap, opacity: interpolate(f, [52, 60], [0, 1], clamp)}}>
      {Array.from({length: 44}).map((_, i) => {
        const on = i < filled;
        return <div key={i} style={{width: cell, height: cell, borderRadius: 10, border: `3px solid ${on ? RED : '#333'}`,
          background: on ? RED : '#121514', boxShadow: on ? `0 0 16px ${RED}88` : 'none'}} />;
      })}
    </div>
    <div style={{position: 'absolute', top: 1110, left: 0, right: 0, textAlign: 'center', fontFamily: 'SukMono', fontWeight: 700, fontSize: 130,
      color: RED, textShadow: glow(RED)}}>{f >= 62 ? `${filled} DITË` : ''}</div>
    {f >= 132 && <Big text="1,5 MUAJ PAGË" color={GOLD} top={1290} size={84} delay={132} mono={false} slam />}
  </Glitch>;
};

const S5: React.FC = () => {
  const f = useCurrentFrame();
  const segs = 25;
  const n = Math.floor(interpolate(f, [26, 80], [0, segs], clamp));
  return <Glitch>
    <CarIcon top={300} color={GREEN} />
    <Label text="MAKINA E RE" top={500} color={GREEN} size={46} />
    <Big text="€20.000" color={GREEN} top={570} size={170} delay={6} />
    <div style={{position: 'absolute', top: 850, left: 90, right: 90, display: 'flex', gap: 6}}>
      {Array.from({length: segs}).map((_, i) => <div key={i} style={{flex: 1, height: 70, borderRadius: 6,
        background: i < n ? RED : '#1A1D1C', boxShadow: i < n ? `0 0 14px ${RED}99` : 'none'}} />)}
    </div>
    <div style={{position: 'absolute', top: 950, left: 0, right: 0, textAlign: 'center', fontFamily: 'SukMono', fontWeight: 700,
      fontSize: 150, color: RED, textShadow: glow(RED)}}>{n > 0 ? `${n} MUAJ` : ''}</div>
    {f >= 84 && <Label text="PAGË E PLOTË, PA NGRËNË, PA QIRA" top={1150} color="white" delay={84} size={40} />}
  </Glitch>;
};

const S6: React.FC = () => {
  const f = useCurrentFrame();
  return <Glitch>
    <Big text="Mos e mat në euro." color="white" top={640} size={84} mono={false} delay={2} />
    <Big text="Mate në ditë pune." color={RED} top={780} size={104} mono={false} delay={30} slam />
    <Label text="RUAJE PARA BLERJES SË RADHËS" top={1050} delay={60} color={GOLD} size={38} />
    <div style={{position: 'absolute', top: 1150, left: 0, right: 0, textAlign: 'center', fontFamily: 'SukInter', fontWeight: 800,
      fontSize: 40, color: GREY, opacity: interpolate(f, [66, 76], [0, 1], clamp)}}>@suksesishqip</div>
  </Glitch>;
};

export const SCENES: [React.FC, number][] = [[S1, 96], [S2, 90], [S3, 75], [S4, 165], [S5, 120], [S6, 114]];
export const DATA_FRAMES = SCENES.reduce((a, [, d]) => a + d, 0);

export const Data: React.FC = () => {
  useFonts();
  const f = useCurrentFrame();
  let from = 0;
  const drift = 1 + 0.02 * Math.sin(f / 50);
  return (
    <AbsoluteFill style={{background: BG}}>
      <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 42%, #18201C 0%, ${BG} 65%)`}} />
      <AbsoluteFill style={{transform: `scale(${drift})`}}>
        {SCENES.map(([C, d], i) => {
          const s = from; from += d;
          return <Sequence key={i} from={s} durationInFrames={d}><C /></Sequence>;
        })}
      </AbsoluteFill>
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(255,255,255,0.025) 0 2px, transparent 2px 5px)'}} />
    </AbsoluteFill>
  );
};
