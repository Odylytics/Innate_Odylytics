import { describe, expect, it } from 'vitest'
import { ComposeRecorder, type Typed } from './compose'

function fake() {
  const h: Record<string, (e: any) => void> = {}
  return { value: '', addEventListener: (n: string, f: (e: any) => void) => { h[n] = f }, removeEventListener: () => {}, fire: (n: string, e: object = {}) => h[n](e) } as Typed & { fire: (n: string, e?: object) => void }
}

describe('ComposeRecorder', () => {
  it('Gboard Telex: a mark or tone key changes the text without changing its length (n = 0, class unknown)', () => {
    let c = 0
    const el = fake(); const r = new ComposeRecorder(el, () => (c += 100))
    for (const v of ['t', 'tr', 'tro', 'trơ', 'trờ', 'trời']) {
      el.fire('keydown', { keyCode: 229, key: 'Unidentified' }); el.value = v; el.fire('input', { inputType: 'insertCompositionText' })
    }
    expect(r.finish().map((e) => e.n)).toEqual([1, 1, 1, 0, 0, 1])
    expect(r.events[3].cls).toBeUndefined()
  })
  it('records paste, suggestion pick and delete by kind and length only', () => {
    const el = fake(); const r = new ComposeRecorder(el, () => 1)
    el.value = 'hom nay'; el.fire('input', { inputType: 'insertFromPaste' })
    el.value = 'hom na'; el.fire('input', { inputType: 'deleteContentBackward' })
    el.value = 'hom nay troi'; el.fire('input', { inputType: 'insertReplacementText' })
    expect(r.finish().map((e) => [e.kind, e.n])).toEqual([['paste', 7], ['delete', 1], ['paste', 6]])
  })
  it('a value set by script, with no input event, becomes set_text at finish()', () => {
    const el = fake(); const r = new ComposeRecorder(el, () => 1)
    el.value = 'hom nay troi dep qua'
    expect(r.finish().map((e) => [e.kind, e.n])).toEqual([['set_text', 20]])
  })
  it('hardware keyboard (VNI): the mark key carries its class', () => {
    const el = fake(); const r = new ComposeRecorder(el, () => 1)
    el.fire('keydown', { keyCode: 79, key: 'o' }); el.value = 'o'; el.fire('input', { inputType: 'insertText' })
    el.fire('keydown', { keyCode: 54, key: '6' }); el.value = 'ô'; el.fire('input', { inputType: 'insertText' })
    expect(r.finish().map((e) => [e.n, e.cls])).toEqual([[1, 'letter'], [0, 'digit']])
  })
})
