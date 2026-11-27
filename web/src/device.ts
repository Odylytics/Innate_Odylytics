// Device detection for the "website as app" mode. Asks the browser about the input, not the device name (user agents lie;
// iPads report as Macs). A touchscreen phone = a coarse primary pointer on a small screen.

/** a touchscreen phone (not a tablet or a laptop with a touchscreen) */
export function isPhone() {
  return window.matchMedia('(pointer: coarse)').matches && Math.min(window.innerWidth, window.innerHeight) <= 600
}

/** opened from the home screen ("Add to Home Screen"), so there is no browser bar */
export function isInstalled() {
  return window.matchMedia('(display-mode: standalone)').matches || (navigator as Navigator & { standalone?: boolean }).standalone === true
}

export const isIOS = () =>
  !/Android/.test(navigator.userAgent) && (/iPhone|iPad|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1))

/**
 * Phone-first entry: a phone that opens the bare site address (no #/route) lands on the data-collection app (#/collect).
 * Any explicit route (#/ for the landing page, #/demo, #/ops ...) is respected, so shared links and "About Innate" still work.
 * Runs once, before React mounts.
 */
export function phoneFirstEntry() {
  const h = window.location.hash
  if ((h === '' || h === '#') && isPhone()) window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}#/collect`)
}

// Android Chrome fires `beforeinstallprompt` once, often before React mounts, so catch it here and let the page use it later.
type InstallEvent = Event & { prompt: () => Promise<void>; userChoice: Promise<{ outcome: string }> }
let deferred: InstallEvent | null = null
const listeners = new Set<() => void>()
window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferred = e as InstallEvent; listeners.forEach((f) => f()) })
window.addEventListener('appinstalled', () => { deferred = null; listeners.forEach((f) => f()) })
export const canPromptInstall = () => deferred !== null
export function onInstallChange(f: () => void) { listeners.add(f); return () => { listeners.delete(f) } }
export async function promptInstall() {
  if (!deferred) return
  const e = deferred
  deferred = null
  await e.prompt()
  listeners.forEach((f) => f())
}
