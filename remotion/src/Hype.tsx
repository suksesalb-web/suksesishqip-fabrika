import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Sequence, continueRender, delayRender, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig, Easing, random} from 'remotion';

// High-contrast story look: pure black, electric yellow, white, hard red. Bold uppercase, hard cuts with a zoom punch.
const BLACK = '#000000';
const YEL = '#FFE600';
const WHITE = '#FFFFFF';
const RED = '#FF1E1E';
const W = 1080;
const FPS = 30;
const sec = (s: number) => Math.round(s * FPS);
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const FONTS: [string, string, string][] = [
  ['SukInter', 'fonts/i800.ttf', '800'], ['SukInter', 'fonts/i700.ttf', '700'], ['SukMono', 'fonts/mono700.ttf', '700'],
];
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([fam, src, weight]) => new FontFace(fam, `url(${staticFile(src)})`, {weight})
      .load().then((l) => document.fonts.add(l)))).then(() => continueRender(h)).catch(() => continueRender(h));
  }, [h]);
};
const useIn = (delay = 0, damping = 11) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: f - delay, fps, config: {damping, mass: 0.5}});
};
const shakeAt = (f: number, at: number, len = 8, amp = 26) =>
  f >= at && f < at + len ? (random(`k${f}`) - 0.5) * amp * (1 - (f - at) / len) : 0;
const money = (v: number) => '$' + String(Math.round(v)).replace(/\B(?=(\d{3})+(?!\d))/g, '.');

const T: React.FC<{children: React.ReactNode; top: number; size: number; color: string; delay?: number; slam?: boolean;
  style?: React.CSSProperties}> = ({children, top, size, color, delay = 0, slam = false, style}) => {
  const p = useIn(delay, slam ? 8 : 11);
  const s = slam ? interpolate(p, [0, 1], [1.9, 1]) : interpolate(p, [0, 1], [0.7, 1]);
  return <div style={{position: 'absolute', top, left: 70, right: 70, textAlign: 'center', fontFamily: 'SukInter', fontWeight: 800,
    fontSize: size, lineHeight: 1.05, color, opacity: Math.min(1, p * 2), transform: `scale(${s})`, textTransform: 'uppercase',
    letterSpacing: -1, ...style}}>{children}</div>;
};

// Karaoke captions in a solid box, so they read on any background.
const Caption: React.FC<{text: string; keys?: string[]; from: number; to: number; dark?: boolean}> = ({text, keys = [], from, to, dark = true}) => {
  const f = useCurrentFrame();
  const words = text.split(' ');
  const shown = Math.ceil(interpolate(f, [from, to], [0, words.length], clamp));
  return <div style={{position: 'absolute', top: 1250, left: 90, right: 90, display: 'flex', justifyContent: 'center'}}>
    <div style={{background: dark ? BLACK : WHITE, borderRadius: 18, padding: '18px 26px', textAlign: 'center', fontFamily: 'SukInter',
      fontWeight: 800, fontSize: 50, lineHeight: 1.25}}>
      {words.map((w, i) => {
        const k = keys.some((x) => w.toLowerCase().startsWith(x.toLowerCase()));
        const base = dark ? WHITE : BLACK;
        return <span key={i} style={{color: k ? (dark ? YEL : RED) : base, opacity: i < shown ? 1 : 0.2}}>{w} </span>;
      })}
    </div>
  </div>;
};

const Shop: React.FC<{color: string; size?: number}> = ({color, size = 90}) => (
  <svg width={size} height={size} viewBox="0 0 90 90">
    <path d="M8 34 L16 10 L74 10 L82 34 Z" fill={color} />
    <rect x={12} y={38} width={66} height={44} fill={color} />
    <rect x={36} y={54} width={18} height={28} fill={BLACK} />
  </svg>
);

// ---------- scenes (seconds measured on Riko's narration) ----------
const S1: React.FC = () => {   // 0 - 6.84
  const f = useCurrentFrame();
  const t = 1;
  const done = true;
  const hit = interpolate(f, [0, 7], [1.25, 1], {...clamp, easing: Easing.out(Easing.back(2))});
  const sh = shakeAt(f, sec(4.86), 12, 34);
  return <AbsoluteFill style={{background: YEL, transform: `translate(${sh}px, ${sh * 0.5}px)`}}>
    <T top={250} size={46} color={BLACK} style={{letterSpacing: 8}}>Netflix ishte në shitje</T>
    <div style={{position: 'absolute', top: 400, left: 0, right: 0, textAlign: 'center', fontFamily: 'SukMono', fontWeight: 700,
      fontSize: 132, color: BLACK, transform: `scale(${hit * (done ? 1 + 0.03 * Math.sin(f / 2.5) : 1)})`}}>{money(50e6 * t)}</div>
    <T top={590} size={64} color={BLACK} delay={sec(1.9)}>vetëm 50 milionë</T>
    {[0, 1, 2].map((i) => {
      const d = sec(4.86) + i * 5;
      return <T key={i} top={780 + i * 120} size={96} color={RED} delay={d} slam
        style={{rotate: `${[-8, 6, -4][i]}deg`, left: [80, 260, 140][i], right: 'auto'}}>
        <span style={{border: `8px solid ${RED}`, borderRadius: 14, padding: '0 22px', background: YEL}}>HA HA HA</span></T>;
    })}
    <Caption text="Netflix-i kushtonte vetëm 50 milionë dollarë, dhe Blockbuster-i qeshi me të." keys={['50', 'milionë', 'qeshi']} from={0} to={sec(5.6)} />
  </AbsoluteFill>;
};

const S2: React.FC = () => {   // 6.84 - 11.44
  const f = useCurrentFrame();
  const n = Math.floor(interpolate(f, [sec(1.0), sec(3.6)], [0, 40], clamp));
  return <AbsoluteFill style={{background: BLACK}}>
    <T top={240} size={50} color={YEL} style={{letterSpacing: 10}}>Viti 2000</T>
    <T top={330} size={120} color={WHITE} slam>Blockbuster</T>
    <div style={{position: 'absolute', top: 520, left: 110, right: 110, display: 'flex', flexWrap: 'wrap', gap: 14, justifyContent: 'center'}}>
      {Array.from({length: 40}).map((_, i) => <div key={i} style={{opacity: i < n ? 1 : 0.08, transform: `scale(${i === n - 1 ? 1.25 : 1})`}}>
        <Shop color={YEL} size={76} /></div>)}
    </div>
    <T top={1110} size={64} color={YEL} delay={sec(2.6)}>Mijëra dyqane</T>
    <Caption text="Ishte viti 2000 dhe Blockbuster-i kishte mijëra dyqane filmash." keys={['2000', 'mijëra']} from={0} to={sec(3.7)} />
  </AbsoluteFill>;
};

const S3: React.FC = () => {   // 11.44 - 15.62
  const f = useCurrentFrame();
  const no = sec(2.85);
  const typing = f < no;
  const sh = shakeAt(f, no, 12, 40);
  const b = useIn(4);
  return <AbsoluteFill style={{background: f >= no ? RED : BLACK, transform: `translate(${sh}px, 0)`}}>
    <T top={260} size={50} color={f >= no ? BLACK : YEL} style={{letterSpacing: 8}}>Shefi i Blockbuster-it:</T>
    <div style={{position: 'absolute', top: 430, left: W / 2 - 330, width: 660, height: 440, borderRadius: 60, background: WHITE,
      transform: `scale(${b})`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
      <div style={{position: 'absolute', bottom: -60, left: 120, width: 0, height: 0, borderLeft: '50px solid transparent',
        borderRight: '50px solid transparent', borderTop: `80px solid ${WHITE}`}} />
      {typing
        ? <div style={{display: 'flex', gap: 30}}>{[0, 1, 2].map((i) => <div key={i} style={{width: 50, height: 50, borderRadius: 25,
            background: BLACK, opacity: 0.3 + 0.7 * Math.max(0, Math.sin((f - i * 5) / 5))}} />)}</div>
        : <div style={{fontFamily: 'SukInter', fontWeight: 800, fontSize: 300, color: RED,
            transform: `scale(${interpolate(f, [no, no + 6], [2, 1], clamp)})`}}>JO.</div>}
    </div>
    <Caption text="Shefi i tyre mezi e mbajti të qeshurën dhe tha jo." keys={['qeshurën', 'jo']} from={0} to={sec(3.2)} />
  </AbsoluteFill>;
};

const S4: React.FC = () => {   // 15.62 - 19.26
  const f = useCurrentFrame();
  const t = interpolate(f, [sec(0.1), sec(1.0)], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const year = Math.round(2000 + 10 * t);
  const bust = sec(2.22);
  const on = f >= bust;
  const sh = shakeAt(f, bust, 12, 44);
  return <AbsoluteFill style={{background: on ? RED : BLACK, transform: `translate(${sh}px, ${sh * 0.4}px)`}}>
    <T top={240} size={50} color={on ? BLACK : YEL} style={{letterSpacing: 8}}>10 vjet më vonë</T>
    <div style={{position: 'absolute', top: 360, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 14}}>
      {String(year).split('').map((d, i) => <div key={i} style={{width: 150, height: 210, borderRadius: 16, background: on ? BLACK : '#161616',
        display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'SukInter', fontWeight: 800, fontSize: 170,
        color: on ? WHITE : YEL}}>{d}</div>)}
    </div>
    {on && <T top={700} size={130} color={WHITE} delay={bust} slam style={{textShadow: '0 8px 0 #000'}}>Falimentoi</T>}
    <div style={{position: 'absolute', top: 920, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 18, opacity: on ? 1 : 0}}>
      {Array.from({length: 6}).map((_, i) => <Shop key={i} color={BLACK} size={90} />)}
    </div>
    <Caption text="Dhjetë vjet më vonë, Blockbuster-i falimentoi." keys={['dhjetë', 'falimentoi']} from={0} to={sec(2.8)} />
  </AbsoluteFill>;
};

const S5: React.FC = () => {   // 19.26 - 23.22
  const f = useCurrentFrame();
  const g = interpolate(f, [sec(1.0), sec(2.3)], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.2))});
  const small = useIn(4);
  return <AbsoluteFill style={{background: BLACK}}>
    <T top={240} size={50} color={YEL} style={{letterSpacing: 8}}>Netflix sot</T>
    <div style={{position: 'absolute', bottom: 760, left: 170, width: 260, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      <div style={{fontFamily: 'SukInter', fontWeight: 800, fontSize: 40, color: WHITE, marginBottom: 12, opacity: small}}>$50 MILIONË</div>
      <div style={{width: 200, height: 14 * small, background: WHITE}} />
      <div style={{fontFamily: 'SukInter', fontWeight: 700, fontSize: 34, color: '#999', marginTop: 14}}>2000</div>
    </div>
    <div style={{position: 'absolute', bottom: 760, right: 170, width: 300, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      <div style={{fontFamily: 'SukInter', fontWeight: 800, fontSize: 48, color: YEL, marginBottom: 12, textAlign: 'center', lineHeight: 1.05,
        opacity: g}}>QINDRA<br />MILIARDA $</div>
      <div style={{width: 240, height: 640 * g, background: YEL, boxShadow: `0 0 60px ${YEL}66`}} />
      <div style={{fontFamily: 'SukInter', fontWeight: 700, fontSize: 34, color: '#999', marginTop: 14}}>SOT</div>
    </div>
    <Caption text="Netflix-i sot vlen qindra miliarda dollarë." keys={['qindra', 'miliarda']} from={0} to={sec(3.1)} />
  </AbsoluteFill>;
};

const S6: React.FC = () => {   // 23.22 - end
  return <AbsoluteFill style={{background: YEL}}>
    <T top={330} size={78} color={BLACK} delay={2}>Ideja që sot duket qesharake</T>
    <T top={620} size={104} color={RED} delay={sec(1.9)} slam>mund të jetë<br />Netflix-i<br />i nesërm.</T>
    <T top={1010} size={40} color={BLACK} delay={sec(3.4)} style={{textTransform: 'none', letterSpacing: 2}}>@suksesishqip</T>
    <Caption text="Ideja që sot duket qesharake mund të jetë Netflix-i i nesërm." keys={['qesharake', 'netflix']} from={0} to={sec(3.3)} />
  </AbsoluteFill>;
};

const ENDS = [6.84, 11.44, 15.62, 19.26, 23.22, 28.3];
export const HYPE_SCENES: [React.FC, number][] = [S1, S2, S3, S4, S5, S6]
  .map((C, i) => [C, sec(ENDS[i]) - (i ? sec(ENDS[i - 1]) : 0)]);
export const HYPE_FRAMES = sec(ENDS[ENDS.length - 1]);

const Punch: React.FC<{children: React.ReactNode}> = ({children}) => {   // hard cut + zoom punch + white flash
  const f = useCurrentFrame();
  const z = interpolate(f, [0, 8], [1.12, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const flash = interpolate(f, [0, 3], [0.6, 0], clamp);
  return <AbsoluteFill style={{transform: `scale(${z})`}}>{children}
    <AbsoluteFill style={{background: WHITE, opacity: flash}} /></AbsoluteFill>;
};

export const Hype: React.FC = () => {
  useFonts();
  let from = 0;
  return <AbsoluteFill style={{background: BLACK}}>
    {HYPE_SCENES.map(([C, d], i) => {
      const s = from; from += d;
      return <Sequence key={i} from={s} durationInFrames={d}>{i ? <Punch><C /></Punch> : <C />}</Sequence>;
    })}
  </AbsoluteFill>;
};
