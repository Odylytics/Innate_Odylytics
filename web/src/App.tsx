import { useEffect, useState } from 'react'
import { LangContext, dict, useT, type Lang } from './i18n'
import DemoChoice from './DemoChoice'
import type { StoryCase } from './story'
import Footer from './Footer'
import LandingPage from './landing/LandingPage'
import { Atmosphere } from './landing/Atmosphere'
import { AppIcon, Wordmark } from './landing/ui'
import Demo from './Demo'
import Collect from './Collect'
import Ops from './Ops'
import { scrollToEl, scrollToY, startSmoothScroll } from './smooth'
import { ArrowBtn, Glyph, T } from './ui'

const store = {
  get: (k: string) => { try { return localStorage.getItem(k) } catch { return null } },
  set: (k: string, v: string) => { try { localStorage.setItem(k, v) } catch { /* private mode */ } },
}
export { store }

type Theme = 'dark' | 'light'

// Hash routes (#/, #/demo, #/demo?story=1) so the static build works on any host without rewrites.
function useHash() {
  const [hash, setHash] = useState(window.location.hash)
  useEffect(() => {
    const on = () => { setHash(window.location.hash); if (!window.location.hash.includes('#how')) scrollToY(0, false) }
    window.addEventListener('hashchange', on)
    return () => window.removeEventListener('hashchange', on)
  }, [])
  return hash
}

export function Mark({ className = 'brand-mark' }: { className?: string }) {
  // approved app icon (Figma "App icon 160"); a hairline ring keeps it visible on the dark nav
  return (
    <span className={className} style={{ display: 'inline-flex', borderRadius: '22.5%', boxShadow: '0 0 0 1px rgba(226,236,246,0.22)' }} aria-hidden="true">
      <AppIcon size={30} />
    </span>
  )
}

const L = {
  how: { en: 'How it works', vi: 'Cách hoạt động' },
  menu: { en: 'Menu', vi: 'Menu' },
  closeMenu: { en: 'Close menu', vi: 'Đóng menu' },
  toLight: { en: 'Switch to light theme', vi: 'Chuyển sang giao diện sáng' },
  toDark: { en: 'Switch to dark theme', vi: 'Chuyển sang giao diện tối' },
  skip: { en: 'Skip to content', vi: 'Bỏ qua tới nội dung' },
}

export function LangSwitch() {
  return (
    <LangContext.Consumer>
      {({ lang, setLang }) => (
        <div className="lang" role="group" aria-label="Language">
          <button aria-pressed={lang === 'en'} onClick={() => setLang('en')}>EN</button>
          <button aria-pressed={lang === 'vi'} onClick={() => setLang('vi')}>VI</button>
        </div>
      )}
    </LangContext.Consumer>
  )
}

function ThemeSwitch({ theme, setTheme }: { theme: Theme; setTheme: (t: Theme) => void }) {
  const { lang } = useT()
  const next: Theme = theme === 'dark' ? 'light' : 'dark'
  const label = theme === 'dark' ? L.toLight[lang] : L.toDark[lang]
  return (
    <button className="icon-btn theme-btn" onClick={() => setTheme(next)} aria-label={label} title={label}>
      <Glyph name={theme === 'dark' ? 'sun' : 'moon'} />
    </button>
  )
}

function Nav({ path, theme, setTheme }: { path: string; theme: Theme; setTheme: (t: Theme) => void }) {
  const { t, lang } = useT()
  const [open, setOpen] = useState(false)
  useEffect(() => { setOpen(false) }, [path])

  // Movora's nav slides away while scrolling down and returns on the way up.
  const [tucked, setTucked] = useState(false)
  useEffect(() => {
    let last = window.scrollY
    let raf = 0
    const on = () => {
      cancelAnimationFrame(raf)
      raf = requestAnimationFrame(() => {
        const y = window.scrollY
        if (Math.abs(y - last) < 6) return
        setTucked(y > 160 && y > last)
        last = y
      })
    }
    window.addEventListener('scroll', on, { passive: true })
    return () => { window.removeEventListener('scroll', on); cancelAnimationFrame(raf) }
  }, [])
  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setOpen(false) }
    window.addEventListener('keydown', onKey)
    document.documentElement.style.overflow = 'hidden'
    return () => { window.removeEventListener('keydown', onKey); document.documentElement.style.overflow = '' }
  }, [open])

  const other: Lang = lang === 'en' ? 'vi' : 'en'
  const links = [
    { href: '#/#how', label: L.how[lang], alt: L.how[other], current: false },
    { href: '#/ops', label: t('navOps'), alt: dict.navOps[other], current: path.startsWith('/ops') },
  ]

  return (
    <header className={`nav-bar ${tucked && !open ? 'tucked' : ''}`}>
      <a className="skip" href="#content" onClick={(e) => { e.preventDefault(); document.getElementById('content')?.focus() }}>{L.skip[lang]}</a>
      <nav className="nav" aria-label="Main">
        <a className="brand" href="#/" aria-label="Innate"><Mark /><Wordmark height={18} className="brand-word" /><span className="sr-only">Innate</span></a>
        <div className="nav-right">
          <div className="nav-links">
            {links.map((l) => (
              <a key={l.href} href={l.href} aria-current={l.current ? 'page' : undefined}>
                <span className="nl">{l.label}</span>
                {/* the other language's label holds the width, so switching language never moves the links */}
                <span className="nl-ghost" aria-hidden="true">{l.alt}</span>
              </a>
            ))}
          </div>
          <div className="nav-tools">
            <LangSwitch />
            <ThemeSwitch theme={theme} setTheme={setTheme} />
            <ArrowBtn href="#/demo?choose=1"><T k="navDemo" /></ArrowBtn>
            <button className="icon-btn burger" aria-expanded={open} aria-controls="menu-sheet" aria-label={open ? L.closeMenu[lang] : L.menu[lang]} onClick={() => setOpen(!open)}>
              <Glyph name={open ? 'close' : 'menu'} />
            </button>
          </div>
        </div>
      </nav>
      {open && (
        <div className="menu-sheet" id="menu-sheet">
          {links.map((l) => <a key={l.href} className="m-link" href={l.href} onClick={() => setOpen(false)}>{l.label}</a>)}
          <a className="m-link" href="#/demo?choose=1" onClick={() => setOpen(false)}><T k="navDemo" /></a>
          <div className="menu-tools"><LangSwitch /><ThemeSwitch theme={theme} setTheme={setTheme} /></div>
        </div>
      )}
    </header>
  )
}

/** Marks <html> while a demo/ops page is shown, so the page background can sit behind the atmosphere. */
function AppPage() {
  useEffect(() => {
    const html = document.documentElement
    html.dataset.page = 'app'
    return () => { if (html.dataset.page === 'app') delete html.dataset.page }
  }, [])
  return null
}

function Site() {
  useEffect(() => { startSmoothScroll() }, [])

  // dark by default (DEMO_DESIGN_RULES.md); index.html applies the stored choice before first paint
  const [theme, setThemeState] = useState<Theme>(() => (document.documentElement.dataset.theme === 'light' ? 'light' : 'dark'))
  const setTheme = (next: Theme) => { setThemeState(next); store.set('innate.theme', next) }
  useEffect(() => {
    document.documentElement.dataset.theme = theme
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', theme === 'dark' ? '#0A1522' : '#EEF4FA')
  }, [theme])

  const hash = useHash()
  const [path, query] = hash.replace(/^#/, '').split('?')
  const isDemo = path.startsWith('/demo')
  const isOps = path.startsWith('/ops')
  const sv = new URLSearchParams(query ?? '').get('story') // 1 = remote (old links), remote, stolen
  const storyCase: StoryCase | null = sv === 'stolen' ? 'stolen' : sv === '1' || sv === 'remote' ? 'remote' : null
  const choose = new URLSearchParams(query ?? '').get('choose') === '1'

  useEffect(() => {
    if (!isDemo && !isOps && hash.includes('#how')) scrollToEl(document.getElementById('how'))
  }, [hash, isDemo, isOps])

  return (
    <>
      {isDemo || isOps ? (
        <>
          <AppPage />
          <div className="app-atmos" aria-hidden="true">{theme === 'dark' ? <Atmosphere dark /> : <Atmosphere />}</div>
          <Nav path={path} theme={theme} setTheme={setTheme} />
          <main id="content" tabIndex={-1} style={{ outline: 'none' }}>{isDemo ? <><Demo key={String(storyCase)} storyCase={storyCase} />{choose && <DemoChoice />}</> : <Ops />}</main>
          {!isDemo && <Footer />}
        </>
      ) : (
        <LandingPage />
      )}
    </>
  )
}

// #/collect is a standalone phone-only page (no site nav, footer or smooth scroll), so it is routed before the site mounts.
export default function App() {
  // The language lives here so the standalone collection page follows the same language as the site.
  // The collection page is for Vietnamese volunteers, so it defaults to Vietnamese until they pick a language.
  const [lang, setLang] = useState<Lang>(() => {
    const saved = store.get('innate.lang')
    return saved === 'vi' || saved === 'en' ? saved : window.location.hash.startsWith('#/collect') ? 'vi' : 'en'
  })
  useEffect(() => { document.documentElement.lang = lang; store.set('innate.lang', lang) }, [lang])
  const hash = useHash()
  return (
    <LangContext.Provider value={{ lang, setLang }}>
      {hash.startsWith('#/collect') ? <Collect /> : <Site />}
    </LangContext.Provider>
  )
}
