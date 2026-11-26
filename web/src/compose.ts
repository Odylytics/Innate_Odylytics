import type { FieldEvent } from './api'

// Records the typed challenge phrase as {t, kind, n, cls} events, never the text. Port of sdk/innate-compose.js (tested there too).
// Phones report Vietnamese Telex/VNI marks as "composition" updates: the field length does not change, so a mark/tone key shows up as
// a `key` event with n = 0. Mobile keyboards do not say which key it was (keyCode 229), so cls is null there; hardware keyboards give it.
// NOT yet verified on real Gboard / iOS keyboards: use sdk/probe.html and compare (docs/plan/innate-challenge-vi.md).
const cls = (c: string): FieldEvent['cls'] => (/\d/.test(c) ? 'digit' : /\s/.test(c) ? 'space' : /\p{L}/u.test(c) ? 'letter' : 'symbol')

export interface Typed { value: string; addEventListener: (t: string, f: (e: any) => void) => void; removeEventListener: (t: string, f: (e: any) => void) => void }

export class ComposeRecorder {
  events: FieldEvent[] = []
  private len: number
  private keyCls: FieldEvent['cls'] | null = null
  private onKey = (e: { keyCode?: number; key?: string }) => {
    const mobile = e.keyCode === 229 || e.key === 'Process' || e.key === 'Unidentified'
    this.keyCls = mobile || !e.key || e.key.length !== 1 ? null : cls(e.key)
  }
  private onInput = (e: { inputType?: string }) => {
    const d = this.el.value.length - this.len
    this.len = this.el.value.length
    const type = e.inputType ?? ''
    const t = this.now()
    if (/^insertFromPaste|^insertFromDrop|^insertReplacementText|^insertFromYank/.test(type) || d > 1) this.events.push({ t, kind: 'paste', n: Math.max(d, 0) })
    else if (d < 0 || /^delete/.test(type)) this.events.push({ t, kind: 'delete', n: Math.abs(d) })
    else if (d === 1) this.events.push({ t, kind: 'key', n: 1, cls: cls(this.el.value.slice(-1)) })
    else this.events.push({ t, kind: 'key', n: 0, ...(this.keyCls ? { cls: this.keyCls } : {}) }) // d === 0: the IME changed what was typed
    this.keyCls = null
  }

  /** now() must be on the same clock as the PIN recorder (ms since the session began) */
  constructor(private el: Typed, private now: () => number) {
    this.len = el.value.length
    el.addEventListener('keydown', this.onKey)
    el.addEventListener('input', this.onInput)
  }

  /** call before sending: a value set without any input event (script, ACTION_SET_TEXT) becomes a `set_text` event */
  finish(): FieldEvent[] {
    if (this.el.value.length !== this.len) { this.events.push({ t: this.now(), kind: 'set_text', n: Math.abs(this.el.value.length - this.len) }); this.len = this.el.value.length }
    this.el.removeEventListener('keydown', this.onKey)
    this.el.removeEventListener('input', this.onInput)
    return this.events
  }
}
