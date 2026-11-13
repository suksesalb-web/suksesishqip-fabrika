import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Sequence, continueRender, delayRender, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig, Easing, random} from 'remotion';

// Daily Reel look ("engine": "hype"): pure black, electric yellow, white, hard red.
// Bold uppercase, hard cuts with a zoom punch, karaoke captions timed on Riko's voice.
// All times in a beat are frames relative to the beat start (computed in fabrika/reel.py).
const BLACK = '#000000';
const YEL = '#FFE600';
const WHITE = '#FFFFFF';
const RED = '#FF1E1E';
const GREY = '#8C8C8C';
const W = 1080;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

export type HBeat = {
  type: 'hook' | 'count' | 'icons' | 'chat' | 'year' | 'bars' | 'list' | 'checks' | 'text';
  from: number; dur: number; speech: number;      // speech = frames until the voice ends in this beat
  text: string; word_at: number[]; keys?: string[];
  at?: number; item_at?: number[];
  bg?: 'yellow' | 'black' | 'red';
  kicker?: string;
  big?: string; sub?: string; stamp?: string;                       // hook
  value?: number; prefix?: string; suffix?: string; label?: string;  // count
  icon?: string; n?: number; title?: string;                        // icons
  reply?: string; alarm?: boolean;                                  // chat
  from_year?: number; to_year?: number;                             // year (+ stamp)
  left?: {label: string; sub?: string}; right?: {label: string; sub?: string};  // bars
  items?: string[];                                                 // list
  rows?: {label: string; ok: boolean}[];                            // checks
  highlight?: string;                                               // text
};
export type HypeReelProps = {durationInFrames: number; handle: string; beats: HBeat[]};

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
const shakeAt = (f: number, at: number, len = 10, amp = 34) =>
  f >= at && f < at + len ? (random(`k${f}`) - 0.5) * amp * (1 - (f - at) / len) : 0;
const fmtNum = (v: number) => String(Math.round(v)).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
const fit = (s: string, base: number, max: number) => Math.min(base, Math.floor(max / Math.max(1, s.length)));
// size for text that may wrap: 1-4 lines across ~940px
const tsize = (s: string, max: number) => {
  const n = Math.max(1, s.length);
  const lines = n <= 10 ? 1 : n <= 22 ? 2 : n <= 40 ? 3 : 4;
  return Math.min(max, Math.floor(940 / (0.62 * Math.ceil(n / lines))));
};

const bgOf = (b: HBeat) => ({yellow: YEL, black: BLACK, red: RED}[b.bg || (b.type === 'hook' || b.type === 'text' ? 'yellow' : 'black')]);
const ink = (bg: string) => (bg === YEL ? BLACK : WHITE);
const accent = (bg: string) => (bg === YEL ? RED : bg === RED ? BLACK : YEL);

// ---------- pieces ----------
const T: React.FC<{children: React.ReactNode; top: number; size: number; color: string; delay?: number; slam?: boolean;
  mono?: boolean; style?: React.CSSProperties}> = ({children, top, size, color, delay = 0, slam = false, mono = false, style}) => {
  const p = useIn(delay, slam ? 8 : 11);
  const s = slam ? interpolate(p, [0, 1], [1.6, 1]) : interpolate(p, [0, 1], [0.75, 1]);
  return <div style={{position: 'absolute', top, left: 70, right: 70, textAlign: 'center', fontFamily: mono ? 'SukMono' : 'SukInter',
    fontWeight: 800, fontSize: size, lineHeight: 1.05, color, opacity: Math.min(1, p * 2), transform: `scale(${s})`,
    textTransform: mono ? 'none' : 'uppercase', letterSpacing: mono ? -2 : -1, ...style}}>{children}</div>;
};

const Kicker: React.FC<{text?: string; color: string}> = ({text, color}) =>
  text ? <T top={240} size={46} color={color} style={{letterSpacing: 8}}>{text}</T> : null;

const Caption: React.FC<{b: HBeat}> = ({b}) => {
  const f = useCurrentFrame();
  const words = b.text.split(' ');
  const keys = (b.keys || []).map((k) => k.toLowerCase());
  return <div style={{position: 'absolute', top: 1250, left: 80, right: 80, display: 'flex', justifyContent: 'center'}}>
    <div style={{background: BLACK, borderRadius: 18, padding: '18px 26px', textAlign: 'center', fontFamily: 'SukInter',
      fontWeight: 800, fontSize: 50, lineHeight: 1.25, border: bgOf(b) === BLACK ? `3px solid #222` : 'none'}}>
      {words.map((w, i) => {
        const clean = w.toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');
        const k = keys.some((x) => clean.startsWith(x.replace(/[^\p{L}\p{N}]/gu, '')) && x.length > 0);
        const on = f >= (b.word_at[i] ?? 0);
        return <span key={i} style={{color: k ? YEL : WHITE, opacity: on ? 1 : 0.2}}>{w} </span>;
      })}
    </div>
  </div>;
};

const ICONS: Record<string, string> = {
  shop: 'M8 34 L16 10 L74 10 L82 34 Z M12 38 H78 V82 H54 V54 H36 V82 H12 Z',
  person: 'M45 8 a18 18 0 1 1 0 36 a18 18 0 1 1 0 -36 Z M12 84 Q12 50 45 50 Q78 50 78 84 Z',
  coin: 'M45 6 a39 39 0 1 1 0 78 a39 39 0 1 1 0 -78 Z',
  house: 'M45 6 L84 40 H74 V84 H54 V60 H36 V84 H16 V40 H6 Z',
  car: 'M6 62 V48 Q8 40 20 38 L28 22 Q32 16 40 16 H58 Q66 16 70 22 L78 38 Q86 40 86 50 V62 Z M18 64 a10 10 0 1 0 20 0 Z M54 64 a10 10 0 1 0 20 0 Z',
  phone: 'M26 4 H64 Q72 4 72 12 V78 Q72 86 64 86 H26 Q18 86 18 78 V12 Q18 4 26 4 Z',
  laptop: 'M16 14 H74 V58 H16 Z M4 64 H86 L80 76 H10 Z',
  bag: 'M14 30 H76 L82 86 H8 Z M30 30 V22 Q30 8 45 8 Q60 8 60 22 V30',
  clock: 'M45 6 a39 39 0 1 1 0 78 a39 39 0 1 1 0 -78 Z',
};
const Icon: React.FC<{name: string; color: string; size: number}> = ({name, color, size}) => (
  <svg width={size} height={size} viewBox="0 0 90 90">
    <path d={ICONS[name] || ICONS.coin} fill={name === 'bag' ? 'none' : color} stroke={color} strokeWidth={name === 'bag' ? 8 : 0}
      fillRule="evenodd" />
    {name === 'coin' && <text x={45} y={60} textAnchor="middle" fontSize={44} fontWeight={800} fill={BLACK} fontFamily="SukInter">€</text>}
    {name === 'clock' && <path d="M45 22 V46 L60 56" stroke={BLACK} strokeWidth={8} fill="none" strokeLinecap="round" />}
  </svg>
);

// ---------- scenes ----------
const Hook: React.FC<{b: HBeat}> = ({b}) => {
  const f = useCurrentFrame();
  const bg = bgOf(b), c = ink(bg), a = accent(bg);
  const big = b.big || '';
  const mono = big.replace(/\s/g, '').length > 0 && (big.match(/[\d.,€$%]/g) || []).length / big.replace(/\s/g, '').length >= 0.6;
  const hit = interpolate(f, [0, 7], [1.2, 1], {...clamp, easing: Easing.out(Easing.back(2))});
  const at = b.at ?? Math.round(b.speech * 0.6);
  return <AbsoluteFill style={{transform: `translateX(${shakeAt(f, at)}px)`}}>
    <Kicker text={b.kicker} color={c} />
    <div style={{position: 'absolute', top: 360, left: 50, right: 50, textAlign: 'center', fontFamily: mono ? 'SukMono' : 'SukInter',
      fontWeight: 800, fontSize: mono ? fit(big, 150, 1500) : tsize(big, 130), lineHeight: 1.0, color: c,
      textTransform: mono ? 'none' : 'uppercase', transform: `scale(${hit})`}}>{big}</div>
    {b.sub && <T top={big.length > 10 && !mono ? 720 : 640} size={62} color={c} delay={Math.round(b.speech * 0.35)}>{b.sub}</T>}
    {b.stamp && [0, 1].map((i) => <T key={i} top={800 + i * 140} size={90} color={a} delay={at + i * 5} slam
      style={{rotate: `${i ? 5 : -7}deg`}}><span style={{border: `8px solid ${a}`, borderRadius: 14, padding: '0 24px'}}>{b.stamp}</span></T>)}
  </AbsoluteFill>;
};

const Count: React.FC<{b: HBeat}> = ({b}) => {
  const f = useCurrentFrame();
  const bg = bgOf(b), c = ink(bg), a = accent(bg);
  const at = b.at ?? 4;
  const t = interpolate(f, [at, at + 28], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const s = (b.prefix || '') + fmtNum((b.value || 0) * t) + (b.suffix || '');
  const done = t >= 1;
  return <AbsoluteFill>
    <Kicker text={b.kicker} color={a} />
    <div style={{position: 'absolute', top: 430, left: 40, right: 40, textAlign: 'center', fontFamily: 'SukMono', fontWeight: 700,
      fontSize: fit((b.prefix || '') + fmtNum(b.value || 0) + (b.suffix || ''), 190, 1600), color: done ? a : c,
      transform: `scale(${done ? 1 + 0.03 * Math.sin(f / 2.5) : 1})`, opacity: f >= at - 2 ? 1 : 0.15}}>{s}</div>
    {b.label && <T top={700} size={60} color={c} delay={at + 20}>{b.label}</T>}
  </AbsoluteFill>;
};

const Icons: React.FC<{b: HBeat}> = ({b}) => {
  const f = useCurrentFrame();
  const bg = bgOf(b), c = ink(bg), a = accent(bg);
  const N = Math.max(1, Math.min(40, b.n || 20));
  const at = b.at ?? 6;
  const shown = Math.floor(interpolate(f, [at, at + Math.min(70, 4 + N * 2)], [0, N], clamp));
  const size = N <= 6 ? 150 : N <= 15 ? 110 : 80;
  return <AbsoluteFill>
    <Kicker text={b.kicker} color={a} />
    {b.title && <T top={320} size={fit(b.title, 110, 1520)} color={c} slam>{b.title}</T>}
    <div style={{position: 'absolute', top: 500, left: 100, right: 100, display: 'flex', flexWrap: 'wrap', gap: 14, justifyContent: 'center'}}>
      {Array.from({length: N}).map((_, i) => <div key={i} style={{opacity: i < shown ? 1 : 0.08, transform: `scale(${i === shown - 1 ? 1.25 : 1})`}}>
        <Icon name={b.icon || 'coin'} color={a} size={size} /></div>)}
    </div>
    {b.label && <T top={1110} size={60} color={a} delay={at + 20}>{b.label}</T>}
  </AbsoluteFill>;
};

const Chat: React.FC<{b: HBeat}> = ({b}) => {
  const f = useCurrentFrame();
  const at = b.at ?? Math.round(b.speech * 0.75);
  const after = f >= at;
  const bg = after && b.alarm ? RED : bgOf(b);
  const reply = b.reply || '';
  const pop = useIn(3);
  return <AbsoluteFill style={{background: bg, transform: `translateX(${b.alarm ? shakeAt(f, at, 12, 40) : 0}px)`}}>
    <Kicker text={b.kicker} color={bg === BLACK ? YEL : BLACK} />
    <div style={{position: 'absolute', top: 420, left: 120, right: 120, minHeight: 420, borderRadius: 60, background: WHITE,
      transform: `scale(${pop})`, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 40}}>
      <div style={{position: 'absolute', bottom: -60, left: 120, width: 0, height: 0, borderLeft: '50px solid transparent',
        borderRight: '50px solid transparent', borderTop: `80px solid ${WHITE}`}} />
      {!after
        ? <div style={{display: 'flex', gap: 30}}>{[0, 1, 2].map((i) => <div key={i} style={{width: 50, height: 50, borderRadius: 25,
            background: BLACK, opacity: 0.3 + 0.7 * Math.max(0, Math.sin((f - i * 5) / 5))}} />)}</div>
        : <div style={{fontFamily: 'SukInter', fontWeight: 800, fontSize: tsize(reply, 220), lineHeight: 1.05, textAlign: 'center',
            color: b.alarm ? RED : BLACK, transform: `scale(${interpolate(f, [at, at + 6], [1.8, 1], clamp)})`}}>{reply}</div>}
    </div>
  </AbsoluteFill>;
};

const Year: React.FC<{b: HBeat}> = ({b}) => {
  const f = useCurrentFrame();
  const y0 = b.from_year ?? 2000, y1 = b.to_year ?? y0;
  const t = interpolate(f, [3, 30], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const year = Math.round(y0 + (y1 - y0) * t);
  const at = b.at ?? Math.round(b.speech * 0.7);
  const hit = !!b.stamp && f >= at;
  const bg = hit ? RED : bgOf(b);
  return <AbsoluteFill style={{background: bg, transform: `translate(${b.stamp ? shakeAt(f, at, 12, 44) : 0}px, 0)`}}>
    <Kicker text={b.kicker} color={hit ? BLACK : YEL} />
    <div style={{position: 'absolute', top: 360, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 14}}>
      {String(year).split('').map((d, i) => <div key={i} style={{width: 150, height: 210, borderRadius: 16, background: hit ? BLACK : '#161616',
        display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'SukInter', fontWeight: 800, fontSize: 170,
        color: hit ? WHITE : YEL}}>{d}</div>)}
    </div>
    {hit && <T top={700} size={fit(b.stamp || '', 130, 1500)} color={WHITE} delay={at} slam style={{textShadow: '0 8px 0 #000'}}>{b.stamp}</T>}
  </AbsoluteFill>;
};

const Bars: React.FC<{b: HBeat}> = ({b}) => {
  const f = useCurrentFrame();
  const bg = bgOf(b), c = ink(bg), a = accent(bg);
  const at = b.at ?? Math.round(b.speech * 0.4);
  const g = interpolate(f, [at, at + 36], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.2))});
  const small = useIn(4);
  const col = (side: 'left' | 'right', h: number, color: string, p: number, label?: {label: string; sub?: string}) => (
    <div style={{position: 'absolute', bottom: 760, [side]: 170, width: 300, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      <div style={{fontFamily: 'SukInter', fontWeight: 800, fontSize: 46, color, marginBottom: 12, textAlign: 'center', lineHeight: 1.05,
        opacity: p, textTransform: 'uppercase'}}>{label?.label}</div>
      <div style={{width: 220, height: h * p, background: color}} />
      <div style={{fontFamily: 'SukInter', fontWeight: 700, fontSize: 34, color: GREY, marginTop: 14, textTransform: 'uppercase'}}>{label?.sub}</div>
    </div>);
  return <AbsoluteFill>
    <Kicker text={b.kicker} color={a} />
    {col('left', 16, c, small, b.left)}
    {col('right', 600, a, g, b.right)}
  </AbsoluteFill>;
};

const List: React.FC<{b: HBeat}> = ({b}) => {
  const bg = bgOf(b), c = ink(bg), a = accent(bg);
  const items = (b.items || []).slice(0, 4);
  return <AbsoluteFill>
    <Kicker text={b.kicker} color={a} />
    {b.title && <T top={320} size={tsize(b.title, 96)} color={c}>{b.title}</T>}
    <div style={{position: 'absolute', top: 480, left: 110, right: 110, display: 'flex', flexDirection: 'column', gap: 30}}>
      {items.map((it, i) => <ListRow key={i} n={i + 1} text={it} at={(b.item_at || [])[i] ?? 6 + i * 20} c={c} a={a} />)}
    </div>
  </AbsoluteFill>;
};
const ListRow: React.FC<{n: number; text: string; at: number; c: string; a: string}> = ({n, text, at, c, a}) => {
  const p = useIn(at, 10);
  return <div style={{display: 'flex', alignItems: 'center', gap: 28, opacity: p, transform: `translateX(${(1 - p) * -120}px)`}}>
    <div style={{minWidth: 110, height: 110, borderRadius: 20, background: a, display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'SukInter', fontWeight: 800, fontSize: 70, color: a === YEL ? BLACK : WHITE}}>{n}</div>
    <div style={{fontFamily: 'SukInter', fontWeight: 800, fontSize: fit(text, 64, 1500), color: c, textTransform: 'uppercase', lineHeight: 1.05}}>{text}</div>
  </div>;
};

const Checks: React.FC<{b: HBeat}> = ({b}) => {
  const bg = bgOf(b), c = ink(bg), a = accent(bg);
  const rows = (b.rows || []).slice(0, 3);
  return <AbsoluteFill>
    <Kicker text={b.kicker} color={a} />
    <div style={{position: 'absolute', top: 460, left: 170, right: 100, display: 'flex', flexDirection: 'column', gap: 60}}>
      {rows.map((r, i) => <CheckRow key={i} label={r.label} ok={r.ok} at={(b.item_at || [])[i] ?? 6 + i * 25} c={c} a={a} />)}
    </div>
  </AbsoluteFill>;
};
const CheckRow: React.FC<{label: string; ok: boolean; at: number; c: string; a: string}> = ({label, ok, at, c, a}) => {
  const p = useIn(at, 9);
  const col = ok ? a : RED;
  return <div style={{display: 'flex', alignItems: 'center', gap: 34, opacity: p, transform: `scale(${interpolate(p, [0, 1], [1.4, 1])})`,
    transformOrigin: 'left center'}}>
    <div style={{width: 130, height: 130, borderRadius: 65, background: col, display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'SukInter', fontWeight: 800, fontSize: 80, color: col === YEL ? BLACK : WHITE}}>{ok ? '✓' : '✕'}</div>
    <div style={{fontFamily: 'SukInter', fontWeight: 800, fontSize: fit(label, 100, 1100), color: ok ? c : RED, textTransform: 'uppercase'}}>{label}</div>
  </div>;
};

const Text: React.FC<{b: HBeat; handle: string; last: boolean}> = ({b, handle, last}) => {
  const bg = bgOf(b), c = ink(bg), a = accent(bg);
  const at = b.at ?? Math.round(b.speech * 0.45);
  const title = b.title || '';
  const hl = b.highlight || '';
  return <AbsoluteFill>
    <Kicker text={b.kicker} color={c} />
    {title && <T top={330} size={tsize(title, 84)} color={c} delay={2}>{title}</T>}
    {hl && <T top={title ? 600 : 450} size={tsize(hl, 120)} color={a} delay={at} slam>{hl}</T>}
    {last && <T top={1060} size={40} color={c} delay={at + 20} style={{textTransform: 'none', letterSpacing: 2}}>{handle}</T>}
  </AbsoluteFill>;
};

const Scene: React.FC<{b: HBeat; handle: string; last: boolean}> = ({b, handle, last}) => {
  const f = useCurrentFrame();
  const z = interpolate(f, [0, 8], [1.12, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const flash = interpolate(f, [0, 3], [0.6, 0], clamp);
  const first = b.from === 0;   // the first frame is the cover: crisp, no flash
  const body = {hook: <Hook b={b} />, count: <Count b={b} />, icons: <Icons b={b} />, chat: <Chat b={b} />, year: <Year b={b} />,
    bars: <Bars b={b} />, list: <List b={b} />, checks: <Checks b={b} />, text: <Text b={b} handle={handle} last={last} />}[b.type]
    || <Text b={b} handle={handle} last={last} />;
  return <AbsoluteFill style={{background: bgOf(b), transform: first ? undefined : `scale(${z})`}}>
    {body}
    <Caption b={b} />
    {!first && <AbsoluteFill style={{background: WHITE, opacity: flash}} />}
  </AbsoluteFill>;
};

export const HypeReel: React.FC<HypeReelProps> = ({beats, handle}) => {
  useFonts();
  return <AbsoluteFill style={{background: BLACK}}>
    {beats.map((b, i) => <Sequence key={i} from={b.from} durationInFrames={b.dur}>
      <Scene b={b} handle={handle} last={i === beats.length - 1} /></Sequence>)}
  </AbsoluteFill>;
};

export const HYPE_SAMPLE: HypeReelProps = {
  durationInFrames: 240, handle: '@suksesishqip',
  beats: [
    {type: 'hook', from: 0, dur: 80, speech: 70, text: 'Netflix-i kushtonte vetëm 50 milionë dollarë.', word_at: [0, 10, 20, 30, 40, 50],
      keys: ['50'], big: '$50.000.000', kicker: 'Netflix në shitje', stamp: 'HA HA HA', at: 50},
    {type: 'chat', from: 80, dur: 80, speech: 70, text: 'Shefi tha jo.', word_at: [0, 20, 40], kicker: 'Shefi:', reply: 'JO.', at: 40, alarm: true},
    {type: 'text', from: 160, dur: 80, speech: 60, text: 'Ideja qesharake mund të jetë Netflix-i i nesërm.', word_at: [0, 8, 16, 24, 32, 40, 48, 56],
      title: 'Ideja qesharake', highlight: 'mund të jetë Netflix-i i nesërm.', at: 30},
  ],
};
