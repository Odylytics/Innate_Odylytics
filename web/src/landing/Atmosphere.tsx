/**
 * Page atmosphere behind the landing: pale-blue canvas, luminous white bands, soft washes and a few
 * contour lines, like quiet signals moving through the page. Pure CSS + one small inline SVG.
 * Fixed to the viewport (no huge image), never interactive, hidden from assistive tech.
 * One jade line carries the "living signal"; it drifts slowly and stops under prefers-reduced-motion.
 */
export function Atmosphere({ dark = false }: { dark?: boolean }) {
  // Contours in a 1440×900 box, scaled to cover the viewport (preserveAspectRatio slice).
  const contours = [
    'M-60 250 C 220 170, 420 330, 700 260 S 1180 120, 1500 210',
    'M-60 300 C 240 220, 430 390, 720 310 S 1190 170, 1500 260',
    'M-60 350 C 260 280, 450 440, 740 360 S 1200 230, 1500 320',
    'M-60 640 C 260 560, 520 720, 860 640 S 1260 520, 1500 590',
    'M-60 690 C 280 610, 540 770, 880 690 S 1270 580, 1500 640',
  ]
  return (
    <div className={`lp-atmos${dark ? ' lp-atmos-dark' : ''}`} aria-hidden="true">
      <div className="lp-atmos-wash" />
      <svg className="lp-atmos-lines" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        <defs>
          <linearGradient id="lp-fade" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0" stopColor="#fff" stopOpacity="0" />
            <stop offset="0.25" stopColor="#fff" stopOpacity="1" />
            <stop offset="0.75" stopColor="#fff" stopOpacity="1" />
            <stop offset="1" stopColor="#fff" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="lp-signal" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0" stopColor="#11b88f" stopOpacity="0" />
            <stop offset="0.5" stopColor="#11b88f" stopOpacity="0.55" />
            <stop offset="1" stopColor="#63e6be" stopOpacity="0" />
          </linearGradient>
        </defs>
        {/* luminous white bands */}
        <path d="M-80 300 C 240 200, 460 400, 760 300 S 1200 160, 1520 250 L 1520 380 C 1200 300, 980 470, 720 420 S 220 330, -80 440 Z" fill="url(#lp-fade)" opacity={dark ? 0.05 : 0.55} />
        <path d="M-80 660 C 280 570, 560 760, 900 670 S 1280 560, 1520 620 L 1520 700 C 1260 650, 980 800, 860 760 S 260 650, -80 760 Z" fill="url(#lp-fade)" opacity={dark ? 0.035 : 0.4} />
        {/* contour lines */}
        {contours.map((d, i) => (
          <path key={i} d={d} fill="none" stroke={i % 2 ? '#ffffff' : '#9fb7cf'} strokeOpacity={dark ? (i % 2 ? 0.07 : 0.12) : i % 2 ? 0.9 : 0.28} strokeWidth="1" vectorEffect="non-scaling-stroke" />
        ))}
        {/* the living signal: one jade contour that slowly travels */}
        <path className="lp-atmos-signal" d={contours[1]} fill="none" stroke="url(#lp-signal)" strokeWidth="1.5" strokeLinecap="round" vectorEffect="non-scaling-stroke" pathLength={100} />
      </svg>
    </div>
  )
}
