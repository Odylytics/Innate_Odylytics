import type { ComponentProps, CSSProperties, MouseEvent, ReactNode } from 'react'
import { useT } from '../i18n'
import { scrollToY } from '../smooth'

/** A string in both languages. The landing follows the site-wide EN/VI switch. */
export type TT = { en: string; vi: string }
export function useL() {
  const { lang } = useT()
  return (s: TT) => s[lang]
}

export const API_DOCS = 'https://nhip-api-taupe.vercel.app/docs'

/* ───── Brand (Figma "Innate / Brand identity kit": logo + fonts; colours from the Holst guideline) ───── */

/** Symbol mark: the gesture stroke that draws "in", with the i-dot. Paths copied from the Figma vectors. */
export function Mark({ size = 32, className = '', animate = false, dot = 'currentColor' }: { size?: number; className?: string; animate?: boolean; dot?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40.56 40.5" fill="none" aria-hidden="true" className={className}>
      <path
        d="M3.96 15.6V28.2C3.96 33.6 6.66 37.2 9.96 37.2C13.26 37.2 15.96 33.6 15.96 28.2V22.2C15.96 15 19.875 10.8 24.66 10.8C29.445 10.8 33.36 15 33.36 22.2V30.6C33.36 34.5 34.92 37.2 37.26 37.2"
        stroke="currentColor"
        strokeWidth="6.6"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={animate ? 'animate-draw' : undefined}
        style={animate ? ({ '--len': 90 } as CSSProperties) : undefined}
      />
      <path d="M5.05065 8.78429C7.25473 8.31579 8.63378 6.01787 8.13084 3.65172C7.6279 1.28557 5.43343 -0.252778 3.22935 0.215713C1.02526 0.684205 -0.353783 2.98213 0.149156 5.34828C0.652096 7.71443 2.84657 9.25278 5.05065 8.78429Z" fill={dot} />
    </svg>
  )
}

/** Approved app icon, exact Figma vector ("App icon 160", node 25:17): #071A1C tile with r = 36/160,
 *  white gesture stroke, mint dot; symbol 89.73 × 89.6 placed at (35.135, 35.2). Also public/brand/app-icon.svg. */
export const BRAND_INK = '#071A1C'
export function AppIcon({ size = 40, className = '', title }: { size?: number; className?: string; title?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 160 160" fill="none" className={`shrink-0 ${className}`} role={title ? 'img' : undefined} aria-label={title} aria-hidden={title ? undefined : true}>
      <rect width="160" height="160" rx="36" fill={BRAND_INK} />
      <g transform="translate(35.135 35.2)">
        <path d="M8.76062 34.5129V62.3876C8.76062 74.3339 14.7338 82.2981 22.0343 82.2981C29.3348 82.2981 35.308 74.3339 35.308 62.3876V49.1139C35.308 33.1855 43.969 23.894 54.5548 23.894C65.1405 23.894 73.8016 33.1855 73.8016 49.1139V67.6971C73.8016 76.325 77.2528 82.2981 82.4295 82.2981" stroke="#FFFFFF" strokeWidth="14.601" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M11.1734 19.4347C16.0495 18.3982 19.1003 13.3146 17.9877 8.07999C16.875 2.84542 12.0203 -0.557845 7.14421 0.47859C2.26817 1.51502 -0.782664 6.59868 0.329978 11.8333C1.44262 17.0678 6.29741 20.4711 11.1734 19.4347Z" fill="#63E6BE" />
      </g>
    </svg>
  )
}

/** Wordmark: custom-drawn "innate" (never retyped in a font). */
export function Wordmark({ height = 24, className = '' }: { height?: number; className?: string }) {
  return (
    <svg height={height} width={(height * 173.61) / 43.73} viewBox="0 0 173.61 43.73" fill="none" aria-hidden="true" className={className}>
      <path
        d="M3.32045 13.9141V40.4171M18.5597 40.4171V24.5153C18.5597 17.8895 22.5351 13.9141 27.8358 13.9141C33.1364 13.9141 37.1118 17.8895 37.1118 23.1902V40.4171M52.3511 40.4171V24.5153C52.3511 17.8895 56.3265 13.9141 61.6271 13.9141C66.9277 13.9141 70.9032 17.8895 70.9032 23.1902V40.4171M109.995 13.9141V40.4171M125.234 7.28833V33.7914C125.234 38.4294 127.885 40.4171 131.86 40.4171M119.934 13.9141H131.86M144.449 27.1656H170.29C170.286 24.1766 169.246 21.2813 167.348 18.973C165.449 16.6646 162.808 15.086 159.876 14.506C156.944 13.9261 153.901 14.3807 151.267 15.7925C148.632 17.2042 146.569 19.4857 145.428 22.2483C144.287 25.0109 144.139 28.0837 145.009 30.9431C145.879 33.8025 147.714 36.2717 150.201 37.9301C152.688 39.5884 155.673 40.3332 158.647 40.0376C161.621 39.7421 164.401 38.4244 166.513 36.3092M109.995 27.1656C109.995 23.7389 108.634 20.4526 106.211 18.0296C103.788 15.6066 100.502 14.2454 97.0749 14.2454C93.6483 14.2454 90.362 15.6066 87.9389 18.0296C85.5159 20.4526 84.1547 23.7389 84.1547 27.1656C84.1547 30.5923 85.5159 33.8786 87.9389 36.3016C90.362 38.7246 93.6483 40.0858 97.0749 40.0858C100.502 40.0858 103.788 38.7246 106.211 36.3016C108.634 33.8786 109.995 30.5923 109.995 27.1656Z"
        stroke="currentColor"
        strokeWidth="6.49324"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path d="M4.29067 7.47228C6.15192 7.07666 7.31538 5.13103 6.88933 3.1266C6.46327 1.12217 4.60904 -0.182026 2.74778 0.213596C0.886527 0.609218 -0.276934 2.55485 0.14912 4.55928C0.575175 6.56371 2.42941 7.8679 4.29067 7.47228Z" fill="currentColor" />
    </svg>
  )
}

/** Lockup: the approved app icon + the custom Figma wordmark in brand ink. `height` is the wordmark height. */
export function Logo({ dark = false, height = 22 }: { dark?: boolean; height?: number }) {
  return (
    <span className="inline-flex items-center" style={{ gap: height * 0.5, color: dark ? '#FFFFFF' : BRAND_INK }}>
      <AppIcon size={Math.round(height * 1.5)} />
      <Wordmark height={height} />
      <span className="sr-only">Innate</span>
    </span>
  )
}

/* ───── Layout helpers ───── */

/** In-page link: the router owns the hash (#/…), so scroll instead of navigating. */
export function jump(id: string) {
  return (e: MouseEvent) => {
    e.preventDefault()
    const el = document.getElementById(id)
    if (!el) return
    const head = document.getElementById('lp-head')?.getBoundingClientRect().height ?? 100
    scrollToY(Math.max(0, window.scrollY + el.getBoundingClientRect().top - head - 16))
  }
}

export function Eyebrow({ children, dark = false }: { children: ReactNode; dark?: boolean }) {
  return (
    <p className={`inline-flex items-center gap-2 font-sans text-[11px] font-bold uppercase tracking-[0.14em] ${dark ? 'text-mint' : 'text-teal'}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${dark ? 'bg-mint' : 'bg-jade'}`} />
      {children}
    </p>
  )
}

export function SectionHead({ eyebrow, title, lead, dark = false, center = false }: { eyebrow: string; title: ReactNode; lead?: ReactNode; dark?: boolean; center?: boolean }) {
  return (
    <div className={`max-w-2xl ${center ? 'mx-auto text-center' : ''}`}>
      <Eyebrow dark={dark}>{eyebrow}</Eyebrow>
      <h2 className={`mt-4 font-display text-[34px] font-semibold leading-[1.1] tracking-tight md:text-[44px] ${dark ? 'text-canvas' : 'text-ink'}`}>{title}</h2>
      {lead && <p className={`mt-5 text-lg leading-relaxed ${dark ? 'text-canvas/70' : 'text-teal'}`}>{lead}</p>}
    </div>
  )
}

type ButtonProps = ComponentProps<'a'> & { variant?: 'primary' | 'ghost' | 'light' | 'glass' }

export function Button({ variant = 'primary', className = '', children, ...rest }: ButtonProps) {
  const styles = {
    primary: 'bg-ink text-canvas hover:bg-navy',
    ghost: 'border border-line bg-surface text-ink hover:border-jade',
    light: 'bg-mint text-ink hover:bg-canvas',
    glass: 'bg-canvas/10 text-canvas hover:bg-canvas/20',
  }[variant]
  return (
    <a className={`inline-flex h-12 items-center gap-2 whitespace-nowrap rounded-full px-6 text-[15px] font-semibold transition-colors ${styles} ${className}`} {...rest}>
      {children}
    </a>
  )
}

export function Arrow() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M3 8h10m-4-4 4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export type Action = 'allow' | 'step_up' | 'hold'

export const ACTION_STYLE: Record<Action, { label: TT; dot: string; chip: string; color: string }> = {
  allow: { label: { en: 'Allow', vi: 'Cho qua' }, dot: 'bg-jade', chip: 'bg-mist text-jade-ink', color: 'var(--color-jade)' },
  step_up: { label: { en: 'Step-up', vi: 'Xác thực thêm' }, dot: 'bg-stepup', chip: 'bg-stepup/20 text-[#7a5717]', color: 'var(--color-stepup)' },
  hold: { label: { en: 'Hold', vi: 'Giữ lệnh' }, dot: 'bg-hold', chip: 'bg-hold/15 text-[#8c3a30]', color: 'var(--color-hold)' },
}
