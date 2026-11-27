import { describe, expect, it } from 'vitest'
import { MAX_ENROLL, impostorStopped } from './enrollCurve'

describe('impostorStopped', () => {
  it('uses the measured E30 points and rises with more entries', () => {
    expect(impostorStopped(1).value).toBe(0)
    expect(impostorStopped(3)).toEqual({ value: 1 - 0.503, measured: true })
    let prev = 0
    for (let k = 2; k <= MAX_ENROLL; k++) {
      const { value } = impostorStopped(k)
      expect(value).toBeGreaterThan(prev)
      expect(value).toBeLessThan(1)
      prev = value
    }
    expect(impostorStopped(5).measured).toBe(false)
  })
})
