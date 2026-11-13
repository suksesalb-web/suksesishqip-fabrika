import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';

// Flat, bold illustrations for Hype Reels (no photos needed). All drawn on a 200x200 grid.
// c = main colour, a = accent, bg = background colour (used for cut-outs).
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

type P = {c: string; a: string; bg: string; t: number};   // t = 0..1 draw progress (for charts)

const ART: Record<string, (p: P) => React.ReactNode> = {
  keypad: ({c, bg}) => <g>
    <rect x={58} y={8} width={84} height={184} rx={26} fill={c} />
    <rect x={92} y={0} width={14} height={20} rx={5} fill={c} />
    <rect x={70} y={28} width={60} height={52} rx={8} fill={bg} />
    {Array.from({length: 12}).map((_, i) => <rect key={i} x={70 + (i % 3) * 21} y={92 + Math.floor(i / 3) * 22} width={16} height={14} rx={4} fill={bg} />)}
  </g>,
  smartphone: ({c, a}) => <g>
    <rect x={48} y={4} width={104} height={192} rx={22} fill={c} />
    <rect x={56} y={16} width={88} height={168} rx={14} fill={a} />
    <rect x={84} y={20} width={32} height={8} rx={4} fill={c} />
    {Array.from({length: 12}).map((_, i) => <rect key={i} x={64 + (i % 3) * 26} y={40 + Math.floor(i / 3) * 30} width={20} height={20} rx={6} fill={c} opacity={0.35} />)}
  </g>,
  crown: ({a, c}) => <g>
    <path d="M24 150 L34 58 L74 104 L100 40 L126 104 L166 58 L176 150 Z" fill={a} stroke={c} strokeWidth={6} strokeLinejoin="round" />
    <rect x={24} y={150} width={152} height={26} rx={6} fill={a} stroke={c} strokeWidth={6} />
    {[34, 100, 166].map((x, i) => <circle key={i} cx={x} cy={[58, 40, 58][i]} r={11} fill={c} />)}
  </g>,
  chart_down: ({c, a, t}) => <g>
    <path d="M24 20 V178 H186" stroke={c} strokeWidth={8} fill="none" strokeLinecap="round" />
    <path d="M30 40 L70 62 L98 54 L136 118 L178 162" stroke={a} strokeWidth={14} fill="none" strokeLinecap="round" strokeLinejoin="round"
      pathLength={1} strokeDasharray={1} strokeDashoffset={1 - t} />
    {t > 0.95 && <path d="M160 164 L182 166 L176 144" stroke={a} strokeWidth={14} fill="none" strokeLinecap="round" strokeLinejoin="round" />}
  </g>,
  chart_up: ({c, a, t}) => <g>
    <path d="M24 20 V178 H186" stroke={c} strokeWidth={8} fill="none" strokeLinecap="round" />
    <path d="M30 160 L70 130 L98 140 L136 76 L178 34" stroke={a} strokeWidth={14} fill="none" strokeLinecap="round" strokeLinejoin="round"
      pathLength={1} strokeDasharray={1} strokeDashoffset={1 - t} />
    {t > 0.95 && <path d="M156 32 L180 32 L178 56" stroke={a} strokeWidth={14} fill="none" strokeLinecap="round" strokeLinejoin="round" />}
  </g>,
  money: ({c, a}) => <g>
    {[0, 1, 2].map((i) => <g key={i} transform={`translate(${i * 8}, ${-i * 22})`}>
      <rect x={22} y={110} width={150} height={74} rx={10} fill={a} stroke={c} strokeWidth={6} />
      <circle cx={97} cy={147} r={20} fill="none" stroke={c} strokeWidth={6} />
    </g>)}
  </g>,
  rocket: ({c, a}) => <g>
    <path d="M100 10 Q146 52 140 132 L60 132 Q54 52 100 10 Z" fill={c} />
    <circle cx={100} cy={72} r={18} fill={a} />
    <path d="M60 104 L32 150 L64 140 Z M140 104 L168 150 L136 140 Z" fill={a} />
    <path d="M76 138 Q100 200 124 138 Z" fill="#FF8A00" />
  </g>,
  bulb: ({c, a}) => <g>
    <circle cx={100} cy={84} r={60} fill={a} stroke={c} strokeWidth={6} />
    <rect x={74} y={138} width={52} height={24} rx={6} fill={c} />
    <rect x={80} y={166} width={40} height={14} rx={6} fill={c} />
    <path d="M84 96 L100 70 L116 96" stroke={c} strokeWidth={6} fill="none" />
  </g>,
  trophy: ({c, a}) => <g>
    <path d="M56 20 H144 V70 Q144 122 100 126 Q56 122 56 70 Z" fill={a} stroke={c} strokeWidth={6} />
    <path d="M56 36 H28 Q28 84 62 90 M144 36 H172 Q172 84 138 90" stroke={c} strokeWidth={8} fill="none" />
    <rect x={90} y={126} width={20} height={34} fill={c} />
    <rect x={62} y={160} width={76} height={24} rx={6} fill={c} />
  </g>,
  robot: ({c, a, bg}) => <g>
    <rect x={44} y={56} width={112} height={96} rx={22} fill={c} />
    <circle cx={78} cy={100} r={14} fill={a} /><circle cx={122} cy={100} r={14} fill={a} />
    <rect x={80} y={126} width={40} height={8} rx={4} fill={bg} />
    <rect x={96} y={26} width={8} height={30} fill={c} /><circle cx={100} cy={24} r={11} fill={a} />
    <rect x={30} y={90} width={14} height={34} rx={6} fill={c} /><rect x={156} y={90} width={14} height={34} rx={6} fill={c} />
    <rect x={66} y={156} width={68} height={30} rx={8} fill={c} />
  </g>,
  laptop: ({c, a}) => <g>
    <rect x={36} y={36} width={128} height={90} rx={10} fill={c} />
    <rect x={46} y={46} width={108} height={70} rx={4} fill={a} />
    <path d="M14 136 H186 L172 160 H28 Z" fill={c} />
  </g>,
  store: ({c, a, bg}) => <g>
    <path d="M18 70 L36 24 H164 L182 70 Z" fill={a} stroke={c} strokeWidth={6} />
    <rect x={28} y={74} width={144} height={104} fill={c} />
    <rect x={84} y={112} width={32} height={66} fill={bg} />
    <rect x={40} y={92} width={34} height={30} fill={bg} /><rect x={126} y={92} width={34} height={30} fill={bg} />
  </g>,
  piggy: ({c, a, bg}) => <g>
    <ellipse cx={100} cy={112} rx={70} ry={56} fill={a} stroke={c} strokeWidth={6} />
    <rect x={84} y={60} width={32} height={8} rx={4} fill={c} />
    <circle cx={140} cy={98} r={7} fill={c} />
    <ellipse cx={170} cy={118} rx={14} ry={18} fill={a} stroke={c} strokeWidth={6} />
    {[60, 120].map((x) => <rect key={x} x={x} y={156} width={20} height={26} rx={6} fill={c} />)}
    <circle cx={100} cy={120} r={4} fill={bg} />
  </g>,
  clock: ({c, a}) => <g>
    <circle cx={100} cy={100} r={80} fill={a} stroke={c} strokeWidth={10} />
    <path d="M100 52 V102 L134 122" stroke={c} strokeWidth={12} fill="none" strokeLinecap="round" />
  </g>,
  people: ({c, a}) => <g>
    {[[52, a], [148, a], [100, c]].map(([x, col], i) => <g key={i}>
      <circle cx={x as number} cy={i === 2 ? 64 : 80} r={i === 2 ? 26 : 22} fill={col as string} />
      <path d={`M${(x as number) - 40} 184 Q${(x as number) - 40} ${i === 2 ? 100 : 114} ${x} ${i === 2 ? 100 : 114} Q${(x as number) + 40} ${i === 2 ? 100 : 114} ${(x as number) + 40} 184 Z`} fill={col as string} />
    </g>)}
  </g>,
  house: ({c, a, bg}) => <g>
    <path d="M100 18 L184 92 H164 V182 H36 V92 H16 Z" fill={a} stroke={c} strokeWidth={6} strokeLinejoin="round" />
    <rect x={84} y={124} width={32} height={58} fill={bg} />
  </g>,
  car: ({c, a, bg}) => <g>
    <path d="M14 140 V112 Q16 98 36 94 L58 60 Q64 52 76 52 H128 Q140 52 148 62 L170 94 Q186 98 186 116 V140 Z" fill={a} stroke={c} strokeWidth={6} />
    <path d="M70 66 H98 V94 H54 Z M108 66 H132 L150 94 H108 Z" fill={bg} />
    {[56, 144].map((x) => <circle key={x} cx={x} cy={142} r={22} fill={c} />)}
  </g>,
};
export const FIGURES = Object.keys(ART);

export const Figure: React.FC<{name: string; size: number; top: number; left?: number; delay?: number; c: string; a: string; bg: string;
  mode?: 'pop' | 'fall'; idle?: boolean}> = ({name, size, top, left, delay = 0, c, a, bg, mode = 'pop', idle = true}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const draw = ART[name];
  if (!draw) return null;
  const p = spring({frame: f - delay, fps, config: {damping: 9, mass: 0.6}});
  const t = interpolate(f, [delay, delay + 24], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const bob = idle ? Math.sin((f - delay) / 11) * 8 : 0;
  const tilt = idle ? Math.sin((f - delay) / 17) * 3 : 0;
  let transform = `translateY(${bob}px) rotate(${tilt}deg) scale(${p})`;
  if (mode === 'fall') {
    const d = interpolate(f, [delay, delay + 14], [0, 1], {...clamp, easing: Easing.in(Easing.quad)});
    transform = `translateY(${d * 260}px) rotate(${d * 38}deg) scale(${1 - d * 0.15})`;
  }
  return <svg width={size} height={size} viewBox="0 0 200 200" style={{position: 'absolute', top, left: left ?? (1080 - size) / 2,
    transform, opacity: mode === 'fall' ? interpolate(f, [delay + 8, delay + 16], [1, 0], clamp) : Math.min(1, p * 2), overflow: 'visible', filter: 'drop-shadow(0 14px 0 rgba(0,0,0,0.25))'}}>
    {draw({c, a, bg, t})}
  </svg>;
};

// Moving background texture: drifting dots (dark) or stripes (yellow/red), plus a soft vignette.
export const Backdrop: React.FC<{bg: string}> = ({bg}) => {
  const f = useCurrentFrame();
  const dark = bg === '#000000';
  const off = (f * 1.2) % 60;
  return <AbsoluteFill>
    {dark
      ? <AbsoluteFill style={{backgroundImage: 'radial-gradient(rgba(255,230,0,0.13) 2px, transparent 2.5px)', backgroundSize: '60px 60px',
          backgroundPosition: `${off}px ${off}px`}} />
      : <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(135deg, rgba(0,0,0,0.06) 0 22px, transparent 22px 60px)',
          backgroundPosition: `${off}px 0`}} />}
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 40%, transparent 55%, rgba(0,0,0,0.28) 100%)'}} />
  </AbsoluteFill>;
};

// Donut ring that fills to `pct` around the hook number.
export const Donut: React.FC<{pct: number; cx: number; cy: number; r: number; c: string; a: string; delay?: number}> = ({pct, cx, cy, r, c, a, delay = 0}) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [delay, delay + 30], [0, pct / 100], {...clamp, easing: Easing.out(Easing.cubic)});
  const C = 2 * Math.PI * r;
  return <svg width={1080} height={1920} style={{position: 'absolute', top: 0, left: 0}}>
    <circle cx={cx} cy={cy} r={r} fill="none" stroke={c} strokeOpacity={0.15} strokeWidth={46} />
    <circle cx={cx} cy={cy} r={r} fill="none" stroke={a} strokeWidth={46} strokeDasharray={`${C * t} ${C}`}
      transform={`rotate(-90 ${cx} ${cy})`} strokeLinecap="butt" />
  </svg>;
};
